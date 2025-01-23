# app/core/cloudinary_config.py
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
import os
from typing import Optional

# Initialize cloudinary configuration
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

async def upload_image(file: UploadFile, folder: str) -> Optional[str]:
    """
    Upload an image to Cloudinary
    
    Args:
        file: UploadFile object containing the image
        folder: Cloudinary folder to upload to
    
    Returns:
        URL of the uploaded image
    """
    try:
        # Verify file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read file contents
        contents = await file.read()
        
        # Upload to cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="auto"
        )
        
        return result['secure_url']
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )