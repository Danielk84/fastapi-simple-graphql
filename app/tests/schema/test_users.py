import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.tests.utils import BASE_URL, get_client, get_user
from app.database.db import db
from app.database.models import User, UserLogin, UserPermission
from app.database.utils import create_user, auth_token, create_token, authenticate


@pytest.mark.asyncio
async def test_login(client: TestClient, user: User):
    login_mutation = """
        mutation {
          login(input: {password: "%s", username: "%s"}) {
            ... on ResultStatus {
              statusCode
            }
            ... on LoginSuccess {
              token
            }
          }
        }
    """
    response = client.post(
        BASE_URL,
        json={"query": login_mutation % ("123123123", "testuser")}
    )
    assert response.status_code == status.HTTP_200_OK
    assert await auth_token(response.json()["data"]["login"]["token"]) == user

    response = client.post(
        BASE_URL,
        json={"query": login_mutation % ("invalidPass", "invalidUser")}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["login"]["statusCode"] == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_check_auth(client: TestClient, user: User):
    auth_check_mutation = """
        mutation {
          checkAuth {
            ... on UserInfoType {
              fName
              lName
              _id
              permission
              username
            }
            ... on ResultStatus {
              message
              statusCode
            }
          }
        }
    """
    token = await create_token(user)
    assert token is not None

    response = client.post(
        BASE_URL,
        json={"query": auth_check_mutation},
        headers={"Authorization": token},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["checkAuth"]["username"] == user.username

    response = client.post(
        BASE_URL,
        json={"query": auth_check_mutation},
        headers={"Authorization": "invalidToken"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["checkAuth"]["statusCode"] == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_register(client: TestClient):
    register_mutation = """
        mutation {
          register(input: {password: "%s", username: "%s"}) {
            ... on UserInfoType {
              fName
              lName
              _id
              permission
              username
            }
            ... on ResultStatus {
              message
              statusCode
            }
          }
        }
    """
    response = client.post(
        BASE_URL,
        json={"query": register_mutation % ("123123123", "testuser")}
    )
    assert response.status_code == status.HTTP_200_OK
    user = await authenticate(
        login=UserLogin(
            username="testuser",
            password="123123123",
        ),
    )
    assert user is not None
    assert user.permission == UserPermission.guest


@pytest.mark.asyncio
async def test_users_list(client: TestClient, user: User):
    users_list_mutation = """
        mutation {
          usersList {
            ... on UserListType {
              __typename
              root {
                _id
                fName
                username
                permission
                lName
              }
            }
            ... on ResultStatus {
              message
              statusCode
            }
          }
        }
    """
    token = await create_token(user)
    assert token is not None

    response = client.post(
        BASE_URL,
        json={"query": users_list_mutation},
        headers={"Authorization": token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["usersList"]["root"][0]["username"] == user.username


@pytest.mark.asyncio
async def test_change_permission(client: TestClient, user: User):
    change_permission_mutation = """
        mutation {
          changePermission(id: "%s", permission: {permission: staff}) {
            ... on UserInfoType {
              fName
              lName
              _id
              permission
              username
            }
            ... on ResultStatus {
              message
              statusCode
            }
          }
        }
    """
    token = await create_token(user)
    assert token is not None

    test_user = await create_user(
        login=UserLogin(
            username="testuser2",
            password="123123123",
        ),
    )
    assert test_user is not None

    test_user = await db["users"].find_one({"username": test_user.username})
    assert test_user is not None

    response = client.post(
        BASE_URL,
        json={"query": change_permission_mutation % (test_user["_id"])},
        headers={"Authorization": token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["changePermission"]["permission"] == UserPermission.staff.value