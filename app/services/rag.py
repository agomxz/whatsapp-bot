from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from app.db import vectorstore
from app.config import logger
import os


# LLM de OpenAI
llm = OpenAI(
            model_name="gpt-4o-mini", 
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Chain de RAG
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

def insert_document(text: str):
    """Inserta texto en la base vectorial"""
    vectorstore.add_texts([text])
    vectorstore.persist()
    return {"message": "Documento insertado", "text": text}

def ask_question(query: str):
    """Consulta RAG"""
    try:
        logger.info(f"Asking: {query}")
        return {"query": query, "answer": qa_chain.run(query)}
    except:
        logger.error(f"Error asking: {query}")
        return {}
    
def ask_simil(query: str):
    logger.info('Ask simil def')
    
    results = vectorstore.similarity_search(query, k=1)
    answer = {}
    
    logger.info(type(results))
    logger.info(results)
    
    for r in results:
        logger.info(r.page_content)
        answer['answer'] = r.page_content
        
    return answer
