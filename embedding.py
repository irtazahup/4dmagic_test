from huggingface_hub import InferenceClient
from config import settings

client_HF = InferenceClient(api_key=settings.HUGGINGFACE_API_KEY)

def get_embedding(text: str):
    vector = client_HF.feature_extraction(
        text,
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    return vector.tolist()