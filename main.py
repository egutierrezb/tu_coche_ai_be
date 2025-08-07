from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
from googlesearch import search
from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO

model = OllamaLLM(model="llama3.2")

# Original answer generation prompt
template = """
You are an expert in answering questions about car reviews.

Here are some relevant reviews: {reviews}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Extract only the best-ranked car
best_car_prompt = ChatPromptTemplate.from_template("""
Extract only the name of the car with the best ranking from the following text.
Text: {result}

Respond with only the name, no explanation.
""")
best_car_chain = best_car_prompt | model


# 🧠 Function to find the first result containing an image
def find_first_link_with_image(query, max_results=5):
    for url in search(query, num_results=max_results):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = soup.find('img')

            if img_tag and 'src' in img_tag.attrs:
                img_url = img_tag['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = url + img_url
                elif not img_url.startswith('http'):
                    continue  # skip invalid links
                if ".svg" in img_url:
                    continue # skip img_urls that contain svg
                print(f"Found image on: {url}")
                return url, img_url

        except Exception as e:
            print(f"Skipped {url} due to error: {e}")
    return None, None


# 🖼️ Function to show image
def show_image_from_url(img_url):
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.show()
    except Exception as e:
        print(f"Error showing image: {e}")


# 🔁 Main loop
while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    if question.lower() == "q":
        break

    print("\nProcessing...\n")
    reviews = retriever.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print("LLM Answer:\n", result)

    # Extract best car name
    best_car = best_car_chain.invoke({"result": result}).strip()
    print(f"\nBest-ranked car: {best_car}")

    # Search Google and find a link with an image
    search_query = f"{best_car} car"
    page_url, img_url = find_first_link_with_image(search_query)

    if page_url and img_url:
        print(f"Page URL: {page_url}")
        print(f"Image URL: {img_url}")
        show_image_from_url(img_url)
    else:
        print("No valid image found.")