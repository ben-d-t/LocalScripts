import sys
from utils.completion import openai_completion

def chat_loop():
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

    # Start the conversation loop
    while True:
        # Call the OpenAI API through completion.py
        assistant_message = openai_completion(messages, model, max_tokens, temperature)

        # Print the assistant's response
        print(f"\nassistant: {assistant_message}\n")

        # Ask for the next user message
        user_message = input("user: ")

        # Check if the user wants to quit
        if user_message.lower() == "quit":
            break

        # Append the user's message to the conversation history
        messages.append({"role": "user", "content": user_message})

if __name__ == "__main__":
    chat_loop()