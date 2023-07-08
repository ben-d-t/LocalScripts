# TODO -- reject invalid output / be able to handle abbreviations or different cases of verses
# eg kinda like the YV format? 

import sys
import requests
import re
from bs4 import BeautifulSoup
from utils.completion import openai_completion

# Function to get the verse info 
def get_verse_info(verse_ref):
    # Check if input is in correct format
    if not isinstance(verse_ref, str) or ':' not in verse_ref:
        return "Invalid format. Please input a string in the format 'book chapter:verse'."
    
    # Split the verse reference into book name and chapter:verse
    parts = verse_ref.rsplit(' ', 1)
    book_name = parts[0].replace(' ', '_')
    chapter_verse = parts[1].replace(':', '-')
    
    # Format the URL
    url = f"https://biblehub.com/{book_name.lower()}/{chapter_verse}.htm"
    print(url)
    
    # Make a request to the website
    r = requests.get(url)
    r.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup)
    
    # Extract information from div id='par'
    par_div = soup.find(id='par')
    #print(par_div)
    translations = []
    if par_div is not None:
        version_spans = par_div.find_all('span', {'class': 'versiontext'})
        for span in version_spans:
            version_name = span.get_text(strip=True)
            verse_text = span.find_next_sibling(string=True)
            if verse_text is None:
                verse_text = ''  # substitute with '' or any placeholder text
            translations.append({
                'version': version_name,
                'text': verse_text.strip(),
            })
            
    #print(translations)

    # Extract Hebrew or Greek translation
    original_language_heading = soup.find('div', string=re.compile('(Hebrew|Greek)'))
    original_language_spans = []

    if original_language_heading is not None:
        for sibling in original_language_heading.next_siblings:
            # Stop at the next 'vheading' div (which is the 'Links' section)
            if sibling.name == 'div' and sibling.get('class') == ['vheading']:
                break
            # Only consider span tags
            if sibling.name == 'span':
                original_language_spans.append(sibling.get_text(strip=True))

    original_language_translation = ' '.join(original_language_spans)

    # Combine and return information
    translation_strings = []
    for translation in translations:
        translation_strings.append(f"{translation['version']}: {translation['text']}")

    return '\n'.join(translation_strings) + '\n' + original_language_translation


# TESTING
#verse_info = get_verse_info("Genesis 1:1")
#print(verse_info)
#verse_info = get_verse_info("1 John 1:1")
#print(verse_info)


# Function to construct the prompt
def construct_prompt(translations):
    prompt_array = [
        {
            "role": "user",
            "content": "I have multiple English translations of a text, along with the original language."
        },
        {
            "role": "user",
            "content": "I need you to write a short paragraph contrasting where these different translations differ, not where they agree."
        },
        {
            "role": "user",
            "content": "You should focus only on highlighting MAJOR areas of disagreement, not where the texts agree."
        },
        {
            "role": "user",
            "content": "Please identify which words in the original Hebrew or Greek were difficult to translate where relevant."
        },
        {
            "role": "user",
            "content": "The response should be adequate for a biblical studies expert."
        },
        {
            "role": "user",
            "content": translations
        },
        {
            "role": "user",
            "content": "In your response, please include specific examples from the translations provided to illustrate the differences, and reference the original language when appropriate."
        }
        ]
    
    return prompt_array

# Function to run the chat loop
def verse_loop():
    
    # Parse command-line arguments
    if len(sys.argv) < 6:
        # Handle the case when there are not enough command-line arguments
        # Assign default values or prompt the user for input
        model = "gpt-3.5-turbo"
        system_prompt = "You are a helpful AI assistant."
        max_tokens = 1000
        temperature = 0.5
    else:
        try:
            model = sys.argv[2]
            system_prompt = sys.argv[3]
            max_tokens = int(sys.argv[4])
            temperature = float(sys.argv[5])
        except IndexError:
            # Handle the case when there are not enough command-line arguments
            # Assign default values or prompt the user for input
            model = "gpt-3.5-turbo"
            system_prompt = "You are a helpful AI assistant."
            max_tokens = 1000
            temperature = 0.5

    
    # Start the conversation loop
    while True:

        # Create or restart the conversation history
        all_messages = [
            {"role": "system", "content": system_prompt}
            ]

        # Ask for the next user message
        verse_input = input("Verse to look up: ")

        # Check if the user wants to quit
        if verse_input.lower() == "quit":
            break
            
        # Call web scrape on the verse_input -- might throw an error
        bs = get_verse_info(verse_input)
        print(bs)

        # Call construct prompt
        user_messages = construct_prompt(bs)
        #print(user_messages)

        #  Append the user's message to the conversation history
        all_messages.extend(user_messages)

        # Call the OpenAI API through completion.py
        assistant_message = openai_completion(all_messages, model, max_tokens, temperature)

        # Print the assistant's response
        print(f"\nassistant: {assistant_message}\n")


if __name__ == "__main__":
    verse_loop()