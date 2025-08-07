from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("cars_reviews.csv", dtype={"id": str})
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chrome_langchain_db6"
add_documents = not os.path.exists(db_location)

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
        print(f"{id}")
        #ids.append(str(i))
        ids.append(str(row["id"]))
        #print(f"ids: {ids}")
        documents.append(document)
        
vector_store = Chroma(
    collection_name="cars_reviews",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)
    
retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)