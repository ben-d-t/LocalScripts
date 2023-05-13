import openai
import sys
import time
import json
import datetime
import os
from dotenv import load_dotenv

# Set up OpenAI API Key
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_completion(messages, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.5):
    # Call the OpenAI API
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )

    # Extract the assistant's response
    assistant_message = response['choices'][0]['message']['content']

    # Append the assistant's response to the messages
    messages.append({"role": "assistant", "content": assistant_message})

    # Create the input object with all the parameters used to call the API
    api_input = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages
    }

    # Create an array with two objects, where [0] is the input and [1] is the output
    api_call_data = [api_input, response]

    # Create the "responses" folder if it doesn't exist
    # Note this depends on where ai.sh is located / being run from
    folder_name = "responses" 
    os.makedirs(folder_name, exist_ok=True)

    # Save the full response and input to a timestamped .txt file within the "responses" folder
    current_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S")
    filename = os.path.join(folder_name, f"{current_time}.txt")
    with open(filename, 'w') as file:
        json.dump(api_call_data, file, indent=2)

    return assistant_message