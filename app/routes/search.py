from fastapi import APIRouter, HTTPException, status
from app.services.rag import ask_question, ask_simil
from fastapi import Request, Form
from app.config import logger
from app.utils.twilio import send_message

router = APIRouter()

@router.post(
    "/ask",
    summary="Fetch a trip's timeline",
    status_code=status.HTTP_200_OK,
)
def ask(
    From: str = Form(...),
    Body: str = Form(...),
):
    
    logger.info(f"Message from {From}: {Body}")
    #result = ask_question(Body)
    
    
    result = ask_simil(Body)
    
    logger.info(result)
    logger.info(type(result))
    
    send_message(result['answer'])
    
    return True
