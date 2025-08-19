from langchain.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd
import logging

# ---------------- Logger Setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("VectorDB")
# ------------------------------------------------

df = pd.read_csv("cars_reviews.csv", dtype={"id": str})
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db_location = "./chrome_langchain_db6"
add_documents = not os.path.exists(db_location)
logger.info(f"Add documents: {add_documents}")

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():
        document = Document(
            page_content=row["Title"] + " " + row["Review"],
            #page_content=row["Title"],
            metadata={"rating": row["Rating"], "review": row["Review"]},
            #id=str(i)
            id=str(row["id"])
        )
        logger.info(f'Iterating on rows: {str(row["id"])}')
        #ids.append(str(i))
        ids.append(str(row["id"]))
        #print(f"ids: {ids}")
        documents.append(document)

logger.info(f"Initialization on chroma")
vector_store = Chroma(
    collection_name="cars_reviews",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    logger.info(f"Add documents on vector_store")
    vector_store.add_documents(documents=documents, ids=ids)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)
logger.info(f"Retriever ready ... ")