from typing import Annotated

import strawberry as sb

from .depends import (
    UserLoginInput,
    UserInfoType,
    UserInfoInput,
    PermissionInput,
    LoginSuccess,
    ErrorStatus,
    LoginResult,
)


@sb.type
class Mutation:
    @sb.field
    async def login(self, input: UserLoginInput) ->  LoginResult:
        pass