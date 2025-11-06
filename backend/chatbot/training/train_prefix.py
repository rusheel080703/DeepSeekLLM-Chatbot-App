import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from peft import PrefixTuningConfig, get_peft_model, TaskType
from transformers import TrainingArguments, Trainer, DataCollatorForSeq2Seq

# ✅ Step 1: Load DeepSeek-R1 Model without Quantization Issues
model_name = "mistralai/Mistral-7B-Instruct-v0.3"  # or replace with your chosen model name

# Load configuration with trust_remote_code enabled
config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
# Remove the quantization_config attribute if it exists
if hasattr(config, "quantization_config"):
    delattr(config, "quantization_config")

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    config=config,
    trust_remote_code=True,  # Required for models with custom code
    torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
# ✅ Set padding token if missing
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("✅ Base model loaded successfully!")

# ✅ Step 2: Load and Reduce Dataset Size for Faster Training
dataset = load_dataset("json", data_files={"train": "train_data_fixed.json"})
# Use only 500 examples (adjust as needed)
dataset["train"] = dataset["train"].shuffle(seed=42).select(range(500))

# ✅ Step 3: Tokenize Dataset
def tokenize_function(examples):
    full_texts = [f"<|user|>\n{inp}\n<|assistant|>\n{out}" 
                  for inp, out in zip(examples["input"], examples["output"])]
    tokenized = tokenizer(full_texts, truncation=True, padding="max_length", max_length=256)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["input", "output"])
print("✅ Dataset loaded and tokenized!")

# ✅ Step 4: Apply Prefix Tuning
peft_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,  # Use 20 prefix tokens for efficiency
    token_dim=model.config.hidden_size
)

model = get_peft_model(model, peft_config)
model.print_trainable_parameters()
print("✅ Prefix tuning applied!")

# ✅ Step 5: Training Setup
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="no",
    save_strategy="epoch",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=2,
    max_steps=1000,
    logging_dir="./logs",
    logging_steps=10,
    save_total_limit=1,
    fp16=False,  # Disable fp16; use bf16 if supported
    bf16=torch.cuda.is_bf16_supported(),
    gradient_accumulation_steps=2,
    load_best_model_at_end=False,
    remove_unused_columns=False,
)

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# ✅ Step 6: Start Training
trainer.train()

# ✅ Step 7: Save Model
save_path = "/home/ubuntu/deepseekllm_chatbot/backend/chatbot/models/prefix_tuning_model"
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)

print(f"✅ Training Completed! Model saved at {save_path}")
