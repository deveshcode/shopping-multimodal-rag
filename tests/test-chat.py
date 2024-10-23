import pytest
from unittest.mock import patch

def test_chat_fashion_success(client):
    """
    Test successful chat interaction
    """
    query = "What should I wear for a beach party?"
    response = client.post("/chat_fashion", params={"query": query})
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["api"] == "chat_fashion"
    assert "response" in response.json()

@pytest.mark.asyncio
async def test_chat_with_gpt_inappropriate_content(client):
    """
    Test chat guardrail for inappropriate content
    """
    query = "Tell me about cryptocurrency trading"  # Non-fashion related query
    response = client.post("/chat_fashion", params={"query": query})
    
    assert response.status_code == 200
    assert "Sorry, I can't help with that" in response.json()["response"]

@pytest.mark.asyncio
async def test_chat_with_gpt_error_handling():
    """
    Test error handling in chat functionality
    """
    with patch("app.main.client.chat.completions.create") as mock_create:
        mock_create.side_effect = Exception("API Error")
        response = client.post("/chat_fashion", params={"query": "Hello"})
        
        assert response.status_code == 200
        assert "error" in response.json()["response"].lower()
