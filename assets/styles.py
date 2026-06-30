"""
styles.py - Premium CSS styles for the Streamlit UI.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ─── Global ─── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    border-right: 1px solid rgba(108, 99, 255, 0.2);
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e0e0ff;
}

/* ─── Cards ─── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(108,99,255,0.15);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(12px);
    transition: transform 0.2s, box-shadow 0.2s;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(108,99,255,0.15);
}

/* ─── Score Card ─── */
.score-card {
    background: linear-gradient(135deg, rgba(108,99,255,0.15) 0%, rgba(0,201,167,0.10) 100%);
    border: 1px solid rgba(108,99,255,0.25);
    border-radius: 20px;
    padding: 32px;
    text-align: center;
}
.score-value {
    font-size: 64px;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #00C9A7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.score-label {
    color: #a0a0c0;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 8px;
}
.grade-badge {
    display: inline-block;
    background: linear-gradient(135deg, #6C63FF, #A855F7);
    color: white;
    padding: 6px 20px;
    border-radius: 24px;
    font-weight: 700;
    font-size: 18px;
    margin-top: 12px;
}

/* ─── Metric Pill ─── */
.metric-pill {
    background: rgba(108,99,255,0.08);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.metric-pill .value {
    font-size: 28px;
    font-weight: 700;
    color: #6C63FF;
}
.metric-pill .label {
    font-size: 12px;
    color: #8888aa;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* ─── Tags ─── */
.tag-matched {
    display: inline-block;
    background: rgba(0,201,167,0.15);
    color: #00C9A7;
    border: 1px solid rgba(0,201,167,0.3);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    margin: 3px;
    font-weight: 500;
}
.tag-missing {
    display: inline-block;
    background: rgba(255,71,87,0.12);
    color: #FF4757;
    border: 1px solid rgba(255,71,87,0.3);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    margin: 3px;
    font-weight: 500;
}
.tag-skill {
    display: inline-block;
    background: rgba(108,99,255,0.12);
    color: #6C63FF;
    border: 1px solid rgba(108,99,255,0.25);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    margin: 3px;
}

/* ─── Issue Cards ─── */
.issue-card {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
}
.issue-card.high { border-color: #FF4757; }
.issue-card.medium { border-color: #FFC107; }
.issue-card.low { border-color: #54A0FF; }

/* ─── Chat ─── */
.chat-message {
    padding: 16px 20px;
    border-radius: 16px;
    margin: 8px 0;
    line-height: 1.6;
}
.chat-user {
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.2);
    margin-left: 40px;
}
.chat-assistant {
    background: rgba(0,201,167,0.08);
    border: 1px solid rgba(0,201,167,0.15);
    margin-right: 40px;
}

/* ─── Section Headers ─── */
.section-header {
    font-size: 22px;
    font-weight: 700;
    color: #e0e0ff;
    margin: 24px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(108,99,255,0.3);
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.02);
    padding: 4px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    color: #a0a0c0;
}
.stTabs [aria-selected="true"] {
    background: rgba(108,99,255,0.15);
    color: #6C63FF;
}

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF 0%, #A855F7 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(108,99,255,0.4);
}

/* ─── File Uploader ─── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(108,99,255,0.3);
    border-radius: 16px;
    padding: 20px;
    transition: border-color 0.3s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(108,99,255,0.6);
}

/* ─── Expander ─── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    font-weight: 600;
}

/* ─── Progress Bars ─── */
.stProgress > div > div {
    background: linear-gradient(90deg, #6C63FF, #00C9A7);
    border-radius: 10px;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(108,99,255,0.3); border-radius: 3px; }

/* ─── Animations ─── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeIn 0.5s ease-out forwards; }

/* ─── Hero ─── */
.hero-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF 0%, #00C9A7 50%, #A855F7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    line-height: 1.2;
    margin-bottom: 8px;
}
.hero-subtitle {
    text-align: center;
    color: #8888aa;
    font-size: 16px;
    margin-bottom: 32px;
}
</style>
"""
