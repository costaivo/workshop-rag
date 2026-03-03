"""Retrieval: embed the query, search the index, return the top-K chunks."""

import numpy as np


def retrieve(query, index, chunks, client, top_k=3):
    """
    Find the chunks most similar to the query.
    Returns a list of chunk strings (length top_k).
    """
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[{"text": query}],
    )
    query_embedding = response.embeddings[0].values
    query_vector = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_vector, top_k)
    return [chunks[i] for i in indices[0]]
