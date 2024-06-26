import streamlit as st
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests
import torch
from pinecone import Pinecone
import os
from io import BytesIO
import pandas as pd
import pydotenv
rdf = pd.read_csv('nike_mens_clothing_with_additional_data.csv')


pydotenv.load_dotenv()

# Initialize Pinecone
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
)
index_name = "nike-inventory"
index = pc.Index(index_name)

# Load CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Helper function to get text embeddings
def get_text_embedding(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_text_features(**inputs).numpy().flatten()
    return embeddings

# Helper function to get image embeddings from a local file
def get_image_embedding_local(image_path):
    img = Image.open(image_path).convert("RGB")
    inputs = processor(images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_image_features(**inputs).numpy().flatten()
    return embeddings

# Helper function to get image embeddings from a URL
def get_image_embedding(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    inputs = processor(images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        embeddings = model.get_image_features(**inputs).numpy().flatten()
    return embeddings

# Function to display search results in a conversational format
def display_results(results):
    for match in results['matches']:
        row = rdf.iloc[int(match['id'])]
        st.markdown(f"Hey, here's what I found. It's a {row['Description']} and it's priced at {row['Price']}.")
        st.image(row['Image URL'], width=150)
        st.markdown(f"[Product Link]({row['Product URL'][20:]})")
        st.markdown("---")

# Streamlit app structure
st.title("Nike Product Search Bot")
st.write("Welcome to the Nike Product Search Bot! How can I help you today?")

# Initialize session state for conversation context
if 'last_query' not in st.session_state:
    st.session_state['last_query'] = None

# Scenario 1: Text search
query = st.text_input("Enter your search query")
if query:
    embedding = get_text_embedding(query)
    results = index.query(vector=embedding.tolist(), top_k=2)
    display_results(results)
    st.session_state['last_query'] = query

# Scenario 2: Image upload and search
uploaded_file = st.file_uploader("Upload an image of the product you're looking for")
if uploaded_file:
    embedding = get_image_embedding_local(uploaded_file)
    results = index.query(vector=embedding.tolist(), top_k=10)
    display_results(results)
    st.session_state['last_query'] = "image_search"

# Scenario 3: Follow-up queries
follow_up_query = st.text_input("Ask a follow-up question based on the results above")
if follow_up_query and st.session_state['last_query']:
    if st.session_state['last_query'] == "image_search":
        # Handle follow-up for image search (assuming it refers to the last displayed results)
        pass
    else:
        # Refine the previous text query
        refined_query = f"{st.session_state['last_query']} {follow_up_query}"
        embedding = get_text_embedding(refined_query)
        results = index.query(vector=embedding.tolist(), top_k=10)
        display_results(results)
        st.session_state['last_query'] = refined_query
