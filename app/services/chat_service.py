from langchain.prompts import ChatPromptTemplate
from app.constants.propmts import (
    WELCOME_PROMPT,
    RECOMMENDATION_PROMPT,
    FINANCING_PROMPT,
    FINANCING_ERROR_PROMPT,
    VEHICLE_SUGGESTION_PROMPT,
    SUMMARY_FRIENDLY_PROMPT,
    SPELLCHECK_PROMPT,
)
from app.redis_memory import (
    get_last_car,
    save_last_car,
)
from app.services.rag import show_car_by_question, show_random_vehicle
from app.services.rag_blog import ask_company_info
from app.config import logger


def handle_user_input(llm, user_text: str):
    """
    Corrects user input using a spellcheck LLM chain and returns it in lowercase.
    """
    spellcheck_chain = ChatPromptTemplate.from_template(SPELLCHECK_PROMPT)
    corrected_input = spellcheck_chain | llm
    user_input = corrected_input.invoke({})
    logger.info(user_input.content)
    return user_input.content.lower()


def handle_welcome(llm):
    """
    Returns a welcome message using the welcome prompt and LLM.
    """
    prompt = ChatPromptTemplate.from_messages([("system", WELCOME_PROMPT)])
    chain = prompt | llm
    return chain.invoke({})


def handle_random_vehicle(user_id, vectorstore):
    """
    Retrieves a random vehicle from the vectorstore, saves it for the user in Redis,
    and returns the vehicle information.
    """
    response = show_random_vehicle(vectorstore, query="Muestra 1 auto al azar")
    save_last_car(user_id, response.content)
    return response


def handle_vehicle_suggestion(user_input, chat_history, llm):
    """
    Suggests vehicles based on user input and recent chat history using the LLM.
    Only the last 3 chat messages are considered in the prompt context.
    """
    prompt = ChatPromptTemplate.from_messages([("system", VEHICLE_SUGGESTION_PROMPT)])
    chain = prompt | llm
    return chain.invoke({"chat_history": chat_history[-3:], "input": user_input})


def handle_financing(user_id: str, user_input: str, llm):
    """
    Provides financing options for the last selected car.
    If a car is available, formats the financing prompt with price and budget.
    Returns an error prompt if no car is found or an exception occurs.
    """
    try:
        last_car = get_last_car(user_id)
        price = last_car.get("car", False)

        if isinstance(price, str):
            chain = (
                ChatPromptTemplate.from_template(
                    FINANCING_PROMPT.format(price=price, budget=user_input)
                )
                | llm
            )
            return chain.invoke({})
        else:
            chain = ChatPromptTemplate.from_template(FINANCING_ERROR_PROMPT) | llm
            return chain.invoke({})
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        logger.error("Error getting financing")
        chain = ChatPromptTemplate.from_template(FINANCING_ERROR_PROMPT) | llm
        return chain.invoke({})


def handle_company_info(user_input, llm, vectorstore_blog):
    """
    Answers user questions about a company by querying the blog vectorstore
    and summarizing the response in a friendly format.
    """
    result = ask_company_info(vectorstore_blog, user_input)
    response = result["answer"]
    chain = (
        ChatPromptTemplate.from_template(SUMMARY_FRIENDLY_PROMPT.format(text=response))
        | llm
    )
    return chain.invoke({})


def handle_vehicle_question(user_input, user_id, vectorstore):
    """
    Responds to user queries about specific vehicles by searching the vectorstore.
    Saves the resulting car information to Redis for later reference.
    """
    response = show_car_by_question(vectorstore=vectorstore, query=user_input)
    save_last_car(user_id, response.content)
    return response


def handle_recommendation(user_input, chat_history, llm):
    """
    Provides vehicle recommendations based on user input using a recommendation prompt.
    """
    prompt = ChatPromptTemplate.from_messages([("system", RECOMMENDATION_PROMPT)])
    chain = prompt | llm
    response = chain.invoke({})
    return response
