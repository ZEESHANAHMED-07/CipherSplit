from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import encrypt, reconstruct

app = FastAPI(title="CipherSplit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(encrypt.router)
app.include_router(reconstruct.router)

STORAGE_DIRS = ["uploads", "encrypted", "shares", "recovered"]

@app.on_event("startup")
def ensure_storage_dirs():
    base = os.path.join(os.path.dirname(__file__), "..", "storage")
    for d in STORAGE_DIRS:
        os.makedirs(os.path.join(base, d), exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "CipherSplit backend is running"}
