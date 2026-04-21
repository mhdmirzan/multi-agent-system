import streamlit as st
import time
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

st.set_page_config(
    page_title="Agent Orchestra",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
    color: #0D0D0D;
}

.stApp {
    background: #FFFFFF;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6E6E80;
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'Inter', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 600;
    line-height: 1.1;
    letter-spacing: -0.02em;
    color: #0D0D0D;
    margin: 0 0 1rem;
}
.hero h1 span.text-green {
    color: #10A37F;
}
.hero h1 span.text-navy {
    color: #2D3748;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 400;
    color: #6E6E80;
    max-width: 520px;
    margin: 0 auto;
    text-align: center;
    line-height: 1.65;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: rgba(0,0,0,0.1);
    margin: 2rem 0;
}

/* ── Input card ── */
.input-card {
    background: #FFFFFF;
    border: 1px solid rgba(0,0,0,0.1);
    box-shadow: 0 0 15px rgba(0,0,0,0.03);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.2) !important;
    border-radius: 8px !important;
    color: #0D0D0D !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #10A37F !important;
    box-shadow: 0 0 0 1px #10A37F !important;
}
.stTextInput > label {
    font-size: 0.8rem !important;
    color: #6E6E80 !important;
    font-weight: 500 !important;
}

/* ── Button ── */
.stButton > button, .stDownloadButton > button {
    background: #10A37F !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: opacity 0.15s, background 0.15s !important;
    width: 100%;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #1A7F64 !important;
}
.stButton > button:active, .stDownloadButton > button:active {
    opacity: 0.8 !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: #FFFFFF;
    border: 1px solid rgba(0,0,0,0.1);
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: background 0.3s;
}
.step-card.active {
    background: #F7F7F8;
    border-color: rgba(16,163,127,0.3);
}
.step-card.done {
    background: #FFFFFF;
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 8px 0 0 8px;
    background: transparent;
    transition: background 0.3s;
}
.step-card.active::before { background: #10A37F; }
.step-card.done::before   { background: #8E8EA0; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-size: 0.8rem;
    font-weight: 500;
    color: #6E6E80;
}
.step-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #0D0D0D;
}
.step-status {
    margin-left: auto;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    font-weight: 500;
}
.status-waiting  { color: #8E8EA0; }
.status-running  { color: #10A37F; }
.status-done     { color: #6E6E80; }

/* ── Result panels ── */
.result-panel {
    background: #F7F7F8;
    border: 1px solid rgba(16,163,127,0.15);
    border-radius: 12px;
    padding: 1.2rem;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}
.result-panel-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #10A37F;
    margin-bottom: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(16,163,127,0.15);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.4;
    color: #2D2D2D;
    white-space: pre-wrap;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: #FFFFFF;
    border: 1px solid rgba(16,163,127,0.25);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
    border-radius: 12px;
    padding: 3rem;
    margin-top: 1rem;
}
.feedback-panel {
    background: #F0FDF8;
    border: 1px solid rgba(16,163,127,0.2);
    border-radius: 12px;
    padding: 2.5rem;
    margin-top: 1rem;
}
.panel-label {
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.green {
    color: #10A37F;
    border-bottom: 1px solid rgba(16,163,127,0.2);
}
.panel-label.dark {
    color: #0D0D0D;
    border-bottom: 1px solid rgba(0,0,0,0.1);
}

/* ── Progress text ── */
.stSpinner > div { color: #10A37F !important; }

/* ── Expander ── */
details summary {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #0D0D0D !important;
    cursor: pointer;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Inter', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #0D0D0D;
    margin: 2rem 0 1rem;
}
.theme-heading {
    font-family: 'Inter', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #10A37F;
    margin: 2.5rem 0 1.5rem;
    border-bottom: 2px solid rgba(16,163,127,0.2);
    padding-bottom: 0.5rem;
}

/* ── Toast-style notice ── */
.notice {
    font-size: 0.75rem;
    color: #8E8EA0;
    text-align: center;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.85rem;color:#8E8EA0;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1><span class="text-navy">Agent</span><span class="text-green">Orchestra</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5.5, 0.75, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span style="font-size:0.75rem;color:#8E8EA0;letter-spacing:0.05em;margin-top:0.25rem;">TRY →</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f"""
        <span style="
            background: rgba(255,255,255,0.05);
            border:1px solid rgba(255,255,255,0.1);
            border-radius:6px;
            padding:0.35rem 0.8rem;
            font-size:0.9rem;
            color:#9c96aa;
            cursor:default;
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    pipeline_container = st.empty()

    def render_pipeline():
        with pipeline_container.container():
            r = st.session_state.results
            done = st.session_state.done

            def s(step):
                if not r and not st.session_state.running:
                    return "waiting"
                steps = ["search", "reader", "writer", "critic"]
                if step in r:
                    return "done"
                if st.session_state.running:
                    for k in steps:
                        if k not in r:
                            return "running" if k == step else "waiting"
                return "waiting"

            step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
            step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
            step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
            step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")

    # Initial render
    render_pipeline()


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("🔍  Search Agent is working…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
        render_pipeline()

    # ── Step 2: Reader ──
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)
        render_pipeline()

    # ── Step 3: Writer ──
    with st.spinner("✍️  Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)
        render_pipeline()

    # ── Step 4: Critic ──
    with st.spinner("🧐  Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)
        render_pipeline()

    st.session_state.running = False
    st.session_state.done = True
    render_pipeline()
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Final report
    if "writer" in r:
        st.markdown('<div class="theme-heading">📝 Final Research Report</div>', unsafe_allow_html=True)
        st.markdown(r["writer"])   # render markdown natively

        st.download_button(
            label="⬇ Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Search & Reader logic placed below
    if "search" in r or "reader" in r:
        st.markdown('<div class="theme-heading">Results</div>', unsafe_allow_html=True)

        # Raw outputs in expanders
        if "search" in r:
            with st.expander("🔍 Search Results (raw)", expanded=False):
                st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                            f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

        if "reader" in r:
            with st.expander("📄 Scraped Content (raw)", expanded=False):
                st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                            f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Critic feedback
    if "critic" in r:
        st.markdown('<div class="theme-heading">🧐 Critic Feedback</div>', unsafe_allow_html=True)
        st.markdown(r["critic"])


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    Agent Orchestra · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)