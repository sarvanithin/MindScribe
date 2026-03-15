from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config import DEMO_MODE

app = FastAPI(
    title="MindScribe API",
    description="Conversational mental health screening + clinical note generation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "MindScribe API",
        "version": "0.1.0",
        "demo_mode": DEMO_MODE,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "demo_mode": DEMO_MODE}
