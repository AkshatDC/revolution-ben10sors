import streamlit as st
import streamlit.components.v1 as components
import os
import httpx
import requests
from dotenv import load_dotenv
from db_utils import init_db, add_message, fetch_messages, export_community_json, clear_community, get_user_profile
from kb_utils import _kb_store, init_kb, add_to_kb, search_kb, get_kb_size
from config import DB_PATH
from opportunity_matcher import (
    add_opportunity, get_opportunities, match_opportunities,
    update_user_profile, get_user_profile as get_profile
)
from template_assistant import (
    get_available_templates, get_template, save_template_instance,
    get_user_templates, generate_field_suggestion_sync, export_template_to_markdown
)
from analytics import (
    get_community_stats, get_top_contributors, get_engagement_trends,
    get_user_engagement_score, generate_analytics_report
)
from multi_tenant import (
    create_organization, get_organization, get_user_organizations,
    add_member_to_organization, create_invite_code, use_invite_code
)
import time
import html
import uuid
import json

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
AUTO_SUMMARY_THRESHOLD = int(os.getenv("AUTO_SUMMARY_THRESHOLD", 5))
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 2))
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
WS_URL = BACKEND_URL.replace("http", "ws")

# -----------------------------
# Initialize SQLite DB
# -----------------------------
init_db()

# -----------------------------
# Ensure user profile is set
# -----------------------------
if "user_name" not in st.session_state:
    st.session_state.user_name = st.text_input("Enter your name to join the chat:", key="username_input")
    if not st.session_state.user_name:
        st.stop()
user_name = st.session_state.user_name.strip() or "Anonymous"

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
user_id = st.session_state.user_id

# -----------------------------
# Sidebar: Communities + Admin
# -----------------------------
def sidebar():
    if "communities" not in st.session_state:
        st.session_state.communities = ["General", "Hackathon", "AI Enthusiasts"]
    st.sidebar.header("Communities")
    community = st.sidebar.selectbox("Select Community", st.session_state.communities)
    st.sidebar.markdown("---")
    if st.sidebar.button("Export community JSON"):
        path = f"data/{community.replace(' ', '_')}_export_{int(time.time())}.json"
        export_community_json(community, path)
        st.sidebar.success(f"Exported to `{path}`")
    if st.sidebar.button("Clear community (danger)"):
        clear_community(community)
        st.sidebar.warning("Cleared chat history for this community. Refresh to see changes.")
    return community

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="AI Community Platform", layout="wide", page_icon="🚀")

# Add navigation tabs
tab_selection = st.sidebar.radio(
    "Navigation",
    ["💬 Chat", "🎯 Opportunities", "📝 Templates", "📊 Analytics", "👤 Profile", "🏢 Organizations"],
    key="main_nav"
)

community = sidebar()

# -----------------------------
# Load KB once per session
# -----------------------------
if "kb_loaded" not in st.session_state or st.session_state.get("kb_community") != community:
    st.session_state.kb = init_kb(community)
    st.session_state.kb_loaded = True
    st.session_state.kb_community = community

# -----------------------------
# Gemini Summarization
# -----------------------------
def summarize_with_gemini(texts):
    if not GEMINI_API_KEY:
        return "Error: Gemini API key not found in .env"
    max_messages = 50
    truncated = texts[-max_messages:]
    prompt = "Summarize the following chat conversation with short bullet points and key actions:\n\n"
    prompt += "\n".join(truncated)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    try:
        resp = httpx.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error: {str(e)}"

# -----------------------------
# Main Content Area - Route based on tab selection
# -----------------------------

