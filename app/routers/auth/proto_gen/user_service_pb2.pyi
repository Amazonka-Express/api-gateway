import user_pb2 as _user_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AuthenticateWithGoogleRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.UserMetadata
    def __init__(self, user: _Optional[_Union[_user_pb2.UserMetadata, _Mapping]] = ...) -> None: ...

class AuthenticateWithGoogleResponse(_message.Message):
    __slots__ = ("user", "is_new_user")
    USER_FIELD_NUMBER: _ClassVar[int]
    IS_NEW_USER_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    is_new_user: bool
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ..., is_new_user: bool = ...) -> None: ...

class GetUserByEmailRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class DeleteUserResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
