import orjson
import strawberry as sb
from bson import ObjectId
from fastapi import status
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from app.database.db import db
from app.database.utils import find_one_or_404
from app.database.models import Article, ArticleList
from .depends import (
    ResultStatus,
    ArticleType,
    ArticleResult,
    ArticleInput,
    ArticleListType,
    ArticleListResult,
)


@sb.type
class Query:
    @sb.field
    async def articles_list(self) -> ArticleListResult:
        try:
            articles = ArticleList(
                root=await db["articles"].find(
                {}, {"_id": 1, "title": 1, "author": 1, "pub_date": 1, "mod_date": 1}
                ).to_list()
            )
            return ArticleListType.from_pydantic(articles)
        except Exception:
            return ResultStatus(status_code=status.HTTP_404_NOT_FOUND)


    @sb.field
    async def article(self, id: str) -> ArticleResult:
        try:
            article = await find_one_or_404(
                filter={"_id": ObjectId(id)},
                collection=db.get_collection("articles"),
                model=Article
            )
            assert article is not None
            return ArticleType.from_pydantic(article)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_404_NOT_FOUND)

@sb.type
class Mutation:
    @sb.field
    async def create_article(self, input: ArticleInput) -> ArticleResult:
        try:
            article = input.to_pydantic()

            result = await db["articles"].insert_one(
                orjson.loads(article.model_dump_json())
            )
            assert isinstance(result.inserted_id, ObjectId)

            return ArticleType.from_pydantic(article)
        except ValidationError:
            return ResultStatus(status_code=status.HTTP_400_BAD_REQUEST)
        except DuplicateKeyError:
            return ResultStatus(status_code=status.HTTP_409_CONFLICT)


    @sb.field
    async def update_article(self, id: str, input: ArticleInput) -> ArticleResult:
        try:
            article = input.to_pydantic()

            modified = await db["articles"].update_one(
                {"_id": ObjectId(id)},
                {"$set": orjson.loads(article.model_dump_json())},
            )
            assert modified.matched_count == 1
            assert modified.modified_count == 1

            return ArticleType.from_pydantic(article)
        except ValidationError:
            return ResultStatus(
                message="Invalid fields.",
                status_code=status.HTTP_400_BAD_REQUEST)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_404_NOT_FOUND)


    @sb.field
    async def delete_article(self, id: str) -> ResultStatus:
        try:
            deleted = await db["articles"].delete_one({"_id": ObjectId(id)})
            assert deleted.deleted_count == 1
            return ResultStatus(status_code=status.HTTP_204_NO_CONTENT)
        except AssertionError:
            return ResultStatus(status_code=status.HTTP_404_NOT_FOUND)