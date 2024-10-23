import pytest
from unittest.mock import patch, MagicMock
import requests
import json
from PIL import Image
import os

def test_remove_background_success(mock_env_variables, requests_mock):
    """Test successful background removal"""
    from azure_cv import remove_background
    
    # Mock successful API response
    requests_mock.post(
        "https://test.azure.com/computervision/imageanalysis:segment",
        content=b"fake-image-content",
        status_code=200
    )
    
    result = remove_background("https://example.com/test.jpg")
    assert isinstance(result, str)
    assert os.path.exists(result)
    
    # Clean up
    if os.path.exists(result):
        os.remove(result)

def test_remove_background_api_error(mock_env_variables, requests_mock):
    """Test background removal with API error"""
    from azure_cv import remove_background
    
    requests_mock.post(
        "https://test.azure.com/computervision/imageanalysis:segment",
        status_code=400,
        json={"error": "Bad request"}
    )
    
    result = remove_background("https://example.com/test.jpg")
    assert result is None

@pytest.mark.asyncio
async def test_build_virtual_try_on_success(
    mock_env_variables,
    mock_storage_client,
    mock_openai_client,
    mock_gradio_client,
    sample_image_urls
):
    """Test successful virtual try-on pipeline"""
    from azure_cv import build_virtual_try_on
    
    with patch("azure_cv.storage.Client", return_value=mock_storage_client), \
         patch("azure_cv.remove_background"), \
         patch("azure_cv.Client", return_value=mock_gradio_client), \
         patch("azure_cv.OpenAI", return_value=mock_openai_client), \
         patch("azure_cv.requests.get") as mock_get:
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"fake-image-content"
        
        result = await build_virtual_try_on(
            sample_image_urls["user_image"],
            sample_image_urls["product_image"]
        )
        
        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("https://")
