import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Use a smaller model for faster load times (e.g., Ministral-3B-Instruct)
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"  # Update this if needed
# Note: The use_auth_token argument is deprecated; you may replace it with token=YOUR_TOKEN if necessary.
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_auth_token=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_auth_token=True)

# Define the system instruction for the collections officer persona.
SYSTEM_PROMPT = (
    "You are a professional collections officer. Be firm yet empathetic, provide clear payment instructions, "
    "and always remain courteous and compliant with regulatory guidelines."
)

class ChatbotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.accept()
            # Store the system prompt separately.
            self.system_prompt = SYSTEM_PROMPT
            # Initialize conversation history as empty.
            self.chat_history = []
            # Send an initial greeting.
            await self.send(text_data=json.dumps({
                "message": "Hello, I'm your collections assistant. How can I help you today?"
            }))
            logging.info("Connection accepted and greeting sent.")
        except Exception as e:
            logging.error(f"Connect error: {e}")
            await self.close()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            user_message = data.get("message", "").strip()
            if not user_message:
                return

            logging.info(f"Received user message: {user_message}")

            # For the first user message, combine the system prompt and the user message.
            if not self.chat_history:
                combined = f"{self.system_prompt} {user_message}"
                self.chat_history.append({"role": "user", "content": combined})
            else:
                self.chat_history.append({"role": "user", "content": user_message})

            # Format the chat history using the tokenizer's helper.
            encoding = tokenizer.apply_chat_template(self.chat_history, return_tensors="pt")
            # Check if encoding is a dict; if not, treat it as a tensor.
            if isinstance(encoding, dict):
                input_ids = encoding.get("input_ids")
                attention_mask = encoding.get("attention_mask")
                if attention_mask is None:
                    attention_mask = torch.ones_like(input_ids)
            else:
                input_ids = encoding
                attention_mask = torch.ones_like(input_ids)

            logging.debug(f"Formatted input_ids: {input_ids}")

            # Generate a response using model.generate in an executor.
            loop = asyncio.get_running_loop()
            generated_ids = await loop.run_in_executor(
                None,
                lambda: model.generate(
                    input_ids, 
                    attention_mask=attention_mask, 
                    max_new_tokens=5, 
                    do_sample=False
                )
            )

            response_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
            logging.info(f"Generated response: {response_text}")

            # Append the assistant's response to the conversation history.
            self.chat_history.append({"role": "assistant", "content": response_text})
            await self.send(text_data=json.dumps({"message": response_text}))
        except Exception as e:
            logging.error(f"Receive error: {e}")
            await self.send(text_data=json.dumps({"error": "Internal server error"}))

    async def disconnect(self, close_code):
        logging.info(f"WebSocket disconnected with code: {close_code}")
