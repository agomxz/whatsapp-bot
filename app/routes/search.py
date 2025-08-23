from fastapi import APIRouter, Query
from app.services.rag import ask_question
from fastapi import Request, Form

router = APIRouter()

@router.get("/ask")
#def ask(query: str = Query(...)):
def ask(
    From: str = Form(...),  # sender phone number
    Body: str = Form(...),  # text of the message
):
    #request: Request
    print(f"Message from {From}: {Body}")
    return 'END'
    #return ask_question(query)
