import bcrypt
import jwt

from app.config import settings
from app.database.models import UserLogin

async def password_hasher(passwd: str) -> bytes:
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(passwd.encode(), salt)

    return pw_hash


async def authenticate(login: UserLogin):
    pass
