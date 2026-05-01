from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    
    # ✅ Check file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # ✅ Read file (optional: save or process later)
        content = await file.read()

        return {
            "filename": file.filename,
            "message": "PDF uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))