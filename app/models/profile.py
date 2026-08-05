import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Occupation(str, enum.Enum):
    PRIVATE_SECTOR = "private_sector"
    GOVERNMENT = "government"
    UNEMPLOYED = "unemployed"
    FARMER = "farmer"
    STUDENT = "student"
    OTHER = "other"


class SalaryRange(str, enum.Enum):
    BELOW_10K = "below_10k"
    FROM_10K_TO_25K = "10k_to_25k"
    FROM_25K_TO_50K = "25k_to_50k"
    FROM_50K_TO_100K = "50k_to_100k"
    ABOVE_100K = "above_100k"


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    occupation: Mapped[Occupation] = mapped_column(
        Enum(
            Occupation,
            name="occupation",
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
    )
    salary_range: Mapped[SalaryRange] = mapped_column(
        Enum(
            SalaryRange,
            name="salary_range",
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="profile")
