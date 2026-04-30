"""Premium dark editorial styling for Streamlit.

Deep neutral background, paper-like surfaces, amber accent, generous
whitespace, and modern SaaS polish (rounded buttons, card shadows,
trust indicators).
"""

CSS = """
<style>
  /* -------- Fonts -------- */
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --bg: #0e0e10;
    --surface: #16161a;
    --surface-2: #1d1d22;
    --surface-3: #222228;
    --border: #2a2a30;
    --border-strong: #3a3a44;
    --text: #e8e6e1;
    --text-dim: #9b9892;
    --text-faint: #6c6a64;
    --accent: #c89b3c;
    --accent-soft: rgba(200, 155, 60, 0.12);
    --accent-line: rgba(200, 155, 60, 0.35);
    --good: #6db896;
    --good-soft: rgba(109, 184, 150, 0.10);
    --good-line: rgba(109, 184, 150, 0.25);
    --warn: #d49a5b;
    --bad: #c87979;
    --bad-soft: rgba(200, 100, 100, 0.10);
    --bad-line: rgba(200, 100, 100, 0.25);
    --shadow-sm: 0 1px 4px rgba(0,0,0,0.35);
    --shadow-md: 0 3px 12px rgba(0,0,0,0.45);
  }

  html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', system-ui, -apple-system, sans-serif !important;
    color: var(--text);
    background: var(--bg);
  }

  h1, h2, h3, h4 {
    font-family: 'Fraunces', Georgia, serif !important;
    font-weight: 400 !important;
    letter-spacing: -0.01em;
    color: var(--text) !important;
  }
  h1 { font-size: 2.4rem !important; line-height: 1.1; }
  h2 { font-size: 1.6rem !important; }

  code, pre, .stCode {
    font-family: 'JetBrains Mono', monospace !important;
  }

  /* -------- Hide chrome we don't need -------- */
  #MainMenu, footer { visibility: hidden; height: 0; }
  .stDeployButton { display: none; }

  /* -------- App container -------- */
  .block-container {
    padding-top: 2.4rem !important;
    padding-bottom: 4rem !important;
    max-width: 1180px;
  }

  /* -------- Sidebar -------- */
  [data-testid="stSidebar"] {
    background: #0a0a0c;
    border-right: 1px solid var(--border);
  }
  [data-testid="stSidebar"] .block-container { padding-top: 1.4rem !important; }

  /* -------- Brand block -------- */
  .brand {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
  }
  .brand-main {
    display: flex;
    align-items: baseline;
    gap: 0;
  }
  .brand-mark {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 1.75rem;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1;
  }
  .brand-ai {
    color: var(--accent);
    font-size: 1.1rem;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.02em;
    margin-left: 0.1rem;
  }
  .brand-sub {
    font-size: 0.72rem;
    color: var(--text-faint);
    letter-spacing: 0.04em;
    font-family: 'DM Sans', sans-serif;
  }

  /* -------- Status pill -------- */
  .pill {
    display: inline-flex; align-items: center; gap: 0.45rem;
    padding: 0.28rem 0.8rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    font-size: 0.76rem;
    color: var(--text-dim);
    font-family: 'DM Sans', sans-serif;
  }
  .pill .dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--good);
    box-shadow: 0 0 8px var(--good);
  }
  .pill.bad .dot { background: var(--bad); box-shadow: 0 0 8px var(--bad); }

  /* -------- Privacy bar -------- */
  .privacy-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.45rem 0.9rem;
    background: var(--good-soft);
    border: 1px solid var(--good-line);
    border-radius: 8px;
    font-size: 0.73rem;
    color: var(--good);
    letter-spacing: 0.02em;
    margin: 0.6rem 0 1rem 0;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
  }

  /* -------- Sidebar helper text -------- */
  .sidebar-helper {
    font-size: 0.76rem;
    color: var(--text-faint);
    line-height: 1.45;
    margin: 0.3rem 0 0.7rem 0;
    font-family: 'DM Sans', sans-serif;
  }

  /* -------- Cards -------- */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.65rem;
    box-shadow: var(--shadow-sm);
    transition: border-color 160ms ease, transform 160ms ease, box-shadow 160ms ease;
  }
  .card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
  .card-title {
    font-family: 'Fraunces', serif;
    font-size: 1rem;
    margin: 0 0 0.3rem 0;
    color: var(--text);
    line-height: 1.3;
  }
  .card-meta {
    font-size: 0.74rem;
    color: var(--text-faint);
    letter-spacing: 0.03em;
    font-family: 'DM Sans', sans-serif;
  }

  /* -------- Section headings -------- */
  .rule-heading {
    display: flex; align-items: center; gap: 0.8rem;
    margin: 1.8rem 0 1rem 0;
  }
  .rule-heading .label {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.73rem;
    color: var(--accent);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .rule-heading .line {
    flex: 1; height: 1px;
    background: linear-gradient(to right, var(--accent-line), transparent);
  }

  /* -------- Hero -------- */
  .hero {
    padding: 0.6rem 0 1.6rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.8rem;
  }
  .hero h1 {
    margin: 0 0 0.1rem 0 !important;
    font-size: 2.8rem !important;
    background: linear-gradient(135deg, var(--text) 60%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: inline-block;
  }
  .hero-ai-badge {
    display: inline-block;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--accent);
    vertical-align: super;
    margin-left: 0.15rem;
    -webkit-text-fill-color: var(--accent);
  }
  .hero-tagline {
    color: var(--text-dim);
    font-size: 1rem;
    margin: 0.35rem 0 0.9rem 0;
    max-width: 64ch;
    line-height: 1.55;
    font-family: 'DM Sans', sans-serif;
  }
  .hero-trust {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.2rem;
  }
  .trust-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.28rem 0.75rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    font-size: 0.74rem;
    color: var(--text-dim);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    box-shadow: var(--shadow-sm);
  }

  /* -------- Grounded note -------- */
  .grounded-note {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 1rem;
    background: var(--accent-soft);
    border: 1px solid var(--accent-line);
    border-radius: 8px;
    font-size: 0.80rem;
    color: var(--accent);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    margin: 0 0 1.2rem 0;
  }

  /* -------- Get-started empty state -------- */
  .get-started-wrap {
    padding: 0.4rem 0;
  }
  .get-started-header {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    color: var(--text);
    margin: 0 0 0.5rem 0;
    font-weight: 400;
  }
  .get-started-sub {
    color: var(--text-dim);
    font-size: 0.92rem;
    margin: 0 0 0.5rem 0;
    line-height: 1.55;
    max-width: 60ch;
    font-family: 'DM Sans', sans-serif;
  }

  /* -------- Buttons -------- */
  .stButton > button {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 0.48rem 1.1rem;
    box-shadow: var(--shadow-sm);
    transition: all 160ms ease;
  }
  .stButton > button:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-soft);
    box-shadow: 0 0 0 1px var(--accent-line);
  }
  .stButton > button:focus { box-shadow: none !important; }

  .stButton > button[kind="primary"] {
    background: var(--accent);
    color: #16110a;
    border: 1px solid var(--accent);
    font-weight: 600;
  }
  .stButton > button[kind="primary"]:hover {
    background: #d6a94a;
    border-color: #d6a94a;
    color: #16110a;
    box-shadow: 0 2px 8px rgba(200,155,60,0.3);
  }

  /* -------- Tabs -------- */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-dim);
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.92rem;
    padding: 0.75rem 1.1rem;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    transition: color 160ms ease;
  }
  .stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
  }

  /* -------- Inputs -------- */
  .stTextInput input, .stTextArea textarea,
  .stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent-line) !important;
  }
  .stTextInput input::placeholder { color: var(--text-faint) !important; }

  /* -------- Chat bubbles -------- */
  [data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
  }
  [data-testid="stChatMessageContent"] {
    background: var(--surface) !important;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow-sm);
  }
  [data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: var(--surface-2) !important;
    border-color: var(--border-strong);
  }

  /* -------- Chat input -------- */
  [data-testid="stChatInput"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--surface) !important;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent-line) !important;
  }

  /* -------- Source citation chips -------- */
  .src-chip {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.22rem 0.65rem;
    background: var(--accent-soft);
    border: 1px solid var(--accent-line);
    border-radius: 999px;
    color: var(--accent);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.74rem;
    font-weight: 500;
    margin: 0.18rem 0.28rem 0.18rem 0;
  }

  /* -------- File uploader -------- */
  [data-testid="stFileUploader"] section {
    background: var(--surface);
    border: 2px dashed var(--border-strong);
    border-radius: 10px;
    padding: 1.4rem;
    transition: border-color 160ms ease, background 160ms ease;
  }
  [data-testid="stFileUploader"] section:hover {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  [data-testid="stFileUploader"] section p {
    color: var(--text-dim);
    font-size: 0.82rem;
    font-family: 'DM Sans', sans-serif;
  }

  /* -------- Expander -------- */
  [data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: var(--shadow-sm);
  }
  [data-testid="stExpander"] summary {
    color: var(--text-dim);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
  }
  [data-testid="stExpander"] summary:hover { color: var(--accent); }

  /* -------- Stat cards (Workspace) -------- */
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.3rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 160ms ease;
  }
  .stat-card:hover { box-shadow: var(--shadow-md); }
  .stat-card-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-faint);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
  }
  .stat-card-value {
    font-family: 'Fraunces', serif;
    font-size: 2.4rem;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 0.2rem;
  }
  .stat-card-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.74rem;
    color: var(--text-faint);
  }

  /* -------- Danger zone card -------- */
  .danger-card {
    background: var(--bad-soft);
    border: 1px solid var(--bad-line);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-top: 0.5rem;
  }
  .danger-card-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    color: var(--bad);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
  }
  .danger-card-note {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    color: var(--text-faint);
    margin-bottom: 0.8rem;
    line-height: 1.45;
  }

  /* -------- Markdown answer body -------- */
  .answer-body { line-height: 1.70; color: var(--text); }
  .answer-body p { margin: 0 0 0.75rem 0; }
  .answer-body ul, .answer-body ol { padding-left: 1.3rem; margin: 0.3rem 0 0.85rem 0; }
  .answer-body li { margin: 0.25rem 0; }
  .answer-body strong { color: var(--text); font-weight: 600; }
  .answer-body code {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.1rem 0.35rem;
    font-size: 0.88em;
  }

  /* -------- Ornament -------- */
  .ornament {
    text-align: center; color: var(--text-faint);
    font-family: 'Fraunces', serif; font-style: italic;
    font-size: 0.85rem; margin: 1.4rem 0;
    letter-spacing: 0.25em;
  }

  /* -------- Plotly -------- */
  .js-plotly-plot .plotly { background: transparent !important; }

  /* -------- Scrollbars -------- */
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 6px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--accent-line); }

  /* -------- Alert / info overrides -------- */
  [data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
  }

  /* -------- Suggestion chips row -------- */
  .suggestion-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.8rem 0; }
</style>
"""


