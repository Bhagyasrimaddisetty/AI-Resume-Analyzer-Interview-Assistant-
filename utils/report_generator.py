"""
report_generator.py
Generates a downloadable PDF analysis report using fpdf2.
"""
from fpdf import FPDF
import datetime
import io


class ResumeReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 30, 80)
        self.cell(0, 10, "AI Resume Analysis Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 6, f"Generated on {ts}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_draw_color(30, 30, 80)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 30, 80)
        self.ln(4)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 220)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        # Clean non-latin chars that fpdf can't handle
        safe = text.encode("latin-1", errors="replace").decode("latin-1")
        self.multi_cell(0, 6, safe)
        self.ln(2)

    def keyword_pills(self, keywords: list[str], color: tuple):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*color)
        line = "  |  ".join(keywords) if keywords else "None"
        safe = line.encode("latin-1", errors="replace").decode("latin-1")
        self.multi_cell(0, 6, safe)
        self.ln(2)


def generate_pdf_report(
    analysis_text: str,
    keyword_data: dict,
    interview_questions: str = "",
    optimized_summary: str = "",
) -> bytes:
    """
    Build a PDF report and return as bytes.
    """
    pdf = ResumeReport()
    pdf.add_page()

    # ── Keyword Match Overview ────────────────────────────────────────────────
    pdf.section_title("Keyword Match Overview")
    score = keyword_data.get("match_score", 0)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 14, f"{score}%  ATS Keyword Match", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 120, 60)
    pdf.cell(0, 7, "Matched Skills:", new_x="LMARGIN", new_y="NEXT")
    pdf.keyword_pills(keyword_data.get("matched", []), (0, 120, 60))

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(180, 40, 40)
    pdf.cell(0, 7, "Missing Skills:", new_x="LMARGIN", new_y="NEXT")
    pdf.keyword_pills(keyword_data.get("missing", []), (180, 40, 40))

    # ── AI Analysis ───────────────────────────────────────────────────────────
    pdf.section_title("AI Analysis")
    pdf.body_text(analysis_text)

    # ── Optimized Summary ─────────────────────────────────────────────────────
    if optimized_summary:
        pdf.section_title("AI-Generated Optimized Summary")
        pdf.body_text(optimized_summary)

    # ── Interview Questions ───────────────────────────────────────────────────
    if interview_questions:
        pdf.add_page()
        pdf.section_title("Interview Preparation Questions")
        pdf.body_text(interview_questions)

    output = io.BytesIO()
    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)
