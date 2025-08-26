from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes import bot
from app.routes import search
from app.utils.loader_db import load_data
from app.utils.loader_website import load_web_page
from contextlib import asynccontextmanager
from app.config import logger


# # Create Chroma DataBase
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 API iniciada, cargando datos...")
    load_data()
    load_web_page()
    yield
    logger.info("🛑 API apagada")
    

app = FastAPI(lifespan=lifespan, title='WhatsApp BOT')

app.include_router(bot.router,    prefix="/docs", tags=["Bot"])
app.include_router(search.router, prefix="/docs", tags=["Search"])

# Configure CORS
origins = ["*", "/"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
    expose_headers=["*"],
)