from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.document import DocumentResponse
from app.services.documents import create_document, get_document

router = APIRouter()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    current_user: CurrentUser, db: DBSession, file: UploadFile = File(...)
) -> DocumentResponse:
    """Store a document and create an AI-processing record with status `uploaded`."""
    try:
        return create_document(
            db=db,
            user=current_user,
            file=file.file,
            original_filename=file.filename or "",
            content_type=file.content_type,
        )
    finally:
        file.file.close()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_my_document(
    document_id: UUID, current_user: CurrentUser, db: DBSession
) -> DocumentResponse:
    """Return the authenticated user's document processing state and results."""
    return get_document(db, current_user.id, document_id)
