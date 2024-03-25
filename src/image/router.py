from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from botocore.exceptions import BotoCoreError, ClientError

import src.aws.client as aws
from src.image.service import get_image_metadata_by_object_key
from src.utils.exceptions import ItemNotFoundError

router = APIRouter(
    prefix="/image",
    tags=["image"],
    responses={404: {"description": "Not found"}},
)


@router.get("/generate-presigned-url")
async def generate_presigned_url(action: str, file_name: str, content_type: str = Query(None), user_id: Optional[str] = None):
    """Generate a pre-signed URL for S3 actions."""

    if action not in ['put', 'get']:
        raise HTTPException(status_code=400, detail="Invalid action")

    try:
        object_name = f"{user_id}/{file_name}" if user_id else f"general/{file_name}"

        if action == 'get':
            response = aws.s3_generate_presigned_url('get_object',
                                                     method_parameters={
                                                         'Key': object_name},
                                                     expires_in=3600)
        else:
            response = aws.s3_generate_presigned_url('put_object',
                                                     method_parameters={
                                                         'Key': object_name, 'ContentType': content_type},
                                                     expires_in=3600)
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"url": response, "objectName": object_name}


@router.get("/list-user-images-metadata")
async def list_user_images_metadata(user_id: str):
    """List all images metadata for a user."""
    try:
        response = aws.s3_list_objects(f"{user_id}/")

        if 'Contents' not in response:
            return {"message": "No images found for the user."}

        objects_metadata = []
        for obj in response['Contents']:
            metadata = aws.s3_fetch_object_metadata(obj)
            objects_metadata.append({
                "Key": obj['Key'],
                "LastModified": obj['LastModified'],
                "Size": obj['Size'],
                "ContentType": metadata['ContentType'],
                # Add any other metadata you need
            })
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return objects_metadata


@router.get("/metadata")
async def get_all_image_metadata(user_id: str):
    """Get all images metadata for a user."""
    try:
        response = aws.s3_list_objects("general/")

        if 'Contents' not in response:
            return {"message": "No images found."}

        objects_metadata = []
        for obj in response['Contents']:
            metadata = aws.s3_fetch_object_metadata(obj)
            objects_metadata.append({
                "Key": obj['Key'],
                "LastModified": obj['LastModified'],
                "Size": obj['Size'],
                "ContentType": metadata['ContentType'],
                # Add any other metadata you need
            })
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return objects_metadata


@router.get("/metadata")
async def get_all_image_metadata():
    """Get all images metadata."""
    try:
        response = aws.s3_list_objects("general/")

        if 'Contents' not in response:
            return {"message": "No images found."}

        objects_metadata = []
        for obj in response['Contents']:
            metadata = aws.s3_fetch_object_metadata(obj)
            objects_metadata.append({
                "Key": obj['Key'],
                "LastModified": obj['LastModified'],
                "Size": obj['Size'],
                "ContentType": metadata['ContentType'],
                # Add any other metadata you need
            })
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return objects_metadata


@router.get("/metadata")
async def get_image_metadata(object_key: str):
    """Get a specific image metadata."""
    try:
        response = get_image_metadata_by_object_key(object_key)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return response
