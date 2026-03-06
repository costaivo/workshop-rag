import os
from dotenv import load_dotenv
from google import genai

from generation import generate_answer
from ingestion import run_ingestion
from retrieval import retrieve

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# -------- MAIN --------
if __name__ == "__main__":

    print("🔄 Ingesting documents...")
    all_chunks, index = run_ingestion("data", client)
    print("✅ Ingestion complete.")
    print("--------------------------------")
    print("✅ Ready. Ask your question.")

    while True:
        query = input("\nAsk (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        retrieved = retrieve(query, index, all_chunks, client)
        answer = generate_answer(query, retrieved, client)

        print("\nAnswer:\n")
        print(answer)
