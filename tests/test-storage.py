import pytest
from unittest.mock import patch, MagicMock
import os

def test_upload_blob_success(mock_env_variables, mock_storage_client, mock_image):
    """Test successful file upload to Google Cloud Storage"""
    from azure_cv import upload_blob
    
    # Create a temporary test file
    test_file = "test_image.png"
    with open(test_file, "wb") as f:
        f.write(mock_image.getvalue())
    
    with patch("azure_cv.storage.Client", return_value=mock_storage_client):
        result = upload_blob(test_file, "destination/test_image.png")
        
        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("https://storage.googleapis.com")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

def test_upload_blob_error(mock_env_variables, mock_storage_client):
    """Test file upload with error"""
    from azure_cv import upload_blob
    
    mock_storage_client.bucket.side_effect = Exception("Upload error")
    
    with patch("azure_cv.storage.Client", return_value=mock_storage_client):
        result = upload_blob("nonexistent_file.jpg", "destination/test.jpg")
        assert result is None
