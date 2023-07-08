# TODO -- reject invalid output / be able to handle abbreviations or different cases of verses
# eg kinda like the YV format? 

import sys
import requests
import re
from bs4 import BeautifulSoup, NavigableString, Tag

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
    #print(url)
    
    # Make a request to the website
    try:
        r = requests.get(url)
        r.raise_for_status()
    except:
        return "Invalid format. Please input a string in the format 'book chapter:verse'."

    # Parse HTML
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Extract information from div id='par'
    par_div = soup.find(id='par')
    nasb_translation = None
    if par_div is not None:
        version_spans = par_div.find_all('span', {'class': 'versiontext'})
        for span in version_spans:
            version_name = span.get_text(strip=True)
            if version_name == "New American Standard Bible":
                verse_text = ""
                content_flag = False  # A flag to start recording text
                for content in span.parent.contents:
                    if content == span:
                        content_flag = True
                        continue
                    if content_flag:
                        if (content.name == "span" and ('versiontext' in content.get('class', []) or 'p' in content.get('class', []))):
                            # Stop if we encounter the next 'versiontext' span or 'p' span
                            break
                        if type(content) == NavigableString:  # Direct text
                            verse_text += content + " "
                        elif type(content) == Tag:  # Tagged text
                            for string in content.stripped_strings:
                                verse_text += string + " "
                verse_text = verse_text.strip()  # strip the final text to remove leading/trailing whitespace
                nasb_translation = {
                    'version': version_name,
                    'text': verse_text,
                }
                break

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
    if nasb_translation is not None:
        #print(nasb_translation['text'])
        formatted_text = nasb_translation['text'].replace('\n', '')
        return f"{formatted_text}\n{original_language_translation}"
    else:
        return original_language_translation
