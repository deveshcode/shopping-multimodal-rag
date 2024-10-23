import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import os

def test_get_caption_success(mock_gradio_client):
    """Test successful image captioning"""
    from azure_cv import get_caption
    
    with patch("azure_cv.Client", return_value=mock_gradio_client):
        result = get_caption("https://example.com/test.jpg")
        assert isinstance(result, str)
        assert len(result) > 0

def test_combine_captions(mock_openai_client):
    """Test caption combination with GPT"""
    from azure_cv import combine_captions
    
    with patch("azure_cv.OpenAI", return_value=mock_openai_client):
        result = combine_captions(
            "A person with blonde hair",
            "A red Nike t-shirt"
        )
        assert isinstance(result, str)
        assert len(result) > 0

def test_generate_image(mock_openai_client):
    """Test DALL-E image generation"""
    from azure_cv import generate_image
    
    with patch("azure_cv.OpenAI", return_value=mock_openai_client):
        result = generate_image("A person wearing Nike clothing")
        assert isinstance(result, str)
        assert result.startswith("https://")
