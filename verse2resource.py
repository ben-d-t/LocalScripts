from utils.find_videos import search_videos
from utils.completion import openai_completion
from utils.get_verse import get_verse_info

def main():

    previous_search_text = None  # To store the previous verse request
    previous_message = ""  # Initialize previous message as an empty string

    while True:        

        # Get user input
        search_text = input("Verse to search ('quit' to exit): ")

        # Quit condition
        if search_text.lower() == 'quit':
            break

        # Get verse info
        verse_text = get_verse_info(search_text)
        
        # Start over if the verse didn't work
        if verse_text.split()[0] == "Invalid":
            print(verse_text)
            continue

        # If the verse is the same as the previous request
        if previous_search_text == search_text:
            messages = [
                {"role": "assistant", "content": previous_message},
                {"role": "user", "content": "Thanks! Please recommend a different resource"}
            ]
            assistant_message = openai_completion(messages)
            print(assistant_message)
            print("\n---\n")
            continue  # Skip to the next iteration
        

        # Print the verse without the original translation (just too long) 
        print("\n---\n")
        # print(verse_text)
        print(verse_text.split('\n')[0])
        print(search_text)
        print("\n---\n")

        # Search videos
        results = search_videos(search_text+" "+verse_text)

        # Print each result
        #print("The most relevant resources are: ")
        #for result in results:
            #print(f'Title: {result[0]}, Description: {result[1]}, URL: {result[2]}')

        #print("\n---\n")

        # Create a single string of the results with line breaks
        result_string = ""
        for result in results:
            result_string += f"Title: {result[0]}\nDescription: {result[1]}\nURL: {result[2]}\n\nNext result\n"


        # Build prompt to ask for recommendation -- this should be an array of objects representing the conversation so far
        messages = [
            {"role": "user", "content": f"""**Task**
                Another agent has selected a set of resources that might be relevant to the text the user wants to understand. 
                Your job is to select one resource from the list and explain why it is relevant.
                Determine which of the following resources would be most helpful to help the user understand the text.
                Respond as if talking to the user. Provide the name of the resource and write two sentences on why that resource would be helpful to understand the text."""},
            {"role": "user", "content": f"**Text**\n{search_text}\n{verse_text}"},
            {"role": "user", "content": f"**Resource Options**\n{result_string}"},
            {"role": "user", "content": f"""**Agent Response**
                Librarian's recommendation: insert title here
                How to view: insert URL here
                Why this one: insert reasoning here""" }
        ]

        # Call the OpenAI API with the messages prmopt using completions.py. That needs to receive a messages array. The function saves the full api call but returns just the string of the chat completion
        #print(messages)
        assistant_message = openai_completion(messages)
        print(assistant_message)
        print("\n---\n")

        # Update the previous verse request and the previous message
        previous_search_text = search_text
        previous_message = assistant_message


if __name__ == "__main__":
    main()
