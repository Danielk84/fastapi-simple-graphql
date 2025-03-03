from typing import Annotated

import strawberry as sb
from app.database.models import (
    UserLogin,
    UserPermission,
    UserInfo,
    Article,
    ArticleInfo,
    ArticleList,
)


@sb.experimental.pydantic.type(model=Article)
class ArticleType:
    title: sb.auto
    author: sb.auto
    pub_date: sb.auto
    mod_date:sb.auto
    body: sb.auto
    summary: sb.auto


@sb.experimental.pydantic.input(model=Article)
class ArticleInput:
    title: sb.auto
    author: sb.auto
    body: sb.auto
    summary: sb.auto


@sb.experimental.pydantic.type(model=ArticleInfo)
class ArticleInfoType:
    id: str
    title: sb.auto
    author: sb.auto
    pub_date: sb.auto
    mod_date:sb.auto


@sb.experimental.pydantic.type(model=ArticleList)
class ArticleListType:
    root: sb.auto




@sb.experimental.pydantic.input(model=UserLogin)
class UserLoginInput:
    username: sb.auto
    password: sb.auto


@sb.experimental.pydantic.type(model=UserInfo)
class UserInfoType:
    id: str
    username: sb.auto
    f_name: sb.auto
    l_name: sb.auto
    permission: sb.auto


@sb.experimental.pydantic.input(model=UserInfo)
class UserInfoInput:
    username: sb.auto
    f_name: sb.auto
    l_name: sb.auto


@sb.input
class PermissionInput:
    permission: UserPermission


@sb.type
class LoginSuccess:
    token: str


@sb.type
class ErrorStatus:
    message: str
    status_code: int


LoginResult = Annotated[
    LoginSuccess | ErrorStatus, sb.union("LoginResult")
]