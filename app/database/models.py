from enum import Enum
from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, WithJsonSchema
from pymongo import IndexModel
from bson import ObjectId


class BaseID:
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Annotated[
        ObjectId | None,
        WithJsonSchema(
            {
                "title": "id",
                "type": "oid",
            }
        )
    ] = Field(default=None, alias="_id")


class BaseUsername:
    username: str = Field(min_length=4 , max_length=32)


class BasePassword:
    password: str = Field(min_length=8, max_length=32)


class UserLogin(
    BaseModel,
    BaseUsername,
    BasePassword,
):
    model_config = ConfigDict(extra='forbid')


class BaseUserInfo:
    f_name: str | None = Field(default=None, max_length=32)
    l_name: str | None = Field(default=None, max_length=32)


class UserPermission(Enum):
    guest = "guest"
    staff = "staff"
    admin = "admin"


class UserInfo(
    BaseModel,
    BaseID,
    BaseUsername,
    BaseUserInfo,
):
    permission: UserPermission | None = Field(default=None)


class UserList(BaseModel):
    root: list[UserInfo]


class User(
    BaseModel,
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


class BaseTitle:
    title: str = Field(max_length=64)


class BaseAuthor:
    author: str = Field(min_length=4, max_length=32)


class BaseDate:
    pub_date: Annotated[
        datetime,
        WithJsonSchema(
            {
                "title": "pub_date",
                "type": "string",
            }
        )
    ] = Field(default_factory=datetime.now)
    mod_date: Annotated[
        datetime,
        WithJsonSchema(
            {
                "title": "mod_date",
                "type": "string",
            }
        )
    ] = Field(default_factory=datetime.now) 


class Article(
    BaseModel,
    BaseTitle,
    BaseAuthor,
    BaseDate,
):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra = {
            "indexes": [
                IndexModel([("title", 1)], unique=True),
                IndexModel([("pub_date", 1), ("mod_date", 1), ("author", 1)]),
            ],
        },
    )

    body: str | None = Field(default=None)
    summary: str | None = Field(default=None)


class ArticleInfo(
    BaseModel,
    BaseID,
    BaseTitle,
    BaseAuthor,
    BaseDate,
):
    pass


class ArticleList(BaseModel):
    root: list[ArticleInfo]