from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(question: str, chunks: list):

    context_text = "\n\n".join(
        [c["text"] for c in chunks]
    )

    system_prompt = (
        "You are a strict RAG assistant.\n"
        "Answer ONLY using provided context.\n"
        "If answer is not present, respond: NOT_FOUND\n"
        "Do not use outside knowledge."
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content