import uuid
from typing import BinaryIO

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User
from app.services.storage import delete_file, upload_file


def create_document(
    *,
    db: Session,
    user: User,
    file: BinaryIO,
    original_filename: str,
    content_type: str | None,
) -> Document:
    s3_key, resolved_content_type = upload_file(
        user_id=user.id,
        file=file,
        original_filename=original_filename,
        content_type=content_type,
    )
    document = Document(
        user_id=user.id,
        s3_key=s3_key,
        original_filename=original_filename,
        content_type=resolved_content_type,
    )
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except SQLAlchemyError:
        db.rollback()
        # Do not leave an S3 object behind when its database record cannot be created.
        try:
            delete_file(user_id=user.id, object_key=s3_key)
        except HTTPException:
            pass
        raise
    return document


def get_document(db: Session, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
    document = db.scalar(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return document
