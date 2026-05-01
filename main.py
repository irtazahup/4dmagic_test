from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil

from pydantic import BaseModel

from ingestion import ingest_pdf
from embedding import get_embedding
from retrievel import retrieve_context
from generator import generate_answer
from helper import compute_confidence

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    question: str
    
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document_id, chunk_count = ingest_pdf(file_path)

        return {
            "document_id": document_id,
            "chunks_stored": chunk_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/chat")
async def chat(request: ChatRequest):

    # 1. Embed question
    vector = get_embedding(request.question)

    # 2. Retrieve structured chunks
    chunks = retrieve_context(vector)

    # 3. NOT FOUND HANDLING (VERY IMPORTANT)
    if not chunks:
        return {
            "answer": "I don't know based on the provided documents.",
            "sources": [],
            "confidence": 0.0
        }

    # 4. Generate answer
    answer = generate_answer(request.question, chunks)

    # 5. Detect hallucination guard
    if "NOT_FOUND" in answer:
        return {
            "answer": "I don't know based on the provided documents.",
            "sources": chunks,
            "confidence": compute_confidence(chunks)
        }

    # 6. Final response
    return {
        "answer": answer,
        "sources": chunks,
        "confidence": compute_confidence(chunks)
    }
