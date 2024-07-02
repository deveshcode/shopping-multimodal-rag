import os
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import torch
import numpy as np
import logging
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Constants
MODEL_ID = "openai/clip-vit-base-patch32"
INDEX_NAME = "nike-inventory-storage"
MAX_LENGTH = 250

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
logger.info("Pinecone initialized")

def create_pinecone_index():
    logger.info(f"Checking if index '{INDEX_NAME}' exists")
    if INDEX_NAME not in pc.list_indexes().names():
        logger.info(f"Creating new index: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=512,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    else:
        logger.info(f"Index '{INDEX_NAME}' already exists")
    return pc.Index(INDEX_NAME)

def load_model_and_processors():
    logger.info(f"Loading CLIP model and processors from {MODEL_ID}")
    model = CLIPModel.from_pretrained(MODEL_ID)
    processor = CLIPProcessor.from_pretrained(MODEL_ID)
    tokenizer = CLIPTokenizer.from_pretrained(MODEL_ID)
    logger.info("Model and processors loaded successfully")
    return model, processor, tokenizer

def get_image_embedding(image_url, model, processor):
    logger.info(f"Getting image embedding for URL: {image_url}")
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        inputs = processor(images=img, return_tensors="pt", padding=True)
        with torch.no_grad():
            embeddings = model.get_image_features(**inputs).numpy().flatten()
        logger.info("Image embedding generated successfully")
        return embeddings
    except Exception as e:
        logger.error(f"Error getting image embedding: {str(e)}")
        raise

def get_text_embeddings(text, model, tokenizer):
    logger.info("Generating text embeddings")
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        text_embeddings = model.get_text_features(**inputs)
    logger.info("Text embeddings generated successfully")
    return text_embeddings.numpy().flatten()

def split_text(text, max_length=MAX_LENGTH):
    logger.info(f"Splitting text into chunks of max length {max_length}")
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def hierarchical_embedding(text, model, tokenizer, max_length=MAX_LENGTH):
    logger.info("Generating hierarchical embedding")
    chunks = split_text(text, max_length=max_length)
    embeddings = [get_text_embeddings(chunk, model, tokenizer) for chunk in chunks]
    combined_embedding = np.mean(embeddings, axis=0)
    logger.info("Hierarchical embedding generated successfully")
    return combined_embedding

def create_vector(id, embedding, metadata):
    logger.info(f"Creating vector for ID: {id}")
    return {
        'id': str(id),
        'values': embedding.tolist(),
        'metadata': metadata
    }

def process_dataframe(df, index, model, processor, tokenizer):
    logger.info(f"Processing dataframe with {len(df)} rows")
    for i, row in df.iterrows():
        logger.info(f"Processing row {i + 1}/{len(df)}: {row['Title']}")
        
        try:
            # Image embedding
            image_embedding = get_image_embedding(row['Image URL'], model, processor)
            image_vector = create_vector(i, image_embedding, row.to_dict())
            index.upsert([image_vector])
            logger.info(f"Image vector upserted for row {i + 1}")
            
            # # Text embedding
            # text = f"{row['Title']} {row['Details']} {row['Description']} Price {row['Price']}"
            # text_embedding = hierarchical_embedding(text, model, tokenizer)
            # text_vector = create_vector(len(df) + i, text_embedding, row.to_dict())
            # index.upsert([text_vector])
            # logger.info(f"Text vector upserted for row {i + 1}")
        
        except Exception as e:
            logger.error(f"Error processing row {i + 1}: {str(e)}")

def main():
    logger.info("Starting main process")
    
    try:
        # Load data
        df = pd.read_csv('nike_mens_clothing_with_additional_data.csv')
        logger.info(f"Data loaded: {len(df)} rows")
        
        # Initialize Pinecone index
        index = create_pinecone_index()
        logger.info("Pinecone index initialized")
        
        # Load model and processors
        model, processor, tokenizer = load_model_and_processors()
        logger.info("Model and processors loaded")
        
        # Process dataframe
        process_dataframe(df, index, model, processor, tokenizer)
        
        logger.info("All embeddings have been stored in Pinecone")
        stats = index.describe_index_stats()
        logger.info(f"Final index stats: {stats}")
    
    except Exception as e:
        logger.error(f"An error occurred in the main process: {str(e)}")
    
    logger.info("Main process completed")

if __name__ == "__main__":
    main()