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
    padding-top: 0.65rem;
    padding-bottom: 1.05rem;
}
.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 0.82rem 0.9rem 0.9rem 0.9rem;
    box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
    margin-bottom: 0.55rem;
}
.section-title {
    font-size: 0.92rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #374151;
    text-transform: uppercase;
    margin: 0.4rem 0 0.5rem 0;
}
.result-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.15;
    margin-top: 0.2rem;
    margin-bottom: 0.22rem;
}
.status-chip {
    display: inline-block;
    padding: 0.32rem 0.68rem;
    border-radius: 999px;
    border: 1px solid #dbe6ff;
    background: #eff6ff;
    color: #1e40af;
    font-weight: 600;
    font-size: 0.88rem;
    margin-bottom: 0.42rem;
}
.compact-list {
    font-size: 0.84rem;
    line-height: 1.35;
    color: #1f2937;
}
.mode-label {
    color: var(--muted);
    font-size: 0.92rem;
    margin-top: -0.2rem;
    margin-bottom: 0.6rem;
}
.stButton > button {
    min-height: 3rem;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
    border: 1px solid var(--primary-strong);
    color: #ffffff;
    font-weight: 700;
    font-size: 1rem;
}
.stButton > button:hover {
    filter: brightness(1.03);
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
    .result-value {
        font-size: 1.95rem;
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
    .chat-log {
        max-height: 210px;
    }
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    .mode-label {
        font-size: 0.86rem;
    }
    .result-value {
        font-size: 1.75rem;
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
        padding-top: 0.7rem;
    }
    .panel {
        padding: 0.72rem;
        border-radius: 12px;
    }
    .section-title {
        font-size: 0.84rem;
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
