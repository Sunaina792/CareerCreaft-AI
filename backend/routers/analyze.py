"""
CareerCraft AI — /api/analyze
Accepts a resume file, extracts text, runs Groq analysis.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from core.parser import extract_text
from core.groq_client import ask_groq
from core.prompts import ANALYZE_SYSTEM, ANALYZE_USER

router = APIRouter()


@router.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Upload a resume (PDF/DOCX) → get AI analysis with score, sections,
    skills, improvement tips, and overall feedback.
    """
    # 1. Extract text
    resume_text = await extract_text(file)

    if len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Resume text is too short to analyze. Please upload a complete resume.",
        )

    # 2. Send to Groq
    try:
        result = ask_groq(
            system_prompt=ANALYZE_SYSTEM,
            user_prompt=ANALYZE_USER.format(resume_text=resume_text),
            json_mode=True,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # 3. Attach raw text for use in subsequent calls (stored client-side)
    result["resume_text"] = resume_text
    return result
