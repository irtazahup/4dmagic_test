from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil

from pinecone import Pinecone
from pydantic import BaseModel

from ingestion import ingest_pdf
from embedding import get_embedding
from retrievel import retrieve_context
from generator import generate_answer
from helper import compute_confidence
from collections import defaultdict
from datetime import datetime
from config import settings
from local_db import load_db,delete_document

app = FastAPI()
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.INDEX_NAME)
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


@app.get("/documents")
def get_documents():

    db = load_db()

    response = []

    for doc_id, data in db.items():
        response.append({
            "document_id": doc_id,
            "filename": data["filename"],
            "chunk_count": data["chunk_count"],
            "timestamp": datetime.fromtimestamp(
                data["timestamp"]
            ).isoformat()
        })

    return response




@app.delete("/documents/{doc_id}")
def delete_document_api(doc_id: str):

    # 1️⃣ Delete from Pinecone
    try:
        index.delete(
            filter={"document_id": doc_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pinecone delete failed: {str(e)}"
        )

    # 2️⃣ Delete from local DB
    removed = delete_document(doc_id)

    if not removed:
        raise HTTPException(
            status_code=404,
            detail="Document not found in local DB"
        )

    return {
        "message": "Document deleted successfully",
        "document_id": doc_id
    }