import strawberry as sb
from bson import ObjectId

from app.database.db import db
from app.database.models import (
    Article,
    ArticleInfo,
)

@sb.experimental.pydantic.type(model=Article)
class ArticleType:
    title: sb.auto
    author: sb.auto
    pub_date: sb.auto
    mod_date:sb.auto
    body: sb.auto
    summary: sb.auto


@sb.experimental.pydantic.type(model=ArticleInfo)
class ArticleInfoType:
    id: sb.auto
    title: sb.auto
    author: sb.auto
    pub_date: sb.auto
    mod_date:sb.auto


@sb.type
class ArticleListType:
    root: list[ArticleInfoType]


@sb.type
class Query:
    @sb.field
    async def articles_list(self) -> ArticleListType:
        articles = await db["articles"].find(
            {}, {"_id": 1, "title": 1, "author": 1, "pub_date": 1, "mod_date": 1}
        ).to_list()
        return ArticleListType(root=articles)


    @sb.field
    async def article(self, id: str) -> ArticleType:
        article = await db["articles"].find_one({"_id": ObjectId(id)})
        article.pop("_id")
        return ArticleType(**article)


@sb.type
class Mutation:
    @sb.field
    async def create_articles(self, article: ArticleType) -> ArticleType:
        pass