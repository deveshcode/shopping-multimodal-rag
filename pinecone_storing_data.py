import os
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import torch
# import torchvision.transforms as transforms
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from pinecone import Pinecone, ServerlessSpec

# Load the CSV file
df = pd.read_csv('nike_mens_clothing_with_additional_data.csv')


df['textual']= df['Title'] + ' ' + df['Details'] + ' '+ df['Description']  + ' '+ 'Price' +'  '+ df['Price']
#embedding len issue (max 81)
#df = df[5:] # Limit the number of products for demonstration

# Initialize Pinecone with the new API
pc = Pinecone(
    api_key="d3668c25-8ef3-4fe9-b8f0-f02be12cdad5",
)
# Create Pinecone index

#pc.delete_index("nike-inventory-storage")

index_name = "nike-inventory-storage3"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=512,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# Connect to the index
index = pc.Index(index_name)

model_ID="openai/clip-vit-base-patch32"
# Load CLIP model and processor
model = CLIPModel.from_pretrained(model_ID)
processor = CLIPProcessor.from_pretrained(model_ID)
tokenizer = CLIPTokenizer.from_pretrained(model_ID)

# Define a function to get the image embeddings
def get_image_embedding(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    inputs = processor(images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_image_features(**inputs).numpy().flatten()
    return embeddings




# Loop through each row and process the image
for ind, row in df.iterrows():
    print(f"Processing {ind + 1}/{len(df)}: {row['Title']}")
    image_url = row['Image URL']
    embedding = get_image_embedding(image_url)
    # text_embedding=get_text_embeddings(row['textual'])
    
    # Create a vector with the embedding
    vector = {
        'id': str(ind),  # You can use any unique identifier
        'values': embedding.tolist(),
        'metadata': {
            'Title': row['Title'],
            'Details': row['Details'],
            'Description': row['Description'],
            'Price': row['Price'],
            'Product URL': row['Product URL'],
            'Image URL':row['Image URL']
        }
    }
    print(index)
    # Upsert the vector into Pinecone
    index.upsert([vector])

print("Image Embeddings have been stored in Pinecone.")
print('stats after inserting image embeddings', print(index.describe_index_stats()))

# Define a function to get the text embeddings
import numpy as np
import torch
MAX_LENGTH = 250  # Adjust based on your model's max length
def get_text_embeddings(text):
    inputs = tokenizer(text, return_tensors = "pt")
    text_embeddings = model.get_text_features(**inputs)
    with torch.no_grad():
        embedding_as_np = text_embeddings.numpy().flatten()
    return embedding_as_np


def split_text(text, max_length=MAX_LENGTH):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def hierarchical_embedding(text, max_length=MAX_LENGTH):
    chunks = split_text(text, max_length=max_length)
    embeddings = [get_text_embeddings(chunk) for chunk in chunks]
    combined_embedding = np.mean(embeddings, axis=0)
    return combined_embedding

i=len(df)+1
for ind, row in df.iterrows():
    print(f"Processing {ind + 1}/{len(df)}: {row['Title']}")
    image_url = row['Image URL']
    text_embedding=hierarchical_embedding(row['textual'])
  
    # Create a vector with the embedding
    vector = {
        'id': str(i),  # You can use any unique identifier
        'values': text_embedding.tolist(),
        'metadata': {
            'Title': row['Title'],
            'Details': row['Details'],
            'Description': row['Description'],
            'Price': row['Price'],
            'Product URL': row['Product URL'],
            'Image URL':row['Image URL']
        }

    }

    i=i+1
    # Upsert the vector into Pinecone
    index.upsert([vector])

print("Text Embeddings have been stored in Pinecone.")
print(index.describe_index_stats())
