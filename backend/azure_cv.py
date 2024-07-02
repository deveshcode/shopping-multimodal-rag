import glob
import json
import os
import requests
import sys
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse
from gradio_client import Client, handle_file
from typing import Dict, Any, Optional, BinaryIO
from google.cloud import storage
import logging
from openai import OpenAI

load_dotenv()
key = os.getenv("azure_cv_key")
endpoint = os.getenv("azure_cv_endpoint")

url = endpoint + "/computervision/imageanalysis:segment?api-version=2023-02-01-preview"
background_removal = "&mode=backgroundRemoval"
foreground_matting = "&mode=foregroundMatting"

remove_background_url = url + background_removal  # For removing the background
get_mask_object_url = url + foreground_matting  # Mask of the object

headers = {"Content-type": "application/json", 
            "Ocp-Apim-Subscription-Key": key}

IMAGES_DIR = "images"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

load_dotenv("azure.env")
BUCKET_NAME = os.getenv('BUCKET_NAME')
project_id = os.getenv('PROJECT_ID')
SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 
UPLOAD_FOLDER = "raw_images"
PROCESSED_FOLDER = "processed_images"

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_blob(source_file_name: str, destination_blob_name: str, bucket_name: str = BUCKET_NAME) -> Optional[str]:
    """Uploads a file to Google Cloud Storage and returns its public URL."""
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name, if_generation_match=0)
        logger.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
        
        blob.make_public()
        return blob.public_url
    except Exception as e:
        logger.error(f"Error uploading file to GCS: {e}")
        return None

def remove_background(image_url):
    """
    Removing background
    """
    image = {"url": image_url}
    r = requests.post(remove_background_url, data=json.dumps(image), headers=headers)

    object_image = os.path.join(
        RESULTS_DIR, "object_" + os.path.basename(urlparse(image_url).path)
    )
    with open(object_image, "wb") as f:
        f.write(r.content)
    # Save the processed image in the 'images' folder
    image_path = os.path.join('images', 'processed_image.png')
    remove_background_img = Image.open(object_image)
    remove_background_img.save(image_path)
    return Image.open(object_image)



def get_caption(processed_img_url):    
    client = Client("gokaygokay/Florence-2-SD3-Captioner")
    result = client.predict(
            image=handle_file(processed_img_url),
            api_name="/run_example"
    )
    return result



# Load environment variables
BUCKET_NAME = os.getenv('BUCKET_NAME')
project_id = os.getenv('PROJECT_ID')
azure_cv_key = os.getenv("azure_cv_key")
azure_cv_endpoint = os.getenv("azure_cv_endpoint")

# Azure Computer Vision setup
url = azure_cv_endpoint + "/computervision/imageanalysis:segment?api-version=2023-02-01-preview&mode=backgroundRemoval"
headers = {
    "Content-type": "application/json",
    "Ocp-Apim-Subscription-Key": azure_cv_key
}

# Define response model

# Function to upload to Google Cloud Storage
def upload_blob(source_file_name: str, destination_blob_name: str, bucket_name: str = BUCKET_NAME) -> Optional[str]:
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name, if_generation_match=0)
        logger.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
        
        blob.make_public()
        return blob.public_url
    except Exception as e:
        logger.error(f"Error uploading file to GCS: {e}")
        return None

# Function to remove background
def remove_background(image_url):
    image = {"url": image_url}
    r = requests.post(url, data=json.dumps(image), headers=headers)

    if r.status_code != 200:
        logger.error(f"Error removing background: {r.status_code}, {r.text}")
        return None

    image_path = 'processed_image.png'
    with open(image_path, "wb") as f:
        f.write(r.content)
    
    return image_path

# Function to get image caption
def get_caption(image_url):
    client = Client("gokaygokay/Florence-2-SD3-Captioner")
    result = client.predict(
        image=handle_file(image_url),
        api_name="/run_example"
    )
    return result

# Function to combine captions using GPT-3.5
def combine_captions(user_caption, product_caption):
    prompt = f"""
    I want you to create an combined caption using 2 prompts. 

    From the first prompt I want you to extract details of clothing item. Ignore the person's features only focus on the clothing item:
    {product_caption}

    From the second prompt I want you to extract details of the person. Ignore the clothing item they have worn and focus on the person's features:
    {user_caption}

    Then give me a merged prompt combining the clothing and the person's attributes. The prompt should be a detailed description of the person wearing the clothing item using the same words from the above captions.
    """
    system_prompt = """
    You are a helpful fashion assistant for Nike products.
    """
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

# # Function to generate image using DALL-E
def generate_image(prompt):
    logger.info(f"Generating image with prompt: {prompt}")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    print
    logger.info(f"Generated image Internal URL: {response.data[0].url}")
    return response.data[0].url

# Main function to build virtual try-on
async def build_virtual_try_on(user_image_url, product_image_url):
    # Remove background from user image
    logger.info(f"Removing background from user image: {user_image_url}")
    processed_user_image = remove_background(user_image_url)

    logger.info(f"Processed user image: {processed_user_image}")
    if not processed_user_image:
        return None

    # Upload processed user image
    logger.info("Uploading processed user image to GCS...")
    processed_user_image_url = upload_blob(processed_user_image, f"processed_user_image_{os.path.basename(user_image_url)}")

    logger.info(f"Processed user image URL: {processed_user_image_url}")
    if not processed_user_image_url:
        return None

    # Get captions
    logger.info("Getting captions for user and product images...")
    user_caption = get_caption(processed_user_image_url)
    product_caption = get_caption(product_image_url)

    logger.info(f"User caption: {user_caption}")
    logger.info(f"Product caption: {product_caption}")

    # Combine captions
    logger.info("Combining captions...")
    combined_prompt = combine_captions(user_caption, product_caption)
    logger.info(f"Combined prompt: {combined_prompt}")

    # Generate image
    logger.info("Generating image...")
    generated_image_url = "dummpy_image_url_from_build"
    generated_image_url = generate_image(combined_prompt)

    logger.info(f"Generated image URL: {generated_image_url}")
    response = requests.get(generated_image_url)

    logger.info(f"Downloading generated image...")
    if response.status_code == 200:
        logger.info("Saving generated image...")
        with open("generated_image.png", "wb") as f:
            f.write(response.content)
        
        logger.info("Uploading generated image to GCS...")
        final_image_url = upload_blob("generated_image.png", f"virtual_try_on_{os.path.basename(user_image_url)}")
        return final_image_url
    else:
        logger.error(f"Failed to download generated image: {response.status_code}")
        return None
    

    