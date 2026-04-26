import html
import os
from pathlib import Path

import streamlit as st
from openai import OpenAI


def build_chat_context(model_input: dict, prediction: float, status: str) -> str:
    return (
        "Prediction context:\n"
        f"- Predicted Vitamin D: {prediction:.2f} ng/mL\n"
        f"- Status: {status}\n"
        f"- Sun exposure: {model_input['Sun_Exposure_min']:.0f} min/day\n"
        f"- Physical activity: {model_input['Physical_activity_hours_week']:.1f} hrs/week\n"
        f"- Fish intake: {model_input['Fish_intake_week']:.0f}/week\n"
        f"- Dairy intake: {model_input['Dairy_intake_week']:.0f}/week\n"
        f"- Indoor work: {model_input['Indoor_work_hours_day']:.1f} hrs/day\n"
    )


def get_openai_reply(api_key: str, conversation: list[dict], context: str) -> str:
    client = OpenAI(api_key=api_key)
    system_prompt = (
        "You are a helpful Vitamin D health assistant in a Streamlit app. "
        "Explain predictions in simple language, provide practical lifestyle suggestions, "
        "and keep responses concise. Avoid diagnosis claims and remind users this is educational only."
    )

    messages = [{"role": "system", "content": system_prompt + "\n\n" + context}] + conversation
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,
    )
    return response.choices[0].message.content or "I could not generate a response right now."


def map_chat_error(err: Exception) -> str:
    error_text = str(err).lower()

    if "insufficient_quota" in error_text or "exceeded your current quota" in error_text:
        return (
            "Your OpenAI key is valid, but its billing quota is exhausted. "
            "Please add credits or switch to a key with available quota, then try again."
        )

    if "invalid_api_key" in error_text or "incorrect api key" in error_text:
        return "The API key appears invalid. Double-check the key and try again."

    if "rate limit" in error_text or "too many requests" in error_text:
        return "OpenAI rate limit reached. Please wait a moment and retry."

    if "timeout" in error_text:
        return "The request timed out. Please retry in a few seconds."

    return "Chatbot is temporarily unavailable. Please try again later."


def is_quota_error(err: Exception) -> bool:
    error_text = str(err).lower()
    error_code = str(getattr(err, "code", "")).lower()
    status_code = str(getattr(err, "status_code", "")).strip()

    return (
        "insufficient_quota" in error_text
        or "exceeded your current quota" in error_text
        or error_code == "insufficient_quota"
        or (status_code == "429" and "quota" in error_text)
    )


def get_rule_based_reply(user_prompt: str, model_input: dict, prediction: float, status: str) -> str:
    prompt_text = user_prompt.lower()
    suggestions = []

    if model_input["Sun_Exposure_min"] < 20:
        suggestions.append("Aim for 20-30 minutes of safe midday sunlight on most days when possible.")
    if (model_input["Fish_intake_week"] + model_input["Dairy_intake_week"]) < 5:
        suggestions.append("Increase Vitamin D rich foods such as fatty fish, eggs, and fortified dairy.")
    if model_input["Physical_activity_hours_week"] < 3:
        suggestions.append("Add at least 3-5 hours/week of regular physical activity, preferably outdoors.")
    if model_input["Indoor_work_hours_day"] > 8:
        suggestions.append("Break long indoor hours with short daylight breaks to improve natural light exposure.")

    if not suggestions:
        suggestions.append("Your current lifestyle profile looks supportive. Keep a consistent routine and monitor levels periodically.")

    if any(word in prompt_text for word in ["30", "above 30", "sufficient", "improve"]):
        target_message = (
            "To move above 30 ng/mL, focus on daily sunlight consistency plus diet upgrades for 8-12 weeks, "
            "then recheck your Vitamin D level."
        )
    elif any(word in prompt_text for word in ["food", "diet", "eat"]):
        target_message = "Diet focus: include fatty fish 2-3 times/week and fortified dairy or alternatives most days."
    elif any(word in prompt_text for word in ["sun", "sunlight", "exposure"]):
        target_message = "Sunlight focus: increase safe daytime exposure gradually, avoiding sunburn."
    else:
        target_message = "Based on your profile, these are the most practical next steps to improve your Vitamin D status."

    lines = [
        f"Current prediction: {prediction:.2f} ng/mL ({status}).",
        target_message,
        "",
        "Recommended actions:",
    ]
    lines.extend([f"- {tip}" for tip in suggestions])
    lines.append("")
    lines.append("Educational guidance only. Please consult a clinician for diagnosis or supplements.")
    return "\n".join(lines)


