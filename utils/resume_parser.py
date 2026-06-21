"""
resume_parser.py
Extracts raw text from PDF and DOCX resume files.
"""
import io
import PyPDF2
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file given its bytes."""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file given its bytes."""
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def parse_resume(uploaded_file) -> str:
    """
    Parse an uploaded Streamlit file object.
    Supports PDF and DOCX.
    Returns extracted text or raises ValueError for unsupported types.
    """
    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.name}")
