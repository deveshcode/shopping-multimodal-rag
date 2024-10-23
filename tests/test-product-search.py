import pytest
from unittest.mock import patch

def test_fetch_similar_given_text_success(client, sample_product):
    """
    Test successful text-based product search
    """
    with patch("app.main.search_by_text") as mock_search:
        mock_search.return_value.matches = [sample_product]
        
        response = client.post("/fetch_similar_given_text", params={
            "description": "red nike shoes"
        })
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert len(response.json()["products"]) > 0
        assert response.json()["products"][0]["id"] == sample_product["id"]

def test_fetch_similar_given_image_success(client, sample_product):
    """
    Test successful image-based product search
    """
    with patch("app.main.search_by_image") as mock_search:
        mock_search.return_value.matches = [sample_product]
        
        response = client.post("/fetch_similar_given_image", params={
            "image_url": "https://example.com/test-image.jpg"
        })
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert len(response.json()["products"]) > 0

def test_fetch_similar_invalid_request(client):
    """
    Test error handling for invalid requests
    """
    response = client.post("/fetch_similar_given_text", params={})
    assert response.status_code == 400
    
    response = client.post("/fetch_similar_given_image", params={})
    assert response.status_code == 400
