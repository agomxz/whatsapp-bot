from fastapi import APIRouter, status
from app.utils.twilio import TwilioService
from app.redis_memory import (
    get_chat_memory,
    get_last_car,
    save_chat_memory,
    save_last_car,
)
from app.services.llm_service import LLMService
from app.dependecies.dependency import get_twilio_service

from langchain.prompts import ChatPromptTemplate
from app.constants.propmts import (
    WELCOME_PROMPT,
    RECOMMENDATION_PROMPT,
    FINANCING_PROMPT,
    VEHICLE_SUGGESTION_PROMPT,
    SUMMARY_FRIENDLY_PROMPT,
)
from app.constants.coincidences import KAVAK_WEBSITE, USER_QUESTION
from app.services.rag import show_car_by_question, show_random_vehicle
from app.services.rag_blog import ask_company_info
from app.db import vectorstore, vectorstore_blog
from fastapi import Form, Depends
from langchain.schema import AIMessage, HumanMessage
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.config import logger



router = APIRouter()


@router.get("/", summary="Healthcheck", status_code=status.HTTP_200_OK)
def home() -> None:
    return {"status": "API Running"}


@router.post(
            "/message", 
            summary="Test Twilio Sandbox", 
            status_code=status.HTTP_200_OK
)
def message(twilio_service: TwilioService = Depends(get_twilio_service)) -> None:
    twilio_service.send_message('Hello from backend')
    


new_llm = LLMService()
llm = new_llm.get_llm()


@router.post(
    "/chat",
    summary="Local Whatsapp chatbot",
    status_code=status.HTTP_200_OK,
)
def chat(user_id: str, user_input: str):

    chat_history = get_chat_memory(user_id)
    last_car = get_last_car(user_id)

    if not chat_history:
        initial_promt = ChatPromptTemplate.from_messages([("system", WELCOME_PROMPT)])
        welcome_chain = initial_promt | llm
        response = welcome_chain.invoke({})

    else:
        if user_input == "1":
            response = show_random_vehicle(
                vectorstore=vectorstore, query="Muestra 1 auto al azar"
            )
            
            #save_last_car(user_id, result)

        elif user_input == "2":
            prompt = ChatPromptTemplate.from_messages(
                [("system", VEHICLE_SUGGESTION_PROMPT)]
            )
            chain = prompt | llm
            response = chain.invoke(
                {"chat_history": chat_history[-3:], "input": user_input}
            )

        else:
            if "financiamiento" in user_input.lower() and last_car:
                price = last_car.get("car", False)
                if isinstance(price, str):
                    chain = (
                        ChatPromptTemplate.from_template(
                            FINANCING_PROMPT.format(price=price)
                        )
                        | llm
                    )
                    response = chain.invoke({})

                else:
                    response = "Ups ocurrio algo al momento de realizar el financiamiento, intenta de nuevo"

            else:
                query = user_input.lower()
                if any(
                    word in query
                    for word in KAVAK_WEBSITE
                ):
                    result = ask_company_info(vectorstore_blog, user_input)
                    response = result["answer"]

                    chain = (
                        ChatPromptTemplate.from_template(
                            SUMMARY_FRIENDLY_PROMPT.format(text=response)
                        )
                        | llm
                    )
                    response = chain.invoke({})

                elif any(
                    word in query
                    for word in USER_QUESTION
                ):

                    result = show_car_by_question(
                        vectorstore=vectorstore, query=user_input
                    )
                    response = result["answer"]
                    save_last_car(user_id, {"answer": response})

                else:
                    prompt = ChatPromptTemplate.from_messages(
                        [("system", RECOMMENDATION_PROMPT)]
                    )
                    chain = prompt | llm
                    response = chain.invoke(
                        {"chat_history": chat_history[-3:], "input": user_input}
                    )

    user_msg = HumanMessage(content=str(user_input))

    if isinstance(response, dict):
        ai_msg = AIMessage(content=str(response.get("answer", "")))
    else:
        ai_msg = AIMessage(content=str(response))

    chat_history.append(user_msg)
    chat_history.append(ai_msg)
    chat_history = chat_history[-6:]
    save_chat_memory(user_id, chat_history)
    
    
    logger.info('=========================================')
    logger.info(type(response))
    logger.info(response)
    logger.info('=========================================')

    return {"response": response}


@router.post(
    "/twilio",
    summary="Whatsapp chatbot",
    status_code=status.HTTP_200_OK,
)
def chat( 
        From: str = Form(...),
        Body: str = Form(...),
        twilio_service: TwilioService = Depends(get_twilio_service)
):
    try:
        user_id = From
        user_input = Body

        chat_history = get_chat_memory(user_id)
        last_car = get_last_car(user_id)

        if not chat_history:
            initial_promt = ChatPromptTemplate.from_messages([("system", WELCOME_PROMPT)])
            welcome_chain = initial_promt | llm
            response = welcome_chain.invoke({})

        else:
            if user_input == "1":
                response = show_random_vehicle(
                    vectorstore=vectorstore, query="Muestra 1 auto al azar"
                )
                #save_last_car(user_id, result)

            elif user_input == "2":
                prompt = ChatPromptTemplate.from_messages(
                    [("system", VEHICLE_SUGGESTION_PROMPT)]
                )
                chain = prompt | llm
                response = chain.invoke()

            else:
                if "financiamiento" in user_input.lower() and last_car:
                    price = last_car.get("car", False)
                    if isinstance(price, str):
                        chain = (
                            ChatPromptTemplate.from_template(
                                FINANCING_PROMPT.format(price=price)
                            )
                            | llm
                        )
                        response = chain.invoke({})

                    else:
                        response = "Ups ocurrio algo al momento de realizar el financiamiento, intenta de nuevo"

                else:
                    query = user_input.lower()
                    if any(
                        word in query
                        for word in KAVAK_WEBSITE
                    ):
                        result = ask_company_info(vectorstore_blog, user_input)
                        response = result["answer"]

                        chain = (
                            ChatPromptTemplate.from_template(
                                SUMMARY_FRIENDLY_PROMPT.format(text=response)
                            )
                            | llm
                        )
                        response = chain.invoke({})

                    elif any(
                        word in query
                        for word in USER_QUESTION
                    ):

                        result = show_car_by_question(
                            vectorstore=vectorstore, query=user_input
                        )
                        response = result["answer"]
                        save_last_car(user_id, {"answer": response})

                    else:
                        prompt = ChatPromptTemplate.from_messages(
                            [("system", RECOMMENDATION_PROMPT)]
                        )
                        chain = prompt | llm
                        response = chain.invoke(
                            {"chat_history": chat_history[-3:], "input": user_input}
                        )

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
        
        #twiml = MessagingResponse()
        #twiml.message(response)
        #return Response(content=str(twiml), media_type="application/xml")
        
        return {"answer": response.content}

    except Exception as e:
        twilio_service.send_message('Agente no disponible')
        logger.error("Unexpected error: %s", e)