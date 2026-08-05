from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate


def create_profile(db: Session, user: User, payload: ProfileCreate) -> Profile:
    existing_profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A profile already exists for this user")

    profile = Profile(user_id=user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_profile(db: Session, user: User) -> Profile:
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


def update_profile(db: Session, user: User, payload: ProfileUpdate) -> Profile:
    profile = get_profile(db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(db: Session, user: User) -> None:
    profile = get_profile(db, user)
    db.delete(profile)
    db.commit()
