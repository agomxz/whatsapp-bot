import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import OPENAI_API_KEY, CHROMA_DIR, CHROMA_DB
from app.config import logger


def load_data():
    try:
        logger.info("Loading database for vehicles ...")

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
            persist_directory=CHROMA_DIR,
        )

        vectorstore.add_texts(documents)
        vectorstore.persist()

        logger.info("✅ Vehicle database ok")

    except Exception as e:
        logger.error("Unexpected error: %s", e)
        logger.error("Error creating vehicle database")
