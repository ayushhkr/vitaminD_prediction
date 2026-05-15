import streamlit as st

APP_CSS = """
<style>
:root {
    --bg: #f7f7fb;
    --panel: #ffffff;
    --border: #e7e8ef;
    --text: #111827;
    --muted: #6b7280;
    --primary: #2563eb;
    --primary-strong: #1d4ed8;
}
.stApp {
    background: radial-gradient(circle at top right, #eef4ff 0%, #f7f7fb 45%, #f7f7fb 100%);
    color: var(--text);
}
.block-container {
    max-width: 1180px;
    padding-top: 0.15rem;
    padding-bottom: 1rem;
}
.block-container > div[data-testid="stVerticalBlock"] {
    gap: 0.45rem;
}
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stToolbar"] {
    top: 0.4rem;
    right: 0.75rem;
}
.block-container h1 {
    margin-top: 0;
    margin-bottom: 0.35rem;
}
.hero-card {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at top right, rgba(37, 99, 235, 0.18), transparent 34%),
        linear-gradient(135deg, #ffffff 0%, #f7fbff 52%, #eef4ff 100%);
    border: 1px solid rgba(191, 219, 254, 0.9);
    border-radius: 22px;
    padding: 1rem 1.15rem 1rem 1.15rem;
    box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
    margin-bottom: 0.5rem;
}
.hero-card::after {
    content: "";
    position: absolute;
    inset: auto -40px -60px auto;
    width: 180px;
    height: 180px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(147, 197, 253, 0.28) 0%, rgba(147, 197, 253, 0) 72%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #1d4ed8;
    margin-bottom: 0.35rem;
}
.hero-card p {
    margin: 0;
    max-width: 760px;
    color: #475569;
    font-size: 0.96rem;
    line-height: 1.5;
}
.mode-switch-label {
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.4rem;
}
div[data-testid="stRadio"] {
    margin-top: -0.05rem;
    margin-bottom: 0.3rem;
}
div[data-testid="stRadio"] > div {
    width: 100%;
}
div[data-testid="stRadio"] [role="radiogroup"] {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.45rem;
    padding: 0.35rem;
    background: linear-gradient(180deg, #eef4ff 0%, #f8fbff 100%);
    border: 1px solid #dbeafe;
    border-radius: 18px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}
div[data-testid="stRadio"] [role="radiogroup"] label {
    margin: 0;
    min-height: 3rem;
    border-radius: 14px;
    border: 1px solid transparent;
    background: rgba(255, 255, 255, 0.72);
    padding: 0.65rem 0.9rem;
    transition: all 0.18s ease;
}
div[data-testid="stRadio"] [role="radiogroup"] label:hover {
    border-color: #bfdbfe;
    background: rgba(255, 255, 255, 0.96);
}
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    border-color: #1d4ed8;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.22);
}
div[data-testid="stRadio"] [role="radiogroup"] label p {
    margin: 0;
    color: #334155;
    font-weight: 700;
    font-size: 0.93rem;
}
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p {
    color: #ffffff;
}
div[data-testid="stRadio"] [role="radiogroup"] label > div:first-child {
    display: none;
}
[data-testid="stSidebar"] {
    border-right: 1px solid #e5e7eb;
    background: linear-gradient(180deg, #f8fbff 0%, #f7f7fb 100%);
}
[data-testid="stSidebar"] .block-container {
    padding-top: 0.45rem;
    padding-left: 0.75rem;
    padding-right: 0.75rem;
}
[data-testid="stSidebar"] .section-title {
    margin-top: 0.25rem;
    margin-bottom: 0.45rem;
}
[data-testid="stSidebar"] .section-gap {
    height: 0.42rem;
}
[data-testid="stSidebar"] [data-testid="stSlider"] {
    padding-top: 0.14rem;
    padding-bottom: 0.14rem;
}
[data-testid="stSidebar"] h3 {
    margin-bottom: 0.2rem;
}
.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.9rem 1rem 1rem 1rem;
    box-shadow: 0 16px 34px rgba(17, 24, 39, 0.07);
    margin-bottom: 0.45rem;
}
.section-title {
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #1f2937;
    margin: 0.18rem 0 0.5rem 0;
}
.section-gap {
    height: 0.38rem;
}
.result-value {
    font-size: 2.65rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.15;
    margin-top: 0.2rem;
    margin-bottom: 0.18rem;
}
.status-chip {
    display: inline-block;
    padding: 0.35rem 0.72rem;
    border-radius: 999px;
    border: 1px solid #e5e7eb;
    background: #f8fafc;
    color: #334155;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 0.42rem;
}
.status-deficient {
    border-color: #fecaca;
    background: #fef2f2;
    color: #b91c1c;
}
.status-insufficient {
    border-color: #fde68a;
    background: #fffbeb;
    color: #b45309;
}
.status-sufficient {
    border-color: #bbf7d0;
    background: #f0fdf4;
    color: #166534;
}
.compact-list {
    font-size: 0.84rem;
    line-height: 1.35;
    color: #1f2937;
}
[data-testid="stCaptionContainer"] {
    margin-top: -0.1rem;
    color: #6b7280;
}
[data-testid="stMarkdownContainer"] ul {
    margin-top: 0.18rem;
    margin-bottom: 0.3rem;
    padding-left: 1.1rem;
}
[data-testid="stMarkdownContainer"] li {
    font-size: 0.92rem;
    line-height: 1.45;
    margin-bottom: 0.22rem;
    color: #1f2937;
}
.mode-label {
    color: var(--muted);
    font-size: 0.92rem;
    margin-top: 0.05rem;
    margin-bottom: 0.55rem;
}
.stButton > button {
    min-height: 3rem;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
    border: 1px solid var(--primary-strong);
    color: #ffffff;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.2);
}
.stButton > button:hover {
    filter: brightness(1.03);
}
.stButton > button:focus-visible {
    outline: 2px solid #93c5fd;
    outline-offset: 2px;
}
[data-testid="stSlider"] {
    padding-top: 0.08rem;
    padding-bottom: 0.08rem;
}
[data-testid="stNumberInput"] {
    margin-bottom: 0.05rem;
}
[data-testid="stMetric"] {
    background: #f8faff;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.7rem;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}
.chat-widget-caption {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 0.35rem;
    line-height: 1.35;
}
.chat-context-chip {
    font-size: 0.76rem;
    color: #1e3a8a;
    background: #eff6ff;
    border: 1px solid #dbeafe;
    border-radius: 10px;
    padding: 0.4rem 0.55rem;
    margin-bottom: 0.45rem;
}
.chat-log {
    max-height: 250px;
    overflow-y: auto;
    background: #f8faff;
    border: 1px solid #e7e8ef;
    border-radius: 10px;
    padding: 0.45rem;
    margin: 0.35rem 0 0.55rem 0;
}
.chat-msg {
    font-size: 0.79rem;
    line-height: 1.4;
    padding: 0.4rem 0.5rem;
    border-radius: 9px;
    margin-bottom: 0.3rem;
    border: 1px solid transparent;
}
.chat-msg-user {
    background: #eaf2ff;
    border-color: #d3e4ff;
    color: #1f2937;
}
.chat-msg-assistant {
    background: #ffffff;
    border-color: #e5e7eb;
    color: #111827;
}
.chat-role {
    font-size: 0.69rem;
    font-weight: 700;
    color: #4b5563;
    letter-spacing: 0.01em;
    margin-bottom: 0.12rem;
    text-transform: uppercase;
}
.chat-hint {
    font-size: 0.72rem;
    color: #6b7280;
    margin-top: -0.25rem;
    margin-bottom: 0.35rem;
}
.chat-fixed-anchor {
    display: none;
}
.chat-fixed-anchor + div[data-testid="stElementContainer"] {
    position: fixed;
    right: 1.05rem;
    bottom: 1.1rem;
    z-index: 9999;
    margin: 0;
    width: auto;
}
.chat-fixed-anchor + div[data-testid="stElementContainer"] [data-testid="stPopover"] > button {
    width: 3.2rem;
    height: 3.2rem;
    min-height: 3.2rem;
    border-radius: 999px;
    padding: 0;
    font-size: 1.15rem;
    box-shadow: 0 10px 24px rgba(29, 78, 216, 0.32);
}
.interp-card {
    background: #f9fbff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.5rem 0.6rem;
    margin-bottom: 0.35rem;
}
.interp-card-title {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #4b5563;
    margin-bottom: 0.14rem;
    font-weight: 700;
}
.interp-card-value {
    font-size: 0.86rem;
    color: #111827;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 0.1rem;
}
.interp-card-delta {
    font-size: 0.72rem;
    color: #1d4ed8;
    font-weight: 600;
    line-height: 1.2;
}
@media (max-width: 1024px) {
    .block-container {
        max-width: 100%;
        padding-left: 0.85rem;
        padding-right: 0.85rem;
    }
    .panel {
        padding: 0.9rem;
        border-radius: 14px;
    }
    .hero-card {
        border-radius: 18px;
        padding: 0.95rem 1rem;
    }
    .result-value {
        font-size: 2.25rem;
    }
}
@media (max-width: 900px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column;
        gap: 0.7rem;
    }
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    .stButton > button {
        min-height: 2.7rem;
        font-size: 0.95rem;
    }
    div[data-testid="stRadio"] [role="radiogroup"] {
        grid-template-columns: 1fr;
    }
    .chat-log {
        max-height: 210px;
    }
}
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        border-right: none;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 0.35rem;
        padding-left: 0.6rem;
        padding-right: 0.6rem;
    }
    [data-testid="stSidebar"] .panel {
        box-shadow: none;
    }
    .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    .hero-card {
        padding: 0.85rem 0.9rem;
    }
    .mode-label {
        font-size: 0.86rem;
    }
    .result-value {
        font-size: 2.1rem;
    }
    .status-chip {
        font-size: 0.8rem;
        padding: 0.28rem 0.58rem;
    }
    .chat-msg {
        font-size: 0.75rem;
    }
    .chat-role {
        font-size: 0.64rem;
    }
}
@media (max-width: 480px) {
    .block-container {
        padding-left: 0.55rem;
        padding-right: 0.55rem;
        padding-top: 0.3rem;
    }
    [data-testid="stSidebar"] .block-container {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    .panel {
        padding: 0.72rem;
        border-radius: 12px;
    }
    .result-value {
        font-size: 1.75rem;
    }
    .status-chip {
        font-size: 0.85rem;
        padding: 0.3rem 0.58rem;
    }
    .section-title {
        font-size: 0.84rem;
    }
    .hero-card p {
        font-size: 0.88rem;
    }
    .chat-widget-caption,
    .chat-context-chip,
    .chat-hint {
        font-size: 0.7rem;
    }
    .chat-log {
        max-height: 180px;
    }
    .chat-fixed-anchor + div[data-testid="stElementContainer"] {
        right: 0.7rem;
        bottom: 0.75rem;
    }
    .chat-fixed-anchor + div[data-testid="stElementContainer"] [data-testid="stPopover"] > button {
        width: 2.9rem;
        height: 2.9rem;
        min-height: 2.9rem;
    }
}
</style>
"""


def apply_global_styles() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
