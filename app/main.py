from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.database.db import client, run_db_setup
from app.schema import graphql_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_db_setup()

    yield

    await client.close()


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["HEAD", "GET", "POST"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=800, compresslevel=5)


app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    uvicorn.run(app)
