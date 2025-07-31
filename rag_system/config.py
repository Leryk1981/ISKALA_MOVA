import os

# RAG Configuration
RAG_CONFIG = {
    "vector_db_path": "/app/vector_store",
    "chat_uploads_path": "/app/uploads",
    "capsules_path": "/app/capsules",
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "max_context_length": 2048
}

# Ensure directories exist
for path in [RAG_CONFIG["vector_db_path"], RAG_CONFIG["chat_uploads_path"], RAG_CONFIG["capsules_path"]]:
    os.makedirs(path, exist_ok=True)
