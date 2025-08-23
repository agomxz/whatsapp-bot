from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import CHROMA_DIR, CHROMA_DB

# Embeddings
embeddings = OpenAIEmbeddings()

# Base de datos vectorial Chroma
vectorstore = Chroma(
    collection_name=CHROMA_DB,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR
)
