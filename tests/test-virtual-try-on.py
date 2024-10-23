import pytest
from unittest.mock import patch

def test_virtual_try_on_success(client, mock_image_urls):
    """
    Test successful virtual try-on request
    """
    with patch("app.main.build_virtual_try_on") as mock_build:
        mock_build.return_value = mock_image_urls["result_image"]
        
        response = client.post("/get_virtual_try_on", params={
            "user_image_url": mock_image_urls["user_image"],
            "product_image_url": mock_image_urls["product_image"]
        })
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["virtual_try_on_image"] == mock_image_urls["result_image"]

def test_virtual_try_on_missing_parameters(client):
    """
    Test error handling for missing parameters
    """
    response = client.post("/get_virtual_try_on", params={
        "user_image_url": "https://example.com/user.jpg"
    })
    assert response.status_code == 422

def test_virtual_try_on_service_error(client, mock_image_urls):
    """
    Test error handling when virtual try-on service fails
    """
    with patch("app.main.build_virtual_try_on") as mock_build:
        mock_build.side_effect = Exception("Service unavailable")
        
        response = client.post("/get_virtual_try_on", params={
            "user_image_url": mock_image_urls["user_image"],
            "product_image_url": mock_image_urls["product_image"]
        })
        
        assert response.status_code == 200
        assert response.json()["status"] == "error"
