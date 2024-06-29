import os
import requests
from PIL import Image
from io import BytesIO
import torch
from transformers import CLIPProcessor, CLIPModel
from pinecone import Pinecone

pc = Pinecone(
    api_key="d3668c25-8ef3-4fe9-b8f0-f02be12cdad5",
)
# Connect to the index
index_name = "nike-inventory-storage3"
index = pc.Index(index_name)

# Load CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Define function to get image embedding
def get_image_embedding(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    inputs = processor(images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_image_features(**inputs).numpy().flatten()
    return embeddings

# Define function to get image embedding from a local file
def get_image_embedding_local(image_path):
    img = Image.open(image_path).convert("RGB")
    inputs = processor(images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_image_features(**inputs).numpy().flatten()
    return embeddings

# Function to search by local image
def search_by_image_local(image_path):
    embedding = get_image_embedding_local(image_path)
    result = index.query([embedding.tolist()], top_k=10)
    return result

# Define function to get text embedding
def get_text_embedding(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_text_features(**inputs).numpy().flatten()
    return embeddings

# Function to search by image
def search_by_image(image_url,n):
    embedding = get_image_embedding(image_url)
    result = index.query(  [embedding.tolist()    ], top_k=n)
    return result

# Function to search by text
def search_by_text(text,n):
    embedding = get_text_embedding(text)
    result = index.query(vector=embedding.tolist(), top_k=n,include_metadata=True)
    return result

# # Search by image
# print("Searching by image...")
# image_search_results = search_by_image_local(image_url)
# for match in image_search_results.matches:
#     print(f"ID: {match.id}, Score: {match.score}, Metadata: {match.metadata}")

import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt

# Load the CSV file

# Function to display image based on ID from CSV
def display_image_by_id(match):
    image_url=match.metadata['Image URL']
    print(image_url)
    #Load and display the image
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    plt.imshow(img)
    plt.axis('off')
    plt.title(f"Title: {match.metadata['Title']}\nDetails: {match.metadata['Details']}\nDescription: {match.metadata['Description']}\nPrice: {match.metadata['Price']}")
    plt.show()
text_query = "black nike sportswear"

# Search by text
print("Searching by text...")
n=5
text_search_results = search_by_text(text_query,n)
for match in text_search_results.matches:
    image_id = match.id  # Replace with the desired ID from the search results
    print(f"ID: {match.id}, Score: {match.score} , Metadata:{match.metadata}")# Example usage
    display_image_by_id(match)