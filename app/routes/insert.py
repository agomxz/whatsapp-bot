from fastapi import APIRouter, Query
from app.services.rag import insert_document

router = APIRouter()

@router.post("/insert")
def insert(text: str = Query(...)):
    return insert_document(text)
