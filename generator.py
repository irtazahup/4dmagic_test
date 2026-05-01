from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(question: str, context: str):

    system_prompt = (
    "You are a helpful AI assistant. Answer the user's question using ONLY the provided context.\n"
    
    "Instructions:\n"
    "- If the answer is clearly found in the context, respond accurately.\n"
    "- If the answer is partially found, respond with what is available.\n"
    "- If the answer is NOT in the context, say: 'I don't know based on the provided document.'\n"
    "- Do NOT make up information.\n"
    "- Keep the answer clear and concise.\n"
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