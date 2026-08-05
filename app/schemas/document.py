import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    content_type: str
    status: DocumentStatus
    extracted_text: str | None
    analysis_result: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
