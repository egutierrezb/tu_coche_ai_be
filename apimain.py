import os

from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
from serpapi import GoogleSearch
import requests


#For running the application using FastAPI use the following:
#uvicorn apimain:app --reload --host 0.0.0.0 --port 8000
#For installing a specific package within a virtual environment:
#python -m pip install <library>


app = FastAPI()
model = OllamaLLM(model="llama3.2")

template = """
You are an expert in answering questions about car reviews. 
Here are some relevant reviews: {reviews}
Here is the question to answer: {question}
Respond with only five sentences as maximum. Include for each
sentence its belonging id (do not include parentheses, just the id) that supports its corresponding review
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

best_car_prompt = ChatPromptTemplate.from_template("""
Extract only the name of the car with the best match from the following text.
Text: {result}
Respond with only the name, no explanation.
""")
best_car_chain = best_car_prompt | model

class QuestionInput(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(data: QuestionInput):
    reviews = retriever.invoke(data.question)
    result = chain.invoke({"reviews": reviews, "question": data.question})
    best_car = best_car_chain.invoke({"result": result}).strip()

    # Search image
    search = GoogleSearch({
        "q": f"{best_car}",
        "tbm": "isch",
        "api_key": os.getenv("SERPAPI_API_KEY","e4a8c680a059180f4ef1ffaf3e0d40afc1d8f4676f7b7849846109b3af9969bc"),
    })
    images = search.get_dict().get("images_results", [])
    image_url = images[0]["original"] if images else None

    return {
        "answer": result,
        "best_car": best_car,
        "image_url": image_url
    }