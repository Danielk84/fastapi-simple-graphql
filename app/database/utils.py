from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
import orjson
from pydantic import BaseModel, ValidationError
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
) -> User | None:
    passwd_hash = await password_hasher(login.password)

    try:
        user = User(
            username=login.username,
            passwd_hash=passwd_hash,
            permission=permission,
            f_name=f_name,
            l_name=l_name,
        )

        result = await db.users.insert_one(orjson.loads(user.model_dump_json()))

        assert isinstance(result.inserted_id, ObjectId)
        return user
    except (ValidationError, AssertionError):
        return None


async def create_token(user: User) -> str | None:
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
        return None
    except Exception:
        raise


async def find_one_or_404(filter: dict, collection, model: BaseModel):
    try:
        assert await collection.count_documents(filter) == 1

        item = await collection.find(filter).next()
        item.pop("_id")
        return model(**item)
    except AssertionError:
        return None
    except Exception:
        raise


async def authenticate(
    login: UserLogin,
    permission: UserPermission | None = None,
) -> User | None:
    try:
        user = await find_one_or_404(
            filter={ "username": login.username },
            collection=db.get_collection("users"),
            model=User
        )
        assert user is not None
        assert bcrypt.checkpw(
            password=login.password.encode(),
            hashed_password=user.passwd_hash,
        )
        if permission is not None:
            assert user.permission is permission

        return user
    except AssertionError:
        return None
    except Exception:
        raise


async def auth_token(
    token: str,
    permission: UserPermission | None = None
) -> User | None:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
        )
        user = find_one_or_404(
            filter={ "username": payload["username"]},
            collection=db.get_collection("users"),
            model=User,
        )  
        assert user is not None
        if permission is not None:
            assert user.permission == permission
    except (
        jwt.InvalidTokenError,
        jwt.ExpiredSignatureError,
        AssertionError,
    ):
        return None
    except Exception:
        raise

    return user
