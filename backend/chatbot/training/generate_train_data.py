import json
import random

# Sample lists for random data
names = ["John Doe", "Jane Smith", "Mark Johnson", "Alice Brown", "Robert Lee"]
account_numbers = ["12345", "67890", "98765", "54321", "11223"]
balances = [500, 750, 300, 650, 900]
amounts = [150, 200, 100, 250, 50]
dates_future = ["March 1, 2025", "April 15, 2025", "May 10, 2025", "June 20, 2025"]

# Define varied template examples
templates = [
    {
        "input": "Hello",
        "output": "Hello! I am your Collection Officer. Could you please provide your name and account number so I can check your balance?"
    },
    {
        "input": "Hi, my name is {}",
        "output": "Thank you, {}. May I have your account number, please?"
    },
    {
        "input": "My account number is {}",
        "output": "Great! Your current outstanding balance is ${}. How may I assist you with your payment today?"
    },
    {
        "input": "What is my account balance?",
        "output": "Your outstanding balance is ${}."
    },
    {
        "input": "I want to schedule a payment for {}",
        "output": "Sure! Your payment is scheduled for {}."
    },
    {
        "input": "I want to make a one-time payment of ${}",
        "output": "Okay, I have processed a payment of ${}. Your new balance is updated."
    },
    {
        "input": "Can I set up a recurring payment of ${} on {}?",
        "output": "Recurring payment of ${} has been scheduled starting on {}."
    },
    {
        "input": "I need help with my account",
        "output": "I'd be happy to help. Please provide your name and account number for verification."
    },
    {
        "input": "Bye",
        "output": "Thank you for using our service. If you need any further assistance, feel free to reach out!"
    }
]

# Generate 1000 varied examples
data = []
for _ in range(1000):
    template = random.choice(templates)
    inp = template["input"]
    out = template["output"]

    # Replace placeholders in input and output dynamically
    placeholders = inp.count("{}")
    values = []

    if "name" in inp.lower():
        values.append(random.choice(names))
    if "account number" in inp.lower():
        values.append(random.choice(account_numbers))
    if "$" in inp:
        values.append(random.choice(amounts))
    if "payment for {}" in inp:
        values.append(random.choice(dates_future))
    if "recurring payment of {} on {}" in inp:
        values.append(random.choice(amounts))
        values.append(random.choice(dates_future))

    # Format input with the correct number of arguments
    inp = inp.format(*values)

    # Replace placeholders in output dynamically
    placeholders = out.count("{}")
    values = []

    if "Thank you," in out:
        values.append(random.choice(names))
    if "Your outstanding balance is ${}" in out:
        values.append(random.choice(balances))
    if "a payment of ${}" in out:
        values.append(random.choice(amounts))
    if "Recurring payment of ${} has been scheduled starting on {}" in out:
        values.append(random.choice(amounts))
        values.append(random.choice(dates_future))

    out = out.format(*values)

    data.append({"input": inp, "output": out})

# Save as a flat JSON array
with open("train_data_flat_1000.json", "w") as f:
    json.dump(data, f, indent=4)

print("✅ Training data file created: train_data_flat_1000.json")
