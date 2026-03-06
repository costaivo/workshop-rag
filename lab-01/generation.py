"""Generation: build a prompt from retrieved chunks and get an answer from the LLM."""


def generate_answer(query, retrieved_chunks, client):
    """
    Answer the question using only the retrieved chunks as context.
    """
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