def get_secret_or_default(secret_key: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(secret_key, default))
    except Exception:
        return default


def _read_key_from_env_file(env_file: Path, key_name: str) -> str:
    if not env_file.exists():
        return ""

    try:
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue

            candidate_key, candidate_value = line.split("=", 1)
            if candidate_key.strip() != key_name:
                continue

            value = candidate_value.strip().strip("\"'")
            return value
    except Exception:
        return ""

    return ""


def get_api_key() -> str:
    env_value = os.getenv("OPENAI_API_KEY", "").strip()
    if env_value:
        return env_value

    secrets_value = get_secret_or_default("OPENAI_API_KEY", "").strip()
    if secrets_value:
        return secrets_value

    candidate_files = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]

    for candidate in candidate_files:
        file_value = _read_key_from_env_file(candidate, "OPENAI_API_KEY").strip()
        if file_value:
            return file_value

    return ""


def init_chat_state() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": "Hi. I am your Vitamin D assistant. Ask me about your prediction, status, or how to improve your levels.",
            }
        ]


def render_chat_widget(model_input: dict, prediction: float, status: str) -> None:
    api_key = get_api_key()

    st.markdown('<div class="chat-fixed-anchor"></div>', unsafe_allow_html=True)

    with st.popover("💬", help="Open chatbot widget"):
        st.markdown(
            '<div class="chat-widget-caption">Context window: answers are based on your current prediction panel.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="chat-context-chip">Prediction context: {prediction:.2f} ng/mL ({status})</div>',
            unsafe_allow_html=True,
        )

        if st.button("Clear Chat", use_container_width=True, key="clear_chat_widget"):
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": "Chat cleared. Ask a new question about your Vitamin D report.",
                }
            ]

        chat_rows = []
        for message in st.session_state["chat_messages"][-8:]:
            role_name = "You" if message["role"] == "user" else "Assistant"
            role_class = "chat-msg-user" if message["role"] == "user" else "chat-msg-assistant"
            safe_content = html.escape(message["content"]).replace("\n", "<br>")
            chat_rows.append(
                f'<div class="chat-msg {role_class}"><div class="chat-role">{role_name}</div>{safe_content}</div>'
            )

        chat_html = "".join(chat_rows) if chat_rows else '<div class="chat-hint">No messages yet.</div>'
        st.markdown(f'<div class="chat-log">{chat_html}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="chat-hint">Tip: Ask short, specific questions for better suggestions.</div>',
            unsafe_allow_html=True,
        )

        with st.form("chat_widget_form", clear_on_submit=True):
            user_prompt = st.text_input(
                "Ask a question",
                placeholder="Example: How can I move from insufficient to sufficient?",
                label_visibility="collapsed",
            )
            send_clicked = st.form_submit_button("Send")

        if send_clicked and user_prompt.strip():
            prompt_text = user_prompt.strip()
            st.session_state["chat_messages"].append({"role": "user", "content": prompt_text})

            if not api_key:
                bot_reply = (
                    "OpenAI API key not found. Switching to offline guidance mode.\n\n"
                    + get_rule_based_reply(prompt_text, model_input, prediction, status)
                )
            else:
                try:
                    with st.spinner("Thinking..."):
                        context = build_chat_context(model_input, prediction, status)
                        conversation = st.session_state["chat_messages"][-10:]
                        bot_reply = get_openai_reply(api_key, conversation, context)
                except Exception as err:
                    if is_quota_error(err):
                        bot_reply = (
                            "OpenAI quota is exhausted. Switching to logic-based guidance mode.\n\n"
                            + get_rule_based_reply(prompt_text, model_input, prediction, status)
                        )
                    else:
                        bot_reply = (
                            map_chat_error(err)
                            + "\n\nUsing offline guidance for now:\n\n"
                            + get_rule_based_reply(prompt_text, model_input, prediction, status)
                        )

            st.session_state["chat_messages"].append({"role": "assistant", "content": bot_reply})
            st.rerun()
