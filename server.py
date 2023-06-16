import logging
import os
import sys
from contextlib import asynccontextmanager

import pandas
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tinydb import TinyDB
from config import KwertyAPIConfig
from routes import router
from services import STARTUP_OBJECTS

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

config = KwertyAPIConfig()


def load_validation_data():
    return pandas.read_csv("kwerty_data.csv", encoding='utf-8', engine='python')


def load_tiny():
    db = TinyDB('db.json')
    return db


@asynccontextmanager
async def lifespan(app: FastAPI):
    STARTUP_OBJECTS["validation_data"] = load_validation_data()
    STARTUP_OBJECTS["db"] = load_tiny()

    yield
    STARTUP_OBJECTS.clear()



def load_app():
    app = FastAPI(
        title=config.app_name,
        debug=config.environment == "TEST",
        lifespan=lifespan,
    )
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/kwerty")
    return app


if __name__ == "__main__":
    uvicorn.run(
        "server:load_app",
        host="0.0.0.0",
        port=3500,
        reload=os.environ.get("ENVIRONMENT") == "TEST",
    )
