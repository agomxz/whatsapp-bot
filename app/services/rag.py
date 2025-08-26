from langchain.chains import RetrievalQA
from app.db import retriever_vehicle, vectorstore
from app.config import logger
from app.services.llm_service import LLMService
import random

# Inicializar LLM
llm_obj = LLMService()
llm = llm_obj.get_llm()

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever_vehicle)


def show_random_vehicle(vectorstore, query: str, k: int = 1):
    """
    Devuelve un vehículo al azar entre los k más relevantes
    """
    results = vectorstore.similarity_search(query, k=k)
    
    if not results:
        return {"answer": "No se encontraron vehículos."}

    selected_vehicle = random.choice(results)
    autos_list = selected_vehicle.page_content

    prompt = f"Resume brevemente este vehículo:\n{autos_list}"
    answer_text = qa_chain.run(prompt)

    logger.info("Resumen generado por RAG:\n%s", answer_text)

    return {"answer": answer_text, "vehicle": autos_list}



def show_car_by_question(vectorstore, query: str, k: int = 1):
    """
    Busca el documento más relevante y devuelve su contenido
    """
    results = vectorstore.similarity_search(query, k=k)
    
    if not results:
        return {"answer": "No se encontraron resultados."}
    
    answer_texts = [r.page_content for r in results]
    logger.info("Resultados encontrados: %d", len(answer_texts))
    
    return {"answer": "\n".join(answer_texts)}


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

