import os
from dotenv import load_dotenv
from google import genai

from ingestion import run_ingestion
from retrieval import retrieve

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# -------- GENERATE ANSWER --------
def generate_answer(query, retrieved_chunks):

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
    Answer the question using ONLY the context below.

    Context:
    {context}

    Question:
    {query}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# -------- MAIN --------
if __name__ == "__main__":

    print("🔄 Ingesting documents...")
    all_chunks, index = run_ingestion("data", client)
    print("✅ Ready. Ask your question.")

    while True:
        query = input("\nAsk (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        retrieved = retrieve(query, index, all_chunks, client)
        answer = generate_answer(query, retrieved)

        print("\nAnswer:\n")
        print(answer)
