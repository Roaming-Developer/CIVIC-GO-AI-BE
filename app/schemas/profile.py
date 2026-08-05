import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.profile import Occupation, SalaryRange


class ProfileCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    district: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    occupation: Occupation
    salary_range: SalaryRange

    @field_validator("first_name", "last_name", "district", "state")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_must_be_in_the_past(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("must be in the past")
        return value


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    district: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    occupation: Occupation | None = None
    salary_range: SalaryRange | None = None

    @field_validator("first_name", "last_name", "district", "state")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def updated_date_of_birth_must_be_in_the_past(
        cls, value: date | None
    ) -> date | None:
        if value is not None and value >= date.today():
            raise ValueError("must be in the past")
        return value


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    district: str
    state: str
    occupation: Occupation
    salary_range: SalaryRange
    created_at: datetime
    updated_at: datetime
