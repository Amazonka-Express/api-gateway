import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status
from starlette.config import Config

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

from .schemas import GoogleUser, User

ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

TokenDep = Annotated[str, Depends(oauth_bearer)]

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


db_test: list[User] = []


def create_access_token(
    username: str, user_id: int, expires_delta: timedelta, refresh: bool = False
):
    encode = {"sub": username, "id": user_id, "refresh": refresh}

    expires = datetime.now(UTC) + expires_delta

    encode.update({"exp": expires})

    return jwt.encode(encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)


def create_refresh_token(username: str, user_id: int, expires_delta: timedelta):
    return create_access_token(username, user_id, expires_delta, refresh=True)


def decode_token(token):
    return jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is not valid.",
            )

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )

        current_user = None
        for user in db_test:
            if user.username == username and user.id == user_id:
                current_user = user

        # user: User = (
        #     db.query(User)
        #     .filter(User.username == str(username))
        #     .options(defer(User.hashed_password), defer(User.google_sub))
        #     .first()
        # )
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


def get_user_by_google_sub(google_sub: int):
    for user in db_test:
        if user.google_sub == google_sub:
            return user
    return None
    # return db.query(User).filter(User.google_sub == str(google_sub)).first()


def create_user_from_google_info(google_user: GoogleUser):
    google_sub = google_user.sub
    email = google_user.email

    existing_user = None
    for user in db_test:
        if user.email == str(email):
            existing_user = user
    # existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        existing_user.google_sub = google_sub
        # db.commit()
        return existing_user
    else:
        new_user = User(
            id=len(db_test) + 1,
            username=email,
            email=email,
            google_sub=google_sub,
            hashed_password="password",
        )
        db_test.append(new_user)
        # db.add(new_user)
        # db.commit()
        # db.refresh(new_user)
        return new_user


user_dependency = Annotated[dict, Depends(get_current_user)]
