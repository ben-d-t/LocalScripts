import json
import sys
import os
import re
from utils.completion import openai_completion

# Ask the user for the name or path of a file to load
filename = input("Please enter the name or path of the file to load: ")

# Remove escape characters from the filename
filename = re.sub(r'\\(.)', r'\1', filename)

# Remove trailing space, if present
filename = filename.strip()

# Check if the input contains the full path
if not os.path.isabs(filename):
    # Append the 'responses/' directory path if the input is just the filename
    filename = os.path.join('responses', filename)

# Append '.txt' to the filename if it's not already there
if not filename.endswith('.txt'):
    filename = filename + '.txt'

# Try to open the file
try:
    with open(filename, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"File '{filename}' not found.")
    sys.exit(1)

# Get the parameters and conversation history from the loaded data
api_input = data[0]
model = api_input["model"]
max_tokens = api_input["max_tokens"]
temperature = api_input["temperature"]
messages = api_input["messages"]

# Print the conversation history
for message in messages:
    print(f"\n{message['role']}: {message['content']}")

# Start the conversation loop
while True:
    # Ask for the next user message
    user_message = input("\nuser: ")

    # Check if the user wants to quit
    if user_message.lower() == "quit":
        break

    # Append the user's message to the conversation history
    messages.append({"role": "user", "content": user_message})

    # Call the OpenAI API through completion.py
    assistant_message = openai_completion(messages, model, max_tokens, temperature)

    # Print the assistant's response
    print(f"\nassistant: {assistant_message}")