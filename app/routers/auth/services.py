import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import grpc
import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from google.protobuf.json_format import (
    MessageToDict,
)
from passlib.context import CryptContext
from starlette import status
from starlette.config import Config

from app.config import (
    ALGORITHM,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    USER_SERVICE_URL,
)

from .proto_gen import (
    user_p2p,
    user_pb2,
    user_service_pb2,
    user_service_pb2_grpc,
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise Exception("Missing env variables")
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

TokenDep = Annotated[str, Depends(oauth_bearer)]


def create_access_token(
    email: str, role: str, user_id: int, expires_delta: timedelta, refresh: bool = False
):
    encode = {"email": email, "id": user_id, "role": role, "refresh": refresh}
    expires = datetime.now(UTC) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)


def create_refresh_token(email: str, role: str, user_id: int, expires_delta: timedelta):
    return create_access_token(email, role, user_id, expires_delta, refresh=True)


def decode_token(token):
    return jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth_bearer)]) -> user_p2p.User:
    try:
        payload = decode_token(token)
        email: str = payload.get("email")
        user_id: int = payload.get("id")

        if payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is not valid.",
            )

        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )

        with grpc.insecure_channel(USER_SERVICE_URL) as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            try:
                response: user_pb2.User = stub.GetUserByEmail(
                    user_service_pb2.GetUserByEmailRequest(email=email)
                )
            except grpc.RpcError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate user.",
                )
        current_user = user_p2p.User(**MessageToDict(response))
        return current_user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


def token_expired(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = decode_token(token)
        if not datetime.fromtimestamp(payload.get("exp"), UTC) > datetime.now(UTC):
            return True
        return False

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


user_dependency = Annotated[user_p2p.User, Depends(get_current_user)]
