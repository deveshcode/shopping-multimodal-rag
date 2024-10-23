import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def client():
    """
    Test client fixture that can be used across all tests
    """
    return TestClient(app)

@pytest.fixture
def mock_openai_response():
    """
    Mock fixture for OpenAI responses
    """
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock response from the fashion assistant."
                }
            }
        ]
    }

@pytest.fixture
def sample_product():
    """
    Sample product fixture for testing
    """
    return {
        "id": "test_product_id",
        "score": 0.95,
        "metadata": {
            "name": "Test Product",
            "category": "Clothing",
            "price": "99.99",
            "image_url": "https://example.com/test-image.jpg"
        }
    }

@pytest.fixture
def mock_image_urls():
    """
    Mock image URLs for testing
    """
    return {
        "user_image": "https://example.com/user-image.jpg",
        "product_image": "https://example.com/product-image.jpg",
        "result_image": "https://example.com/result-image.jpg"
    }
