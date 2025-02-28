import bcrypt
import jwt
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
            detail="Try creating user again."
        )


async def find_one_or_404(filter: dict, collection):
    try:
        assert await collection.count_documents(filter) == 1

        item = await collection.find(filter)
        return await item.anext()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )


async def authenticate(login: UserLogin):
    pass
