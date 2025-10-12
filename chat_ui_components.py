"""
Modern Chat UI Components
Bubble-style messages, reactions, threading, typing indicators, and more
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
import base64


# ==================== CSS Styles ====================

def inject_chat_css():
    """Inject modern chat CSS styles"""
    st.markdown("""
    <style>
    /* Chat Container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 20px;
        max-height: 600px;
        overflow-y: auto;
        background: linear-gradient(to bottom, #f8f9fa, #ffffff);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Message Bubble - User */
    .message-bubble-user {
        display: flex;
        justify-content: flex-end;
        margin: 8px 0;
        animation: slideInRight 0.3s ease-out;
    }
    
    .message-bubble-user .bubble-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        word-wrap: break-word;
    }
    
    /* Message Bubble - Other */
    .message-bubble-other {
        display: flex;
        justify-content: flex-start;
        margin: 8px 0;
        animation: slideInLeft 0.3s ease-out;
    }
    
    .message-bubble-other .bubble-content {
        background: #ffffff;
        color: #2c3e50;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e1e8ed;
        word-wrap: break-word;
    }
    
    /* Message Bubble - System */
    .message-bubble-system {
        display: flex;
        justify-content: center;
        margin: 12px 0;
    }
    
    .message-bubble-system .bubble-content {
        background: #f0f4f8;
        color: #64748b;
        padding: 8px 16px;
        border-radius: 12px;
        font-size: 0.85em;
        font-style: italic;
        max-width: 80%;
        text-align: center;
    }
    
    /* Avatar */
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin: 0 10px;
        object-fit: cover;
        border: 2px solid #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Message Meta */
    .message-meta {
        font-size: 0.75em;
        color: #94a3b8;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .message-username {
        font-weight: 600;
        color: #475569;
        margin-bottom: 2px;
    }
    
    /* Reactions */
    .message-reactions {
        display: flex;
        gap: 6px;
        margin-top: 6px;
        flex-wrap: wrap;
    }
    
    .reaction-pill {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.85em;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .reaction-pill:hover {
        background: #e2e8f0;
        transform: scale(1.05);
    }
    
    .reaction-pill.active {
        background: #dbeafe;
        border-color: #3b82f6;
    }
    
    /* Typing Indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px;
        background: #f8fafc;
        border-radius: 12px;
        margin: 8px 0;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #94a3b8;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    /* Thread Indicator */
    .thread-indicator {
        font-size: 0.8em;
        color: #667eea;
        cursor: pointer;
        margin-top: 4px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    
    .thread-indicator:hover {
        text-decoration: underline;
    }
    
    /* Unread Badge */
    .unread-badge {
        background: #ef4444;
        color: white;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.75em;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Message Status */
    .message-status {
        font-size: 0.7em;
        color: #94a3b8;
    }
    
    .status-sent::before { content: "✓"; }
    .status-delivered::before { content: "✓✓"; }
    .status-read::before { content: "✓✓"; color: #3b82f6; }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    /* Input Area */
    .chat-input-container {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
        margin-top: 16px;
    }
    
    /* Suggested Replies */
    .suggested-replies {
        display: flex;
        gap: 8px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }
    
    .suggested-reply-chip {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 6px 12px;
        font-size: 0.85em;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .suggested-reply-chip:hover {
        background: #e2e8f0;
        border-color: #cbd5e1;
    }
    
    /* Media Attachment Preview */
    .media-preview {
        max-width: 300px;
        border-radius: 8px;
        margin-top: 8px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .media-preview:hover {
        transform: scale(1.02);
    }
    
    /* Emoji Picker Button */
    .emoji-picker-btn {
        background: none;
        border: none;
        font-size: 1.5em;
        cursor: pointer;
        padding: 4px;
        transition: transform 0.2s;
    }
    
    .emoji-picker-btn:hover {
        transform: scale(1.2);
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== Message Components ====================

def render_message_bubble(message: Dict, current_user: str):
    """Render a single message bubble"""
    username = message.get("username", "Unknown")
    content = message.get("content", "")
    timestamp = message.get("timestamp", datetime.now().timestamp())
    reactions = message.get("reactions", {})
    thread_count = message.get("thread_count", 0)
    status = message.get("status", "sent")
    role = message.get("role", "user")
    avatar_url = message.get("avatar_url", f"https://ui-avatars.com/api/?name={username}")
    
    # Format timestamp
    dt = datetime.fromtimestamp(timestamp)
    time_str = dt.strftime("%I:%M %p")
    
    # Determine bubble type
    is_current_user = username == current_user
    is_system = role == "system"
    
    if is_system:
        bubble_class = "message-bubble-system"
    elif is_current_user:
        bubble_class = "message-bubble-user"
    else:
        bubble_class = "message-bubble-other"
    
    # Build HTML
    html = f'<div class="{bubble_class}">'
    
    # Avatar (for other users)
    if not is_current_user and not is_system:
        html += f'<img src="{avatar_url}" class="message-avatar" alt="{username}">'
    
    # Bubble content
    html += '<div class="bubble-wrapper">'
    
    if not is_system:
        html += f'<div class="message-username">{username}</div>'
    
    html += f'<div class="bubble-content">{content}</div>'
    
    # Meta info
    html += f'<div class="message-meta">'
    html += f'<span>{time_str}</span>'
    
    if is_current_user:
        html += f'<span class="message-status status-{status}"></span>'
    
    html += '</div>'
    
    # Reactions
    if reactions:
        html += '<div class="message-reactions">'
        for emoji, users in reactions.items():
            count = len(users)
            is_active = current_user in users
            active_class = "active" if is_active else ""
            html += f'<span class="reaction-pill {active_class}">{emoji} {count}</span>'
        html += '</div>'
    
    # Thread indicator
    if thread_count > 0:
        html += f'<div class="thread-indicator">💬 {thread_count} replies</div>'
    
    html += '</div>'  # bubble-wrapper
    
    # Avatar (for current user)
    if is_current_user and not is_system:
        html += f'<img src="{avatar_url}" class="message-avatar" alt="{username}">'
    
    html += '</div>'  # message-bubble
    
    st.markdown(html, unsafe_allow_html=True)


def render_typing_indicator(username: str):
    """Render typing indicator"""
    html = f'''
    <div class="typing-indicator">
        <strong>{username}</strong> is typing
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def render_unread_badge(count: int):
    """Render unread message badge"""
    if count > 0:
        html = f'<span class="unread-badge">{count} new</span>'
        st.markdown(html, unsafe_allow_html=True)


# ==================== Input Components ====================

def render_suggested_replies(suggestions: List[str]):
    """Render AI-suggested reply chips"""
    if suggestions:
        st.markdown('<div class="suggested-replies">', unsafe_allow_html=True)
        
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                    return suggestion
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return None


def render_emoji_picker():
    """Render emoji picker"""
    common_emojis = ["😊", "👍", "❤️", "🎉", "🚀", "💡", "🔥", "✨", "👏", "🙌"]
    
    cols = st.columns(len(common_emojis))
    for i, emoji in enumerate(common_emojis):
        with cols[i]:
            if st.button(emoji, key=f"emoji_{i}"):
                return emoji
    
    return None


def render_reaction_buttons(message_id: str):
    """Render reaction buttons for a message"""
    reactions = ["👍", "❤️", "😂", "🎉", "🚀", "💡"]
    
    cols = st.columns(len(reactions))
    for i, emoji in enumerate(reactions):
        with cols[i]:
            if st.button(emoji, key=f"react_{message_id}_{i}"):
                return emoji
    
    return None


# ==================== Chat Container ====================

def render_chat_container(messages: List[Dict], current_user: str, 
                         show_typing: bool = False, typing_user: str = None):
    """Render complete chat container with messages"""
    inject_chat_css()
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for message in messages:
        render_message_bubble(message, current_user)
    
    if show_typing and typing_user:
        render_typing_indicator(typing_user)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== Media Handling ====================

def render_media_attachment(file_data: bytes, file_type: str, filename: str):
    """Render media attachment preview"""
    if file_type.startswith('image/'):
        # Image preview
        st.image(file_data, caption=filename, use_column_width=True)
    elif file_type == 'application/pdf':
        # PDF preview
        base64_pdf = base64.b64encode(file_data).decode('utf-8')
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        # Generic file download
        st.download_button(
            label=f"📎 Download {filename}",
            data=file_data,
            file_name=filename,
            mime=file_type
        )


def file_uploader_component():
    """File uploader for chat attachments"""
    uploaded_file = st.file_uploader(
        "Attach file",
        type=['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'],
        help="Upload images, documents, or PDFs"
    )
    
    return uploaded_file


# ==================== Thread View ====================

def render_thread_view(parent_message: Dict, replies: List[Dict], current_user: str):
    """Render threaded conversation view"""
    st.markdown("### 💬 Thread")
    
    # Parent message
    with st.container():
        st.markdown("**Original Message:**")
        render_message_bubble(parent_message, current_user)
    
    st.markdown("---")
    
    # Replies
    if replies:
        st.markdown(f"**{len(replies)} Replies:**")
        for reply in replies:
            render_message_bubble(reply, current_user)
    else:
        st.info("No replies yet. Be the first to respond!")
    
    # Reply input
    st.markdown("---")
    reply_text = st.text_area("Write a reply...", key="thread_reply")
    if st.button("Send Reply", type="primary"):
        return reply_text
    
    return None


# ==================== Message Actions ====================

def render_message_actions(message_id: str, is_own_message: bool):
    """Render message action buttons (edit, delete, reply, etc.)"""
    cols = st.columns([1, 1, 1, 1, 6])
    
    actions = {}
    
    with cols[0]:
        if st.button("💬", key=f"reply_{message_id}", help="Reply in thread"):
            actions['reply'] = True
    
    with cols[1]:
        if st.button("➕", key=f"react_{message_id}", help="Add reaction"):
            actions['react'] = True
    
    if is_own_message:
        with cols[2]:
            if st.button("✏️", key=f"edit_{message_id}", help="Edit message"):
                actions['edit'] = True
        
        with cols[3]:
            if st.button("🗑️", key=f"delete_{message_id}", help="Delete message"):
                actions['delete'] = True
    
    return actions


# ==================== Search & Filter ====================

def render_chat_search():
    """Render chat search bar"""
    search_query = st.text_input(
        "🔍 Search messages",
        placeholder="Search in conversation...",
        key="chat_search"
    )
    
    return search_query


def render_chat_filters():
    """Render chat filter options"""
    col1, col2, col3 = st.columns(3)
    
    filters = {}
    
    with col1:
        filters['user'] = st.selectbox(
            "Filter by user",
            ["All users", "Me", "Others"],
            key="filter_user"
        )
    
    with col2:
        filters['date'] = st.selectbox(
            "Filter by date",
            ["All time", "Today", "This week", "This month"],
            key="filter_date"
        )
    
    with col3:
        filters['type'] = st.selectbox(
            "Filter by type",
            ["All messages", "With attachments", "With reactions", "Threads"],
            key="filter_type"
        )
    
    return filters
