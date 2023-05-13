import sys
from utils.completion import openai_completion

# Parse command-line arguments
user_message = sys.argv[1]
model = sys.argv[2]
system_prompt = sys.argv[3]
max_tokens = int(sys.argv[4])
temperature = float(sys.argv[5])

# Create the conversation history
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message}
]

# Call the OpenAI API through completion.py
assistant_message = openai_completion(messages, model, max_tokens, temperature)
print("Assistant: " + assistant_message)
