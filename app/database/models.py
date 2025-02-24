from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict, WithJsonSchema
from pymongo import IndexModel


class BaseUsername(BaseModel):
    username: str = Field(max_length=32)


class BasePassword(BaseModel):
    password: str = Field(min_length=8, max_length=32)


class UserLogin(
    BaseUsername,
    BasePassword,
):
    model_config = ConfigDict(extra='forbid')


class BaseUserInfo(BaseModel):
    f_name: str | None = Field(default=None, max_length=32)
    l_name: str | None = Field(default=None, max_length=32)


class UserPermission(Enum):
    guest = "guest"
    staff = "staff"
    admin = "admin"


class UserInfo(
    BaseUsername,
    BaseUserInfo,
):
    permission: UserPermission


class User(
    BaseUsername,
    BaseUserInfo,
):
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "indexes": [
                IndexModel([("username", 1)], unique=True),
            ]
        }
    )

    passwd_hash: Annotated[
        bytes,
        WithJsonSchema(
            {
                "title": "passwd_hash",
                "type": "string",
                "maxLength": 64,
            }
        )
    ] = Field(max_length=64)
    permission: Annotated[
        UserPermission,
        WithJsonSchema(
            {
                "title": "permission",
                "type": "string",
                "enum": [perm.value for perm in UserPermission],
            }
        )
    ] = Field(default=UserPermission.guest)