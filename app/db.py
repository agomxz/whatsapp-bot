from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import CHROMA_DIR, CHROMA_DB

embeddings = OpenAIEmbeddings()

vectorstore = Chroma(
    collection_name=CHROMA_DB,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

retriever_vehicle = vectorstore.as_retriever()
