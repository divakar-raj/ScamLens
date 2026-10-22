"""api.py - FastAPI wrapper so the mobile app can call our detection engine.

Run:  uvicorn api:app --host 0.0.0.0 --port 8000 --reload
Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from detector import analyze
from explainer import explain
from i18n import NEXT_STEPS, text_lang

app = FastAPI(title="ScamLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str
    language: str = "Auto"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_message(req: AnalyzeRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is empty")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text is too long (max 5000 characters)")

    result = analyze(text)
    detected = result["language"]
    chosen = detected if req.language == "Auto" else req.language
    explanation, source = explain(text, result, chosen)
    steps = [s.replace("**", "") for s in NEXT_STEPS[text_lang(chosen)]]

    return {
        "score": result["score"],
        "level": result["level"],
        "language": chosen,
        "detected_language": detected,
        "explanation": explanation,
        "explanation_source": source,
        "findings": result["findings"],
        "next_steps": steps,
    }
