from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes import bot
from app.utils.loader_db import load_data
from app.utils.loader_website import load_web_page
from contextlib import asynccontextmanager


# Create Chroma DataBases
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data()
    #load_web_page()
    yield


app = FastAPI(lifespan=lifespan, title="WhatsApp BOT")

app.include_router(bot.router, prefix="/docs", tags=["Bot"])

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
