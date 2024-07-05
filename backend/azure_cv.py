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

load_dotenv("azure.env")
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

# remove_background_img = remove_background(image_url)
# remove_background_img.thumbnail((360, 360), Image.Resampling.LANCZOS)
# remove_background_img.save("results/remove_background.jpg")