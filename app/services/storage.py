import re
import uuid
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status

from app.core.config import settings

_SAFE_SUFFIX = re.compile(r"^\.[a-zA-Z0-9]{1,10}$")


def _get_bucket_name() -> str:
    if not settings.s3_bucket_name:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="S3 storage is not configured")
    return settings.s3_bucket_name


def _get_s3_client():
    client_kwargs = {"region_name": settings.aws_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        client_kwargs.update(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
    return boto3.client("s3", **client_kwargs)


def _owned_object_key(user_id: uuid.UUID, object_key: str) -> str:
    expected_prefix = f"users/{user_id}/"
    if not object_key.startswith(expected_prefix):
        # Do not reveal whether an object belonging to another user exists.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    print(f"Owned object key: {object_key}")
    return object_key


def _storage_error(exc: ClientError | BotoCoreError) -> HTTPException:
    if isinstance(exc, ClientError) and exc.response["Error"].get("Code") in {"404", "NoSuchKey", "NoSuchBucket"}:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Storage service is unavailable")


def upload_file(
    *, user_id: uuid.UUID, file: BinaryIO, original_filename: str, content_type: str | None
) -> tuple[str, str]:
    if not original_filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A filename is required")

    suffix = Path(original_filename).suffix
    suffix = suffix if _SAFE_SUFFIX.fullmatch(suffix) else ""
    object_key = f"users/{user_id}/{uuid.uuid4().hex}{suffix}"
    resolved_content_type = content_type or "application/octet-stream"
    try:
        _get_s3_client().upload_fileobj(
            file,
            _get_bucket_name(),
            object_key,
            ExtraArgs={"ContentType": resolved_content_type},
        )
    except (ClientError, BotoCoreError) as exc:
        raise _storage_error(exc) from exc
    return object_key, resolved_content_type


def read_file(*, user_id: uuid.UUID, object_key: str):
    try:
        return _get_s3_client().get_object(Bucket=_get_bucket_name(), Key=_owned_object_key(user_id, object_key))
    except (ClientError, BotoCoreError) as exc:
        raise _storage_error(exc) from exc


def create_download_url(*, user_id: uuid.UUID, object_key: str, expires_in: int) -> str:
    try:
        return _get_s3_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": _get_bucket_name(), "Key": _owned_object_key(user_id, object_key)},
            ExpiresIn=expires_in,
        )
    except (ClientError, BotoCoreError) as exc:
        raise _storage_error(exc) from exc


def delete_file(*, user_id: uuid.UUID, object_key: str) -> None:
    try:
        _get_s3_client().delete_object(Bucket=_get_bucket_name(), Key=_owned_object_key(user_id, object_key))
    except (ClientError, BotoCoreError) as exc:
        raise _storage_error(exc) from exc
