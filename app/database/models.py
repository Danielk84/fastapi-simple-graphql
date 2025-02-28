from enum import Enum
from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, WithJsonSchema
from pymongo import IndexModel
from bson import ObjectId


class BaseID(BaseModel):
    _id: Annotated[
        ObjectId,
        WithJsonSchema(
            {
                "title": "_id",
                "type": "oid",
            }
        )
    ]


class BaseUsername(BaseModel):
    username: str = Field(min_length=4 , max_length=32)


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
    BaseID,
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


class BaseTitle(BaseModel):
    title: str = Field(max_length=64)


class BaseAuthor(BaseModel):
    author: str = Field(min_length=4, max_length=32)


class BaseDate(BaseModel):
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
    BaseID,
    BaseTitle,
    BaseAuthor,
    BaseDate,
):
    pass


class ArticleList():
    root: list[ArticleInfo]


class Book(
    BaseTitle,
    BaseAuthor,
    BaseDate,
):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra = {
            "indexes": [
                IndexModel([
                    ("title", 1), ("pub_date", 1), ("mod_date", 1), ("author", 1),
                ]),
            ],
        },
    )

    intro: str | None = Field(default=None)


class BookInfo(
    BaseTitle,
    BaseAuthor,
    BaseDate,
):
    pass


class BookList(BaseModel):
    root: list[BookInfo]
