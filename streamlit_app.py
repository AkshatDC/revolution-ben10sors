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
import firebase_admin
from firebase_admin import db as firebase_db
from auth_ui import require_authentication, get_current_user, get_username, get_auth_headers
from revolution_design_system import get_revolution_css
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
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
WS_URL = BACKEND_URL.replace("http", "ws")

# -----------------------------
# Initialize Firebase
# -----------------------------
try:
    from firebase_admin import credentials
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase-service-key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://revolution-7a48d-default-rtdb.firebaseio.com'
        })
except Exception as e:
    print(f"Firebase initialization: {e}")

# -----------------------------
# Initialize SQLite DB
# -----------------------------
init_db()

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="REVOLUTION - Community Platform", 
    layout="wide", 
    page_icon="🌊",
    initial_sidebar_state="expanded"  # Sidebar starts open and can be toggled
)

# -----------------------------
# INJECT REVOLUTION DESIGN SYSTEM
# -----------------------------
st.markdown(get_revolution_css(), unsafe_allow_html=True)

# -----------------------------
# AUTHENTICATION REQUIRED
# -----------------------------
require_authentication()

# Add REVOLUTION branding header (only after authentication)
st.markdown("""
<div style="text-align: center; padding: 20px 0 10px 0;">
    <div style="font-size: 48px; font-weight: 700; background: linear-gradient(90deg, #5C7CFF, #7FB8FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 2px;">REVOLUTION</div>
</div>
""", unsafe_allow_html=True)

# Get authenticated user
current_user = get_current_user()
user_name = get_username()
user_id = current_user.get('username', 'anonymous')

