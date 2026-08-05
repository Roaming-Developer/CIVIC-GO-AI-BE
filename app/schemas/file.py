from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    object_key: str
    original_filename: str
    content_type: str


class PresignedDownloadResponse(BaseModel):
    url: str
    expires_in: int
