import os
import logging
from flask import Flask, request
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
from serpapi import GoogleSearch

# ---------------- Logger Setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("CarReviewApp")
# ------------------------------------------------

app2 = Flask(__name__)

# Create prompts once (they don't call Ollama immediately)
template = """
You are an expert in answering questions about car reviews. 
Here are some relevant reviews: {reviews}
Here is the question to answer: {question}
Respond with only five sentences as maximum. Include for each
sentence its belonging id (do not include parentheses, just the id) that supports its corresponding review
"""
prompt = ChatPromptTemplate.from_template(template)

best_car_prompt = ChatPromptTemplate.from_template("""
Extract only the name of the car with the best match from the following text.
Text: {result}
Respond with only the name, no explanation.
""")

class QuestionInput(BaseModel):
    question: str

@app2.route("/ask", methods=["POST"])
def ask_question():
    try:
        logger.info("Received request at /ask")

        # Initialize Ollama and chains lazily
        model = OllamaLLM(
            model="llama3.2",
            #This url was set via ngrok, which served as an api-gateway where it mounted the 
            #ollama server
            #base_url="https://tight-ladybird-neatly.ngrok-free.app"
            #Instead of that, we are going to install and serve ollama in 38.29.145.77 which
            #was deployed via TensorDock
            #base_url="http://91.108.80.251:47924"
            base_url="http://91.108.80.251:47924"
        )
        chain = prompt | model
        best_car_chain = best_car_prompt | model

        # Get JSON body
        body = request.get_json(force=True)
        data = QuestionInput(**body)
        logger.info(f"User question: {data.question}")

        # Retrieve relevant reviews
        reviews = retriever.invoke(data.question)
        logger.debug(f"Retrieved reviews: {reviews}")

        # Generate response from model
        result = chain.invoke({"reviews": reviews, "question": data.question})
        logger.info(f"Generated answer: {result}")

        # Extract best car
        best_car = best_car_chain.invoke({"result": result}).strip()
        logger.info(f"Identified best car: {best_car}")

        # Fetch image with SerpAPI
        search = GoogleSearch({
            "q": f"{best_car}",
            "tbm": "isch",
            "api_key": os.getenv(
                "SERPAPI_API_KEY",
                "e4a8c680a059180f4ef1ffaf3e0d40afc1d8f4676f7b7849846109b3af9969bc"
            )
        })
        images = search.get_dict().get("images_results", [])
        image_url = images[0]["original"] if images else None
        logger.info(f"Image URL found: {image_url}")

        return {
            "answer": result,
            "best_car": best_car,
            "image_url": image_url
        }

    except Exception as e:
        logger.exception("Error while processing /ask request")
        return {"error": str(e)}, 500


# For flask we only need to "run" as is the python file
if __name__ == "__main__":
    #5000 is for version deployed in TensorDock GPU VM or 5002 is port for running this from localhost
    logger.info("Starting Flask app on 0.0.0.0:5002")
    app2.run(host="0.0.0.0", port=5002, debug=True)

    # After installing ngrok locally we should do the following
    # ngrok config add-authtoken 31NQfDzC1yD9CSHmKH4kR6FwiYK_7shvcxDqLUNdV5NUkkZ4D
    # Authtoken saved to configuration file: /Users/alejandro/Library/Application Support/ngrok/ngrok.yml

    # This commands should be run in Google Colab (no luck with the GPUs preinstalled there)
    # or this should be run locally

    # Start Ollama in background
    #ollama serve &

    # Give it a moment to start
    #sleep 2

    # Start ngrok tunnel (custom domain)
    #ngrok http 11434 --host-header="localhost:11434" --domain="tight-ladybird-neatly.ngrok-free.app" &

    # Wait a bit for tunnel
    #sleep 5

    # Run the model once (optional)
    #ollama run llama3.2

    #ollama serve & sleep 2 & ngrok http --domain=tight-ladybird-neatly.ngrok-free.app 11434 & sleep 5 && ollama run llama3.2

    #For checking that our ollama is running
    #curl http://localhost:11434/v1/models

    #To allow external connections for the host on which we have ollama
    #export OLLAMA_HOST="0.0.0.0:11434"
    #ollama serve
    #or we can do a list to see which models are installed on that server
    #ollama list

    # On your TensorDock VM
    # ngrok http 11434 -> this gives you an url an endpoint which can be seen/consulted in the Endpoints section

    # ollama is running in TensorDock VM at 0.0.0.0 in IP 91.108.80.251
    # when running under a browser: http://91.108.80.251:47921/ .. indicates that it is running our Ollama