import strawberry as sb
from strawberry.tools import merge_types
from strawberry.fastapi import GraphQLRouter

from . import articles
from . import books
from . import users
from . import depends

Query = merge_types(
    "Query",
    (
        articles.Query,
    )
)

Mutation = merge_types(
    "Mutation",
    (
        articles.Mutation,
        users.Mutation,
    )
)
"""
Subscription = merge_types(
    "Subscription",
    ()
)
"""
schema = sb.Schema(query=Query, mutation=Mutation,)# subscription=Subscription)

graphql_app = GraphQLRouter(
    schema=schema,
    context_getter=depends.get_context,
)
