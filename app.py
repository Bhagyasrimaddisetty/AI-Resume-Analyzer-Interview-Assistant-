"""
app.py  –  AI Resume Analyzer & Interview Assistant
Streamlit entry point.
"""
import streamlit as st
import plotly.graph_objects as go

from utils.resume_parser import parse_resume
from utils.keyword_extractor import compute_keyword_match
from utils.analyzer import (
    analyze_resume_vs_jd,
    generate_interview_questions,
    generate_optimized_summary,
    generate_cover_letter,
)
from utils.report_generator import generate_pdf_report
from utils.llm_client import get_available_providers

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #0f1117; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a1d27; }
    
    /* Metric cards */
    .score-card {
        background: linear-gradient(135deg, #1e2235 0%, #252a40 100%);
        border: 1px solid #2d3356;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 8px 0;
    }
    .score-number {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(90deg, #6c63ff, #48cfad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-label {
        color: #8892b0;
        font-size: 13px;
        margin-top: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Keyword pills */
    .pill-matched {
        display: inline-block;
        background: #0d3321;
        color: #48cfad;
        border: 1px solid #1a7a50;
        border-radius: 20px;
        padding: 3px 12px;
        margin: 3px;
        font-size: 12px;
        font-weight: 500;
    }
    .pill-missing {
        display: inline-block;
        background: #3a1020;
        color: #ff6b8a;
        border: 1px solid #7a1535;
        border-radius: 20px;
        padding: 3px 12px;
        margin: 3px;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        color: #6c63ff;
        font-size: 18px;
        font-weight: 700;
        border-bottom: 2px solid #2d3356;
        padding-bottom: 8px;
        margin: 20px 0 12px 0;
    }
    
    /* Analysis output box */
    .analysis-box {
        background: #1a1d27;
        border: 1px solid #2d3356;
        border-radius: 10px;
        padding: 20px;
        font-family: 'Inter', sans-serif;
        color: #ccd6f6;
        line-height: 1.7;
        white-space: pre-wrap;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6c63ff, #48cfad);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        color: #8892b0;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #6c63ff !important;
        border-bottom-color: #6c63ff !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 AI Resume Analyzer")
    st.markdown("*ATS Screening & Interview Prep*")
    st.divider()

    st.markdown("### ⚙️ Configuration")
    providers = get_available_providers()
    if not providers:
        st.warning("⚠️ No API keys detected.\nAdd `OPENAI_API_KEY` or `GEMINI_API_KEY` to `.env` or Streamlit Secrets.")
        providers = ["gemini", "openai"]  # still show options

    provider = st.selectbox(
        "LLM Provider",
        options=providers if providers else ["gemini", "openai"],
        help="Choose your AI provider. Gemini Flash is free-tier friendly.",
    )

    st.divider()
    st.markdown("### 📋 How to Use")
    st.markdown("""
1. Upload your **resume** (PDF/DOCX/TXT)
2. Paste the **job description**
3. Click **Analyze**
4. Explore results across tabs
5. Download your **PDF report**
""")
    st.divider()
    st.markdown("### 🔑 API Keys")
    st.markdown("""
Add to `.env` file:
```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```
Or Streamlit Secrets → ⚙️ Settings
""")
    st.markdown("---")
    st.caption("Built by Bhagya Sri Maddisetty · 2025")


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("# 🎯 AI Resume Analyzer & Interview Assistant")
st.markdown("*Upload your resume, paste a job description, and get instant ATS analysis + interview prep.*")
st.divider()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📄 Upload Resume")
    uploaded_file = st.file_uploader(
        "Supports PDF, DOCX, TXT",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.success(f"✅ Loaded: **{uploaded_file.name}**")

with col2:
    st.markdown("### 📋 Job Description")
    jd_text = st.text_area(
        "Paste the full job description here",
        height=180,
        placeholder="Paste the complete job description including requirements, responsibilities, and qualifications...",
        label_visibility="collapsed",
    )

# Optional extras
with st.expander("Optional: Company name (for cover letter)"):
    company_name = st.text_input("Company Name", placeholder="e.g. Google, Apple, Infosys...")

st.markdown("---")

# ── Analyze Button ────────────────────────────────────────────────────────────
analyze_col, _ = st.columns([1, 3])
with analyze_col:
    analyze_btn = st.button("🚀 Analyze Resume", use_container_width=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key in ["analysis_done", "analysis_result", "interview_qs", "opt_summary", "cover_letter", "resume_text"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Analysis Logic ─────────────────────────────────────────────────────────────
if analyze_btn:
    if not uploaded_file:
        st.error("❌ Please upload your resume first.")
    elif not jd_text.strip():
        st.error("❌ Please paste the job description.")
    else:
        # Parse resume
        with st.spinner("📄 Parsing resume..."):
            try:
                resume_text = parse_resume(uploaded_file)
                st.session_state["resume_text"] = resume_text
            except Exception as e:
                st.error(f"Failed to parse resume: {e}")
                st.stop()

        # Keyword match (fast, no LLM)
        with st.spinner("🔍 Running keyword analysis..."):
            kw_data = compute_keyword_match(resume_text, jd_text)

        # LLM analysis
        with st.spinner(f"🤖 Running AI analysis via {provider.title()}..."):
            try:
                result = analyze_resume_vs_jd(resume_text, jd_text, provider=provider)
                st.session_state["analysis_result"] = result
                st.session_state["analysis_done"] = True
            except Exception as e:
                st.error(f"LLM analysis failed: {e}")
                st.stop()

        # Pre-generate interview questions in background
        with st.spinner("🎤 Generating interview questions..."):
            try:
                iq = generate_interview_questions(resume_text, jd_text, provider=provider)
                st.session_state["interview_qs"] = iq
            except Exception:
                st.session_state["interview_qs"] = "Could not generate interview questions."

        st.success("✅ Analysis complete! Explore the tabs below.")


# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.get("analysis_done"):
    result = st.session_state["analysis_result"]
    kw = result["keyword_match"]
    resume_text = st.session_state["resume_text"]

    st.divider()

    # ── Score cards row ───────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number">{kw['match_score']}%</div>
            <div class="score-label">ATS Keyword Match</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number">{len(kw['matched'])}</div>
            <div class="score-label">Skills Matched</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number">{len(kw['missing'])}</div>
            <div class="score-label">Skills Missing</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Gauge chart ───────────────────────────────────────────────────────────
    gauge_col, info_col = st.columns([1, 1])
    with gauge_col:
        score = kw["match_score"]
        color = "#48cfad" if score >= 70 else "#f7c948" if score >= 45 else "#ff6b8a"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 40, "color": color}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#8892b0"},
                "bar": {"color": color},
                "bgcolor": "#1a1d27",
                "steps": [
                    {"range": [0, 45], "color": "#2a1020"},
                    {"range": [45, 70], "color": "#2a2510"},
                    {"range": [70, 100], "color": "#0d2820"},
                ],
                "threshold": {
                    "line": {"color": "#6c63ff", "width": 3},
                    "thickness": 0.75,
                    "value": 70,
                },
            },
            title={"text": "ATS Match Score", "font": {"color": "#8892b0", "size": 14}},
        ))
        fig.update_layout(
            paper_bgcolor="#0f1117",
            font_color="#ccd6f6",
            height=280,
            margin=dict(t=40, b=10, l=30, r=30),
        )
        st.plotly_chart(fig, use_container_width=True)

    with info_col:
        hint = (
            "🟢 **Strong match!** Your resume aligns well with this role."
            if score >= 70 else
            "🟡 **Moderate match.** Add the missing keywords to improve shortlisting chances."
            if score >= 45 else
            "🔴 **Low match.** Significant skill gaps — tailor your resume heavily."
        )
        st.markdown(f"\n\n{hint}\n\n")
        st.markdown(f"**Threshold for shortlisting:** 70%+")
        st.markdown(f"**Your score:** {score}%")

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Analysis", "🔑 Keywords", "🎤 Interview Prep",
        "✍️ Optimized Summary", "📝 Cover Letter", "📥 Download Report"
    ])

    # Tab 1: AI Analysis
    with tabs[0]:
        st.markdown('<div class="section-header">🤖 AI Analysis</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="analysis-box">{result["llm_analysis"]}</div>',
            unsafe_allow_html=True,
        )

    # Tab 2: Keywords
    with tabs[1]:
        st.markdown('<div class="section-header">✅ Matched Skills</div>', unsafe_allow_html=True)
        if kw["matched"]:
            pills_html = " ".join(f'<span class="pill-matched">{k}</span>' for k in kw["matched"])
            st.markdown(pills_html, unsafe_allow_html=True)
        else:
            st.info("No ATS skills matched. Heavily tailor your resume.")

        st.markdown('<div class="section-header">❌ Missing Skills (from JD)</div>', unsafe_allow_html=True)
        if kw["missing"]:
            pills_html = " ".join(f'<span class="pill-missing">{k}</span>' for k in kw["missing"])
            st.markdown(pills_html, unsafe_allow_html=True)
            st.markdown(
                "> 💡 **Tip:** Add these to your Skills section and weave them into bullet points where applicable.",
                unsafe_allow_html=False,
            )
        else:
            st.success("🎉 You've matched all detected JD keywords!")

    # Tab 3: Interview Prep
    with tabs[2]:
        st.markdown('<div class="section-header">🎤 Role-Specific Interview Questions</div>', unsafe_allow_html=True)
        if st.session_state["interview_qs"]:
            st.markdown(
                f'<div class="analysis-box">{st.session_state["interview_qs"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button("Generate Interview Questions"):
                with st.spinner("Generating..."):
                    iq = generate_interview_questions(resume_text, jd_text, provider=provider)
                    st.session_state["interview_qs"] = iq
                    st.rerun()

    # Tab 4: Optimized Summary
    with tabs[3]:
        st.markdown('<div class="section-header">✍️ AI-Optimized Professional Summary</div>', unsafe_allow_html=True)
        st.caption("A tailored summary using JD keywords, ready to paste into your resume.")
        if not st.session_state.get("opt_summary"):
            if st.button("Generate Optimized Summary"):
                with st.spinner("Generating..."):
                    st.session_state["opt_summary"] = generate_optimized_summary(resume_text, jd_text, provider=provider)
                    st.rerun()
        if st.session_state.get("opt_summary"):
            st.markdown(
                f'<div class="analysis-box">{st.session_state["opt_summary"]}</div>',
                unsafe_allow_html=True,
            )
            st.button("🔄 Regenerate", on_click=lambda: st.session_state.update({"opt_summary": None}))

    # Tab 5: Cover Letter
    with tabs[4]:
        st.markdown('<div class="section-header">📝 AI Cover Letter</div>', unsafe_allow_html=True)
        if not st.session_state.get("cover_letter"):
            if st.button("Generate Cover Letter"):
                with st.spinner("Writing cover letter..."):
                    st.session_state["cover_letter"] = generate_cover_letter(
                        resume_text, jd_text, company=company_name, provider=provider
                    )
                    st.rerun()
        if st.session_state.get("cover_letter"):
            st.markdown(
                f'<div class="analysis-box">{st.session_state["cover_letter"]}</div>',
                unsafe_allow_html=True,
            )
            st.button("🔄 Regenerate", key="regen_cl", on_click=lambda: st.session_state.update({"cover_letter": None}))

    # Tab 6: Download
    with tabs[5]:
        st.markdown('<div class="section-header">📥 Download Full Report</div>', unsafe_allow_html=True)
        st.markdown("Get a complete PDF with keyword analysis, AI feedback, and interview questions.")
        if st.button("📄 Generate PDF Report"):
            with st.spinner("Building PDF..."):
                try:
                    pdf_bytes = generate_pdf_report(
                        analysis_text=result["llm_analysis"],
                        keyword_data=kw,
                        interview_questions=st.session_state.get("interview_qs", ""),
                        optimized_summary=st.session_state.get("opt_summary", ""),
                    )
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name="resume_analysis_report.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")

# ── Empty state ───────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; color: #8892b0;">
        <div style="font-size: 64px; margin-bottom: 16px;">🎯</div>
        <h3 style="color: #ccd6f6;">Ready to analyze your resume</h3>
        <p>Upload your resume and paste a job description above, then click <strong>Analyze Resume</strong>.</p>
        <br>
        <div style="display:flex; justify-content:center; gap: 40px; margin-top:10px;">
            <div>📊 ATS Score</div>
            <div>🔑 Skill Gap Analysis</div>
            <div>🎤 Interview Questions</div>
            <div>✍️ Optimized Summary</div>
            <div>📝 Cover Letter</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
