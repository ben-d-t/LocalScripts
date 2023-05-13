import pandas as pd
import openai
import numpy as np
import pickle
from transformers import GPT2TokenizerFast
from transformers import AutoTokenizer
import os
import pinecone
from dotenv import load_dotenv
import sys
from utils.completion import openai_completion


# Load API keys and other parameters
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
openai.api_key = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
QUERY_EMBEDDINGS_MODEL = "text-embedding-ada-002"

MAX_SECTION_LEN = 7000
SEPARATOR = "\n* "
NO_KNOWLEDGE_STRING = "Sorry, I don't know. I can only construct a response based on transcripts from BibleProject Podcast episodes and I can't find an answer."

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
separator_len = len(tokenizer.tokenize(SEPARATOR))

# Parse command-line arguments
user_message = sys.argv[1]
model = sys.argv[2]
system_prompt = sys.argv[3]
max_tokens = int(sys.argv[4])
temperature = float(sys.argv[5])


# This function is used to query the Pinecone index for relevant sections
def request_pinecone_documents(query: str):
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections. 
    
    Return the list of document sections, sorted by relevance in descending order.
    """
    pinecone.init(
        api_key= PINECONE_API_KEY,
        #Double check environment is matching
        environment="us-east1-gcp"
    )

    xq = openai.Embedding.create(input=query, engine=QUERY_EMBEDDINGS_MODEL)['data'][0]['embedding']
    index = pinecone.Index('transcripts')

    # can I change top_k=5 to get more pieces of context?
    res = index.query([xq], top_k=10, include_metadata=True, namespace='bibleprojectpodcast')

    return res["matches"]


# This function constructs the prompt to give to GPT3
def construct_prompt(question: str) -> str:

    most_relevant_document_sections = request_pinecone_documents(question)
    
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []
    sources = []

    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
     
    for section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.        
        document_section = section_index['metadata']['text']
        title = section_index['metadata']['episode_title']
        position = float(section_index['metadata']['position'])

        chosen_sections_len += len(tokenizer.tokenize(document_section)) + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break
            
        chosen_sections.append(SEPARATOR + document_section.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))
        sources.append({"title": title, "position": position, "text": document_section})

    header = f"""You are a helpful AI assistant"""

    # For gpt-3.5-turbo and gpt-4, need a prompt that is an array of objects/dictionaries, each with a role and content
    prompt = []
    
    system_content = {"role": "system", "content": header}
    prompt.append(system_content)

    # Add the prompt and context as the first user prompt
    header2= f"""Answer my question as truthfully as possible based only on the context given below, and if you're at all unsure of the answer from the context, say "{NO_KNOWLEDGE_STRING}" and do not add anything else. Always begin the response with either "Tim Bot" or "Jon Bot" chosen at random. \n\nContext:\n"""
    header2 = header2 + "".join(chosen_sections)
    user_prompt = {"role": "user", "content": header2}
    prompt.append(user_prompt)

    user_question = {"role": "user", "content": question}
    prompt.append(user_question)

    #print(prompt)

    return {"prompt": prompt, "sources": sources}


# This function actually sends the prompt to OpenAI and gets the completion back
def answer_question(question: str) -> str:
    res = construct_prompt(question)
    response = openai_completion(res["prompt"], model, max_tokens, temperature)
    sources = res["sources"]

    if response.find(NO_KNOWLEDGE_STRING) != -1:
        sources = []

    return {"answer": response, "sources": sources}

# Start the conversation loop
def ask_bp():
    while True:
        query = input("What do you want to ask Tim & Jon? -- ")
        response = answer_question(query)
        print(response["answer"])
        try:
            print("For more information see: " + response["sources"][0]["title"])
        except:
            pass

ask_bp()