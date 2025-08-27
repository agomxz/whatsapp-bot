from langchain.chains import RetrievalQA
from app.db import retriever_vehicle
from app.config import logger
from app.services.llm_service import LLMService
from app.constants.propmts import SUMMARY_SHOW_VEHICLE
import random
from langchain.prompts import ChatPromptTemplate


# Inicializar LLM
llm_obj = LLMService()
llm = llm_obj.get_llm()

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever_vehicle)


def show_random_vehicle(vectorstore, query: str, k: int = 1):

    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return {"answer": "No se encontraron vehículos."}

    selected_vehicle = random.choice(results)
    vehicle = selected_vehicle.page_content
    
    
    prompt = ChatPromptTemplate.from_messages([("system", SUMMARY_SHOW_VEHICLE + vehicle)])
    chain = prompt | llm
    
    response = chain.invoke({})
    
    answer_text = qa_chain.invoke(SUMMARY_SHOW_VEHICLE + vehicle )
    
    logger.info('\n\n')
    logger.info(type(response))
    logger.info(response.content)
    logger.info('\n\n')

    return response


def show_car_by_question(vectorstore, query: str, k: int = 1):
    """
    Busca el documento más relevante y devuelve su contenido
    """
    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return {"answer": "No se encontraron resultados."}

    answer_text = qa_chain.run(SUMMARY_SHOW_VEHICLE)

    return {"answer": answer_text}


def show_resume(vectorstore, query: str, k: int = 3):
    """
    Consulta RAG para devolver un resumen de los k autos más relevantes
    """
    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return {"answer": "No se encontraron autos."}

    # Concatenamos los textos
    autos_list = "\n".join([r.page_content for r in results])

    # Generamos un resumen usando el LLM a través del qa_chain
    answer_text = qa_chain.run(f"Resume brevemente estos autos:\n{autos_list}")

    logger.info(answer_text)
    return {"answer": answer_text}
