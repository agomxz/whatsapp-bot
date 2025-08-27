from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from app.config import logger

# Diccionario global para almacenar historial por usuario
user_histories = {}


def get_user_history(user_id: str) -> ChatMessageHistory:
    logger.info("Buscando usuario en la base de datos")
    logger.info(f"user_id: {user_id}")
    if user_id not in user_histories:
        user_histories[user_id] = ChatMessageHistory()
    return user_histories[user_id]


def get_user_runnable(user_id: str, llm: ChatOpenAI) -> RunnableWithMessageHistory:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Eres un asistente automotriz."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm
    runnable = RunnableWithMessageHistory(
        chain,
        get_user_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    return runnable
