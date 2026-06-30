"""
app.py - ResumeInsight AI: Production-Ready Resume Analyzer & ATS Optimizer
Main Streamlit application with premium UI.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import time

from assets.styles import CUSTOM_CSS
from utils.constants import APP_TITLE, APP_ICON, CHART_COLORS, CHART_COLOR_SCALE

# ─── Page Config ───
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─── Session State Initialization ───
def init_session():
    defaults = {
        "resumes": [], "parsed_resumes": [], "jd_text": "",
        "ats_report": None, "retriever": None, "chat_history": [],
        "analysis_done": False, "chunks": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─── Sidebar ───
with st.sidebar:
    st.markdown(f"# {APP_ICON} {APP_TITLE}")
    st.markdown("---")

    st.markdown("### 📄 Upload Resumes")
    uploaded_files = st.file_uploader(
        "PDF or DOCX", type=["pdf", "docx"],
        accept_multiple_files=True, key="resume_upload",
        label_visibility="collapsed",
    )

    st.markdown("### 📋 Job Description")
    jd_input_method = st.radio("Input method", ["Paste Text", "Upload File"], horizontal=True, label_visibility="collapsed")

    if jd_input_method == "Paste Text":
        jd_text = st.text_area("Paste JD here", height=200, placeholder="Paste the job description...", label_visibility="collapsed")
    else:
        jd_file = st.file_uploader("Upload JD", type=["txt", "pdf", "docx"], key="jd_upload")
        jd_text = ""
        if jd_file:
            if jd_file.name.endswith('.txt'):
                jd_text = jd_file.read().decode('utf-8', errors='ignore')
            elif jd_file.name.endswith('.pdf'):
                from core.parser import parse_pdf
                result = parse_pdf(jd_file.read())
                jd_text = result.get("text", "")
            elif jd_file.name.endswith('.docx'):
                from core.parser import parse_docx
                result = parse_docx(jd_file.read())
                jd_text = result.get("text", "")

    analyze_btn = st.button("🚀 Analyze Resume", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password", help="Overrides .env key")

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#666;font-size:12px;'>"
        "Built with ❤️ using Streamlit, LangChain & Gemini"
        "</div>", unsafe_allow_html=True,
    )


# ─── Helper: Build Charts ───
def build_gauge(score, title="ATS Score"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": title, "font": {"size": 16, "color": "#a0a0c0"}},
        number={"font": {"size": 48, "color": "#e0e0ff"}, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#444"},
            "bar": {"color": "#6C63FF"},
            "bgcolor": "rgba(255,255,255,0.03)",
            "steps": [
                {"range": [0, 40], "color": "rgba(255,71,87,0.15)"},
                {"range": [40, 70], "color": "rgba(255,193,7,0.15)"},
                {"range": [70, 100], "color": "rgba(0,201,167,0.15)"},
            ],
            "threshold": {"line": {"color": "#00C9A7", "width": 3}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(
        height=250, margin=dict(t=40, b=10, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#e0e0ff"},
    )
    return fig


def build_radar(scores_dict):
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    values.append(values[0])
    categories.append(categories[0])
    fig = go.Figure(go.Scatterpolar(r=values, theta=categories, fill='toself',
        fillcolor='rgba(108,99,255,0.15)', line=dict(color='#6C63FF', width=2),
        marker=dict(size=6, color='#6C63FF'),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.08)', tickfont=dict(color='#666')),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.08)', tickfont=dict(color='#a0a0c0', size=11)),
        ),
        showlegend=False, height=350, margin=dict(t=30, b=30, l=60, r=60),
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def build_bar(scores_dict, title="Component Scores"):
    names = list(scores_dict.keys())
    vals = list(scores_dict.values())
    colors = [CHART_COLOR_SCALE[i % len(CHART_COLOR_SCALE)] for i in range(len(names))]
    fig = go.Figure(go.Bar(
        x=vals, y=[n.replace('_', ' ').title() for n in names],
        orientation='h', marker=dict(color=colors, cornerradius=6),
        text=[f"{v:.0f}%" for v in vals], textposition='outside',
        textfont=dict(color='#e0e0ff', size=12),
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color='#a0a0c0', size=14)),
        height=max(250, len(names) * 45), margin=dict(t=40, b=20, l=10, r=40),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 110], gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#666')),
        yaxis=dict(tickfont=dict(color='#a0a0c0', size=12)),
    )
    return fig


def build_pie(matched, missing):
    fig = go.Figure(go.Pie(
        labels=["Matched", "Missing"], values=[matched, missing],
        marker=dict(colors=[CHART_COLORS["success"], CHART_COLORS["danger"]]),
        hole=0.55, textinfo='label+percent', textfont=dict(color='#e0e0ff'),
    ))
    fig.update_layout(
        height=280, margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
    )
    return fig


# ─── Main Area ───
if not st.session_state.analysis_done and not analyze_btn:
    # Hero Landing
    st.markdown('<div class="hero-title">ResumeInsight AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">AI-Powered Resume Analyzer & ATS Optimizer with RAG</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("🎯", "ATS Scoring", "Deterministic, weighted scoring across 7 dimensions"),
        ("🔍", "Keyword Analysis", "Exact, fuzzy & semantic keyword matching"),
        ("🤖", "RAG Chat", "Ask questions about your resume using retrieval-augmented generation"),
        ("✍️", "Smart Rewrite", "AI-powered bullet point improvement suggestions"),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], features):
        col.markdown(
            f'<div class="glass-card" style="text-align:center;min-height:180px;">'
            f'<div style="font-size:36px;margin-bottom:12px;">{icon}</div>'
            f'<div style="font-size:16px;font-weight:600;color:#e0e0ff;margin-bottom:8px;">{title}</div>'
            f'<div style="font-size:13px;color:#8888aa;">{desc}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Upload your resume and paste a job description in the sidebar to get started!")


# ─── Analysis Pipeline ───
if analyze_btn:
    if not uploaded_files:
        st.error("Please upload at least one resume.")
        st.stop()
    if not jd_text.strip():
        st.warning("No job description provided. Analysis will be limited.")
        jd_text = ""

    # Configure API
    if api_key:
        import os; os.environ["GOOGLE_API_KEY"] = api_key

    progress = st.progress(0, "Starting analysis...")

    # Step 1: Parse resumes
    progress.progress(10, "📄 Parsing resumes...")
    from core.parser import parse_resume
    parsed_resumes = []
    for f in uploaded_files:
        data = parse_resume(f.read(), f.name)
        if data.get("error"):
            st.error(f"Error parsing {f.name}: {data['error']}")
        else:
            parsed_resumes.append(data)

    if not parsed_resumes:
        st.error("No resumes could be parsed.")
        st.stop()

    st.session_state.parsed_resumes = parsed_resumes

    # Step 2: Chunk
    progress.progress(30, "✂️ Chunking text...")
    from core.chunking import create_resume_chunks
    all_chunks = []
    for pr in parsed_resumes:
        all_chunks.extend(create_resume_chunks(pr))
    st.session_state.chunks = all_chunks

    # Step 3: Build retriever
    progress.progress(50, "🧠 Building vector index...")
    from core.retriever import ResumeRetriever
    retriever = ResumeRetriever(all_chunks)
    st.session_state.retriever = retriever

    # Step 4: ATS analysis
    progress.progress(75, "📊 Running ATS analysis...")
    from core.ats import run_ats_analysis
    report = run_ats_analysis(parsed_resumes[0], jd_text)
    st.session_state.ats_report = report
    st.session_state.jd_text = jd_text
    st.session_state.analysis_done = True

    progress.progress(100, "✅ Analysis complete!")
    time.sleep(0.5)
    progress.empty()
    st.rerun()


# ─── Results Dashboard ───
if st.session_state.analysis_done and st.session_state.ats_report:
    report = st.session_state.ats_report
    ats = report["ats_score"]
    kw = report["keyword_analysis"]
    resume_info = report["resume_info"]
    parsed = st.session_state.parsed_resumes[0]

    # Tabs
    tabs = st.tabs(["📊 Dashboard", "🔑 Keywords", "📝 Quality", "✍️ Rewrite", "💬 AI Chat", "🎤 Interview"])

    # ─── TAB 1: Dashboard ───
    with tabs[0]:
        st.markdown('<div class="section-header">ATS Analysis Dashboard</div>', unsafe_allow_html=True)

        # Top row: Score + Grade + Key Metrics
        col_score, col_radar = st.columns([1, 1.5])

        with col_score:
            st.plotly_chart(build_gauge(ats["overall_score"]), use_container_width=True)
            st.markdown(
                f'<div style="text-align:center;"><span class="grade-badge">Grade: {ats["grade"]}</span></div>',
                unsafe_allow_html=True,
            )

        with col_radar:
            st.plotly_chart(build_radar(ats["component_scores"]), use_container_width=True)

        # Component scores bar chart
        st.plotly_chart(build_bar(ats["component_scores"]), use_container_width=True)

        # Match summary metrics
        st.markdown('<div class="section-header">Match Summary</div>', unsafe_allow_html=True)
        from core.ats import get_match_summary
        match_sum = get_match_summary(report)
        cols = st.columns(len(match_sum))
        for col, (label, val) in zip(cols, match_sum.items()):
            col.markdown(
                f'<div class="metric-pill"><div class="value">{val:.0f}%</div>'
                f'<div class="label">{label}</div></div>',
                unsafe_allow_html=True,
            )

        # Resume Info
        st.markdown('<div class="section-header">Resume Information</div>', unsafe_allow_html=True)
        ic1, ic2, ic3 = st.columns(3)
        contact = resume_info.get("contact", {})
        ic1.markdown(f"**Name:** {contact.get('name', 'N/A')}")
        ic1.markdown(f"**Email:** {contact.get('email', 'N/A')}")
        ic2.markdown(f"**Phone:** {contact.get('phone', 'N/A')}")
        ic2.markdown(f"**Format:** {resume_info.get('format', 'N/A').upper()}")
        ic3.markdown(f"**Pages:** {resume_info.get('page_count', 'N/A')}")
        ic3.markdown(f"**Sections:** {len(resume_info.get('sections_found', []))}")

        # Suggestions
        st.markdown('<div class="section-header">💡 Improvement Suggestions</div>', unsafe_allow_html=True)
        for sug in ats.get("suggestions", []):
            st.markdown(f"• {sug}")

    # ─── TAB 2: Keywords ───
    with tabs[1]:
        st.markdown('<div class="section-header">Keyword Analysis</div>', unsafe_allow_html=True)

        kc1, kc2 = st.columns(2)
        with kc1:
            st.plotly_chart(build_pie(len(kw["matched_keywords"]), len(kw["missing_keywords"])), use_container_width=True)
        with kc2:
            st.metric("Match Rate", f"{kw['match_percentage']:.1f}%")
            st.metric("Matched", len(kw["matched_keywords"]))
            st.metric("Missing", len(kw["missing_keywords"]))

        st.markdown('<div class="section-header">✅ Matched Keywords</div>', unsafe_allow_html=True)
        html = " ".join(f'<span class="tag-matched">{k}</span>' for k in kw["matched_keywords"])
        st.markdown(html or "No matches found.", unsafe_allow_html=True)

        st.markdown('<div class="section-header">❌ Missing Keywords</div>', unsafe_allow_html=True)
        html = " ".join(f'<span class="tag-missing">{k}</span>' for k in kw["missing_keywords"])
        st.markdown(html or "None missing!", unsafe_allow_html=True)

        if kw.get("high_priority_missing"):
            st.markdown('<div class="section-header">🔥 High Priority Missing</div>', unsafe_allow_html=True)
            for k in kw["high_priority_missing"]:
                st.markdown(f"- **{k}**")

        st.markdown('<div class="section-header">🏷️ Skills Found in Resume</div>', unsafe_allow_html=True)
        html = " ".join(f'<span class="tag-skill">{s}</span>' for s in resume_info.get("skills_found", []))
        st.markdown(html or "No skills detected.", unsafe_allow_html=True)

    # ─── TAB 3: Quality ───
    with tabs[2]:
        st.markdown('<div class="section-header">Resume Quality Analysis</div>', unsafe_allow_html=True)

        from core.grammar import analyze_resume_quality
        quality = analyze_resume_quality(parsed.get("text", ""), parsed.get("sections", {}))

        qc1, qc2 = st.columns([1, 2])
        with qc1:
            st.plotly_chart(build_gauge(quality["score"], "Quality Score"), use_container_width=True)
            st.markdown(f"**{quality['summary']}**")

        with qc2:
            if quality["issues"]:
                for issue in quality["issues"][:15]:
                    sev = issue.get("severity", "low")
                    st.markdown(
                        f'<div class="issue-card {sev}">'
                        f'<strong>{issue["type"].replace("_"," ").title()}</strong> '
                        f'({sev.upper()})<br>'
                        f'<em>{issue.get("text","")[:100]}</em><br>'
                        f'💡 {issue.get("suggestion","")}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.success("No quality issues found! Your resume looks great.")

        # Section feedback
        st.markdown('<div class="section-header">Section Feedback</div>', unsafe_allow_html=True)
        for section, feedbacks in ats.get("feedback", {}).items():
            with st.expander(f"📌 {section.replace('_',' ').title()}", expanded=False):
                for fb in feedbacks:
                    st.markdown(fb)

    # ─── TAB 4: Rewrite ───
    with tabs[3]:
        st.markdown('<div class="section-header">AI Bullet Point Rewriter</div>', unsafe_allow_html=True)

        from core.rewrite import identify_weak_bullets, rewrite_bullet

        weak = identify_weak_bullets(parsed.get("text", ""))
        if weak:
            st.warning(f"Found {len(weak)} bullet points that could be improved.")
            for wb in weak[:8]:
                with st.expander(f"📝 {wb['text'][:80]}..."):
                    st.markdown(f"**Original:** {wb['text']}")
                    st.markdown(f"**Issues:** {', '.join(wb['reasons'])}")
                    if st.button(f"✨ Rewrite", key=f"rw_{wb['line']}"):
                        with st.spinner("Generating improvements..."):
                            improved = rewrite_bullet(wb["text"])
                            for i, v in enumerate(improved, 1):
                                st.markdown(f"**Version {i}:** {v}")
        else:
            st.success("All bullet points look strong!")

        st.markdown("---")
        st.markdown("### ✍️ Custom Rewrite")
        custom_bullet = st.text_input("Enter a bullet point to improve:")
        if custom_bullet and st.button("✨ Rewrite Custom"):
            with st.spinner("Generating..."):
                improved = rewrite_bullet(custom_bullet)
                for i, v in enumerate(improved, 1):
                    st.success(f"**Version {i}:** {v}")

    # ─── TAB 5: AI Chat ───
    with tabs[4]:
        st.markdown('<div class="section-header">💬 Ask AI About Your Resume</div>', unsafe_allow_html=True)
        st.caption("Uses RAG — only relevant resume sections are sent to the LLM.")

        # Display chat history
        for msg in st.session_state.chat_history:
            role_class = "chat-user" if msg["role"] == "user" else "chat-assistant"
            icon = "👤" if msg["role"] == "user" else "🤖"
            st.markdown(
                f'<div class="chat-message {role_class}">{icon} {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

        user_query = st.chat_input("Ask about your resume...")
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})

            # Retrieve context
            retriever = st.session_state.retriever
            results = retriever.retrieve(user_query) if retriever else []
            context = "\n\n---\n\n".join([r["text"] for r in results]) if results else parsed.get("text", "")[:3000]

            from core.prompts import RAG_QA_PROMPT
            from core.llm import generate_response
            prompt = RAG_QA_PROMPT.format(context=context, question=user_query)

            with st.spinner("Thinking..."):
                answer = generate_response(prompt)

            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

    # ─── TAB 6: Interview ───
    with tabs[5]:
        st.markdown('<div class="section-header">🎤 AI Interview Question Generator</div>', unsafe_allow_html=True)

        gen_type = st.selectbox("Question Type", ["Full Interview Set", "Project-Based", "Skill-Based"])

        if st.button("🎯 Generate Questions"):
            with st.spinner("Generating interview questions..."):
                from core.interview import generate_interview_questions, generate_skill_questions

                if gen_type == "Skill-Based":
                    skills = resume_info.get("skills_found", [])[:10]
                    if skills:
                        response = generate_skill_questions(skills)
                    else:
                        response = "No skills detected in resume."
                else:
                    retriever = st.session_state.retriever
                    context = ""
                    if retriever:
                        chunks = retriever.retrieve("experience projects skills", top_k=8)
                        context = "\n\n".join([c["text"] for c in chunks])
                    else:
                        context = parsed.get("text", "")[:4000]
                    response = generate_interview_questions(context, resume_info.get("skills_found", []))

                st.markdown(response)
