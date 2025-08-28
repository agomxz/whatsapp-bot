from fastapi import APIRouter, status
from app.utils.twilio import TwilioService
from app.redis_memory import (
    get_chat_memory,
    save_chat_memory,
)
from app.services.chat_service import (
    handle_welcome,
    handle_random_vehicle,
    handle_vehicle_suggestion,
    handle_financing,
    handle_company_info,
    handle_vehicle_question,
    handle_recommendation,
)
from app.services.llm_service import LLMService
from app.dependecies.dependency import get_twilio_service, get_llm_service
from app.constants.coincidences import KAVAK_WEBSITE, USER_QUESTION, FINNANCING_OPTIONS
from app.db import vectorstore, vectorstore_blog
from fastapi import Form, Depends
from langchain.schema import AIMessage, HumanMessage
from app.schemas.chat_request import ChatRequest
from app.config import logger

router = APIRouter()


@router.get("/", summary="Healthcheck", status_code=status.HTTP_200_OK)
def home() -> None:
    return {"status": "API Running"}


@router.post("/message", summary="Test Twilio Sandbox", status_code=status.HTTP_200_OK)
def message(twilio_service: TwilioService = Depends(get_twilio_service)) -> None:
    twilio_service.send_message("Hello from backend")


@router.post(
    "/chat",
    summary="Local Whatsapp chatbot",
    status_code=status.HTTP_200_OK,
)
def chat(request: ChatRequest, llm_service: LLMService = Depends(get_llm_service)):
    llm = llm_service.get_llm()

    user_id = request.user_id
    user_input = request.user_input

    chat_history = get_chat_memory(user_id)

    if not chat_history:
        response = handle_welcome(llm)

    else:
        if user_input in ["1", "uno"]:
            response = handle_random_vehicle(user_id, vectorstore)

        elif user_input in ["2", "dos"]:
            response = handle_vehicle_suggestion(user_input, chat_history, llm)

        else:
            if user_input in FINNANCING_OPTIONS:
                response = handle_financing(user_id, llm)

            else:
                query = user_input.lower()
                if any(word in query for word in KAVAK_WEBSITE):
                    response = handle_company_info(user_input, llm, vectorstore_blog)

                elif any(word in query for word in USER_QUESTION):
                    response = handle_vehicle_question(user_input, user_id, vectorstore)

                else:
                    response = handle_recommendation(user_input, chat_history, llm)

    user_msg = HumanMessage(content=str(user_input))

    if isinstance(response, dict):
        ai_msg = AIMessage(content=str(response.get("answer", "")))
    else:
        ai_msg = AIMessage(content=str(response))

    chat_history.append(user_msg)
    chat_history.append(ai_msg)
    chat_history = chat_history[-6:]
    save_chat_memory(user_id, chat_history)

    return {"response": response}


@router.post(
    "/twilio",
    summary="Whatsapp chatbot",
    status_code=status.HTTP_200_OK,
)
def twilio_chat(
    From: str = Form(...),
    Body: str = Form(...),
    twilio_service: TwilioService = Depends(get_twilio_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    try:
        logger.info(From)

        llm = llm_service.get_llm()

        user_id = From
        user_input = Body.lower()

        chat_history = get_chat_memory(user_id)

        if not chat_history:
            response = handle_welcome(llm)

        else:
            if user_input in ["1", "uno"]:
                response = handle_random_vehicle(user_id, vectorstore)

            elif user_input in ["2", "dos"]:
                response = handle_vehicle_suggestion(user_input, chat_history, llm)

            else:

                if any(option in user_input for option in FINNANCING_OPTIONS):
                    response = handle_financing(user_id, user_input, llm)

                else:
                    query = user_input.lower()
                    if any(word in query for word in KAVAK_WEBSITE):
                        response = handle_company_info(
                            user_input, llm, vectorstore_blog
                        )

                    elif any(word in query for word in USER_QUESTION):
                        response = handle_vehicle_question(
                            user_input, user_id, vectorstore
                        )

                    else:
                        response = handle_recommendation(user_input, chat_history, llm)

        user_msg = HumanMessage(content=str(user_input))

        if isinstance(response, dict):
            ai_msg = AIMessage(content=str(response.get("answer", "")))
        else:
            ai_msg = AIMessage(content=str(response))

        chat_history.append(user_msg)
        chat_history.append(ai_msg)
        chat_history = chat_history[-6:]
        save_chat_memory(user_id, chat_history)
        twilio_service.send_message(response.content)

    except Exception as e:
        twilio_service.send_message("Agente no disponible")
        logger.error("Unexpected error: %s", e)
