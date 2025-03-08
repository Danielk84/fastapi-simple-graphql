
import strawberry as sb
import orjson
from fastapi import status
from pydantic import ValidationError
from bson import ObjectId

from app.database.db import db
from app.database.models import UserPermission, User, UserList
from app.database.utils import (
    create_user,
    create_token,
    find_one_or_404,
    authenticate,
)
from .depends import (
    ResultStatus,
    UserLoginInput,
    UserInfoType,
    UserInfoResult,
    UserInfoInput,
    UserListType,
    UserListResult,
    PermissionInput,
    LoginSuccess,
    LoginResult,
    Context,
)


@sb.type
class Mutation:
    @sb.field
    async def login(self, input: UserLoginInput) ->  LoginResult:
        try:
            login = input.to_pydantic()

            user = await authenticate(login=login)
            assert user is not None

            token = await create_token(user)
            assert token is not None
            return LoginSuccess(token=token)
        except ValidationError:
            return ResultStatus(status_code=status.HTTP_400_BAD_REQUEST)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            raise


    @sb.field
    async def check_auth(self, info: sb.Info[Context]) -> UserInfoResult:
        try:
            user = await info.context.user()
            assert user is not None
            return UserInfoType.from_pydantic(user)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            raise


    @sb.field
    async def register(self, input: UserLoginInput) -> UserInfoResult:
        try:
            user = await create_user(login=input.to_pydantic())
            assert user is not None
            return UserInfoType.from_pydantic(user)
        except ValidationError:
            return ResultStatus(status_code=status.HTTP_400_BAD_REQUEST)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_409_CONFLICT)


    @sb.field
    async def users_list(self, info: sb.Info[Context]) -> UserListResult:
        try:
            admin = await info.context.user()
            assert admin is not None
            assert admin.permission == UserPermission.admin  

            users = UserList(root=await db["users"].find().to_list())
            return UserListType.from_pydantic(users)
        except ValidationError:
            return ResultStatus(status_code=status.HTTP_400_BAD_REQUEST)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_401_UNAUTHORIZED)


    @sb.field
    async def change_permission(
        self,
        info: sb.Info[Context],
        id: str,
        permission: PermissionInput
    ) -> UserInfoResult:
        try:
            admin = await info.context.user()
            assert admin is not None
            assert admin.permission == UserPermission.admin

            user_filter = {"_id": ObjectId(id)}
            user = await find_one_or_404(
                filter=user_filter,
                collection=db.get_collection("users"),
                model=User,
            )
            user.permission = permission.permission
            result = await db["users"].update_one(
                user_filter,
                {"$set": orjson.loads(user.model_dump_json())}
            )
            if result.modified_count == 1:
                return UserInfoType.from_pydantic(user)
            return ResultStatus(status_code=status.HTTP_409_CONFLICT)
        except ValidationError:
            return ResultStatus(status_code=status.HTTP_400_BAD_REQUEST)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            raise


    @sb.field
    async def update_info(
        self,
        info: sb.Info[Context],
        input: UserInfoInput
    ) -> UserInfoResult:
        try:
            user = await info.context.user()
            assert user is not None

            for key, value in input.to_pydantic().model_dump().items():
                print(key, value)
                if key is "id": continue
                setattr(user, key, value)

            obj = orjson.loads(user.model_dump_json())
            obj.pop("permission")

            result = await db["users"].update_one(
                {"username": user.username},
                {"$set": obj},
            )
            if result.modified_count == 1:
                return UserInfoType.from_pydantic(user)
            return ResultStatus(status_code=status.HTTP_409_CONFLICT) 
        except ValidationError as e:
            return ResultStatus(status_code=status.HTTP_400_BAD_REQUEST, message=e)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_401_UNAUTHORIZED)