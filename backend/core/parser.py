"""
CareerCraft AI — Resume Parser
Extracts clean text from PDF and DOCX files.
"""

import io
import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)


async def extract_text(file: UploadFile) -> str:
    """
    Extract raw text from an uploaded PDF or DOCX file.
    Returns cleaned text string.
    """
    filename = file.filename.lower()
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if filename.endswith(".pdf"):
        return _extract_pdf(content, filename)
    elif filename.endswith(".docx"):
        return _extract_docx(content, filename)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX file.",
        )


def _extract_pdf(content: bytes, filename: str) -> str:
    try:
        import pymupdf as fitz  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        doc.close()

        text = "\n".join(pages_text).strip()
        if not text:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Could not extract text from this PDF. "
                    "It may be a scanned/image-based PDF. "
                    "Please try a text-based PDF or DOCX."
                ),
            )
        return _clean_text(text)

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF processing library (PyMuPDF) not installed.",
        )
    except Exception as e:
        logger.error(f"PDF extraction failed for {filename}: {e}")
        raise HTTPException(
            status_code=422, detail=f"Failed to read PDF: {str(e)}"
        )


def _extract_docx(content: bytes, filename: str) -> str:
    try:
        import docx

        doc = docx.Document(io.BytesIO(content))
        paragraphs = []

        # Extract paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)

        # Extract tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(
                    cell.text.strip() for cell in row.cells if cell.text.strip()
                )
                if row_text:
                    paragraphs.append(row_text)

        text = "\n".join(paragraphs).strip()
        if not text:
            raise HTTPException(
                status_code=422,
                detail="The DOCX file appears to be empty or has no readable text.",
            )
        return _clean_text(text)

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="DOCX processing library (python-docx) not installed.",
        )
    except Exception as e:
        logger.error(f"DOCX extraction failed for {filename}: {e}")
        raise HTTPException(
            status_code=422, detail=f"Failed to read DOCX: {str(e)}"
        )


def _clean_text(text: str) -> str:
    """Normalize whitespace while preserving structure."""
    import re

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove excessive blank lines (max 2 consecutive)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()
