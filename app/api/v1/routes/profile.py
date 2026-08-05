from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile import create_profile, delete_profile, update_profile

router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_my_profile(current_user: CurrentUser) -> ProfileResponse:
    """Return the authenticated user's profile."""
    return current_user.profile


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    payload: ProfileCreate, current_user: CurrentUser, db: DBSession
) -> ProfileResponse:
    """Create the authenticated user's profile."""
    return create_profile(db, current_user, payload)


@router.patch("/", response_model=ProfileResponse)
def update_my_profile(
    payload: ProfileUpdate, current_user: CurrentUser, db: DBSession
) -> ProfileResponse:
    """Update one or more fields on the authenticated user's profile."""
    return update_profile(db, current_user, payload)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_profile(current_user: CurrentUser, db: DBSession) -> None:
    """Permanently delete the authenticated user's profile."""
    delete_profile(db, current_user)
