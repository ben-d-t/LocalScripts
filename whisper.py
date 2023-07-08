import openai
import os
from dotenv import load_dotenv

# Set up OpenAI API Key
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ask for file path as input
file_path = input("Enter the file path: ")

# Check if the file extension is valid
valid_extensions = ["mp3", "mp4", "mpeg", "mega", "m4a", "wav", "web"]
file_extension = file_path.split(".")[-1]
if file_extension not in valid_extensions:
    print("Error: Invalid file format. Supported formats are: mp3, mp4, mpeg, mega, m4a, wav, web.")
    exit()

# Open the audio file
audio_file = open(file_path, "rb")

# Transcribe the audio
transcript = openai.Audio.transcribe("whisper-1", audio_file)

# Extract the text from the transcript
text = transcript['text']
print(text)

# Remove the file extension from the input file name
output_file_name = os.path.splitext(os.path.basename(file_path))[0]

# Save the transcript as a .txt file in the same directory as the input file
output_file_path = os.path.join(os.path.dirname(file_path), output_file_name + ".txt")
with open(output_file_path, "w") as output_file:
    output_file.write(text)

print("Transcript saved as:", output_file_path)