import json

# Load the existing JSON file
with open("train_data.json", "r") as f:
    data = json.load(f)

# Check if the data is already in the correct format
if isinstance(data, dict) and "train" in data and isinstance(data["train"], list):
    fixed_data = data["train"]  # Extract only the list of examples
else:
    raise ValueError("The dataset format is incorrect. Expected {'train': [...] } structure.")

# Save the corrected dataset in proper list format
with open("train_data_fixed.json", "w") as f:
    json.dump(fixed_data, f, indent=4)

print("✅ Fixed dataset saved as train_data_fixed.json")
