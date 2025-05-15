# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic[v0.3.3.0](https://github.com/so1n/protobuf_to_pydantic)
# Protobuf Version: 5.29.4 
# Pydantic Version: 2.11.4 
from google.protobuf.message import Message  # type: ignore
from pydantic import BaseModel
from pydantic import Field


class User(BaseModel):
    firstName: str = Field(default="")
    lastName: str = Field(default="")
    email: str = Field(default="")
    role: str = Field(default="")

class UserMetadata(BaseModel):
    firstName: str = Field(default="")
    lastName: str = Field(default="")
    email: str = Field(default="")
