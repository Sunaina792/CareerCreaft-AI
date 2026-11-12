"""
CareerCraft AI — /api/export
Generates and streams DOCX or PDF resume files.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io

from core.exporter import generate_docx, generate_pdf

router = APIRouter()


class EducationItem(BaseModel):
    degree: str
    institution: str
    year: str = ""
    grade: str = ""


class ExperienceItem(BaseModel):
    title: str
    company: str
    duration: str = ""
    bullets: List[str] = []


class ProjectItem(BaseModel):
    name: str
    tech: str = ""
    bullets: List[str] = []


class ExportRequest(BaseModel):
    format: str  # "docx" or "pdf"
    name: str
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = []
    education: List[EducationItem] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    certifications: List[str] = []


@router.post("/export")
async def export_resume(req: ExportRequest):
    """Export the resume as DOCX or PDF."""
    fmt = req.format.lower().strip()
    if fmt not in ("docx", "pdf"):
        raise HTTPException(status_code=400, detail="Format must be 'docx' or 'pdf'.")

    # Convert pydantic models to plain dicts for the exporter
    data = req.dict()
    data["education"]   = [e.dict() for e in req.education]
    data["experience"]  = [e.dict() for e in req.experience]
    data["projects"]    = [p.dict() for p in req.projects]

    safe_name = "".join(c for c in req.name if c.isalnum() or c in " _-").strip()
    filename = f"{safe_name or 'resume'}_CareerCraft"

    try:
        if fmt == "docx":
            file_bytes = generate_docx(data)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename += ".docx"
        else:
            file_bytes = generate_pdf(data)
            media_type = "application/pdf"
            filename += ".pdf"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
