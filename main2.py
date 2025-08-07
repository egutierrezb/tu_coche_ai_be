from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
from serpapi import GoogleSearch
import requests
from PIL import Image
from io import BytesIO
import os

# Load SerpAPI key from env or just paste it here
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "e4a8c680a059180f4ef1ffaf3e0d40afc1d8f4676f7b7849846109b3af9969bc")  # Replace with your key if needed

model = OllamaLLM(model="llama3.2")

template = """
You are an expert in answering questions about car reviews.

Here are some relevant reviews: {reviews}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Prompt to extract only the best-ranked car
best_car_prompt = ChatPromptTemplate.from_template("""
Extract only the name of the car with the best ranking from the following text.

Text: {result}

Respond with only the name, no explanation.
""")
best_car_chain = best_car_prompt | model

def fetch_image_link(query):
    print(f"Searching image for: {query}")
    params = {
        "q": query,
        "tbm": "isch",  # Image search
        "api_key": SERPAPI_API_KEY,
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        images = results.get("images_results", [])
        if images:
            return images[0]["original"]  # Get full image URL
    except Exception as e:
        print(f"Error during image search: {e}")
    return None

def display_image_from_url(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.show()
        print(f"Image URL: {image_url}")
    except Exception as e:
        print(f"Error fetching image: {e}")

while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    if question.lower() == "q":
        break

    print("\nProcessing...\n")
    reviews = retriever.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print("LLM Answer:\n", result)

    # Extract best-ranked car
    best_car = best_car_chain.invoke({"result": result}).strip()
    print(f"\nBest-ranked car: {best_car}")

    # Search for image using SerpAPI
    image_url = fetch_image_link(f"{best_car} car")
    if image_url:
        display_image_from_url(image_url)
    else:
        print("No image found.")