from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def split_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_embeddings(chunks):
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings


def search_chunks(chunks, embeddings, question, top_k=3):
    question_embedding = model.encode(
        [question],
        convert_to_numpy=True
    )

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings.astype("float32"))

    distances, indices = index.search(
        question_embedding.astype("float32"),
        min(top_k, len(chunks))
    )

    results = []

    for i in indices[0]:
        if i != -1:
            results.append(chunks[i])

    return results