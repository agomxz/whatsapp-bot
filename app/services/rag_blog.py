from langchain.chains import ConversationalRetrievalChain
from app.services.llm_service import LLMService
from app.db import retriever_blog

llm_obj = LLMService()
llm = llm_obj.get_llm()

ask_to_blog = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever_blog,
)


def ask_company_info(vectorstore, query: str):

    results = vectorstore.similarity_search(query, k=4)

    if not results:
        return {"answer": "No se encontraron resultados."}

    answer_texts = [r.page_content for r in results]

    return {"answer": "\n".join(answer_texts)}
