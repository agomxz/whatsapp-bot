from fastapi import APIRouter, status, HTTPException
from app.utils.twilio import TwilioService
from app.services.llm_service import LLMService
from app.services.chat_service import ChatService
from app.redis_memory import RedisMemoryManager
from app.dependecies.dependency import get_twilio_service, get_llm_service, get_redis_memory_manager, get_chat_service
from app.constants.coincidences import KAVAK_WEBSITE, USER_QUESTION, FINNANCING_OPTIONS, USER_CLOSE_CHAT
from app.db import vectorstore, vectorstore_blog
from fastapi import Form, Depends
from langchain.schema import AIMessage, HumanMessage
from app.schemas.chat_request import ChatRequest
from app.config import logger
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
from typing import List
from fastapi import Query
from app.utils.loader_data import load_products

router = APIRouter()


@router.get("/", summary="Healthcheck", status_code=status.HTTP_200_OK)
def home() -> None:
    return {"status": "API Running"}


# === API Endpoint 1: List items ===
@router.get("/items/")
def get_items(ids: List[int] = Query(default=None)):
    products = load_products()
    if ids:
        filtered = [p for p in products if p["id"] in ids]
        if not filtered:
            raise HTTPException(status_code=404, detail="Items not found")
        return filtered
    return products


# === API Endpoint 2: Compare items with Llama3 ===
@router.post("/compare/")
def compare_items(ids: List[int]):
    products = load_products()
    selected = [p for p in products if p["id"] in ids]

    if len(selected) < 2:
        raise HTTPException(status_code=400, detail="Please provide at least two valid item IDs")

    # Initialize the Llama3 model via Ollama
    llm = Ollama(model="llama3")

    # Prompt template for comparison
    prompt = PromptTemplate(
        input_variables=["items"],
        template=(
            "You are a helpful assistant. Compare the following items in detail:\n"
            "{items}\n\n"
            "Explain which product is better overall, and why, considering features, price, and rating."
        )
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    items_text = json.dumps(selected, indent=2)
    result = chain.run(items=items_text)

    return {"comparison": result}


# @router.post("/message", summary="Test Twilio Sandbox", status_code=status.HTTP_200_OK)
# def message(twilio_service: TwilioService = Depends(get_twilio_service)) -> None:
#     """
#     Send a test message to the Twilio sandbox in order to check if the connection is working
#     """
    
#     try:
#         twilio_service.send_message("Hello from backend")
#     except Exception as e:
#         logger.error("Error sending message: %s", e)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to send message"
#         )

# @router.post("/agent", summary="IA Agent", status_code=status.HTTP_200_OK)
# def message(twilio_service: TwilioService = Depends(get_twilio_service)) -> None:
#     """
#     Send a test message to the Twilio sandbox in order to check if the connection is working
#     """
    
#     try:
#         twilio_service.send_message("Hello from backend")
#     except Exception as e:
#         logger.error("Error sending message: %s", e)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to send message"
#         )


# @router.post(
#     "/chat",
#     summary="Local Whatsapp chatbot",
#     status_code=status.HTTP_200_OK,
# )
# def chat(
#     request: ChatRequest, 
#     llm_service: LLMService = Depends(get_llm_service),
#     chat_service: ChatService = Depends(get_chat_service),
#     redis_memory_manager: RedisMemoryManager = Depends(get_redis_memory_manager)
# ):
#     """
#     Handle a local chat request from a user.
#     """
#     try:
#         llm = llm_service.get_llm()

#         user_id = request.user_id
#         user_input = request.user_input

#         logger.info("User id: %s", user_id)
#         logger.info("User input: %s", user_input)

#         chat_history = redis_memory_manager.get_chat_memory(user_id)

#         if not chat_history:
#             logger.info("First message")
#             response = chat_service.handle_welcome(llm)

#         else:
#             if user_input in ["1", "uno"]:
#                 logger.info("Random vehicle")
#                 response = chat_service.handle_random_vehicle(user_id, vectorstore)

#             elif user_input in ["2", "dos"]:
#                 logger.info("Vehicle suggestion")
#                 response = chat_service.handle_vehicle_suggestion(user_input, chat_history, llm)

#             else:
#                 if any(word in user_input.lower() for word in FINNANCING_OPTIONS):

#                     logger.info("Financing option")
#                     response = chat_service.handle_financing(user_id, user_input, llm)

#                 else:
#                     query = user_input.lower()

#                     if any(word in query for word in KAVAK_WEBSITE):
#                         logger.info("Company info")
#                         response = chat_service.handle_company_info(user_input, llm, vectorstore_blog)

#                     elif any(word in query for word in USER_QUESTION):
#                         logger.info("Vehicle question")
#                         response = chat_service.handle_vehicle_question(user_input, user_id, vectorstore)

#                     elif any(word in query for word in USER_CLOSE_CHAT):
#                         logger.info("Close chat")
#                         redis_memory_manager.clean_user_chat(user_id)
#                         response = chat_service.handle_close_chat(user_id, llm)

#                     else:
#                         logger.info("Recommendation")
#                         response = chat_service.handle_recommendation(user_input, chat_history, llm)

#         user_msg = HumanMessage(content=str(user_input))

#         if isinstance(response, dict):
#             ai_msg = AIMessage(content=str(response.get("answer", "")))
#         else:
#             ai_msg = AIMessage(content=str(response))

#         chat_history.append(user_msg)
#         chat_history.append(ai_msg)
#         chat_history = chat_history[-6:]
#         redis_memory_manager.save_chat_memory(user_id, chat_history)

#         return {"response": response}

#     except Exception as e:
#         logger.error("Unexpected error: %s", e)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to process chat"
#         )


# @router.post(
#     "/twilio",
#     summary="Whatsapp chatbot",
#     status_code=status.HTTP_200_OK,
# )
# def twilio_chat(
#     From: str = Form(...),
#     Body: str = Form(...),
#     twilio_service: TwilioService = Depends(get_twilio_service),
#     chat_service: ChatService = Depends(get_chat_service),
#     redis_memory_manager: RedisMemoryManager = Depends(get_redis_memory_manager),
#     llm_service: LLMService = Depends(get_llm_service),
# ):
#     try:
#         """
#         Chatbot webhook for Twilio
#         """

#         llm = llm_service.get_llm()

#         user_id = From
#         user_input = Body.lower()

#         logger.info("User id: %s", user_id)
#         logger.info("User input: %s", user_input)
        
#         chat_history = redis_memory_manager.get_chat_memory(user_id)

#         if not chat_history:
#             response = chat_service.handle_welcome(llm)

#         else:
#             if user_input in ["1", "uno"]:
#                 response = chat_service.handle_random_vehicle(user_id, vectorstore)

#             elif user_input in ["2", "dos"]:
#                 response = chat_service.handle_vehicle_suggestion(user_input, chat_history, llm)

#             else:
#                 if any(word in user_input.lower() for word in FINNANCING_OPTIONS):

#                     logger.info("Financing option")
#                     response = chat_service.handle_financing(user_id, user_input, llm)

#                 else:
#                     query = user_input.lower()
#                     logger.info("Query: %s", query)

#                     if any(word in query for word in KAVAK_WEBSITE):
#                         logger.info("Company info")
#                         response = chat_service.handle_company_info(user_input, llm, vectorstore_blog)

#                     elif any(word in query for word in USER_QUESTION):
#                         logger.info("Vehicle question")
#                         response = chat_service.handle_vehicle_question(user_input, user_id, vectorstore)

#                     elif any(word in query for word in USER_CLOSE_CHAT):
#                         logger.info("Close chat")
#                         redis_memory_manager.clean_user_chat(user_id)
#                         response = chat_service.handle_close_chat(user_id, llm)

#                     else:
#                         logger.info("Recommendation")
#                         response = chat_service.handle_recommendation(user_input, chat_history, llm)

#         user_msg = HumanMessage(content=str(user_input))

#         if isinstance(response, dict):
#             ai_msg = AIMessage(content=str(response.get("answer", "")))
#         else:
#             ai_msg = AIMessage(content=str(response))

#         chat_history.append(user_msg)
#         chat_history.append(ai_msg)
#         chat_history = chat_history[-6:]
#         redis_memory_manager.save_chat_memory(user_id, chat_history)        
#         twilio_service.send_message(response.content)

#         return {"response": response}

#     except Exception as e:
#         twilio_service.send_message("Agente no disponible")
#         logger.error("Unexpected error: %s", e)
