from datetime import timedelta
from pprint import pprint
from typing import Annotated

from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.config import (
    FRONTEND_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)

# from .models import User
from .schemas import CreateUserRequest, GoogleUser, RefreshTokenRequest, Token
from .services import (
    TokenDep,
    # authenticate_user,
    # bcrypt_context,
    create_access_token,
    create_refresh_token,
    create_user_from_google_info,
    decode_token,
    get_user_by_google_sub,
    oauth,
    oauth_bearer,
    token_expired,
    user_dependency,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def login_google(request: Request):
    return await oauth.google.authorize_redirect(request, GOOGLE_REDIRECT_URI)


@router.get("/callback/google")
async def auth_google(request: Request):
    try:
        user_response: OAuth2Token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_info = user_response.get("userinfo")

    google_user = GoogleUser(**user_info)

    existing_user = get_user_by_google_sub(google_user.sub)

    if existing_user:
        pprint("Existing user")
        user = existing_user
    else:
        pprint("Creating user")
        user = create_user_from_google_info(google_user)

    access_token = create_access_token(user.username, user.id, timedelta(days=7))
    refresh_token = create_refresh_token(user.username, user.id, timedelta(days=14))

    response = RedirectResponse(f"{FRONTEND_URL}/auth")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        max_age=2 * 60 * 60,  # 2 hours
        secure=False,  # Set to True if using HTTPS
        samesite="Lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=False,
        max_age=24 * 60 * 60,  # 24 hours
        secure=False,  # Set to True if using HTTPS
        samesite="Lax",
    )
    return response


# @router.post("/create-user", status_code=status.HTTP_201_CREATED)
# async def create_user(create_user_request: CreateUserRequest):
#     create_user_model = User(
#         username=create_user_request.username,
#         hashed_password=bcrypt_context.hash(create_user_request.password),
#     )

#     db.add(create_user_model)
#     db.commit()

#     return create_user_request


@router.get("/get-user", status_code=status.HTTP_201_CREATED)
async def get_user(user: user_dependency):
    return user


# @router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
# async def login_for_access_token(
#     token: Annotated[OAuth2PasswordRequestForm, Depends()],
# ):
#     user = authenticate_user(form_data.username, form_data.password, db)

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
#         )

#     access_token = create_access_token(user.username, user.id, timedelta(days=7))
#     refresh_token = create_refresh_token(user.username, user.id, timedelta(days=14))

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }


@router.post("/refresh")
async def refresh_access_token(token: Annotated[str, Depends(oauth_bearer)]):
    if token_expired(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is expired."
        )

    user = decode_token(token)
    if not user.get("refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is not valid.",
        )

    access_token = create_access_token(user["sub"], user["id"], timedelta(days=7))
    return {
        "access_token": access_token,
    }
