import orjson
import strawberry as sb
from bson import ObjectId
from pydantic import ValidationError
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.database.db import db
from app.database.utils import find_one_or_404
from app.database.models import (
    Article,
    ArticleInfo,
    ArticleList,
)

@sb.experimental.pydantic.type(model=Article)
class ArticleType:
    title: sb.auto
    author: sb.auto
    pub_date: sb.auto
    mod_date:sb.auto
    body: sb.auto
    summary: sb.auto


@sb.experimental.pydantic.input(model=Article)
class ArticleInput:
    title: sb.auto
    author: sb.auto
    body: sb.auto
    summary: sb.auto


@sb.experimental.pydantic.type(model=ArticleInfo)
class ArticleInfoType:
    id: str
    title: sb.auto
    author: sb.auto
    pub_date: sb.auto
    mod_date:sb.auto


@sb.experimental.pydantic.type(model=ArticleList)
class ArticleListType:
    root: sb.auto


@sb.type
class Query:
    @sb.field
    async def articles_list(self) -> ArticleListType:
        articles = ArticleList(
            root=await db["articles"].find(
            {}, {"_id": 1, "title": 1, "author": 1, "pub_date": 1, "mod_date": 1}
            ).to_list()
        )
        return ArticleListType.from_pydantic(articles)


    @sb.field
    async def article(self, id: str) -> ArticleType:
        article = await find_one_or_404(
            filter={"_id": ObjectId(id)},
            collection=db.get_collection("articles"),
            model=Article
        )
        return ArticleType.from_pydantic(article)


@sb.type
class Mutation:
    @sb.field
    async def create_article(self, input: ArticleInput) -> ArticleType:
        try:
            article = input.to_pydantic()

            result = await db["articles"].insert_one(
                orjson.loads(article.model_dump_json())
            )
            assert isinstance(result.inserted_id, ObjectId)

            return ArticleType.from_pydantic(article)
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        except DuplicateKeyError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @sb.field
    async def update_article(self, id: str, input: ArticleInput) -> ArticleType:
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        except PyMongoError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @sb.field
    async def delete_article(self, id: str) -> bool:
        try:
            deleted = await db["articles"].delete_one({"_id": ObjectId(id)})
            return deleted.deleted_count == 1
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)