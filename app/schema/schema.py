import strawberry as sb
from strawberry.fastapi import GraphQLRouter

from . import articles
from . import books
from . import users


@sb.type
class Query():
    pass


@sb.type
class Mutation():
    pass


@sb.type
class Subscription():
    pass


schema = sb.Schema(query=Query, mutation=Mutation, subscription=Subscription)

graphql_app = GraphQLRouter(schema=schema)
