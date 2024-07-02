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