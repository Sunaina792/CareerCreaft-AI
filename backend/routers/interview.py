"""
CareerCraft AI — /api/interview
Generates personalized interview questions from resume + JD.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.groq_client import ask_groq
from core.prompts import INTERVIEW_SYSTEM, INTERVIEW_USER

router = APIRouter()


class InterviewRequest(BaseModel):
    resume_text: str
    job_description: str = ""


@router.post("/interview-prep")
async def interview_prep(req: InterviewRequest):
    """
    Generate 10 personalized interview questions with tips.
    """
    if len(req.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short.")

    try:
        result = ask_groq(
            system_prompt=INTERVIEW_SYSTEM,
            user_prompt=INTERVIEW_USER.format(
                resume_text=req.resume_text,
                job_description=req.job_description or "Not provided — use the resume to generate general questions.",
            ),
            json_mode=True,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result
