from fastapi import APIRouter, HTTPException, status, Depends
from app.services.rag import show_car_by_question
from fastapi import Request, Form
from app.config import logger
from app.utils.twilio import send_message
from twilio.twiml.messaging_response import MessagingResponse
from app.dependecies.llm_dependency import get_llm_service
from app.services.llm_service import LLMService
from app.constants.propmts import WELCOME_PROMPT
from langchain.memory import ConversationBufferMemory
from app.redis_memory import load_memory, save_memory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import LLMChain, PromptTemplate


router = APIRouter()

new_llm = LLMService()
llm = new_llm.get_llm()

# Plantilla de prompt
prompt = ChatPromptTemplate.from_template("{chat_history}\nUsuario: {input}\nAI:")


@router.post(
    "/ask",
    summary="Fetch a trip's timeline",
    status_code=status.HTTP_200_OK,
)
def ask(
    From: str = Form(...),
    Body: str = Form(...),
    #llm_service: LLMService = Depends(get_llm_service)
) :    
    user_id = From
    input = Body.strip()
    
    memory = load_memory(user_id)
    
    if not memory.chat_memory.messages:
        initial_promt = ChatPromptTemplate.from_messages([("system", WELCOME_PROMPT)])
        welcome_chain = initial_promt | llm
        response = welcome_chain.invoke({})

        #send_message(response)
    else:     
        chain = prompt | llm
        
        response = chain.invoke({
            "chat_history": memory.buffer,
            "input": input
        })
    
    memory.chat_memory.add_user_message(input)
    memory.chat_memory.add_ai_message(response)
    save_memory(user_id, memory)
    
    
    return {"response": response}

   
# new_llm = LLMService()
# llm = new_llm.get_llm()

# # Plantilla de prompt
# prompt = ChatPromptTemplate.from_template("{chat_history}\nUsuario: {input}\nAI:")


# @router.post(
#     "/chat",
#     summary="Chat history",
#     status_code=status.HTTP_200_OK,
# )
# def chat(
#     user_id: str, input: str
# ):
    
#     memory = load_memory(user_id)
    
#     chain = prompt | llm
    
#     response = chain.invoke({
#         "chat_history": memory.buffer,
#         "input": input
#     })
    
 
#     response = chain.invoke({
#         "chat_history": memory.buffer,
#         "input": input
#     })

#     # Guardamos en memoria
#     memory.chat_memory.add_user_message(input)
#     memory.chat_memory.add_ai_message(response)
#     save_memory(user_id, memory)
    
#     return {"response": response}
