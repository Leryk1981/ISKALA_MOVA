from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="ISKALA Translation Service", version="1.0.0")

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
    return {"message": "ISKALA Translation Service is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "translation"}

@app.post("/translate")
async def translate(text: str, target_language: str):
    # Placeholder for translation logic
    return {
        "original": text,
        "translated": f"[Translated to {target_language}]: {text}",
        "language": target_language
    }

if __name__ == "__main__":
    port = int(os.getenv("TRANSLATION_PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
