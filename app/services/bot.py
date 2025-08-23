import os
from fastapi import FastAPI, Request, APIRouter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from app.schemas.prompt import PromptRequest, QueryRequest
# from app.db.connection_db import db_chain
from twilio.rest import Client as twilio_client
import chromadb
from app.utils.twilio import send_message


router = APIRouter()

@router.get("/")
def home():
    return {"status": "WhatsApp Bot Running 🚀"}


@router.post("/ask_db")
async def ask_db(request: Request):
    #response = db_chain.run(request.question)
    #return {"answer": response}
    print(request)
    
    
@router.post("/message")
def message():    
    send_message('Hello from backend')    
    return True