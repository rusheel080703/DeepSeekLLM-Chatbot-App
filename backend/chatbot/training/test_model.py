import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# ✅ Step 1: Load Base Model
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
).to("cuda")

# ✅ Step 2: Load Prefix Tuned Model
model_path = "/home/ubuntu/deepseekllm_chatbot/backend/chatbot/models/prefix_tuning_model"
model = PeftModel.from_pretrained(base_model, model_path)
model.eval()

# ✅ Step 3: Load Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

print("✅ Model loaded successfully!")

# ✅ Step 4: Test Inference
input_text = "Hello, my name is John Doe, and my account number is 12345."
inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
outputs = model.generate(
    **inputs,
    max_length=100,
    do_sample=True,
    top_k=50,
    top_p=0.9,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("🗨️ Bot Response:", response)
