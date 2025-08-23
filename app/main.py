from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.services import bot
from app.routes import insert, search
from app.utils.loader_db import load_data
from contextlib import asynccontextmanager


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("🚀 API iniciada, cargando datos...")
#     load_data()
#     yield
#     print("🛑 API apagada")
    

# app = FastAPI(lifespan=lifespan, title='WhatsApp BOT')

app = FastAPI(title='WhatsApp BOT')


app.include_router(bot.router,    prefix="/docs", tags=["Bot"])
app.include_router(insert.router, prefix="/docs", tags=["Insert"])
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