import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import OPENAI_API_KEY, CHROMA_DIR, CHROMA_DB
from app.config import logger


def load_data():
    try:
        logger.info('Loading database for vehicles ...')

        df = pd.read_csv("app/utils/sample.csv")

        def row_to_text(row):
            return (
                f"stock_id: {row['stock_id']}"
                f"{row['make']} {row['model']} {row['year']} {row['version']} "
                f"km: {row['km']}, precio: {row['price']}, "
                f"dimensiones: {row['largo']}x{row['ancho']}x{row['altura']}, "
                f"bluetooth: {row['bluetooth']}, carplay: {row['car_play']}"
            )

        documents = [row_to_text(r) for _, r in df.iterrows()]

        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        vectorstore = Chroma(
            collection_name=CHROMA_DB,
            embedding_function=embeddings,
            persist_directory=CHROMA_DIR
        )

        vectorstore.add_texts(documents)
        vectorstore.persist()

        logger.info("✅ Vehicle database ok")
        
    except:
        logger.error("Error creating vehicle database")
        


    # logger.info('Testing database ...')

    # results = vectorstore.similarity_search("SUV automática con menos de 100,000 km", k=1)
    # for r in results:
    #     logger.info(r.page_content)
