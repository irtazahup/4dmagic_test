from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(question: str, context: str):

    system_prompt = (
        "You are a professional medical assistant. Use the context. "
        "If not found, say you don't know. Always suggest consulting a doctor."
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ],
        max_tokens=400,
        temperature=0.5
    )

    return response.choices[0].message.content