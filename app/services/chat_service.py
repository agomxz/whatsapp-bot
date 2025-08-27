from langchain.prompts import ChatPromptTemplate
from app.constants.propmts import (
    WELCOME_PROMPT,
    RECOMMENDATION_PROMPT,
    FINANCING_PROMPT,
    FINANCING_ERROR_PROMPT,
    VEHICLE_SUGGESTION_PROMPT,
    SUMMARY_FRIENDLY_PROMPT,
)
from app.redis_memory import (
    get_last_car,
    save_last_car,
)
from app.services.rag import show_car_by_question, show_random_vehicle
from app.services.rag_blog import ask_company_info
from app.config import logger


def handle_welcome(llm):
    prompt = ChatPromptTemplate.from_messages([("system", WELCOME_PROMPT)])
    chain = prompt | llm
    return chain.invoke({})


def handle_random_vehicle(user_id, vectorstore):
    response = show_random_vehicle(vectorstore, query="Muestra 1 auto al azar")
    save_last_car(user_id, response.content)
    return response


def handle_vehicle_suggestion(user_input, chat_history, llm):
    prompt = ChatPromptTemplate.from_messages([("system", VEHICLE_SUGGESTION_PROMPT)])
    chain = prompt | llm
    return chain.invoke({"chat_history": chat_history[-3:], "input": user_input})


def handle_financing(user_id: str, llm):
    try:
        last_car = get_last_car(user_id)
        price = last_car.get("car", False)

        if isinstance(price, str):
            chain = (
                ChatPromptTemplate.from_template(FINANCING_PROMPT.format(price=price))
                | llm
            )
            return chain.invoke({})
        else:
            chain = ChatPromptTemplate.from_template(FINANCING_ERROR_PROMPT) | llm
            return chain.invoke({})
    except:
        logger.error("Error getting financing")
        chain = ChatPromptTemplate.from_template(FINANCING_ERROR_PROMPT) | llm
        return chain.invoke({})


def handle_company_info(user_input, llm, vectorstore_blog):
    result = ask_company_info(vectorstore_blog, user_input)
    response = result["answer"]
    chain = (
        ChatPromptTemplate.from_template(SUMMARY_FRIENDLY_PROMPT.format(text=response))
        | llm
    )
    return chain.invoke({})


def handle_vehicle_question(user_input, user_id, vectorstore):
    response = show_car_by_question(vectorstore=vectorstore, query=user_input)
    save_last_car(user_id, response.content)
    return response


def handle_recommendation(user_input, chat_history, llm):
    prompt = ChatPromptTemplate.from_messages([("system", RECOMMENDATION_PROMPT)])
    chain = prompt | llm
    response = chain.invoke({})
    return response
