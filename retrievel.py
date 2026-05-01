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

    context = "\n".join([
        match.get("metadata", {}).get("text", "")
        for match in matches
        if match.get("metadata")
    ])

    return context.strip()