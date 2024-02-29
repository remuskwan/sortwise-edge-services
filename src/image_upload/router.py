from fastapi import APIRouter, UploadFile, HTTPException, status
from uuid import uuid4

from image_upload.constants import SUPPORTED_FILE_SIZE, SUPPORTED_FILE_TYPES
from aws.client import s3_upload
from loguru import logger

router = APIRouter(
    prefix="/image",
    tags=["image"],
    responses={404: {"description": "Not found"}},
)


@router.post("/upload/")
async def upload(image: UploadFile | None = None):
    if not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    # read image
    contents = await image.read()
    size = len(contents)

    if not size in range(SUPPORTED_FILE_SIZE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum file size is 2MB")
    file_type = image.content_type
    if not file_type in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {file_type}. Supported types are {SUPPORTED_FILE_TYPES}")
    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES[file_type]}'
    # upload to s3
    await s3_upload(contents=contents, key=file_name)
    return {'file_name': file_name}
