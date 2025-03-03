from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException, status
from bson import ObjectId

from app.config import settings
from app.database.db import db
from app.database.models import (
    UserLogin,
    UserPermission,
    User,
)


async def password_hasher(passwd: str) -> bytes:
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(passwd.encode(), salt)

    return pw_hash


async def create_user(
    login: UserLogin,
    permission: UserPermission = UserPermission.guest,
    f_name: str | None = None,
    l_name: str | None = None,
) -> User:
    passwd_hash = password_hasher(login.password)

    user = User(
        username=login.username,
        passwd_hash=passwd_hash,
        permission=permission,
        f_name=f_name,
        l_name=l_name,
    )

    try:
        result = await db.users.insert_one(user.model_dump())

        assert isinstance(result.inserted_id, ObjectId)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def create_token(user: User) -> str:
    try:
        token = jwt.encode(
            payload={
                "username": user.username,
                "exp": datetime.now(timezone.utc) +
                    timedelta(minutes=settings.TOKEN_EXPIRED_TIME),
            },
            key=settings.SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )
        return token
    except jwt.PyJWKError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def find_one_or_404(filter: dict, collection, model: BaseModel):
    try:
        assert await collection.count_documents(filter) == 1

        item = await collection.find(filter).next()
        item.pop("_id")
        return model(**item)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def authenticate(
    login: UserLogin,
    permission: UserPermission | None = None,
) -> User:
    user = await find_one_or_404(
        filter={ "username": login.username },
        collection=db.get_collection("users"),
        model=User
    )
    try:
        assert bcrypt.checkpw(
            password=login.password.encode,
            hashed_password=user.passwd_hash,
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if permission is not None:
        try:
            assert user.permission == permission
        except Exception:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user


async def auth_token(token: str, permission: UserPermission | None = None):
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
        )
    except (
        jwt.InvalidTokenError,
        jwt.ExpiredSignatureError,  
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except jwt.PyJWKError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user = find_one_or_404(
        filter={ "username": payload["username"]},
        collection=db.get_collection("users"),
        model=User,
    )  
    if permission is not None:
        try:
            assert user.permission == permission
        except Exception:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user
