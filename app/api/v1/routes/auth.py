from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import (
    authenticate_user,
    create_user,
    delete_user,
    refresh_access_token,
)

router = APIRouter()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def signup(payload: UserCreate, db: DBSession) -> UserResponse:
    """Register a new user with an email address and password."""
    return create_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DBSession) -> TokenResponse:
    """Authenticate a user and return a bearer access token."""
    return authenticate_user(db, payload)


# get new auth token using refresh token
@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest) -> TokenResponse:
    """Refresh the access token using the refresh token."""
    return refresh_access_token(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser) -> UserResponse:
    """Return the user associated with the supplied bearer token."""
    return current_user


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(current_user: CurrentUser, db: DBSession) -> None:
    """Delete the user associated with the supplied bearer token."""
    return delete_user(db, current_user)
