"""
CareerCraft AI — /api/match
Compares resume text vs job description using Groq.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.groq_client import ask_groq
from core.prompts import MATCH_SYSTEM, MATCH_USER

router = APIRouter()


class MatchRequest(BaseModel):
    resume_text: str
    job_description: str


@router.post("/match")
async def match_job(req: MatchRequest):
    """
    Semantically compare a resume against a job description.
    Returns match score, matched/missing skills, and tailoring tips.
    """
    if len(req.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short.")
    if len(req.job_description.strip()) < 30:
        raise HTTPException(status_code=400, detail="Job description is too short.")

    try:
        result = ask_groq(
            system_prompt=MATCH_SYSTEM,
            user_prompt=MATCH_USER.format(
                resume_text=req.resume_text,
                job_description=req.job_description,
            ),
            json_mode=True,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result
