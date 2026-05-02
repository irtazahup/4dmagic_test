from pinecone import Pinecone
from config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.INDEX_NAME)

def retrieve_context(vector, top_k=3):
    
    results = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True
    )

    matches = results.get("matches", [])

    structured_chunks = []

    for m in matches:
        meta = m.get("metadata", {})

        structured_chunks.append({
            "score": m.get("score"),
            "document": meta.get("source", "unknown"),
            "text": meta.get("text", ""),
            "page": meta.get("page", None)
        })

    return structured_chunks