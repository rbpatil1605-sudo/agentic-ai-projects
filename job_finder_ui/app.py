# job_finder_ui/app.py
# Streamlit chatbot UI for Job Finder Agent on Cloud Run

import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv
import google.auth
import google.auth.transport.requests

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
AGENT_URL   = os.getenv("AGENT_URL", "https://job-finder-agent-890743251258.us-central1.run.app")
APP_NAME    = os.getenv("APP_NAME", "job_finder_agent")

def get_token():
    try:
        credentials, _ = google.auth.default()
        credentials.refresh(google.auth.transport.requests.Request())
        return credentials.token
    except Exception as e:
        st.error(f"Auth error: {e}. Run: gcloud auth application-default login")
        return ""

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
    }

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Finder Agent",
    page_icon="💼",
    layout="centered",
)

st.markdown("""
    <style>
        .stChatMessage { border-radius: 12px; }
        .main { max-width: 800px; margin: auto; }
        h1 { font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Job Finder Agent")
st.caption("Powered by Google ADK · Ask me to find jobs for any role or location")

# ── Session state ─────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:6]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_created" not in st.session_state:
    st.session_state.session_created = False

# ── Helper: create session ────────────────────────────────────────────────────
def create_session():
    url = f"{AGENT_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{st.session_state.session_id}"
    try:
        resp = requests.post(url, headers=get_headers(), json={}, timeout=15)
        return resp.status_code in (200, 201)
    except Exception as e:
        st.error(f"Could not connect to agent: {e}")
        return False

# ── Helper: send message ──────────────────────────────────────────────────────
def send_message(user_text: str) -> str:
    payload = {
        "app_name": APP_NAME,
        "user_id": st.session_state.user_id,
        "session_id": st.session_state.session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": user_text}],
        },
        "streaming": False,
    }
    try:
        resp = requests.post(
            f"{AGENT_URL}/run_sse",
            headers=get_headers(),
            json=payload,
            timeout=120,
        )

        if resp.status_code != 200:
            return f"⚠️ Agent error {resp.status_code}: {resp.text}"

        # SSE response — each line starts with "data: "
        final_text = ""
        for line in resp.text.splitlines():
            if line.startswith("data:"):
                import json
                raw = line[5:].strip()
                if not raw or raw == "[DONE]":
                    continue
                try:
                    event = json.loads(raw)
                    # Extract text from model response parts
                    parts = (
                        event.get("content", {}).get("parts", [])
                    )
                    for part in parts:
                        if part.get("text"):
                            final_text = part["text"]  # keep last one
                except json.JSONDecodeError:
                    continue

        return final_text if final_text else "⚠️ No response from agent. Try again."

    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. The agent is still processing — please try again."
    except Exception as e:
        return f"⚠️ Error: {e}"

# ── Create session on first load ──────────────────────────────────────────────
if not st.session_state.session_created:
    with st.spinner("Connecting to Job Finder Agent..."):
        if create_session():
            st.session_state.session_created = True
        else:
            st.error("Failed to create session. Check your AGENT_URL and AUTH_TOKEN in .env")
            st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔧 Session Info")
    st.code(f"Session: {st.session_state.session_id}")
    st.code(f"User:    {st.session_state.user_id}")

    st.markdown("---")
    st.markdown("### 💡 Try asking")
    examples = [
        "Find Python developer jobs in Mumbai",
        "Show me remote data scientist roles",
        "Find entry level jobs in finance",
        "What are the top companies hiring for AI roles?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.prefill = ex

    st.markdown("---")
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.session_created = False
        st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
# Handle sidebar button prefill
prefill_text = st.session_state.pop("prefill", "")

user_input = st.chat_input("Ask me to find jobs... e.g. 'Find React developer jobs in Bangalore'")

# Use prefill if button was clicked
if prefill_text:
    user_input = prefill_text

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching jobs across the web... this may take 30-60 seconds"):
            reply = send_message(user_input)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
