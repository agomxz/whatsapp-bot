from fastapi import APIRouter, status
from app.utils.twilio import send_message
from app.redis_memory import load_memory, save_memory, get_chat_memory, get_last_car, save_chat_memory, save_last_car, deserialize_messages, serialize_messages
from app.services.llm_service import LLMService
from langchain.prompts import ChatPromptTemplate
from app.config import logger
from app.constants.propmts import WELCOME_PROMPT, RECOMMENDATION_PROMPT
from app.services.rag import show_car_by_question, show_random_vehicle
from app.services.rag_blog import ask_to_blog, ask_company_info
from app.db import retriever_vehicle, vectorstore,vectorstore_blog
from langchain.chains import RetrievalQA
from langchain.schema import AIMessage, HumanMessage



router = APIRouter()

@router.get(
    "/",
    summary="Healthcheck",
    status_code=status.HTTP_200_OK
)
def home() -> None:
    return {"status": "WhatsApp Bot Running 🚀"}

    
@router.post("/message", status_code=status.HTTP_200_OK)
def message() -> None:    
    send_message('Hello from backend')    



new_llm = LLMService()
llm = new_llm.get_llm()

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever_vehicle)

@router.post(
    "/chat",
    summary="Chat history",
    status_code=status.HTTP_200_OK,
)
def chat(
    user_id: str, 
    user_input: str
):
    logger.info('Buscando historial de usuario')
        
    chat_history = get_chat_memory(user_id)
    last_car = get_last_car(user_id)
        
    if not chat_history:
        logger.info('Este usuario es nuevo')
        initial_promt = ChatPromptTemplate.from_messages([("system", WELCOME_PROMPT)])
        welcome_chain = initial_promt | llm
        response = welcome_chain.invoke({})

    else:    
        logger.info('Este usuario ya tiene un historial')
        if user_input == "1":
            response = "Aquí tienes algunas opciones de autos. ¿Quieres conocer el financiamiento?\n"
            result = show_random_vehicle(vectorstore=vectorstore, query='Muestra 1 auto al azar')                
            response = response + result['answer']
            save_last_car(user_id, result)

        elif user_input == "2":
            response = "Dime alguna característica que buscas en un auto (ejemplo: año, precio, bluetooth)."

        else:
            if "financiamiento" in user_input.lower() and last_car:    
                logger.info('Financiamiento??????******\n\n')            
                precio = last_car.get("answer", "200000")
                financing_prompt = f"Genera un plan de financiamiento resumido en 4 o 5 oraciones para un auto que cuesta ${precio}. tomando como base el precio del auto, una tasa de interés del 10% y plazos de financiamiento de entre 3 y 6 años."
                chain = ChatPromptTemplate.from_template(financing_prompt) | llm
                response = chain.invoke({})

            else:
                query = user_input.lower()
                if any(word in query for word in ["sede", "oficina", "propuesta", "valor", "ubicación", "blog"]):
                    result = ask_company_info(vectorstore_blog, user_input)
                    response = result['answer']
                
                elif any(word in query for word in ["auto", "coche", "carro", "vehículo", "modelo", "precio", "km", "marca"]):
                    # Usamos qa_chain para responder sobre autos
                    result = show_car_by_question(vectorstore=vectorstore, query=user_input)
                    logger.info(result)
                    response = result['answer']
                    save_last_car(user_id, {'answer':response})
                    response = response + '\n¿Quieres saber el financiamiento, escribe financiar'
                    
                else:
                    # 6️⃣ Pregunta libre general
                    #TODO CHECKTHIS CASE
                    prompt = ChatPromptTemplate.from_messages([("system", RECOMMENDATION_PROMPT)])
                    chain = prompt | llm
                    response = chain.invoke({"chat_history": chat_history[-3:], "input": user_input})

            
    
    
    logger.info('Guardando en memoria el contexto de la conversacion')
        
        
    
   # Convertir a string
    user_msg = HumanMessage(content=str(user_input))

    if isinstance(response, dict):
        # Si response viene como {"answer": "..."}
        ai_msg = AIMessage(content=str(response.get("answer", "")))
    else:
        ai_msg = AIMessage(content=str(response))

    # Agregar al historial
    chat_history.append(user_msg)
    chat_history.append(ai_msg)
    
    
    logger.info('history')
    logger.info(chat_history)
    
    chat_history = chat_history[-6:]
    save_chat_memory(user_id, chat_history)
    
    
    return {"response": response}