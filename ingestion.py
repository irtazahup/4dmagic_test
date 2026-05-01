import uuid
import time
from typing import List
import time
from pinecone import Pinecone
from huggingface_hub import InferenceClient
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from local_db import add_document

import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 ENV
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")

# 🔌 Clients
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

hf_client = InferenceClient(api_key=HF_TOKEN)

BATCH_SIZE = 50


def ingest_pdf(file_path: str):

    document_id = str(uuid.uuid4())
    timestamp = time.time()

    # ✅ Load PDF
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    # ✅ Chunking (≈500 tokens)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,      # ~500 tokens
        chunk_overlap=200
    )

    docs = splitter.split_documents(pages)

    total_chunks = len(docs)

    # ✅ Prepare texts + metadata
    texts = []
    metadatas = []

    for i, doc in enumerate(docs):
        texts.append(doc.page_content)

        metadatas.append({
    "text": doc.page_content,
    "source": os.path.basename(file_path),
    "chunk_index": i,
    "page": doc.metadata.get("page", None),
    "document_id": document_id,
    "timestamp": timestamp   # 🔥 ADD THIS
})

    # ✅ Batch Embedding + Upsert
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_meta = metadatas[i:i+BATCH_SIZE]

        try:
            embeddings = hf_client.feature_extraction(
                batch_texts,
                model="sentence-transformers/all-MiniLM-L6-v2"
            )

            vectors = []
            for j, (vec, meta) in enumerate(zip(embeddings, batch_meta)):
                vectors.append({
                    "id": f"{document_id}_{i+j}",
                    "values": vec,
                    "metadata": meta
                })

            index.upsert(vectors=vectors)

            print(f"Uploaded batch {i//BATCH_SIZE + 1}")

            time.sleep(1)  # rate limit safe

        except Exception as e:
            print(f"Error in batch {i}: {e}")
            continue
        add_document(
    document_id,
    os.path.basename(file_path),
    total_chunks
    )

    return document_id, total_chunks