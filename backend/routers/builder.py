"""
CareerCraft AI — /api/builder
AI-assisted resume content generation endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.groq_client import ask_groq, ask_groq_fast
from core.prompts import (
    SUMMARY_SYSTEM, SUMMARY_USER,
    BULLET_SYSTEM, BULLET_USER,
    SKILLS_SYSTEM, SKILLS_USER,
    IMPROVE_SECTION_SYSTEM, IMPROVE_SECTION_USER,
)

router = APIRouter()


# ── Generate Professional Summary ────────────
class SummaryRequest(BaseModel):
    name: str
    target_role: str
    skills: str
    experience: str = ""
    education: str = ""
    projects: str = ""


@router.post("/builder/summary")
async def generate_summary(req: SummaryRequest):
    """Generate a professional summary using only provided facts."""
    try:
        text = ask_groq_fast(
            system_prompt=SUMMARY_SYSTEM,
            user_prompt=SUMMARY_USER.format(
                name=req.name,
                target_role=req.target_role,
                skills=req.skills,
                experience=req.experience,
                education=req.education,
                projects=req.projects,
            ),
        )
        return {"summary": text.strip()}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ── Rewrite Bullet Point ──────────────────────
class BulletRequest(BaseModel):
    bullet: str
    context: str = ""


@router.post("/builder/rewrite-bullet")
async def rewrite_bullet(req: BulletRequest):
    """Rewrite a bullet point to be more impactful."""
    if len(req.bullet.strip()) < 5:
        raise HTTPException(status_code=400, detail="Bullet point is too short.")
    try:
        text = ask_groq_fast(
            system_prompt=BULLET_SYSTEM,
            user_prompt=BULLET_USER.format(
                bullet=req.bullet,
                context=req.context,
            ),
        )
        return {"rewritten": text.strip()}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ── Suggest Skills ────────────────────────────
class SkillsRequest(BaseModel):
    target_role: str
    current_skills: str = ""
    experience_level: str = "fresher"


@router.post("/builder/suggest-skills")
async def suggest_skills(req: SkillsRequest):
    """Suggest skills to learn/add for a target role."""
    try:
        result = ask_groq(
            system_prompt=SKILLS_SYSTEM,
            user_prompt=SKILLS_USER.format(
                target_role=req.target_role,
                current_skills=req.current_skills,
                experience_level=req.experience_level,
            ),
            json_mode=True,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ── Improve Resume Section ────────────────────
class ImproveRequest(BaseModel):
    section_name: str
    original_content: str
    target_role: str = ""


@router.post("/builder/improve-section")
async def improve_section(req: ImproveRequest):
    """AI-improve a resume section based on target role."""
    if len(req.original_content.strip()) < 10:
        raise HTTPException(status_code=400, detail="Section content is too short.")
    try:
        text = ask_groq_fast(
            system_prompt=IMPROVE_SECTION_SYSTEM,
            user_prompt=IMPROVE_SECTION_USER.format(
                section_name=req.section_name,
                target_role=req.target_role,
                original_content=req.original_content,
            ),
        )
        return {"improved": text.strip()}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
