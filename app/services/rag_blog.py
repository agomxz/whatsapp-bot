from langchain.chains import ConversationalRetrievalChain
from app.services.llm_service import LLMService
from app.db import retriever_blog
from app.config import logger

llm_obj =LLMService()
llm = llm_obj.get_llm()

ask_to_blog = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever_blog,
)

def ask_to_blog(query: str):
    docs = retriever_blog.get_relevant_documents(query)    
    logger.info('\n\n')
    logger.info(docs)
    logger.info('\n\n')
    
    return True


def ask_company_info(vectorstore, query: str):

    results = vectorstore.similarity_search(query, k=4)
    
    if not results:
        return {"answer": "No se encontraron resultados."}
    
    answer_texts = [r.page_content for r in results]
    logger.info("Resultados encontrados: %d", len(answer_texts))
    
    return {"answer": "\n".join(answer_texts)}