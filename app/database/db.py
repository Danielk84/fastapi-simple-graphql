from copy import deepcopy

from pymongo import AsyncMongoClient
from pydantic import BaseModel

from app.config import settings
from app.database.models import User

client = AsyncMongoClient(
    str(settings.mongo_dsn),
    maxPoolSize=10,
    minPoolSize=2,
)

db = client["test_database"] if settings.DEBUG else client["main_line"]

base_models = { "users": User, }

base_schema = {
    "collMod": "",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
        },
    },
    "validationLevel": "strict"
}


async def remove_not_compatible_fields(schema: dict) -> dict:
    for key, value in schema["properties"].items():
        if "default" in value:
            del value["default"]
    return schema


async def create_schema(name: str, model: BaseModel) -> tuple[dict, dict]:
    model_shcema = await remove_not_compatible_fields(
        model.model_json_schema()
    )

    schema = deepcopy(base_schema)

    schema["collMod"] = name
    schema["validator"]["$jsonSchema"]["required"] = model_shcema["required"]
    schema["validator"]["$jsonSchema"]["properties"] = model_shcema["properties"]

    return (schema, model_shcema,)


async def run_db_setup() -> None:
    for name, model in base_models.items():
        schema, model_schema = await create_schema(name, model)

        try:
            await db.command(schema)
            if "indexes" in model_schema:
                await db.get_collection(name).create_indexes(
                    model_schema["indexes"]
                )
        except Exception as e:
            raise e


#  Collections
users = db["users"]
articles = db["articles"]
books = db["books"]