from langchain.chains import RetrievalQA
from app.db import retriever_vehicle
from app.services.llm_service import LLMService
from app.constants.propmts import SUMMARY_SHOW_VEHICLE
import random
from langchain.prompts import ChatPromptTemplate


llm_obj = LLMService()
llm = llm_obj.get_llm()

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever_vehicle)


def show_random_vehicle(vectorstore, query: str, k: int = 20):
    # Use a larger k value and vary the query to get more diverse results
    random_queries = [
        "vehículo automóvil carro",
        "auto sedan SUV pickup",
        "coche vehículo transporte",
        "automóvil carro auto",
        "vehículo motor ruedas",
        "transporte automóvil sedan",
        "carro SUV pickup camioneta"
    ]
    
    # Randomly select a query to get different similarity results each time
    selected_query = random.choice(random_queries)
    results = vectorstore.similarity_search(selected_query, k=k)

    if not results:
        # Fallback to original query if no results
        results = vectorstore.similarity_search(query, k=k)
        
    if not results:
        return {"answer": "No se encontraron vehículos."}

    # Randomly select from the larger pool of results
    selected_vehicle = random.choice(results)
    vehicle = f"ID: {selected_vehicle.metadata.get('id', 'N/A')}\n{selected_vehicle.page_content}"

    prompt = ChatPromptTemplate.from_messages(
        [("system", SUMMARY_SHOW_VEHICLE + vehicle)]
    )
    chain = prompt | llm

    response = chain.invoke({})

    return response


def show_car_by_question(vectorstore, query: str, k: int = 1):
    result = vectorstore.similarity_search(query, k=k)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SUMMARY_SHOW_VEHICLE + result[0].page_content)]
    )
    chain = prompt | llm

    response = chain.invoke({})

    return response
