from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import logger
from app.config import KAVAK_WEBSITE, OPENAI_API_KEY, CHROMA_DIR, CHROMA_DB_BLOG
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma



def load_web_page():
    try:
        logger.info('Loading web page ...')
        loader = WebBaseLoader(KAVAK_WEBSITE)
        web_docs = loader.load()

        # 🔹 Dividir el texto en chunks pequeños (reduce tokens por request)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=5000,   
            chunk_overlap=50
        )
        
        split_docs = text_splitter.split_documents(web_docs)

        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        
        vectorstore_blog = Chroma(
                collection_name=CHROMA_DB_BLOG,
                embedding_function=embeddings,
                persist_directory=CHROMA_DIR
        )
        
        vectorstore_blog.add_documents(split_docs)
        vectorstore_blog.persist()

        logger.info("✅ Blog database ok")

    except:
        logger.error("Error creating blog database")
