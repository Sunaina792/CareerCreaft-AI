"""
CareerCraft AI — Resume & Report Exporter
Generates DOCX and PDF from structured candidate data.
"""

import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_docx(data: dict) -> bytes:
    """
    Generate an ATS-friendly DOCX resume from structured candidate data.
    Returns bytes of the .docx file.
    """
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # ── Page margins ────────────────────────────
    for section in doc.sections:
        section.top_margin    = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin   = Inches(0.85)
        section.right_margin  = Inches(0.85)

    # ── Styles ──────────────────────────────────
    def add_heading(text, level=1, color=(30, 30, 100)):
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = para.add_run(text.upper() if level == 2 else text)
        run.bold = True
        run.font.size = Pt(18 if level == 1 else 11)
        run.font.color.rgb = RGBColor(*color)
        if level == 2:
            # Add bottom border via paragraph border
            para.paragraph_format.space_before = Pt(10)
            para.paragraph_format.space_after  = Pt(2)
        return para

    def add_divider():
        para = doc.add_paragraph("─" * 60)
        para.runs[0].font.color.rgb = RGBColor(180, 180, 180)
        para.runs[0].font.size = Pt(8)
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.space_after  = Pt(4)

    def add_bullet(text, indent=False):
        para = doc.add_paragraph(style="List Bullet")
        para.add_run(text).font.size = Pt(10)
        if indent:
            para.paragraph_format.left_indent = Inches(0.25)
        return para

    def add_body(text):
        para = doc.add_paragraph(text)
        para.runs[0].font.size = Pt(10)
        return para

    # ── Name & Contact ───────────────────────────
    name = data.get("name", "Your Name")
    add_heading(name, level=1)

    contact_parts = []
    for field in ["email", "phone", "linkedin", "github", "location"]:
        val = data.get(field, "")
        if val:
            contact_parts.append(val)
    contact_para = doc.add_paragraph(" | ".join(contact_parts))
    contact_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    contact_para.runs[0].font.size = Pt(9)
    contact_para.runs[0].font.color.rgb = RGBColor(80, 80, 80)

    # ── Professional Summary ─────────────────────
    if data.get("summary"):
        add_divider()
        add_heading("Professional Summary", level=2)
        add_body(data["summary"])

    # ── Skills ───────────────────────────────────
    if data.get("skills"):
        add_divider()
        add_heading("Skills", level=2)
        skills = data["skills"]
        if isinstance(skills, list):
            skills_text = " • ".join(skills)
        else:
            skills_text = str(skills)
        add_body(skills_text)

    # ── Education ────────────────────────────────
    if data.get("education"):
        add_divider()
        add_heading("Education", level=2)
        for edu in data["education"]:
            deg_line = doc.add_paragraph()
            deg_run = deg_line.add_run(
                f"{edu.get('degree', '')} — {edu.get('institution', '')}"
            )
            deg_run.bold = True
            deg_run.font.size = Pt(10)
            detail_line = doc.add_paragraph()
            detail_run = detail_line.add_run(
                f"{edu.get('year', '')}  {edu.get('grade', '')}"
            )
            detail_run.font.size = Pt(9)
            detail_run.font.color.rgb = RGBColor(100, 100, 100)

    # ── Experience ───────────────────────────────
    if data.get("experience"):
        add_divider()
        add_heading("Experience", level=2)
        for exp in data["experience"]:
            title_para = doc.add_paragraph()
            title_run = title_para.add_run(
                f"{exp.get('title', '')} @ {exp.get('company', '')}"
            )
            title_run.bold = True
            title_run.font.size = Pt(10)
            date_para = doc.add_paragraph(exp.get("duration", ""))
            date_para.runs[0].font.size = Pt(9)
            date_para.runs[0].font.color.rgb = RGBColor(100, 100, 100)
            for bullet in exp.get("bullets", []):
                add_bullet(bullet)

    # ── Projects ─────────────────────────────────
    if data.get("projects"):
        add_divider()
        add_heading("Projects", level=2)
        for proj in data["projects"]:
            proj_para = doc.add_paragraph()
            proj_run = proj_para.add_run(proj.get("name", ""))
            proj_run.bold = True
            proj_run.font.size = Pt(10)
            if proj.get("tech"):
                tech_para = doc.add_paragraph(
                    f"Tech: {proj.get('tech', '')}"
                )
                tech_para.runs[0].font.size = Pt(9)
                tech_para.runs[0].font.color.rgb = RGBColor(60, 120, 180)
            for bullet in proj.get("bullets", []):
                add_bullet(bullet)

    # ── Certifications ───────────────────────────
    if data.get("certifications"):
        add_divider()
        add_heading("Certifications", level=2)
        for cert in data["certifications"]:
            add_bullet(cert)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def generate_pdf(data: dict) -> bytes:
    """
    Generate an ATS-friendly PDF resume from structured candidate data.
    Returns bytes of the .pdf file.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem,
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    NAVY   = colors.HexColor("#1E2A5E")
    CYAN   = colors.HexColor("#00C2CB")
    GRAY   = colors.HexColor("#555555")
    LGRAY  = colors.HexColor("#AAAAAA")

    styles = getSampleStyleSheet()
    style_name = ParagraphStyle(
        "Name", fontSize=22, textColor=NAVY, leading=28, spaceAfter=2
    )
    style_contact = ParagraphStyle(
        "Contact", fontSize=9, textColor=GRAY, leading=12, spaceAfter=8
    )
    style_section = ParagraphStyle(
        "Section", fontSize=11, textColor=NAVY, leading=14,
        spaceBefore=10, spaceAfter=3, fontName="Helvetica-Bold"
    )
    style_body = ParagraphStyle(
        "Body", fontSize=10, textColor=colors.black, leading=13, spaceAfter=3
    )
    style_sub = ParagraphStyle(
        "Sub", fontSize=9, textColor=GRAY, leading=11, spaceAfter=2
    )
    style_bullet = ParagraphStyle(
        "Bullet", fontSize=9.5, textColor=colors.black, leading=12,
        leftIndent=12, spaceAfter=2, bulletIndent=4
    )

    story = []

    def section_header(title):
        story.append(Paragraph(title.upper(), style_section))
        story.append(HRFlowable(width="100%", thickness=1, color=CYAN, spaceAfter=4))

    # Name & Contact
    name = data.get("name", "Your Name")
    story.append(Paragraph(name, style_name))

    contact_parts = []
    for field in ["email", "phone", "linkedin", "github", "location"]:
        val = data.get(field, "")
        if val:
            contact_parts.append(val)
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), style_contact))

    # Summary
    if data.get("summary"):
        section_header("Professional Summary")
        story.append(Paragraph(data["summary"], style_body))
        story.append(Spacer(1, 4))

    # Skills
    if data.get("skills"):
        section_header("Skills")
        skills = data["skills"]
        skills_text = " • ".join(skills) if isinstance(skills, list) else str(skills)
        story.append(Paragraph(skills_text, style_body))
        story.append(Spacer(1, 4))

    # Education
    if data.get("education"):
        section_header("Education")
        for edu in data["education"]:
            story.append(Paragraph(
                f"<b>{edu.get('degree', '')}</b> — {edu.get('institution', '')}",
                style_body
            ))
            story.append(Paragraph(
                f"{edu.get('year', '')}  {edu.get('grade', '')}",
                style_sub
            ))
        story.append(Spacer(1, 4))

    # Experience
    if data.get("experience"):
        section_header("Experience")
        for exp in data["experience"]:
            story.append(Paragraph(
                f"<b>{exp.get('title', '')}</b> @ {exp.get('company', '')}",
                style_body
            ))
            story.append(Paragraph(exp.get("duration", ""), style_sub))
            for bullet in exp.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", style_bullet))
        story.append(Spacer(1, 4))

    # Projects
    if data.get("projects"):
        section_header("Projects")
        for proj in data["projects"]:
            story.append(Paragraph(f"<b>{proj.get('name', '')}</b>", style_body))
            if proj.get("tech"):
                story.append(Paragraph(f"Tech Stack: {proj.get('tech', '')}", style_sub))
            for bullet in proj.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", style_bullet))
        story.append(Spacer(1, 4))

    # Certifications
    if data.get("certifications"):
        section_header("Certifications")
        for cert in data["certifications"]:
            story.append(Paragraph(f"• {cert}", style_bullet))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
