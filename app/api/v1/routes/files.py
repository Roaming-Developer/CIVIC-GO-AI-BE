from fastapi import APIRouter, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser
from app.schemas.file import FileUploadResponse, PresignedDownloadResponse
from app.services.storage import (
    create_download_url,
    delete_file,
    read_file,
    upload_file,
)

router = APIRouter()


def _stream_s3_body(body):
    try:
        yield from body.iter_chunks()
    finally:
        body.close()


@router.post("", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_my_file(
    current_user: CurrentUser, file: UploadFile = File(...)
) -> FileUploadResponse:
    """Upload a file to S3 and return its storage object key."""
    try:
        object_key, content_type = upload_file(
            user_id=current_user.id,
            file=file.file,
            original_filename=file.filename or "",
            content_type=file.content_type,
        )
    finally:
        file.file.close()
    return FileUploadResponse(
        object_key=object_key,
        original_filename=file.filename or "",
        content_type=content_type,
    )


@router.get("/download-url", response_model=PresignedDownloadResponse)
def get_download_url(
    object_key: str,
    current_user: CurrentUser,
    expires_in: int = Query(default=300, ge=1, le=3600),
) -> PresignedDownloadResponse:
    """Create a temporary browser-ready S3 URL for one of the user's files."""
    return PresignedDownloadResponse(
        url=create_download_url(
            user_id=current_user.id, object_key=object_key, expires_in=expires_in
        ),
        expires_in=expires_in,
    )


@router.get("/{object_key:path}")
def read_my_file(object_key: str, current_user: CurrentUser) -> StreamingResponse:
    """Stream one of the authenticated user's files from S3."""
    s3_object = read_file(user_id=current_user.id, object_key=object_key)
    return StreamingResponse(
        _stream_s3_body(s3_object["Body"]),
        media_type=s3_object.get("ContentType") or "application/octet-stream",
        headers={"Content-Length": str(s3_object["ContentLength"])},
    )


@router.delete("/{object_key:path}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_file(object_key: str, current_user: CurrentUser) -> None:
    """Delete one of the authenticated user's files from S3."""
    delete_file(user_id=current_user.id, object_key=object_key)
