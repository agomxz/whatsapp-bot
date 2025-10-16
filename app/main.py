from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes import bot
from app.utils.loader_db import load_data
from contextlib import asynccontextmanager


# # Create Chroma DataBases
@asynccontextmanager
async def lifespan(app: FastAPI):
    #load_data()
    yield


app = FastAPI(lifespan=lifespan, title="IA Agent")

app.include_router(bot.router, prefix="/docs", tags=["IA Agent"])

# CORS Config
origins = ["*", "/"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
    expose_headers=["*"],
)
