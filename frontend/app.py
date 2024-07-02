import streamlit as st
from dotenv import load_dotenv
import os
import requests
import json
import logging
from langchain_openai import ChatOpenAI
from langchain.chains.openai_functions.openapi import get_openapi_chain
from openai import OpenAI
from langchain_core.exceptions import OutputParserException
import random
import datetime
from typing import Dict, Any, Optional, BinaryIO
from google.cloud import storage

# List of spinner messages
spinner_messages = [
    "Analyzing the latest trends...",
    "Curating the perfect match for you...",
    "Consulting the fashion gurus...",
    "Searching the style vault...",
    "Finding the best options just for you...",
    "Matching your style preferences...",
    "Scouring the fashion universe...",
    "Crafting the ideal outfit...",
    "Evaluating the latest collections...",
    "Piecing together your perfect look..."
]
UPLOAD_FOLDER = "uploads"
BUCKET_NAME = os.getenv('BUCKET_NAME')

# Select a random spinner message
spinner_message = random.choice(spinner_messages)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_HOST = "http://localhost:8001"  # Update this to your FastAPI host

def upload_blob(source_file_name: str, destination_blob_name: str, bucket_name: str = BUCKET_NAME) -> Optional[str]:
    """Uploads a file to Google Cloud Storage and returns its public URL."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name, if_generation_match=0)
        logger.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
        
        blob.make_public()
        return blob.public_url
    except Exception as e:
        logger.error(f"Error uploading file to GCS: {e}")
        return None

def save_uploaded_file(uploaded_file) -> Optional[str]:
    """Saves the uploaded file and returns its public URL."""
    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_identifier = f"{current_datetime}_{uploaded_file.name}"
    
    if file_identifier in st.session_state.file_identifiers:
        return st.session_state.file_identifiers[file_identifier]
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    destination_blob_name = f"{UPLOAD_FOLDER}/{file_identifier}"
    public_url = upload_blob(file_path, destination_blob_name)
    
    if public_url:
        st.session_state.file_identifiers[file_identifier] = public_url
    
    return public_url

def chat_with_gpt(user_prompt, chat_history):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system_prompt = """
    You are a helpful fashion assistant for Nike products. Guide the user and answer their questions. Give general advice.
    """
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def send_to_api(prompt, file_url=None):
    logger.info(f"Sending prompt to API: {prompt}")
    # Create the LLM instance
    llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
    # URL of the local FastAPI OpenAPI documentation
    openapi_url = f"{API_HOST}/openapi.json"

    # Fetch the OpenAPI spec to ensure it's accessible
    def fetch_openapi_spec(url):
        logger.info(f"Fetching OpenAPI spec from: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch OpenAPI JSON. Status code: {response.status_code}")
            raise ValueError(f"Failed to fetch OpenAPI JSON. Status code: {response.status_code}")
        return response.json()
    
    try:
        openapi_spec_json = fetch_openapi_spec(openapi_url)
        # Manually add the base URL to the OpenAPI spec
        base_url = API_HOST
        if "servers" not in openapi_spec_json:
            openapi_spec_json["servers"] = [{"url": base_url}]
        else:
            openapi_spec_json["servers"].append({"url": base_url})
        
        # Save the updated OpenAPI spec to a temporary file
        with open("updated_openapi.json", "w") as f:
            json.dump(openapi_spec_json, f)
        
        logger.info("Updated OpenAPI spec saved to 'updated_openapi.json'")
        
        # Create the chain using the updated OpenAPI spec file
        chain = get_openapi_chain(spec="updated_openapi.json", llm=llm, verbose=True)
        
        # Example query to the /search_similar endpoint
        query = prompt
        if file_url:
            query = query + f" For the following image: {file_url}"
        
        logger.info(f"Querying chain with prompt: {query}")
        response = chain(query)
        logger.info(f"Received response from chain: {response}")
        return response
    except OutputParserException as e:
        logger.error(f"Error occurred during API request: {e}")
        return chat_with_gpt(prompt, st.session_state.messages)
    except Exception as e:
        logger.error(f"Error occurred during API request: {e}")
        return f"Error: {e}"

def display_results(response):
    logger.info(f"Displaying results: {response}")
    products = response.get('response').get('products', [])
    if not products:
        return "No similar products found."
    
    result_str = "<div style='font-size: 15px;'><br>"
    for product in products:
        metadata = product.get('metadata', {})
        description = metadata.get('Description', 'N/A')
        if "Shown:" in description:
            description = description.split("Shown:")[0].strip()
        
        result_str += f"We have this {metadata.get('Details', 'product')}, titled '{metadata.get('Title', 'N/A')}'. "
        result_str += f"{description}. "
        result_str += f"It's priced at {metadata.get('Price', 'N/A')}. "
        result_str += f"If you want to buy it, <a href='{metadata.get('Product URL', '#')[20:]}'>here's the link</a>.<br>"
        result_str += "If you want to virtual try on, let me know by typing the word 'virtual try'.<br>"
        result_str += f"<img src='{metadata.get('Image URL', '')}' width='300'><br>"
        result_str += "<hr>"
    result_str += "</div>"
    
    return result_str

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "image_url" not in st.session_state:
    st.session_state.image_url = None
if "file_identifiers" not in st.session_state:
    st.session_state.file_identifiers = {}
if "virtual_try_on_flag" not in st.session_state:
    st.session_state.virtual_try_on_flag = False
if "last_product_image_url" not in st.session_state:
    st.session_state.last_product_image_url = None

# Sidebar for image upload
st.sidebar.title("Upload Image")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Save the uploaded file to a local directory and upload to GCS
    public_url = save_uploaded_file(uploaded_file)
    if public_url:
        st.session_state.image_url = public_url
        st.sidebar.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

# Title and initial message
st.title("Nike Fashion Assistant")
st.write("Welcome to the Nike Fashion Assistant! You can chat with me to get fashion advice, find similar products, and even try on items virtually. Upload an image of a product you're interested in, or just ask me a question!")

# Chat interface
if prompt := st.chat_input("Chat with the Nike fashion assistant or ask about the displayed items"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    logger.info(f"User prompt: {prompt}")
    
    if "virtual try" in prompt.lower():
        st.session_state.virtual_try_on_flag = True
        if st.session_state.image_url:
            st.session_state.messages.append({"role": "assistant", "content": "Just before we begin, can you confirm if that's your photo on the left which you want to try? Please type 'Yes' to confirm."})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Please upload your photo first using the sidebar option. Once you've uploaded your photo, type 'done' to proceed."})
    elif st.session_state.virtual_try_on_flag and (prompt.lower() == 'yes' or prompt.lower() == 'done'):
        user_image_url = st.session_state.image_url
        product_image_url = st.session_state.last_product_image_url
        if product_image_url:
            with st.spinner("Processing virtual try-on..."):
                response = send_to_api(f"I want to virtual try on {product_image_url} : {user_image_url}")
                try:
                    response_data = response.get('response', {})
                    virtual_try_on_image = response_data.get('virtual_try_on_image')
                    if virtual_try_on_image:
                        message = f"""
                        Here's how you would look in this, and I think you look amazing!
                        <br><img src="{virtual_try_on_image}" style="max-width: 100%; height: auto;">
                        """
                        st.session_state.messages.append({"role": "assistant", "content": message})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't generate a virtual try-on image."})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {str(e)}"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't find the product image. Please try searching for a product first."})
    else:
        with st.spinner(spinner_message):
            response = send_to_api(prompt, st.session_state.image_url)
        
        # After getting the response, store the last product image URL
        if isinstance(response, dict) and "response" in response:
            products = response.get('response', {}).get('products', [])
            if products:
                st.session_state.last_product_image_url = products[0].get('metadata', {}).get('Image URL', '')
        
        # Display the response
        if isinstance(response, dict) and "response" in response:
            logger.info(f"Response is a dict")
            if response.get('response').get('status') == 'success' and 'fetch_similar' in response.get('response').get('api').lower():
                logger.info(f"Displaying similar results")
                results_str = display_results(response)
                st.session_state.messages.append({"role": "assistant", "content": results_str})
            elif response.get('response').get('status') == 'success' and response.get('response').get('api') == 'chat_fashion':
                logger.info(f"Displaying chat response")
                st.session_state.messages.append({"role": "assistant", "content": response.get('response').get('response')})
            else:
                logger.info(f"Displaying virtual try-on image")
                st.session_state.messages.append({"role": "assistant", "content": "Virtual try-on image: " + response.get('response', {}).get('virtual_try_on_image', 'Not available')})
        else:
            logger.info(f"Displaying chat response")
            st.session_state.messages.append({"role": "assistant", "content": str(response)})

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)