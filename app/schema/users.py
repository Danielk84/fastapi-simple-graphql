
import strawberry as sb
from strawberry.fastapi import BaseContext
from fastapi import status
from pydantic import ValidationError

from app.database.utils import (
    create_token,
    authenticate,
    auth_token,
)
from app.database.models import User
from .depends import (
    ResultStatus,
    UserLoginInput,
    UserInfoType,
    UserInfoResult,
    UserInfoInput,
    PermissionInput,
    LoginSuccess,
    LoginResult,
)


class Context(BaseContext):
    async def user(self) -> User | None:
        if not self.request:
            return None

        token = self.request.headers.get("Authorization", None)
        return await auth_token(token)


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
    async def register(self, user: sb.Info[Context]) -> UserInfoResult:
        return UserInfoType.from_pydantic(user)