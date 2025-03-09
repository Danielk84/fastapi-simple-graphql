import asyncio

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.config import settings
from app.database.db import _db_name
from app.database.utils import create_user
from app.database.models import UserLogin, UserPermission

if settings.DEBUG == True:
    from app import app
else:
    raise ImportError("Debug mode is False!")

BASE_URL = "/graphql/"


@pytest.fixture(name="client")
def get_client():
    with MongoClient(str(settings.mongo_dsn)) as client:
        if _db_name in client.list_database_names():
            client.drop_database(_db_name)
        yield TestClient(app)

@pytest.fixture(name="user")
def get_user():
    user = asyncio.run(
        create_user(
            login=UserLogin(username="testuser", password="123123123"),
            permission=UserPermission.admin
        )
    )
    assert user is not None
    return user