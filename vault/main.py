from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="ISKALA Vault Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ISKALA Vault Service is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "vault"}

@app.get("/status")
async def status():
    return {
        "service": "vault",
        "version": "1.0.0",
        "encryption": "ChaCha20-Poly1305",
        "status": "operational"
    }

if __name__ == "__main__":
    port = int(os.getenv("VAULT_PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
