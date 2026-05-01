from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil

from ingestion import ingest_pdf

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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