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

_db_name = "test_database" if settings.DEBUG else "main_line"
db = client.get_database(_db_name)


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
    existing_collections = await db.list_collection_names()

    for name, model in base_models.items():
        schema, model_schema = await create_schema(name, model)

        try:
            if name not in existing_collections:
                await db.create_collection(name=name)

            await db.command(schema)
            if "indexes" in model_schema:
                await db.get_collection(name).create_indexes(
                    model_schema["indexes"]
                )
        except Exception as e:
            print(f"{name} : {e}")
            raise e
