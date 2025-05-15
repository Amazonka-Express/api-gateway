from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("firstName", "lastName", "email", "role")
    FIRSTNAME_FIELD_NUMBER: _ClassVar[int]
    LASTNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    firstName: str
    lastName: str
    email: str
    role: str
    def __init__(self, firstName: _Optional[str] = ..., lastName: _Optional[str] = ..., email: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class UserMetadata(_message.Message):
    __slots__ = ("firstName", "lastName", "email")
    FIRSTNAME_FIELD_NUMBER: _ClassVar[int]
    LASTNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    firstName: str
    lastName: str
    email: str
    def __init__(self, firstName: _Optional[str] = ..., lastName: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...
