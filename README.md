# Document Ingestion and Chat API

A FastAPI-based project for PDF ingestion, chunk embedding, and question-answering over uploaded documents.

## What this app does

- Accepts PDF uploads via `POST /upload-pdf/`
- Splits PDF content into overlapping text chunks (~500 tokens)
- Embeds chunks using Hugging Face embeddings
- Stores vectors in Pinecone with metadata including source filename, chunk index, page number, and document ID
- Supports retrieval and chat-style question answering via `POST /chat`
- Lists stored documents with `GET /documents`
- Deletes documents via `DELETE /documents/{doc_id}`

## Setup

1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   ```
2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copy the example environment file:
   ```powershell
   copy .env.example .env
   ```
5. Run the app:
   ```powershell
   uvicorn main:app --reload
   ```

## Environment variables

Create `.env` from `.env.example` and set these values:

- `PINECONE_API_KEY` - Pinecone API key
- `INDEX_NAME` - Pinecone index name
- `HUGGINGFACE_API_KEY` - Hugging Face API token
- `GROQ_API_KEY` - Groq API key (optional depending on future usage)

## API Endpoints

### Upload PDF

- `POST /upload-pdf/`
- Form field: `file` as PDF upload

Response:
```json
{
  "document_id": "<uuid>",
  "chunks_stored": 123
}
```

### Chat

- `POST /chat`
- JSON body:
```json
{
  "question": "What does the document say about X?"
}
```

Response:
```json
{
  "answer": "...",
  "sources": [...],
  "confidence": 0.82
}
```

### List uploaded documents

- `GET /documents`

Response:
```json
[
  {
    "document_id": "...",
    "filename": "...",
    "chunk_count": 20,
    "timestamp": "2026-05-01T..."
  }
]
```

### Delete a document

- `DELETE /documents/{doc_id}`

Response:
```json
{
  "message": "Document deleted successfully",
  "document_id": "..."
}
```

## Notes

- The app stores uploaded PDF files in the `uploads/` folder.
- The `ingestion.py` logic uses Pinecone and Hugging Face embeddings to vectorize chunks.
- Make sure the Pinecone index exists before uploading documents.

## Sample queries

Use the `/chat` endpoint after uploading at least one PDF document. Example queries:

- "What does the document say about eligibility?"
- "Summarize the key points from the first chapter."
- "Which page discusses the project timeline?"
- "What are the main risks listed in the document?"
- "How does the document define the success criteria?"
