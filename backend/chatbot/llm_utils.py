# backend/chatbot/llm_utils.py

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load Mistral-7B-Instruct-v0.3 from configuration (.env or settings)
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")

# Load tokenizer and model once at startup.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Global variable for storing the persistent cache.
# In production, you should manage this per-session (e.g., with Django cache or a DB).
PERSISTENT_CACHE = None

def warmup_cache(system_prompt: str):
    """
    Process the system prompt once to pre-warm the key-value cache.
    Returns the computed past_key_values.
    """
    global PERSISTENT_CACHE
    inputs = tokenizer(system_prompt, return_tensors="pt")
    with torch.no_grad():
        output = model(inputs.input_ids, use_cache=True)
    PERSISTENT_CACHE = output.past_key_values
    return PERSISTENT_CACHE

def generate_response(user_input: str, cache=None, max_new_tokens=100):
    """
    Generates a response using the user input and the provided persistent cache.
    Returns the generated response and the updated cache.
    """
    if cache is None:
        cache = PERSISTENT_CACHE  # Use global cache if none is provided

    # Tokenize user input.
    inputs = tokenizer(user_input, return_tensors="pt")
    # Generate response with cache passed in.
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            use_cache=True,
            past_key_values=cache
        )
    # Capture updated cache.
    new_cache = output.past_key_values if hasattr(output, "past_key_values") else cache
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response, new_cache