# -----------------------------
# Sidebar: Communities + Navigation
# -----------------------------
def sidebar():
    # Sidebar Profile Bar (REVOLUTION Design Spec)
    avatar_url = current_user.get('avatar_url', f"https://ui-avatars.com/api/?name={user_name.replace('_', '+')}&background=5C7CFF&color=fff&size=56")
    
    st.sidebar.markdown(f"""
    <div class="sidebar-profile">
        <img src="{avatar_url}" class="avatar" alt="Profile">
        <div class="sidebar-profile-info">
            <div class="sidebar-profile-name">{user_name}</div>
            <div class="sidebar-profile-handle">@{user_id} · Member</div>
            <div class="sidebar-status">
                <span class="sidebar-status-dot"></span>
                Online
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user's organizations from Firebase
    try:
        orgs_ref = firebase_db.reference('organizations')
        all_orgs = orgs_ref.get() or {}
        
        # Filter organizations where user is a member
        user_orgs = []
        for org_id, org_data in all_orgs.items():
            members = org_data.get('members', {})
            if user_name in members:
                user_orgs.append(org_data.get('name', org_id))
        
        # If no orgs, show default
        if not user_orgs:
            user_orgs = ["General", "Hackathon", "AI Enthusiasts"]
        
        st.session_state.communities = user_orgs
    except Exception as e:
        st.sidebar.error(f"Error loading organizations: {e}")
        st.session_state.communities = ["General"]
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("### Your Organizations")
    community = st.sidebar.selectbox("Select Organization", st.session_state.communities, label_visibility="collapsed")
    
    # Handle navigation redirect
    if 'nav_redirect' in st.session_state and st.session_state.nav_redirect:
        redirect_to = st.session_state.nav_redirect
        st.session_state.nav_redirect = None
        st.session_state.main_nav = redirect_to
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("### Navigation")
    
    # Initialize main_nav if not exists
    if 'main_nav' not in st.session_state:
        st.session_state.main_nav = "Dashboard"
    
    tab_selection = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Chat", "Opportunities", "Templates", "Analytics", "Profile", "Organizations"],
        index=["Dashboard", "Chat", "Opportunities", "Templates", "Analytics", "Profile", "Organizations"].index(st.session_state.main_nav),
        key="nav_radio",
        label_visibility="collapsed"
    )
    
    # Update main_nav when radio changes
    if tab_selection != st.session_state.main_nav:
        st.session_state.main_nav = tab_selection
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("Export community JSON"):
        path = f"data/{community.replace(' ', '_')}_export_{int(time.time())}.json"
        export_community_json(community, path)
        st.sidebar.success(f"Exported to `{path}`")
    if st.sidebar.button("Clear community (danger)"):
        clear_community(community)
        st.sidebar.warning("Cleared chat history for this community. Refresh to see changes.")
    
    return community, tab_selection

community, tab_selection = sidebar()

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

# =============================================================================================
# MAIN CONTENT AREA - ROUTE BASED ON TAB SELECTION
# =============================================================================================

if tab_selection == "Dashboard":
    # -----------------------------------------------------------------------------------------
    # DASHBOARD PAGE
    # -----------------------------------------------------------------------------------------
    st.title(f"Dashboard — {community}")
    
    # Initialize reminders in session state
    if 'reminders' not in st.session_state:
        st.session_state.reminders = []
    
    # Show active reminders notification at top
    if st.session_state.reminders:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%); 
                    padding: 15px; border-radius: 12px; color: white; margin-bottom: 20px;">
            <strong>🔔 {len(st.session_state.reminders)} Active Reminder(s)</strong><br>
            <small>You have reminders set for upcoming events</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Welcome message
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Welcome back, {user_name}! 👋")
        st.caption(f"Here's what's happening in {community}")
    with col2:
        current_time = time.strftime("%I:%M %p")
        st.metric("Current Time", current_time)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== ROW 1: Key Metrics ==========
    st.markdown("### 📊 Your Activity Overview")
    st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Messages Sent", "24", "+3 today")
    with col2:
        st.metric("Opportunities", "8", "2 new")
    with col3:
        st.metric("Templates Used", "12", "+1 this week")
    with col4:
        st.metric("Connections", "156", "+5 this month")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== ROW 2: Personalized Opportunity Feed + Conversation Highlights ==========
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 🎯 Personalized Opportunities")
        st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
        st.caption("AI-curated opportunities matching your profile")
        
        # Get user profile
        from personalized_opportunities import get_personalized_opportunities
        current_profile = get_profile(user_name) or {}
        
        # Get personalized opportunities based on user profile
        opportunities = get_personalized_opportunities(current_profile, top_n=5, min_score=30)
        
        if opportunities:
            for i, opp in enumerate(opportunities):
                # Color code by match score
                if opp['match'] >= 80:
                    icon = "🔥"
                elif opp['match'] >= 60:
                    icon = "⭐"
                else:
                    icon = "💡"
                
                with st.expander(f"{icon} {opp['title']} — {opp['match']}% match"):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"**Type:** {opp['type']}")
                        st.markdown(f"**Company:** {opp['company']}")
                        st.markdown(f"**Category:** {opp['category']}")
                        st.markdown(f"**Description:** {opp['description']}")
                        st.markdown(f"**Urgency:** {opp['urgency_icon']} {opp['urgency']}")
                    with col_b:
                        if st.button("View Details", key=f"opp_{i}"):
                            st.session_state.nav_redirect = "Opportunities"
                            st.rerun()
        else:
            st.info("💡 Complete your profile (skills, interests, bio) to see personalized opportunities!")
            if st.button("Go to Profile", key="goto_profile_opp"):
                st.session_state.nav_redirect = "Profile"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown("### 💬 Conversation Highlights")
        st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
        st.caption("Key discussions and suggested actions")
        
        # Sample conversations
        conversations = [
            {
                "topic": "Project Proposal Discussion",
                "participants": 5,
                "unread": 3,
                "suggestion": "Reply to John's question about timeline"
            },
            {
                "topic": "Marketing Strategy Brainstorm",
                "participants": 8,
                "unread": 0,
                "suggestion": "Share your experience with paid ads"
            },
            {
                "topic": "Tech Stack Decision",
                "participants": 4,
                "unread": 2,
                "suggestion": "Vote on React vs Vue"
            }
        ]
        
        for conv in conversations:
            with st.expander(f"💭 {conv['topic']} ({conv['participants']} participants)"):
                if conv['unread'] > 0:
                    st.markdown(f"**🔴 {conv['unread']} unread messages**")
                st.markdown(f"**AI Suggestion:** {conv['suggestion']}")
                if st.button("Jump to Chat", key=f"conv_{conv['topic'][:10]}"):
                    st.session_state.nav_redirect = "Chat"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== ROW 3: Template Quick Actions + Engagement Analytics ==========
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 📄 Template Quick Actions")
        st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
        st.caption("Frequently used templates and AI suggestions")
        
        # Recent templates
        st.markdown("**Recent Templates:**")
        recent_templates = [
            {"name": "Business Proposal", "last_used": "2 hours ago"},
            {"name": "Partnership Agreement", "last_used": "Yesterday"},
            {"name": "Project Brief", "last_used": "3 days ago"}
        ]
        
        for template in recent_templates:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"📋 {template['name']}")
                st.caption(template['last_used'])
            with col_b:
                if st.button("Open", key=f"template_{template['name'][:10]}"):
                    st.session_state.nav_redirect = "Templates"
                    st.rerun()
        
        st.markdown("---")
        st.markdown("**AI Suggestion:**")
        st.info("💡 Based on your recent activity, consider creating a **Partnership Proposal** for the FinTech opportunity.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown("### 📈 Engagement Analytics")
        st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
        st.caption("Your contribution and community health")
        
        # Personal stats
        st.markdown("**Your Contributions:**")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Posts", "24", "+3")
            st.metric("Replies", "67", "+12")
        with col_b:
            st.metric("Proposals", "8", "+1")
            st.metric("Applied", "15", "+2")
        
        st.markdown("---")
        
        # Community health
        st.markdown("**Community Health:**")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Active Users", "89", "+5")
            st.metric("Avg Response", "2.3h", "-0.5h")
        with col_b:
            st.metric("Trending Topics", "12", "+3")
            st.metric("Your Influence", "High", "↑")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== ROW 4: Risk Alerts + Upcoming Events ==========
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### ⚠️ Risk & Deal Forecast Alerts")
        st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
        st.caption("High-priority items needing attention")
        
        alerts = [
            {
                "type": "High Risk",
                "title": "Partnership Proposal Deadline",
                "description": "Proposal for TechCorp expires in 2 days",
                "action": "Review and submit final version",
                "severity": "🔴"
            },
            {
                "type": "Deal Forecast",
                "title": "Marketing Contract Close",
                "description": "E-commerce client ready to sign",
                "action": "Schedule final call",
                "severity": "🟢"
            },
            {
                "type": "Follow-up",
                "title": "Conference Speaker Application",
                "description": "No response in 5 days",
                "action": "Send follow-up email",
                "severity": "🟡"
            }
        ]
        
        for alert in alerts:
            with st.expander(f"{alert['severity']} {alert['type']}: {alert['title']}"):
                st.markdown(f"**Description:** {alert['description']}")
                st.markdown(f"**Suggested Action:** {alert['action']}")
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("Take Action", key=f"alert_{alert['title'][:10]}"):
                        if "Proposal" in alert['title']:
                            st.session_state.nav_redirect = "Templates"
                        elif "Contract" in alert['title']:
                            st.session_state.nav_redirect = "Opportunities"
                        else:
                            st.session_state.nav_redirect = "Chat"
                        st.rerun()
                with col_act2:
                    if st.button("Dismiss", key=f"dismiss_{alert['title'][:10]}"):
                        st.success("Dismissed!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown("### 📅 Upcoming Events & Deadlines")
        st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
        st.caption("Your schedule for the next 7 days")
        
        # Initialize reminders in session state
        if 'reminders' not in st.session_state:
            st.session_state.reminders = []
        
        events = [
            {
                "date": "Today, 3:00 PM",
                "title": "Community Standup Meeting",
                "type": "Meeting"
            },
            {
                "date": "Tomorrow, 10:00 AM",
                "title": "Partnership Proposal Deadline",
                "type": "Deadline"
            },
            {
                "date": "Jan 15, 2:00 PM",
                "title": "Tech Conference Speaker Call",
                "type": "Event"
            },
            {
                "date": "Jan 18, All Day",
                "title": "Startup Pitch Competition",
                "type": "Event"
            }
        ]
        
        for i, event in enumerate(events):
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"**{event['title']}**")
                st.caption(f"📅 {event['date']} · {event['type']}")
            with col_b:
                reminder_key = f"{event['title']}_{event['date']}"
                is_reminded = reminder_key in st.session_state.reminders
                if st.button("📌" if not is_reminded else "✅", key=f"event_{i}", help="Toggle reminder"):
                    if is_reminded:
                        st.session_state.reminders.remove(reminder_key)
                        st.success("Reminder removed!")
                    else:
                        st.session_state.reminders.append(reminder_key)
                        st.success("Reminder set!")
                    st.rerun()
            with col_c:
                if st.button("🔗", key=f"goto_{i}", help="Go to related page"):
                    if "Meeting" in event['type']:
                        st.session_state.nav_redirect = "Chat"
                    elif "Deadline" in event['type']:
                        st.session_state.nav_redirect = "Templates"
                    else:
                        st.session_state.nav_redirect = "Opportunities"
                    st.rerun()
        
        # Show active reminders
        if st.session_state.reminders:
            st.markdown("---")
            st.markdown(f"**Active Reminders: {len(st.session_state.reminders)}**")
            if st.button("Clear All Reminders", key="clear_reminders"):
                st.session_state.reminders = []
                st.success("All reminders cleared!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== ROW 5: AI Growth Coach ==========
    st.markdown('<div class="neuro-card" style="background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%); color: white;">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Growth Coach & Tips")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💡 Engagement Tip:**")
        st.markdown("You're most active on Tuesdays. Try posting on Mondays to increase reach by 30%.")
    
    with col2:
        st.markdown("**🎯 Opportunity Tip:**")
        st.markdown("3 new opportunities match your skills. Check the Opportunities page to apply.")
    
    with col3:
        st.markdown("**🤝 Collaboration Tip:**")
        st.markdown("Connect with Sarah Chen - you share 5 common interests and skills.")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_selection == "Chat":
    # -----------------------------------------------------------------------------------------
    # CHAT PAGE - Modern Neumorphic Design
    # -----------------------------------------------------------------------------------------
    
    # Full width chat (no columns)
    with st.container():
        # Load messages from Firebase
        try:
            # Get organization ID from name
            orgs_ref = firebase_db.reference('organizations')
            all_orgs = orgs_ref.get() or {}
            org_id = None
            for oid, org_data in all_orgs.items():
                if org_data.get('name') == community:
                    org_id = oid
                    break
            
            if org_id:
                # Load chat messages from Firebase
                chats_ref = firebase_db.reference(f'chats/{org_id}')
                messages = chats_ref.get() or {}
                
                # Convert to list and sort by timestamp
                message_list = []
                for msg_id, msg_data in messages.items():
                    msg_data['id'] = msg_id
                    message_list.append(msg_data)
                
                # Sort by timestamp (handle both string and float timestamps)
                def get_sort_key(msg):
                    ts = msg.get('timestamp', 0)
                    if isinstance(ts, (int, float)):
                        # Convert float to string for consistent comparison
                        return str(ts).zfill(20)  # Pad with zeros for proper sorting
                    elif isinstance(ts, str):
                        return ts
                    else:
                        return '0'
                
                try:
                    message_list.sort(key=get_sort_key)
                except Exception as e:
                    # If sorting fails, just use the original order
                    print(f"Warning: Could not sort messages: {e}")
                
                # Chat Header
                unique_users = len(set([m.get('username') for m in message_list]))
                st.subheader(f"{community}")
                st.caption(f"{unique_users} members online")
                st.markdown("---")
                
                # Create a container for messages with auto-scroll
                chat_container = st.container()
                
                with chat_container:
                    last_date = None
                    
                    # Show last 100 messages
                    for msg in message_list[-100:]:
                        username = msg.get('username', 'Unknown')
                        content = msg.get('content', '')
                        timestamp_raw = msg.get('timestamp', '')
                        timestamp_str = str(timestamp_raw) if timestamp_raw else ''
                        has_file = msg.get('has_file', False)
                        file_name = msg.get('file_name', '')
                        file_data = msg.get('file_data', '')
                        file_type = msg.get('file_type', '')
                        msg_id = msg.get('id', '')
                        
                        # Extract date and time
                        try:
                            msg_date = timestamp_str[:10] if len(timestamp_str) >= 10 else ''
                            msg_time = timestamp_str[11:16] if len(timestamp_str) >= 16 else ''
                        except:
                            msg_date = ''
                            msg_time = ''
                        
                        # Show date divider if date changed
                        if msg_date and msg_date != last_date:
                            st.markdown(f"**{msg_date}**")
                            last_date = msg_date
                        
                        # Determine if message is from current user
                        is_sent = username == user_name
                        
                        if is_sent:
                            # Your messages (right aligned)
                            col1, col2 = st.columns([1, 3])
                            with col2:
                                st.markdown(f"**You** · {msg_time}")
                                if content:
                                    st.info(content)
                                
                                # Show file if attached
                                if has_file and file_name and file_data:
                                    import base64
                                    try:
                                        file_bytes = base64.b64decode(file_data)
                                        st.markdown(f"📎 **{file_name}**")
                                        st.download_button(
                                            f"Download {file_name}",
                                            data=file_bytes,
                                            file_name=file_name,
                                            mime=file_type,
                                            key=f"download_sent_{msg_id}"
                                        )
                                    except:
                                        st.caption(f"📎 {file_name}")
                        else:
                            # Others' messages (left aligned)
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{username}** · {msg_time}")
                                if content:
                                    st.success(content)
                                
                                # Show file if attached
                                if has_file and file_name and file_data:
                                    import base64
                                    try:
                                        file_bytes = base64.b64decode(file_data)
                                        st.markdown(f"📎 **{file_name}**")
                                        
                                        col_a, col_b = st.columns(2)
                                        with col_a:
                                            st.download_button(
                                                f"Download",
                                                data=file_bytes,
                                                file_name=file_name,
                                                mime=file_type,
                                                key=f"download_recv_{msg_id}"
                                            )
                                        with col_b:
                                            if st.button("Save to Templates", key=f"save_template_{msg_id}"):
                                                # Save file to user's templates
                                                try:
                                                    templates_ref = firebase_db.reference(f'templates/{user_name}')
                                                    template_data = {
                                                        'template_name': file_name,
                                                        'file_name': file_name,
                                                        'file_data': file_data,
                                                        'file_type': file_type,
                                                        'shared_by': username,
                                                        'shared_at': timestamp_str,
                                                        'community': community,
                                                        'status': 'saved'
                                                    }
                                                    templates_ref.push(template_data)
                                                    st.success(f"Saved to your templates!")
                                                except Exception as e:
                                                    st.error(f"Error saving: {e}")
                                    except:
                                        st.caption(f"📎 {file_name}")
                
                # Add anchor at bottom for scrolling
                st.markdown("<div id='chat-bottom'></div>", unsafe_allow_html=True)
                
                # Auto-scroll to bottom with multiple attempts
                components.html("""
                <script>
                    function scrollToBottom() {
                        // Try multiple methods to scroll
                        try {
                            // Method 1: Scroll main content area
                            const mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                            if (mainContent) {
                                mainContent.scrollTop = mainContent.scrollHeight;
                            }
                            
                            // Method 2: Scroll to bottom element
                            const bottomElement = window.parent.document.getElementById('chat-bottom');
                            if (bottomElement) {
                                bottomElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
                            }
                            
                            // Method 3: Scroll all vertical blocks
                            const blocks = window.parent.document.querySelectorAll('[data-testid="stVerticalBlock"]');
                            blocks.forEach(block => {
                                block.scrollTop = block.scrollHeight;
                            });
                            
                            // Method 4: Scroll window
                            window.parent.scrollTo(0, document.body.scrollHeight);
                        } catch (e) {
                            console.log('Scroll error:', e);
                        }
                    }
                    
                    // Execute immediately
                    scrollToBottom();
                    
                    // Retry after delays to ensure content is loaded
                    setTimeout(scrollToBottom, 100);
                    setTimeout(scrollToBottom, 300);
                    setTimeout(scrollToBottom, 500);
                    setTimeout(scrollToBottom, 1000);
                </script>
                """, height=0)
            else:
                st.warning(f"Organization '{community}' not found in Firebase")
                
        except Exception as e:
            st.error(f"Error loading messages: {e}")
        
        # Message input
        st.markdown('<div class="glass-panel" style="margin-top: 10px;">', unsafe_allow_html=True)
        
        # Text message input
        st.markdown("#### Send Message")
        with st.form(key=f"form_{community}", clear_on_submit=True):
            user_input = st.text_input("Message", placeholder="Type a message...", label_visibility="collapsed")
            uploaded_file = st.file_uploader("Attach Document", type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'], label_visibility="collapsed")
            submit = st.form_submit_button("Send", use_container_width=True)

        if submit:
            try:
                if org_id:
                    from datetime import datetime
                    import base64
                    
                    # Prepare message data
                    new_msg = {
                        'username': user_name,
                        'content': user_input.strip() if user_input else '',
                        'timestamp': datetime.utcnow().isoformat(),
                        'user_id': user_id,
                        'has_file': False
                    }
                    
                    # Handle file upload
                    if uploaded_file is not None:
                        file_bytes = uploaded_file.read()
                        file_data_b64 = base64.b64encode(file_bytes).decode('utf-8')
                        
                        new_msg['has_file'] = True
                        new_msg['file_name'] = uploaded_file.name
                        new_msg['file_data'] = file_data_b64
                        new_msg['file_type'] = uploaded_file.type
                        
                        if not user_input.strip():
                            new_msg['content'] = f"Shared a document: {uploaded_file.name}"
                    
                    # Only send if there's content or a file
                    if user_input.strip() or uploaded_file is not None:
                        chats_ref = firebase_db.reference(f'chats/{org_id}')
                        chats_ref.push(new_msg)
                        st.success("Message sent!")
                        st.rerun()
                    else:
                        st.warning("Please enter a message or attach a file")
            except Exception as e:
                st.error(f"Error sending message: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Knowledge Base Section (Below message input)
        st.markdown('<div class="neuro-card" style="margin-top: 20px;">', unsafe_allow_html=True)
        st.markdown("### 📚 Knowledge Base")
        st.markdown("---")

        # Add chats to KB
        if st.button("Add Recent Chats to KB"):
            try:
                # Get messages from Firebase
                if org_id:
                    chats_ref = firebase_db.reference(f'chats/{org_id}')
                    messages = chats_ref.get() or {}
                    
                    if messages:
                        # Convert to list and get text content
                        message_list = []
                        for msg_id, msg_data in messages.items():
                            content = msg_data.get('content', '')
                            username = msg_data.get('username', 'Unknown')
                            if content:
                                message_list.append(f"{username}: {content}")
                        
                        # Create summary
                        all_texts = message_list[-100:]  # Last 100 messages
                        with st.spinner("Generating summary and adding to KB..."):
                            summary = summarize_with_gemini(all_texts)
                            add_to_kb(community, summary)
                            st.success("Chats added to KB!")
                            st.write(summary)
                    else:
                        st.warning("No messages to add to KB")
            except Exception as e:
                st.error(f"Error adding to KB: {e}")

        # Ask questions from KB
        st.markdown("---")
        st.markdown("**Ask KB:**")
        kb_question = st.text_input("Ask a question", placeholder="What did we discuss about...?", key="kb_question")
        
        if st.button("Search KB"):
            if kb_question.strip():
                with st.spinner("Searching knowledge base..."):
                    try:
                        results = search_kb(community, kb_question, top_k=3)
                        
                        if results:
                            st.success(f"Found {len(results)} relevant results:")
                            for i, result in enumerate(results, 1):
                                with st.expander(f"Result {i}"):
                                    st.write(result)
                        else:
                            st.info("No results found in KB. Try adding chats to KB first.")
                    except Exception as e:
                        st.error(f"Error searching KB: {e}")
            else:
                st.warning("Please enter a question")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif tab_selection == "Opportunities":
    # -----------------------------------------------------------------------------------------
    # OPPORTUNITIES PAGE
    # -----------------------------------------------------------------------------------------
    st.title(f"Opportunities — {community}")
    
    tab1, tab2, tab3 = st.tabs(["Browse Opportunities", "My Matches", "Post Opportunity"])
    
    with tab1:
        st.subheader("Available Opportunities")
        
        # Load opportunities from Firebase
        try:
            # Get organization ID
            orgs_ref = firebase_db.reference('organizations')
            all_orgs = orgs_ref.get() or {}
            org_id = None
            for oid, org_data in all_orgs.items():
                if org_data.get('name') == community:
                    org_id = oid
                    break
            
            if org_id:
                opps_ref = firebase_db.reference(f'opportunities/{org_id}')
                opportunities = opps_ref.get() or {}
                
                if opportunities:
                    for opp_id, opp in opportunities.items():
                        with st.expander(f"📌 {opp.get('title', 'Untitled')} - {opp.get('type', 'General')}"):
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.markdown(f"**Description:** {opp.get('description', 'No description')}")
                                st.markdown(f"**Posted by:** {opp.get('posted_by', 'Unknown')}")
                                if opp.get('skills_required'):
                                    st.markdown(f"**Skills:** {', '.join(opp.get('skills_required', []))}")
                                if opp.get('location'):
                                    st.markdown(f"📍 **Location:** {opp['location']}")
                                if opp.get('deadline'):
                                    st.markdown(f"⏰ **Deadline:** {opp['deadline']}")
                            with col_b:
                                st.markdown(f"**Status:** {opp.get('status', 'active').upper()}")
                                if st.button(f"Apply", key=f"apply_{opp_id}"):
                                    st.success("Application submitted!")
                else:
                    st.info("No opportunities available yet. Be the first to post one!")
            else:
                st.warning(f"Organization '{community}' not found")
        except Exception as e:
            st.error(f"Error loading opportunities: {e}")
    
    with tab2:
        st.subheader("Personalized Matches for You")
        
        # Get user profile and personalized opportunities
        from personalized_opportunities import get_personalized_opportunities, get_opportunity_stats
        current_profile = get_profile(user_name) or {}
        
        if not current_profile.get('skills') and not current_profile.get('interests'):
            st.warning("⚠️ Please complete your profile to see personalized opportunities!")
            if st.button("Go to Profile", key="goto_profile_opps"):
                st.session_state.nav_redirect = "Profile"
                st.rerun()
        else:
            # Get stats
            stats = get_opportunity_stats(current_profile)
            
            # Show stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Matches", stats['total'])
            with col2:
                st.metric("High Match (70%+)", stats['high_match'], delta=None)
            with col3:
                st.metric("Medium Match (50-70%)", stats['medium_match'], delta=None)
            with col4:
                st.metric("Urgent (< 7 days)", stats['urgent'], delta=None)
            
            st.markdown("---")
            
            # Get all personalized opportunities
            all_opportunities = get_personalized_opportunities(current_profile, top_n=50, min_score=30)
            
            if all_opportunities:
                st.success(f"🎯 Found {len(all_opportunities)} opportunities matching your profile!")
                
                # Filter options
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    filter_type = st.selectbox("Filter by Type", ["All"] + list(set(o['type'] for o in all_opportunities)))
                with col_f2:
                    filter_category = st.selectbox("Filter by Category", ["All"] + list(set(o['category'] for o in all_opportunities)))
                with col_f3:
                    min_match = st.slider("Minimum Match %", 0, 100, 30)
                
                # Apply filters
                filtered_opps = all_opportunities
                if filter_type != "All":
                    filtered_opps = [o for o in filtered_opps if o['type'] == filter_type]
                if filter_category != "All":
                    filtered_opps = [o for o in filtered_opps if o['category'] == filter_category]
                filtered_opps = [o for o in filtered_opps if o['match'] >= min_match]
                
                st.markdown(f"**Showing {len(filtered_opps)} opportunities**")
                
                for i, opp in enumerate(filtered_opps):
                    # Color code by match score
                    if opp['match'] >= 80:
                        icon = "🔥"
                        badge_color = "#10b981"
                    elif opp['match'] >= 60:
                        icon = "⭐"
                        badge_color = "#3b82f6"
                    else:
                        icon = "💡"
                        badge_color = "#8b5cf6"
                    
                    with st.expander(f"{icon} {opp['title']} — {opp['match']}% match"):
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**Type:** {opp['type']} | **Category:** {opp['category']}")
                            st.markdown(f"**Company:** {opp['company']}")
                            st.markdown(f"**Description:** {opp['description']}")
                            st.markdown(f"**Urgency:** {opp['urgency_icon']} {opp['urgency']}")
                        with col_b:
                            st.markdown(f"<div style='background:{badge_color}; color:white; padding:8px; border-radius:8px; text-align:center; font-weight:600;'>{opp['match']}% Match</div>", unsafe_allow_html=True)
                            if st.button("Apply Now", key=f"apply_match_{i}"):
                                st.success("✅ Application submitted!")
            else:
                st.info("💡 No opportunities found. Try updating your profile with more skills and interests!")
        
        # Also show Firebase opportunities if any
        try:
            orgs_ref = firebase_db.reference('organizations')
            all_orgs = orgs_ref.get() or {}
            org_id = None
            for oid, org_data in all_orgs.items():
                if org_data.get('name') == community:
                    org_id = oid
                    break
            
            if org_id:
                opps_ref = firebase_db.reference(f'opportunities/{org_id}')
                firebase_opportunities = opps_ref.get() or {}
                
                if firebase_opportunities:
                    st.markdown("---")
                    st.markdown("### 📌 Community Posted Opportunities")
                    
                    for opp_id, opp in firebase_opportunities.items():
                        with st.expander(f"📌 {opp.get('title', 'Untitled')} - {opp.get('type', 'General')}"):
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.markdown(f"**Description:** {opp.get('description', 'No description')}")
                                st.markdown(f"**Type:** {opp.get('type', 'General')}")
                                if opp.get('skills_required'):
                                    st.markdown(f"**Skills:** {', '.join(opp.get('skills_required', []))}")
                                if opp.get('location'):
                                    st.markdown(f"**Location:** {opp['location']}")
                            with col_b:
                                if st.button("Apply", key=f"fb_apply_{opp_id}"):
                                    st.success("✅ Application submitted!")
        except Exception as e:
            st.error(f"Error loading community opportunities: {e}")
    
    with tab3:
        st.subheader("Post a New Opportunity")
        
        with st.form("post_opportunity"):
            title = st.text_input("Opportunity Title*")
            description = st.text_area("Description*")
            category = st.selectbox("Category", ["event", "collaboration", "job", "funding", "partnership", "other"])
            tags_input = st.text_input("Tags (comma-separated)", placeholder="AI, startup, tech")
            requirements_input = st.text_input("Requirements/Skills (comma-separated)", placeholder="Python, ML, teamwork")
            deadline = st.date_input("Deadline (optional)")
            
            submitted = st.form_submit_button("Post Opportunity")
            
            if submitted and title and description:
                tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
                requirements = [r.strip() for r in requirements_input.split(",")] if requirements_input else []
                
                opp_id = add_opportunity(
                    community, title, description, category,
                    tags, requirements, str(deadline), user_name
                )
                
                if opp_id:
                    st.success("Opportunity posted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to post opportunity")

elif tab_selection == "Templates":
    # -----------------------------------------------------------------------------------------
    # TEMPLATES PAGE
    # -----------------------------------------------------------------------------------------
    st.title(f"Business Templates — {community}")
    
    tab1, tab2 = st.tabs(["Available Templates", "My Documents"])
    
    with tab1:
        st.subheader("Choose a Template")
        templates = get_available_templates()
        
        template_names = {tid: t['name'] for tid, t in templates.items()}
        selected_template_id = st.selectbox(
            "Select Template Type",
            options=list(template_names.keys()),
            format_func=lambda x: template_names[x]
        )
        
        if selected_template_id:
            template = get_template(selected_template_id)
            st.write(f"**Description:** {template['description']}")
            
            st.markdown("---")
            st.subheader("Fill Template")
            
            filled_data = {}
            
            for field in template['fields']:
                field_name = field['name']
                field_label = field['label']
                required = field.get('required', False)
                
                label_text = f"{field_label}{'*' if required else ''}"
                
                if field['type'] == 'date':
                    filled_data[field_name] = str(st.date_input(label_text))
                else:
                    filled_data[field_name] = st.text_area(label_text, height=100)
                
                # AI Suggestion button
                if st.button(f"Get AI Suggestion for {field_label}", key=f"suggest_{field_name}"):
                    with st.spinner("Generating suggestion..."):
                        user_profile = get_profile(user_name) or {}
                        suggestion = generate_field_suggestion_sync(
                            field_name, field_label, filled_data, user_profile, ""
                        )
                        st.info(f"Suggestion: {suggestion}")
            
            if st.button("Save Template"):
                instance_id = save_template_instance(community, user_name, selected_template_id, filled_data)
                if instance_id:
                    st.success("Template saved successfully!")
                else:
                    st.error("Failed to save template")
    
    with tab2:
        st.subheader("My Saved Documents")
        
        # Load saved templates from Firebase
        try:
            templates_ref = firebase_db.reference(f'templates/{user_name}')
            saved_templates = templates_ref.get()
            
            saved_docs = []
            if saved_templates:
                for doc_id, doc_data in saved_templates.items():
                    doc_data['id'] = doc_id
                    saved_docs.append(doc_data)
            
            # Also load regular template instances
            templates = get_available_templates()
            dummy_docs = []
            
            # Create some dummy documents for demo
            import random
            from datetime import datetime, timedelta
            
            for i in range(random.randint(3, 5)):
                template_id = random.choice(list(templates.keys()))
                template = templates[template_id]
                
                created_date = datetime.now() - timedelta(days=random.randint(1, 90))
                
                dummy_doc = {
                    'id': f'doc_{i}_{user_name}',
                    'template_id': template_id,
                    'template_name': template['name'],
                    'status': random.choice(['draft', 'completed', 'in_review']),
                    'created_at': created_date.isoformat(),
                    'updated_at': (created_date + timedelta(days=random.randint(0, 10))).isoformat(),
                    'type': 'template'
                }
                dummy_docs.append(dummy_doc)
            
            # Combine saved documents from chat and regular templates
            all_docs = saved_docs + dummy_docs
            
        except Exception as e:
            st.error(f"Error loading documents: {e}")
            all_docs = []
        
        if all_docs:
            st.info(f"You have {len(all_docs)} saved documents")
            
            # Show saved documents from chat first
            for doc in saved_docs:
                doc_name = doc.get('template_name', doc.get('file_name', 'Untitled'))
                shared_by = doc.get('shared_by', 'Unknown')
                shared_at = doc.get('shared_at', '')[:10] if doc.get('shared_at') else 'Unknown'
                
                with st.expander(f"📎 {doc_name} (from {shared_by})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Shared by:** {shared_by}")
                        st.write(f"**Shared on:** {shared_at}")
                    with col2:
                        st.write(f"**Community:** {doc.get('community', 'Unknown')}")
                        st.write(f"**Status:** {doc.get('status', 'saved').title()}")
                    
                    st.markdown("---")
                    
                    # Download button
                    if doc.get('file_data') and doc.get('file_name'):
                        import base64
                        try:
                            file_bytes = base64.b64decode(doc['file_data'])
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.download_button(
                                    "Download File",
                                    data=file_bytes,
                                    file_name=doc['file_name'],
                                    mime=doc.get('file_type', 'application/octet-stream'),
                                    key=f"download_template_{doc['id']}"
                                )
                            with col_b:
                                if st.button("Delete", key=f"delete_saved_{doc['id']}"):
                                    try:
                                        templates_ref = firebase_db.reference(f'templates/{user_name}/{doc["id"]}')
                                        templates_ref.delete()
                                        st.success("Document deleted!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting: {e}")
                        except:
                            st.error("Could not load file data")
            
            # Show regular template documents
            for doc in dummy_docs:
                with st.expander(f"{doc['template_name']} - {doc['status'].title()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Created:** {doc['created_at'][:10]}")
                    with col2:
                        st.write(f"**Last Updated:** {doc['updated_at'][:10]}")
                    
                    st.markdown("---")
                    st.write("**Preview:**")
                    st.info(f"This is a {doc['template_name']} document created on {doc['created_at'][:10]}")
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        if st.button("Edit", key=f"edit_{doc['id']}"):
                            st.info("Edit functionality coming soon!")
                    with col_b:
                        # Export as PDF
                        pdf_content = f"""
# {doc['template_name']}

**Created:** {doc['created_at'][:10]}
**Status:** {doc['status']}
**Author:** {user_name}

---

This is a sample {doc['template_name']} document.

## Content

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                        """
                        st.download_button(
                            "Export PDF",
                            data=pdf_content.encode(),
                            file_name=f"{doc['template_name'].replace(' ', '_')}.txt",
                            mime="text/plain",
                            key=f"pdf_{doc['id']}"
                        )
                    with col_c:
                        # Export as DOCX
                        st.download_button(
                            "Export DOCX",
                            data=pdf_content.encode(),
                            file_name=f"{doc['template_name'].replace(' ', '_')}.txt",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"docx_{doc['id']}"
                        )
                    with col_d:
                        if st.button("Delete", key=f"delete_{doc['id']}"):
                            st.warning("Document deleted!")
        else:
            st.info("No saved documents yet. Create one from the templates above!")

elif tab_selection == "Analytics":
    # -----------------------------------------------------------------------------------------
    # ANALYTICS PAGE - Load from Firebase
    # -----------------------------------------------------------------------------------------
    st.title(f"Community Analytics — {community}")
    
    # Load analytics from Firebase
    try:
        # Get organization ID
        orgs_ref = firebase_db.reference('organizations')
        all_orgs = orgs_ref.get() or {}
        org_id = None
        for oid, org_data in all_orgs.items():
            if org_data.get('name') == community:
                org_id = oid
                break
        
        if org_id:
            # Load analytics data
            analytics_ref = firebase_db.reference(f'analytics/{org_id}')
            analytics_data = analytics_ref.get() or {}
            
            # Calculate stats from Firebase data
            chats_ref = firebase_db.reference(f'chats/{org_id}')
            messages = chats_ref.get() or {}
            
            opps_ref = firebase_db.reference(f'opportunities/{org_id}')
            opportunities = opps_ref.get() or {}
            
            # Get unique users
            unique_users = set()
            for msg in messages.values():
                unique_users.add(msg.get('username'))
            
            # Display metrics
            st.subheader("Community Overview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Messages", len(messages))
            with col2:
                st.metric("Active Users", len(unique_users))
            with col3:
                st.metric("Opportunities", len(opportunities))
            with col4:
                st.metric("Events Tracked", len(analytics_data))
            
            st.markdown("---")
            
            # Top Contributors
            st.subheader(f"Top Contributors in {community}")
            st.caption("Leaderboard is specific to this organization")
            
            # Count messages per user
            user_message_count = {}
            for msg in messages.values():
                username = msg.get('username', 'Unknown')
                user_message_count[username] = user_message_count.get(username, 0) + 1
            
            # Sort and display
            sorted_contributors = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if sorted_contributors:
                for i, (username, count) in enumerate(sorted_contributors, 1):
                    medal = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        is_you = " (You)" if username == user_name else ""
                        st.write(f"{medal} **{username}**{is_you}")
                    with col_b:
                        st.write(f"{count} messages")
            else:
                st.info("No activity yet in this organization")
            
            st.markdown("---")
            
            # Recent Activity
            st.subheader("Recent Activity")
            
            # Count events by type
            event_types = {}
            for event_id, event in analytics_data.items():
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            if event_types:
                for event_type, count in event_types.items():
                    st.write(f"**{event_type.replace('_', ' ').title()}:** {count} events")
            else:
                st.info("No analytics events tracked yet")
                
        else:
            st.warning(f"Organization '{community}' not found")
            
    except Exception as e:
        st.error(f"Error loading analytics: {e}")
    
    st.markdown("---")
    
    # User Engagement Score
    st.subheader("Your Engagement Score")
    try:
        # Calculate user's engagement
        user_messages = sum(1 for msg in messages.values() if msg.get('username') == user_name)
        total_messages = len(messages)
        
        if total_messages > 0:
            engagement_pct = (user_messages / total_messages) * 100
            st.progress(min(engagement_pct / 100, 1.0))
            st.write(f"You've sent **{user_messages}** messages ({engagement_pct:.1f}% of total)")
        else:
            st.info("No messages yet")
    except:
        pass
    

elif tab_selection == "Profile":
    # -----------------------------------------------------------------------------------------
    # PROFILE PAGE
    # -----------------------------------------------------------------------------------------
    st.title(f"User Profile — {user_name}")
    
    # Theme toggle
    col1, col2, col3 = st.columns([8, 1, 1])
    with col2:
        if st.button("☀️", help="Light Mode", key="light_mode"):
            st.session_state.theme = "light"
            st.rerun()
    with col3:
        if st.button("🌙", help="Dark Mode", key="dark_mode"):
            st.session_state.theme = "dark"
            st.rerun()
    
    # Apply theme
    current_theme = st.session_state.get('theme', 'light')
    if current_theme == 'dark':
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
            color: #eaeaea !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%) !important;
        }
        .neuro-card, .glass-panel {
            background: linear-gradient(145deg, #1e2a3a, #243447) !important;
            color: #eaeaea !important;
        }
        h1, h2, h3, p, label, span, div {
            color: #eaeaea !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Get current profile
    current_profile = get_profile(user_name) or {}
    
    # Profile header card
    st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
    col_avatar, col_info = st.columns([1, 3])
    
    with col_avatar:
        avatar_url = current_user.get('avatar_url', f"https://ui-avatars.com/api/?name={user_name.replace('_', '+')}&background=667eea&color=fff&size=128")
        st.image(avatar_url, width=128)
    
    with col_info:
        st.markdown(f"### {user_name}")
        st.markdown(f"**@{user_id}** · Member")
        st.markdown(f"**Email:** {current_user.get('email', 'Not set')}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Edit profile section
    st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
    st.subheader("Edit Your Profile")
    
    with st.form("profile_form"):
        bio = st.text_area("Bio", value=current_profile.get('bio', ''), height=100)
        skills_input = st.text_input(
            "Skills (comma-separated)",
            value=", ".join(current_profile.get('skills', [])),
            placeholder="Python, Machine Learning, Project Management"
        )
        interests_input = st.text_input(
            "Interests (comma-separated)",
            value=", ".join(current_profile.get('interests', [])),
            placeholder="AI, Startups, Technology"
        )
        tags_input = st.text_input(
            "Tags (comma-separated) - Used for opportunity matching",
            value=", ".join(current_profile.get('tags', [])),
            placeholder="python, ai, startup, web, design, marketing",
            help="Tags are the PRIMARY factor for matching opportunities. Add relevant keywords!"
        )
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            skills = [s.strip() for s in skills_input.split(",")] if skills_input else []
            interests = [i.strip() for i in interests_input.split(",")] if interests_input else []
            tags = [t.strip().lower() for t in tags_input.split(",")] if tags_input else []
            
            success = update_user_profile(user_name, skills, interests, bio, tags)
            
            if success:
                st.success("✅ Profile updated! Your opportunity matches will update automatically.")
                st.rerun()
            else:
                st.error("Failed to update profile")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display current profile
    if current_profile:
        st.subheader("Current Profile")
        st.write(f"**Bio:** {current_profile.get('bio', 'Not set')}")
        
        if current_profile.get('skills'):
            st.write("**Skills:**")
            for skill in current_profile['skills']:
                st.badge(skill)
        
        if current_profile.get('interests'):
            st.write("**Interests:**")
            for interest in current_profile['interests']:
                st.badge(interest)

elif tab_selection == "Organizations":
    # -----------------------------------------------------------------------------------------
    # ORGANIZATIONS PAGE
    # -----------------------------------------------------------------------------------------
    st.title("Organizations & Multi-Tenant Management")
    
    tab1, tab2, tab3 = st.tabs(["My Organizations", "Create Organization", "Join Organization"])
    
    with tab1:
        st.subheader("Organizations You Belong To")
        user_orgs = get_user_organizations(user_name)
        
        if user_orgs:
            for org in user_orgs:
                with st.expander(f"{org.get('name', 'Unnamed')}"):
                    st.write(f"**Description:** {org.get('description', 'No description')}")
                    st.write(f"**Admin:** {org.get('admin', 'Unknown')}")
                    st.write(f"**Members:** {len(org.get('members', []))}")
                    st.write(f"**Created:** {org.get('created_at', 'N/A')[:10]}")
        else:
            st.info("You're not part of any organizations yet. Create or join one!")
    
    with tab2:
        st.subheader("Create New Organization")
        
        with st.form("create_org"):
            org_name = st.text_input("Organization Name*")
            org_description = st.text_area("Description")
            is_private = st.checkbox("Private Organization (members only)")
            
            created = st.form_submit_button("Create Organization")
            
            if created and org_name:
                settings = {"is_private": is_private}
                org_id = create_organization(org_name, user_name, org_description, settings)
                
                if org_id:
                    st.success(f"Organization '{org_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create organization or name already exists")
    
    with tab3:
        st.subheader("Join Organization with Invite Code")
        
        with st.form("join_org"):
            invite_code = st.text_input("Invite Code")
            join_submitted = st.form_submit_button("Join")
            
            if join_submitted and invite_code:
                success = use_invite_code(invite_code, user_name)
                
                if success:
                    st.success("Successfully joined organization!")
                    st.rerun()
                else:
                    st.error("Invalid or expired invite code")
        
        st.markdown("---")
        st.subheader("Generate Invite Code")
        
        user_orgs_for_invite = get_user_organizations(user_name)
        if user_orgs_for_invite:
            org_to_invite = st.selectbox(
                "Select Organization",
                options=[org['id'] for org in user_orgs_for_invite],
                format_func=lambda x: next((org['name'] for org in user_orgs_for_invite if org['id'] == x), x)
            )
            
            max_uses = st.number_input("Max Uses", min_value=1, max_value=100, value=1)
            
            if st.button("Generate Invite Code"):
                code = create_invite_code(org_to_invite, user_name, max_uses)
                if code:
                    st.success(f"Invite code generated: `{code}`")
                    st.code(code, language=None)
                else:
                    st.error("Failed to generate invite code")
