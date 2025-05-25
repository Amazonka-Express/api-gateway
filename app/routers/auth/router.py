from datetime import timedelta
from typing import Annotated

import grpc
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.protobuf.json_format import MessageToDict
from starlette import status

from app.config import FRONTEND_URL, GOOGLE_REDIRECT_URI, USER_SERVICE_URL

from .proto_gen import (
    user_p2p,
    user_pb2,
    user_service_p2p,
    user_service_pb2,
    user_service_pb2_grpc,
)
from .services import (
    UserDep,
    create_access_token,
    create_refresh_token,
    decode_token,
    oauth,
    oauth_bearer,
    token_expired,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google", response_class=RedirectResponse)
async def login_google(request: Request):
    """Initiates the Google OAuth2 login flow by redirecting the user to Google's authorization page."""
    return await oauth.google.authorize_redirect(request, GOOGLE_REDIRECT_URI)


@router.get("/callback/google", response_class=RedirectResponse)
async def auth_google(request: Request):
    """
    Handles the Google OAuth2 callback, authenticates the user with the backend user service via gRPC,
    generates access and refresh tokens, and redirects the user to the frontend with authentication cookies.
    \nRaises:
        HTTPException: If the OAuth2 authorization fails.
    \nReturns:
        RedirectResponse: Redirects the user to the frontend application, setting authentication cookies.
    """
    try:
        user_response: OAuth2Token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # TODO przenieś do services
    user_info = user_response.get("userinfo")
    async with grpc.aio.insecure_channel(USER_SERVICE_URL) as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)
        try:
            response: user_service_pb2.AuthenticateWithGoogleResponse = (
                await stub.AuthenticateWithGoogle(
                    user_service_pb2.AuthenticateWithGoogleRequest(
                        user=user_pb2.UserMetadata(
                            email=user_info.get("email"),
                            firstName=user_info.get("given_name"),
                            lastName=user_info.get("family_name"),
                        )
                    )
                )
            )
        except grpc.RpcError as e:
            return RedirectResponse(
                f"{FRONTEND_URL}/auth?error={e.code()} - {e.details()}"
            )

    user = user_p2p.User(**MessageToDict(response.user))
    access_token = create_access_token(
        user.email, user.role, "#TODO ID", timedelta(days=7)
    )
    refresh_token = create_refresh_token(
        user.email, user.role, "#TODO ID", timedelta(days=14)
    )

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


@router.post(
    "/create-user",
    status_code=status.HTTP_201_CREATED,
    response_model=user_service_p2p.CreateUserResponse,
)
async def create_user(user_in: user_p2p.User):
    """Creates a new user by forwarding the user data to a gRPC user service."""
    async with grpc.aio.insecure_channel(USER_SERVICE_URL) as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)
        try:
            response: user_service_pb2.CreateUserResponse = await stub.Create(
                user_pb2.User(**user_in.model_dump())
            )
        except grpc.RpcError as e:
            return HTTPException("Could not create user", status_code=e.code())
    return MessageToDict(response)


@router.delete(
    "/delete-user/{email}",
    response_model=user_service_p2p.DeleteUserResponse,
)
async def delete_user(email: str):
    """Deletes user by forwarding the user ID to a gRPC user service."""
    async with grpc.aio.insecure_channel(USER_SERVICE_URL) as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)
        try:
            response: user_service_pb2.DeleteUserResponse = await stub.Delete(
                user_service_pb2.DeleteUserRequest(email=email)
            )
        except grpc.RpcError as e:
            return HTTPException("Could not delete user", status_code=e.code())
    return MessageToDict(response)


@router.get(
    "/get-user",
    status_code=status.HTTP_201_CREATED,
    response_model=user_p2p.User,
)
async def get_user(user: UserDep):
    """Retrieve the current authenticated user's information."""
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

    access_token = create_access_token(
        user["email"], user["role"], user["id"], timedelta(days=7)
    )
    return {
        "access_token": access_token,
    }