def inject():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def rule_heading(label: str):
    import streamlit as st
    st.markdown(
        f'<div class="rule-heading"><span class="label">{label}</span>'
        f'<span class="line"></span></div>',
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str):
    import streamlit as st
    st.markdown(
        f'<div class="hero">'
        f'<h1>{title}<span class="hero-ai-badge">AI</span></h1>'
        f'<p class="hero-tagline">{subtitle}</p>'
        f'<div class="hero-trust">'
        f'<span class="trust-badge">🔒 100% On-Device Processing</span>'
        f'<span class="trust-badge">🚫 No Cloud · No Data Leaks</span>'
        f'<span class="trust-badge">⚡ Private Knowledge Base</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def status_pill(ok: bool, message: str):
    import streamlit as st
    cls = "pill" if ok else "pill bad"
    st.markdown(
        f'<div class="{cls}"><span class="dot"></span>{message}</div>',
        unsafe_allow_html=True,
    )


def privacy_bar():
    import streamlit as st
    st.markdown(
        '<div class="privacy-bar">🔒 Running locally &nbsp;·&nbsp; No data leaves your device</div>',
        unsafe_allow_html=True,
    )


def sidebar_helper(text: str):
    import streamlit as st
    st.markdown(f'<div class="sidebar-helper">{text}</div>', unsafe_allow_html=True)


def grounded_note():
    import streamlit as st
    st.markdown(
        '<div class="grounded-note">'
        '📎 Answers are grounded in your documents with source citations.'
        '</div>',
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, sub: str = ""):
    import streamlit as st
    sub_html = f'<div class="stat-card-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-card-label">{label}</div>'
        f'<div class="stat-card-value">{value}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def danger_zone(note: str):
    import streamlit as st
    st.markdown(
        f'<div class="danger-card">'
        f'<div class="danger-card-title">⚠ Danger Zone</div>'
        f'<div class="danger-card-note">{note}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def ornament():
    import streamlit as st
    st.markdown('<div class="ornament">· · ·</div>', unsafe_allow_html=True)
