import os
from fastapi import FastAPI, Request, APIRouter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from app.schemas.prompt import PromptRequest, QueryRequest
# from app.db.connection_db import db_chain
from twilio.rest import Client as twilio_client
import chromadb
from app.config import TWILIO_KEY


#from utils import send_whatsapp_message

# load_dotenv()

router = APIRouter()


# #Modelo de OpenAI via LangChain
# llm = ChatOpenAI(
#     model="gpt-4o-mini", 
#     api_key=os.getenv("OPENAI_API_KEY")
# )

@router.get("/")
def home():
    return {"status": "WhatsApp Bot Running 🚀"}

# @router.post("/webhook")
# async def whatsapp_webhook(request: Request):
#     """Webhook de WhatsApp que recibe mensajes"""
#     data = await request.json()

#     try:
#         message = data["entry"][0]["changes"][0]["value"]["messages"][0]
#         from_number = message["from"]      # número de quien manda
#         text = message["text"]["body"]     # texto del usuario

#         # Procesar con modelo LLM (LangChain)
#         response = llm.invoke(text)

#         # Enviar respuesta a WhatsApp
#         #send_whatsapp_message(from_number, response.content)

#     except Exception as e:
#         print("Error:", e)

#     return {"status": "ok"}




@router.post("/ask_db")
async def ask_db(request: Request):
    # LangChain traduce la pregunta a SQL y obtiene la respuesta
    #response = db_chain.run(request.question)
    #return {"answer": response}
    print(request)
    
    
    

@router.post("/message")
def message():
    account_sid = 'AC89a4f161a470135a4c8267f35f85d120'
    auth_token = TWILIO_KEY
    client = twilio_client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        #content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
        #content_variables='{"1":"hola","2":"mensaje"}',
        to='whatsapp:+5215579123590',
        body="👋 Hola, tenemos una nueva promoción disponible para ti!"
    )

    print(message.sid)
    
    return True