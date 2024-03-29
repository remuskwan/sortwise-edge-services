from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from botocore.exceptions import BotoCoreError, ClientError

import src.aws.client as aws
import src.image.service as image_service
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


@router.get("/metadata/user/{user_id}")
async def get_all_image_metadata(user_id: str):
    """Get all images metadata for a user."""
    try:
        response = image_service.get_image_metadata_by_user_id(user_id=user_id)
    except ItemNotFoundError:
        return []
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return response


@router.get("/metadata/inference")
async def get_image_metadata_with_inference():
    """Get all images metadata with non-null inference results."""
    try:
        response = image_service.get_image_metadata_with_inference()
    except ItemNotFoundError:
        return []
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return response


@router.get("/metadata/{object_key:path}")
async def get_image_metadata(object_key: str):
    """Get a specific image metadata."""
    try:
        response = image_service.get_image_metadata_by_object_key(
            object_key=object_key)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return response
