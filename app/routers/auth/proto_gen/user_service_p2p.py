# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic[v0.3.3.0](https://github.com/so1n/protobuf_to_pydantic)
# Protobuf Version: 5.29.4 
# Pydantic Version: 2.11.4 
from .user_p2p import User
from .user_p2p import UserMetadata
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from pydantic import Field


class AuthenticateWithGoogleRequest(BaseModel):
    user: UserMetadata = Field(default_factory=UserMetadata)

class AuthenticateWithGoogleResponse(BaseModel):
    user: User = Field(default_factory=User)
    is_new_user: bool = Field(default=False)

class GetUserByEmailRequest(BaseModel):
    email: str = Field(default="")

class CreateUserResponse(BaseModel):
    success: bool = Field(default=False)

class DeleteUserRequest(BaseModel):
    email: str = Field(default="")

class DeleteUserResponse(BaseModel):
    success: bool = Field(default=False)
