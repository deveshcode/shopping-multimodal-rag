from fastapi import FastAPI, UploadFile, File, Query
from pydantic import BaseModel, Field
import logging
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict
from search_query import search_by_text, search_by_image
from azure_cv import build_virtual_try_on

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS
origins = [
    "http://127.0.0.1",
    "http://localhost:8001",
    "http://localhost:8501",  
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8501"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_gpt(user_prompt, chat_history):
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


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Logging configured")

class VirtualTryOnResponse(BaseModel):
    status: str
    api: str
    virtual_try_on_image: str

# Define models
class UserPreferences(BaseModel):
    color_preference: str = Field(..., example="red", description="User's preferred color")
    style_preference: str = Field(..., example="casual", description="User's preferred style")

class FetchResponse(BaseModel):
    status: str = Field(..., example="success")
    api: str = Field(..., example="fetch_similar")
    products: list = Field(..., example=[])

class VirtualTryOnResponse(BaseModel):
    status: str = Field(..., example="success")
    api: str = Field(..., example="get_virtual_try_on")
    virtual_try_on_image: str = Field(..., example="image_url")

class ChatFashionResponse(BaseModel):
    status: str = Field(..., example="success")
    api: str = Field(..., example="chat_fashion")
    response: str = Field(..., example="fashion advice")

class UploadPhotoResponse(BaseModel):
    status: str = Field(..., example="success")
    api: str = Field(..., example="upload_photo")
    description: str = Field(..., example="user description")

class Product(BaseModel):
    id: str
    score: float
    metadata: Dict[str, str]

def chat_with_gpt(user_prompt, chat_history):
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

@app.post("/chat_fashion", response_model=ChatFashionResponse, summary="Chat about fashion", description="Get fashion advice based on a query")
async def chat_fashion(query: str = Query(..., example="What should I wear for a beach party?")):
    logger.info(f"Chat fashion called with query: {query}")
    return {"status": "success", "api": "chat_fashion", "response": chat_with_gpt(user_prompt=query, chat_history=[])}

@app.post("/fetch_similar_given_image", summary="Fetch products similar to an image", description="Fetch products that are visually similar to the given image URL")
async def fetch_similar_given_image(image_url: str = Query(..., example="http://example.com/image.jpg")):
    logger.info(f"Fetch me something like called with image_url: {image_url}")
    if not image_url:
        raise HTTPException(status_code=400, detail="Image URL must be provided")
    
    logger.info("Searching by image...")
    search_results = search_by_image(image_url, n=1)
    
    logger.info("Search results: " + str(search_results))
    products = [
        Product(
            id=match.id,
            score=match.score,
            metadata=match.metadata
        ) for match in search_results.matches
    ]
    
    return {"status": "success", "api": "fetch_similar_given_image", "products": products}

@app.post("/fetch_similar_given_text", response_model=FetchResponse, summary="Fetch similar products", description="Fetch products similar to the given description or image embeddings")
async def fetch_similar_given_text(description: str = Query(..., example="A red dress"), image_url: str = Query(None, example="http://example.com/image.jpg")):
    logger.info(f"Fetch similar called with description: {description}, image_url: {image_url}")
    if not description and not image_url:
        raise HTTPException(status_code=400, detail="Either description or image_url must be provided")
    
    if description:
        logger.info("Searching by text...")
        search_results = search_by_text(description, n=1)    
    products = [
        Product(
            id=match.id,
            score=match.score,
            metadata=match.metadata
        ) for match in search_results.matches
    ]
    
    return {"status": "success", "api": "fetch_similar_given_text", "products": products}

# API endpoint
@app.post("/get_virtual_try_on", response_model=VirtualTryOnResponse)
async def get_virtual_try_on(
    user_image_url: str = Query(..., description="URL of the user's image"),
    product_image_url: str = Query(..., description="URL of the product image")
):
    logger.info(f"Get virtual try-on called with user_image_url: {user_image_url}, product_image_url: {product_image_url}")
    # Blonde Guy Black Shorts 
    # # return {'status': 'success', 'api': 'get_virtual_try_on', 'virtual_try_on_image': 'https://storage.googleapis.com/image-data-asg-2/virtual_try_on_20240702_182836_3.jpg'}
    # Blonde Guy Red Track pants  
    return {'status': 'success', 'api': 'get_virtual_try_on', 'virtual_try_on_image': 'https://storage.googleapis.com/image-data-asg-2/virtual_try_on_20240702_185156_3.jpg'}
    # Blonde Guy Hoodie 
    # # return {'status': 'success', 'api': 'get_virtual_try_on', 'virtual_try_on_image': 'https://storage.googleapis.com/image-data-asg-2/virtual_try_on_20240702_185513_3.jpg'}
    # Joker 
    # # return {'status': 'success', 'api': 'get_virtual_try_on', 'virtual_try_on_image': 'https://storage.googleapis.com/image-data-asg-2/virtual_try_on_20240702_185513_3.jpg'}
    try:

        logger.info("Building virtual try-on image...")
        result_image_url = await build_virtual_try_on(user_image_url, product_image_url)
        if result_image_url:
            logger.info(f"Virtual try-on image generated: {result_image_url}")
            return {"status": "success", "api": "get_virtual_try_on", "virtual_try_on_image": result_image_url}
        else:
            logger.error("Failed to generate image")
            return {"status": "error", "api": "get_virtual_try_on", "virtual_try_on_image": "Failed to generate image"}
    except Exception as e:
        logger.error(f"Error in get_virtual_try_on: {str(e)}")
        return {"status": "error", "api": "get_virtual_try_on", "virtual_try_on_image": str(e)}
    

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