if tab_selection == "💬 Chat":
    # -----------------------------
    # CHAT PAGE (Original functionality)
    # -----------------------------
    st.title(f"💬 Community Chat — {community}")
    col1, col2 = st.columns([3, 1])
    
    # -----------------------------
    # Left Column: Chat Input + History
    # -----------------------------
    with col1:
    with st.form(key=f"form_{community}", clear_on_submit=True):
        user_input = st.text_input("Type your message here:", placeholder="Say something to the community...")
        submit = st.form_submit_button("Send")

    if submit and user_input.strip():
        user_id = get_user_profile(user_name)
        add_message(community, username=user_name, content=user_input.strip(), role="user")

        # Search KB immediately and inject into chat
        kb_results = search_kb(community, user_input.strip(), top_k=3)
        if kb_results:
            summary_text = "\n".join([f"- {r['doc']['content']}" for r in kb_results])
            add_message(community, username="KB-Bot", content=f"💡 KB Results:\n{summary_text}", role="system")

    # Display chat history with modern UI
    st.subheader("Chat History")
    rows = fetch_messages(community, limit=1000)
    for r in rows[-200:]:
        role = r.get("role", "User").capitalize()
        content = r.get("content", "")
        if content:
            if role.lower() == "user":
                st.markdown(f"<div style='background:#0b6efd;color:white;padding:8px;border-radius:12px;margin:4px 0'>{content}</div>", unsafe_allow_html=True)
            elif role.lower() == "system":
                st.markdown(f"<div style='background:#f1f3f6;color:#333;padding:8px;border-radius:12px;margin:4px 0'>{content}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#d4edda;color:#155724;padding:8px;border-radius:12px;margin:4px 0'>{content}</div>", unsafe_allow_html=True)

    # Auto-summarize after threshold
    user_count = len([r for r in rows if r.get("role","").lower() == user_name.lower()])
    if "last_auto_summary_count" not in st.session_state:
        st.session_state.last_auto_summary_count = {c: 0 for c in st.session_state.communities}
    last_count = st.session_state.last_auto_summary_count.get(community, 0)
    if user_count >= AUTO_SUMMARY_THRESHOLD and (user_count - last_count) >= AUTO_SUMMARY_THRESHOLD:
        all_texts = [f"{r.get('role', 'User').capitalize()}: {r.get('content','')}" for r in rows]
        with st.spinner("Auto-summarizing recent chat and adding to KB..."):
            summary = summarize_with_gemini(all_texts)
            add_to_kb(community, summary)
            add_message(community, username="KB-Summary", content=summary, role="system")
        st.session_state.last_auto_summary_count[community] = user_count

# -----------------------------
# Right Column: KB + Admin Tools
# -----------------------------
with col2:
    st.subheader("Admin Tools & KB")

    # Manual summary
    if st.button("Summarize & Add to KB (manual)"):
        rows2 = fetch_messages(community, limit=1000)
        if rows2:
            all_texts = [f"{r.get('role','User').capitalize()}: {r.get('content','')}" for r in rows2 if r.get('content')]
            with st.spinner("Generating summary..."):
                summary = summarize_with_gemini(all_texts)
            add_to_kb(community, summary)
            add_message(community, username="KB-Summary", content=summary, role="system")
            st.success("Manual summary added to KB.")
            st.write(summary)

    # Admin Tools
    st.markdown("---")
    st.subheader("Admin")
    if st.button("Show KB size"):
        size = get_kb_size(community)
        st.info(f"KB documents: {size}")
    if st.button("Show recent messages"):
        for r in rows[-50:]:
            st.write(f"{r.get('id')} | {r.get('role','User').capitalize()}: {r.get('content','')[:200]}")

# -----------------------------
# Real-time WebSocket chat
# -----------------------------
escaped_community = html.escape(community)
html_code = f"""
<div id="chat" style="height:600px; overflow:auto; border:1px solid #ddd; padding:10px; font-family: Arial;"></div>
<script>
(function(){{
    const chatDiv = document.getElementById("chat");
    const ws = new WebSocket("{WS_URL}/ws/{escaped_community}");
    ws.onopen = function() {{
        const p = document.createElement("div");
        p.innerHTML = "<i>Connected to realtime backend</i>";
        chatDiv.appendChild(p);
    }};
    function appendMessage(obj) {{
        const el = document.createElement("div");
        el.style.marginBottom = "8px";
        let role = obj.role || "user";
        let content = obj.content || "";
        content = content.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        if(role.toLowerCase() === "user"){{
            el.innerHTML = "<b style='color:#0b6efd'>User:</b> " + content;
            el.style.background = "#0b6efd";
            el.style.color = "white";
            el.style.padding = "6px";
            el.style.borderRadius = "12px";
        }} else if(role.toLowerCase() === "system"){{
            el.innerHTML = "<b style='color:#6c757d'>System:</b> " + content;
            el.style.background = "#f1f3f6";
            el.style.color = "#333";
            el.style.padding = "6px";
            el.style.borderRadius = "12px";
        }} else {{
            el.innerHTML = "<b style='color:green'>" + role + ":</b> " + content;
            el.style.background = "#d4edda";
            el.style.color = "#155724";
            el.style.padding = "6px";
            el.style.borderRadius = "12px";
        }}
        chatDiv.appendChild(el);
        chatDiv.scrollTop = chatDiv.scrollHeight;
    }}
    ws.onmessage = function(evt){{
        try {{
            const obj = JSON.parse(evt.data);
            appendMessage(obj);
        }} catch(e){{
            console.error("parse error", e);
        }}
    }};
    ws.onclose = function(){{
        const p = document.createElement("div");
        p.innerHTML = "<i>Disconnected</i>";
        chatDiv.appendChild(p);
    }};
    setInterval(function(){{
        if(ws.readyState === WebSocket.OPEN){{
            try {{ ws.send("ping"); }} catch(e){{}}
        }}
    }}, 20000);
}})();
</script>
"""
st.markdown(html_code, unsafe_allow_html=True)
