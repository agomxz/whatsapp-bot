import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
from app.config import OPENAI_API_KEY, CHROMA_DIR, CHROMA_DB


def load_data():
    
    df = pd.read_csv("app/utils/sample.csv")

    #Convertir cada fila a un string descriptivo
    def row_to_text(row):
        return (
            f"{row['make']} {row['model']} {row['year']} {row['version']} "
            f"km: {row['km']}, precio: {row['price']}, "
            f"dimensiones: {row['largo']}x{row['ancho']}x{row['altura']}, "
            f"bluetooth: {row['bluetooth']}, carplay: {row['car_play']}"
        )

    documents = [row_to_text(r) for _, r in df.iterrows()]

    #Crear embeddings y base Chroma persistente
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectorstore = Chroma(
        collection_name=CHROMA_DB,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    # 4. Insertar los documentos en la base
    vectorstore.add_texts(documents)
    vectorstore.persist()

    print("✅ Base de datos vectorial creada con autos")


# results = vectorstore.similarity_search("SUV automática con menos de 100,000 km", k=3)
# for r in results:
#     print(r.page_content)
