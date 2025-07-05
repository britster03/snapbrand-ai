from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl

from ..services.s3 import s3_service

router = APIRouter(prefix="/v1/assets", tags=["assets"])


class UploadUrlResponse(BaseModel):
    upload_url: HttpUrl
    object_key: str


@router.get("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(filename: str = Query(..., description="Filename with extension")) -> UploadUrlResponse:
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    key = f"brand-assets/{filename}"
    url = s3_service.generate_presigned_upload_url(key)
    return UploadUrlResponse(upload_url=url, object_key=key) 