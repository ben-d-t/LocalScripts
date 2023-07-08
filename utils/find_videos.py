import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
from dotenv import load_dotenv
import os
import openai

# Load .env file
load_dotenv()

def search_videos(verse_input, csv_path='video_data_with_embeddings.csv', n=10):
    # Set OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
        
    # load & inspect dataset
    df = pd.read_csv(csv_path)
    df["embedding"] = df.embedding.apply(eval).apply(np.array)

    verse_embedding = get_embedding(
        verse_input,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, verse_embedding))

    results = (
        df.sort_values("similarity", ascending=False)
        .head(n)[["Full-Title", "Description", "URL"]]
    )
    # Convert the results dataframe into an array of arrays
    results_array = results.values.tolist()

    return results_array