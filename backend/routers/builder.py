"""
CareerCraft AI — /api/builder
AI-assisted resume content generation endpoints.
"""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, ValidationError
from core.parser import extract_text
from core.groq_client import ask_groq, ask_groq_fast
from core.prompts import (
    SUMMARY_SYSTEM, SUMMARY_USER,
    BULLET_SYSTEM, BULLET_USER,
    SKILLS_SYSTEM, SKILLS_USER,
    IMPROVE_SECTION_SYSTEM, IMPROVE_SECTION_USER,
    TAILOR_RESUME_SYSTEM, TAILOR_RESUME_USER,
)

router = APIRouter()


# ── Tailor Resume to a Job Description ────────
class TailoredEducation(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""
    grade: str = ""


class TailoredExperience(BaseModel):
    title: str = ""
    company: str = ""
    duration: str = ""
    bullets: list[str] = Field(default_factory=list)


class TailoredProject(BaseModel):
    name: str = ""
    tech: str = ""
    bullets: list[str] = Field(default_factory=list)


class TailoredResume(BaseModel):
    name: str = Field(min_length=1)
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""
    target_role: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    education: list[TailoredEducation] = Field(default_factory=list)
    experience: list[TailoredExperience] = Field(default_factory=list)
    projects: list[TailoredProject] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


@router.post("/builder/tailor")
async def tailor_resume(
    file: UploadFile = File(...),
    job_description: str = Form(..., min_length=30, max_length=20000),
):
    """Create a job-targeted resume from an uploaded PDF or DOCX."""
    resume_text = await extract_text(file)
    if len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Resume text is too short to build a tailored resume.",
        )
    if len(resume_text) > 30000:
        raise HTTPException(
            status_code=413,
            detail="Resume text is too long to process. Please upload a shorter resume.",
        )

    try:
        result = ask_groq(
            system_prompt=TAILOR_RESUME_SYSTEM,
            user_prompt=TAILOR_RESUME_USER.format(
                resume_text=resume_text,
                job_description=job_description.strip(),
            ),
            json_mode=True,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    try:
        resume = TailoredResume.parse_obj(result)
    except (ValidationError, TypeError) as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI returned an invalid resume structure: {e}",
        )
    return resume.dict()


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
