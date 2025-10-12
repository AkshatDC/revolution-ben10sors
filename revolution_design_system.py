"""
REVOLUTION - Neumorphic Minimal Community Platform Design System
Exact specifications for calm, futuristic, elegant, community-driven UI
"""

def get_revolution_css():
    """Returns complete CSS for REVOLUTION platform with exact design specs"""
    return """
    <style>
    
    /* ==================== REVOLUTION COLOR PALETTE (EXACT HEX) ==================== */
    :root {
        /* Primary Colors */
        --bg: #E8EDF5;                          /* Background - very pale cool grey/blue */
        --glass: rgba(255, 255, 255, 0.65);     /* Glass-like translucent white */
        --card-grad-start: #EEF3F9;             /* Cool lilac gradient start */
        --card-grad-end: #F8FBFF;               /* Sky blue gradient end */
        --accent: #667eea;                      /* Muted blue - action/CTA */
        --warm-accent: #64b5f6;                 /* Pale peach - subtle warm accent */
        
        /* Text Colors */
        --text: #2D3748;                        /* Primary text - near-black */
        --muted: #718096;                       /* Secondary text */
        --disabled: #A0AEC0;                    /* Disabled/placeholder */
        
        /* Spacing & Radii */
        --radius: 20px;                         /* Global border radius */
        --radius-small: 12px;                   /* Small chips */
        --radius-large: 24px;                   /* Large hero cards */
        
        /* Shadows (Neumorphic) */
        --shadow-outer: 12px 12px 24px rgba(174, 191, 212, 0.3), -12px -12px 24px rgba(255, 255, 255, 0.9);
        --shadow-inner: inset 4px 4px 8px rgba(174, 191, 212, 0.3), inset -4px -4px 8px rgba(255, 255, 255, 0.9);
        --shadow-hover: 16px 16px 32px rgba(174, 191, 212, 0.35), -16px -16px 32px rgba(255, 255, 255, 0.95);
    }
    
    /* ==================== GLOBAL STYLES ==================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        transition: background 0.3s ease, color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
    }
    
    body, .main, .stApp {
        background: linear-gradient(135deg, #e8edf5 0%, #f0f4f8 50%, #e5ebf2 100%) !important;
        color: #4a5568;
        min-height: 100vh;
    }
    
    /* ==================== TYPOGRAPHY ==================== */
    h1, .h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 32px;
        letter-spacing: 0.2px;
        color: var(--text);
    }
    
    h2, .h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 24px;
        letter-spacing: 0.2px;
        color: var(--text);
    }
    
    h3, .h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 20px;
        letter-spacing: 0.2px;
        color: var(--text);
    }
    
    p, .body-text {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 15px;
        line-height: 1.5;
        color: var(--text);
    }
    
    .label, small {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 12px;
        color: var(--muted);
    }
    
    /* ==================== NEUMORPHIC GLASS CARDS ==================== */
    .neumo-card {
        background: linear-gradient(135deg, var(--card-grad-start) 0%, var(--card-grad-end) 100%);
        background-color: var(--glass);
        border-radius: var(--radius);
        box-shadow: var(--shadow-outer);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 20px;
        transition: all 0.12s ease;
    }
    
    .neumo-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-hover);
    }
    
    .neumo-card-large {
        border-radius: var(--radius-large);
        padding: 28px;
    }
    
    /* ==================== SIDEBAR - FULL SPEC ==================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8edf5 100%) !important;
        backdrop-filter: blur(20px);
        border-right: none;
        box-shadow: 4px 0 16px rgba(174, 191, 212, 0.15);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 20px 16px;
        background: transparent;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        background: transparent;
    }
    
    /* Sidebar text color */
    [data-testid="stSidebar"] * {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #2d3748 !important;
    }
    
    /* Sidebar Profile Bar */
    .sidebar-profile {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px;
        border-radius: var(--radius-small);
        background: rgba(255, 255, 255, 0.55);
        box-shadow: var(--shadow-inner);
        margin-bottom: 20px;
        transition: all 0.12s ease;
        min-height: 80px;
    }
    
    .sidebar-profile:hover {
        background: rgba(255, 255, 255, 0.65);
        transform: translateY(-2px);
    }
    
    .sidebar-profile img.avatar {
        width: 48px;
        height: 48px;
        min-width: 48px;
        border-radius: 50%;
        box-shadow: 0 6px 18px rgba(12, 20, 30, 0.06);
        border: 2px solid rgba(255, 255, 255, 0.8);
        flex-shrink: 0;
    }
    
    .sidebar-profile-info {
        flex: 1;
        min-width: 0;
        overflow: hidden;
    }
    
    .sidebar-profile-name {
        font-size: 14px;
        font-weight: 600;
        color: #2d3748 !important;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .sidebar-profile-handle {
        font-size: 11px;
        font-weight: 300;
        color: #718096 !important;
        margin: 2px 0 0 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .sidebar-status {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 8px;
        border-radius: 10px;
        background: rgba(102, 126, 234, 0.15);
        font-size: 10px;
        font-weight: 500;
        color: #667eea !important;
        margin-top: 4px;
    }
    
    .sidebar-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Sidebar Navigation Items */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
        background: transparent !important;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] {
        background: transparent !important;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] label {
        display: flex;
        align-items: center;
        height: 48px;
        padding: 12px 16px;
        border-radius: var(--radius-small);
        background: rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s ease;
        cursor: pointer;
        border-left: 3px solid transparent;
        margin: 4px 0;
        color: #2d3748 !important;
        font-weight: 400;
        box-shadow: 2px 2px 4px rgba(174, 191, 212, 0.2), -2px -2px 4px rgba(255, 255, 255, 0.8);
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px);
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.9);
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%) !important;
        border-left-color: transparent;
        font-weight: 500;
        color: white !important;
        box-shadow: 4px 4px 12px rgba(102, 126, 234, 0.4), -2px -2px 8px rgba(255, 255, 255, 0.5);
    }
    
    /* Sidebar selectbox */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.5) !important;
        border: none;
        border-radius: 12px;
        box-shadow: inset 2px 2px 4px rgba(174, 191, 212, 0.2), inset -2px -2px 4px rgba(255, 255, 255, 0.8);
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(145deg, #eef3f9, #f8fbff) !important;
        color: #667eea !important;
        border: none;
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.9);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%) !important;
        color: white !important;
        box-shadow: 6px 6px 12px rgba(102, 126, 234, 0.4), -4px -4px 8px rgba(255, 255, 255, 0.6);
    }
    
    /* ==================== CHAT INTERFACE (WhatsApp Style) ==================== */
    .revolution-chat-container {
        background: #FFFFFF;
        border-radius: var(--radius-large);
        box-shadow: var(--shadow-outer);
        overflow: hidden;
        max-height: 750px;
    }
    
    .chat-header {
        background: #F0F2F5;
        padding: 16px 24px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .chat-header-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text);
        margin: 0;
    }
    
    .chat-header-subtitle {
        font-size: 12px;
        font-weight: 300;
        color: var(--muted);
        margin: 2px 0 0 0;
    }
    
    .chat-messages-area {
        height: 580px;
        overflow-y: auto;
        padding: 20px;
        background: #E5DDD5;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect fill="%23E5DDD5" width="100" height="100"/><circle fill="%23D9D0C8" opacity="0.1" cx="50" cy="50" r="40"/></svg>');
        scroll-behavior: smooth;
        display: flex;
        flex-direction: column;
        overflow-anchor: auto;
    }
    
    /* Custom Scrollbar */
    .chat-messages-area::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages-area::-webkit-scrollbar-track {
        background: rgba(166, 176, 187, 0.1);
        border-radius: 10px;
    }
    
    .chat-messages-area::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--accent), #7FB8FF);
        border-radius: 10px;
    }
    
    /* ==================== MESSAGE BUBBLES ==================== */
    .message-wrapper {
        display: flex;
        align-items: flex-end;
        margin: 16px 0;
        gap: 12px;
        animation: messageSlideIn 0.3s ease-out;
    }
    
    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-wrapper-sent {
        justify-content: flex-end;
    }
    
    .message-wrapper-received {
        justify-content: flex-start;
    }
    
    .message-bubble {
        max-width: 65%;
        padding: 14px 18px;
        border-radius: var(--radius);
        position: relative;
        word-wrap: break-word;
        transition: all 0.12s ease;
    }
    
    .message-bubble:hover {
        transform: scale(1.02);
    }
    
    /* Sent Messages - WhatsApp Green */
    .message-sent {
        background: #DCF8C6;
        color: #000000;
        border-radius: 8px 8px 0px 8px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Received Messages - White */
    .message-received {
        background: #FFFFFF;
        color: var(--text);
        border-radius: 8px 8px 8px 0px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .message-username {
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 4px;
        color: var(--accent);
    }
    
    .message-content {
        font-size: 15px;
        line-height: 1.5;
        font-weight: 300;
    }
    
    .message-time {
        font-size: 11px;
        opacity: 0.6;
        margin-top: 4px;
        text-align: right;
        font-weight: 300;
        color: #667781;
    }
    
    /* ==================== AVATAR ==================== */
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 4px 12px rgba(12, 20, 30, 0.08);
        flex-shrink: 0;
    }
    
    /* ==================== DATE DIVIDER (WhatsApp Style) ==================== */
    .chat-date-divider {
        text-align: center;
        margin: 20px 0 16px 0;
        position: relative;
    }
    
    .chat-date-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.9);
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 400;
        color: #667781;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* ==================== FILE ATTACHMENT ==================== */
    .file-attachment {
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(8px);
        padding: 10px 14px;
        border-radius: var(--radius-small);
        margin-top: 8px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.12s ease;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .file-attachment:hover {
        background: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(12, 20, 30, 0.06);
    }
    
    .file-icon {
        font-size: 18px;
    }
    
    .file-name {
        font-size: 13px;
        font-weight: 400;
        color: var(--text);
    }
    
    /* ==================== BUTTONS (NEUMORPHIC) ==================== */
    .neumo-button {
        background: linear-gradient(90deg, var(--accent), #7FB8FF);
        color: #FFFFFF;
        border: none;
        padding: 12px 28px;
        border-radius: var(--radius-small);
        font-weight: 500;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.12s ease;
        box-shadow: 0 4px 12px rgba(92, 124, 255, 0.25);
    }
    
    .neumo-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(92, 124, 255, 0.35);
    }
    
    .neumo-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(92, 124, 255, 0.25);
    }
    
    .neumo-button-secondary {
        background: rgba(255, 255, 255, 0.7);
        color: var(--accent);
        border: 1px solid rgba(92, 124, 255, 0.3);
        box-shadow: var(--shadow-outer);
    }
    
    .neumo-button-secondary:hover {
        background: rgba(255, 255, 255, 0.9);
        box-shadow: var(--shadow-hover);
    }
    
    /* ==================== INPUT FIELDS (NEUMORPHIC INSET) ==================== */
    .neumo-input, .stTextInput input, .stTextArea textarea {
        border-radius: var(--radius-small);
        padding: 12px 14px;
        box-shadow: var(--shadow-inner);
        background: rgba(255, 255, 255, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.5);
        color: var(--text);
        font-weight: 300;
        transition: all 0.12s ease;
    }
    
    .neumo-input:focus, .stTextInput input:focus, .stTextArea textarea:focus {
        background: rgba(255, 255, 255, 0.75);
        border-color: var(--accent);
        box-shadow: var(--shadow-inner), 0 0 0 3px rgba(92, 124, 255, 0.1);
        outline: none;
    }
    
    .neumo-input::placeholder {
        color: var(--disabled);
        font-weight: 300;
    }
    
    /* ==================== POST CARD DESIGN ==================== */
    .post-card {
        background: linear-gradient(135deg, var(--card-grad-start), var(--card-grad-end));
        background-color: var(--glass);
        border-radius: var(--radius);
        box-shadow: var(--shadow-outer);
        backdrop-filter: blur(8px);
        padding: 20px;
        margin-bottom: 24px;
        transition: all 0.12s ease;
    }
    
    .post-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-hover);
    }
    
    .post-author-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .post-avatar {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(12, 20, 30, 0.08);
        border: 2px solid rgba(255, 255, 255, 0.8);
    }
    
    .post-author-name {
        font-size: 16px;
        font-weight: 600;
        color: var(--text);
        margin: 0;
    }
    
    .post-author-handle {
        font-size: 12px;
        font-weight: 300;
        color: var(--muted);
        margin: 2px 0 0 0;
    }
    
    .post-content {
        font-size: 15px;
        line-height: 1.5;
        font-weight: 300;
        color: var(--text);
        margin: 16px 0;
    }
    
    .post-action-bar {
        display: flex;
        gap: 16px;
        padding-top: 16px;
        border-top: 1px solid rgba(166, 176, 187, 0.15);
    }
    
    .post-action-button {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 14px;
        border-radius: var(--radius-small);
        background: rgba(255, 255, 255, 0.4);
        border: none;
        cursor: pointer;
        transition: all 0.12s ease;
        font-size: 13px;
        font-weight: 400;
        color: var(--muted);
    }
    
    .post-action-button:hover {
        background: rgba(255, 255, 255, 0.7);
        transform: translateY(-2px);
        color: var(--accent);
    }
    
    /* ==================== METRICS & STATS ==================== */
    .metric-card {
        background: linear-gradient(135deg, var(--card-grad-start), var(--card-grad-end));
        background-color: var(--glass);
        border-radius: var(--radius);
        padding: 24px;
        text-align: center;
        box-shadow: var(--shadow-outer);
        backdrop-filter: blur(8px);
        transition: all 0.12s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-hover);
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(90deg, var(--accent), #7FB8FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .metric-label {
        font-size: 12px;
        font-weight: 400;
        color: var(--muted);
        margin-top: 8px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* ==================== TABS ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.4);
        padding: 6px;
        border-radius: var(--radius-small);
        box-shadow: var(--shadow-inner);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--muted);
        font-weight: 400;
        padding: 10px 20px;
        transition: all 0.12s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.5);
        color: var(--text);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, var(--accent), #7FB8FF);
        color: #FFFFFF;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(92, 124, 255, 0.25);
    }
    
    /* ==================== LOADING STATES (SKELETON) ==================== */
    .skeleton {
        background: linear-gradient(90deg, 
            rgba(255, 255, 255, 0.4) 0%, 
            rgba(232, 230, 255, 0.6) 50%, 
            rgba(255, 255, 255, 0.4) 100%
        );
        background-size: 200% 100%;
        animation: shimmer 1.5s ease-in-out infinite;
        border-radius: var(--radius-small);
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* ==================== RESPONSIVE DESIGN ==================== */
    @media (max-width: 768px) {
        .message-bubble {
            max-width: 85%;
        }
        
        .neumo-card {
            padding: 16px;
        }
        
        .chat-messages-area {
            height: 450px;
        }
        
        .sidebar-profile {
            padding: 12px;
        }
        
        .sidebar-profile img.avatar {
            width: 48px;
            height: 48px;
        }
    }
    
    /* ==================== ACCESSIBILITY ==================== */
    *:focus-visible {
        outline: 2px solid var(--accent);
        outline-offset: 2px;
    }
    
    /* Ensure WCAG AA contrast */
    .text-primary {
        color: var(--text);
    }
    
    .text-muted {
        color: var(--muted);
    }
    
    /* ==================== BRANDING ==================== */
    .revolution-logo {
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(90deg, var(--accent), #7FB8FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 1px;
    }
    
    .revolution-tagline {
        font-size: 12px;
        font-weight: 300;
        color: var(--muted);
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* ==================== STREAMLIT SPECIFIC ENHANCEMENTS ==================== */
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%);
        color: white;
        border: none;
        padding: 14px 32px;
        border-radius: 16px;
        font-weight: 300;
        font-size: 15px;
        box-shadow: 6px 6px 12px rgba(102, 126, 234, 0.3), -2px -2px 8px rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 8px 8px 16px rgba(102, 126, 234, 0.4), -4px -4px 12px rgba(255, 255, 255, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        color: #667eea;
        border: none;
        padding: 12px 24px;
        border-radius: 16px;
        font-weight: 300;
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 6px 6px 12px rgba(174, 191, 212, 0.35), -6px -6px 12px rgba(255, 255, 255, 0.95);
        transform: translateY(-2px);
    }
    
    /* Text Input */
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border: none;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: inset 4px 4px 8px rgba(174, 191, 212, 0.3), inset -4px -4px 8px rgba(255, 255, 255, 0.9);
        color: #4a5568;
        font-weight: 300;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        box-shadow: inset 6px 6px 12px rgba(174, 191, 212, 0.4), inset -6px -6px 12px rgba(255, 255, 255, 0.95);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0aec0;
        font-weight: 200;
    }
    
    /* Text Area */
    .stTextArea > div > div > textarea {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border: none;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: inset 4px 4px 8px rgba(174, 191, 212, 0.3), inset -4px -4px 8px rgba(255, 255, 255, 0.9);
        color: #4a5568;
        font-weight: 300;
        transition: all 0.3s ease;
        min-height: 100px;
    }
    
    .stTextArea > div > div > textarea:focus {
        box-shadow: inset 6px 6px 12px rgba(174, 191, 212, 0.4), inset -6px -6px 12px rgba(255, 255, 255, 0.95);
        outline: none;
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border: none;
        border-radius: 16px;
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.9);
    }
    
    .stSelectbox > div > div > div {
        color: #2d3748 !important;
    }
    
    .stSelectbox label {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        color: #2d3748 !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #2d3748 !important;
    }
    
    /* File Uploader */
    .stFileUploader > div {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: inset 2px 2px 4px rgba(174, 191, 212, 0.2);
    }
    
    /* Info/Success/Warning/Error boxes */
    .stAlert {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border-radius: 16px;
        padding: 16px 20px;
        border: none;
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.9);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.9);
        font-weight: 400;
        color: #2d3748;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        box-shadow: 6px 6px 12px rgba(174, 191, 212, 0.35), -6px -6px 12px rgba(255, 255, 255, 0.95);
        transform: translateY(-2px);
    }
    
    /* Metric */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 12px 12px 24px rgba(174, 191, 212, 0.3), -12px -12px 24px rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-6px);
        box-shadow: 16px 16px 32px rgba(174, 191, 212, 0.35), -16px -16px 32px rgba(255, 255, 255, 0.95);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: 300;
        background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 12px;
        font-weight: 200;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Glass Panel */
    .glass-panel {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.8);
        padding: 24px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        transition: all 0.3s ease;
    }
    
    .glass-panel:hover {
        background: rgba(255, 255, 255, 0.75);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.15);
    }
    
    /* Neumorphic Cards */
    .neuro-card {
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        border-radius: var(--radius-large);
        padding: 20px;
        box-shadow: var(--shadow-outer);
        transition: all 0.3s ease;
        margin: 5px 0 20px 0;
    }
    
    /* Floating header bars for sections */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 4px 4px 12px rgba(102, 126, 234, 0.3), -2px -2px 8px rgba(255, 255, 255, 0.5);
        font-weight: 600;
        font-size: 18px;
    }
    
    /* Headings that should be floating bars */
    .stMarkdown h3 {
        background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        margin-top: 10px;
        box-shadow: 4px 4px 12px rgba(102, 126, 234, 0.3), -2px -2px 8px rgba(255, 255, 255, 0.5);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stMarkdown h3:hover {
        box-shadow: 6px 6px 16px rgba(102, 126, 234, 0.4), -3px -3px 10px rgba(255, 255, 255, 0.6);
        transform: translateY(-2px);
    }
    
    /* Card captions and text */
    .neuro-card .stMarkdown p,
    .neuro-card p {
        color: #64748b !important;
    }
    
    /* Strong text in cards */
    .neuro-card strong {
        color: #2d3748 !important;
    }
    
    .neuro-card:hover {
        box-shadow: 6px 6px 16px rgba(174, 191, 212, 0.35), -6px -6px 16px rgba(255, 255, 255, 0.95);
        transform: translateY(-2px);
    }
    
    /* Section Title */
    .section-title {
        font-size: 22px;
        font-weight: 300;
        margin-bottom: 20px;
        color: #2d3748;
        letter-spacing: 1px;
    }
    
    /* Tags */
    .tag {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 12px;
        background: linear-gradient(145deg, #eef3f9, #f8fbff);
        box-shadow: 2px 2px 4px rgba(174, 191, 212, 0.3), -2px -2px 4px rgba(255, 255, 255, 0.9);
        font-size: 12px;
        font-weight: 300;
        color: #667eea;
        margin: 4px;
        transition: all 0.3s ease;
    }
    
    .tag:hover {
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.35), -4px -4px 8px rgba(255, 255, 255, 0.95);
        transform: translateY(-2px);
    }
    
    /* Style Streamlit's built-in sidebar toggle */
    button[kind="header"] {
        background: linear-gradient(145deg, #eef3f9, #f8fbff) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 4px 4px 8px rgba(174, 191, 212, 0.3), -4px -4px 8px rgba(255, 255, 255, 0.9) !important;
        color: #667eea !important;
        transition: all 0.3s ease !important;
        padding: 8px 12px !important;
    }
    
    button[kind="header"]:hover {
        box-shadow: 6px 6px 12px rgba(174, 191, 212, 0.35), -6px -6px 12px rgba(255, 255, 255, 0.95) !important;
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, #667eea 0%, #64b5f6 100%) !important;
        color: white !important;
    }
    
    /* Header styling */
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(174, 191, 212, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #64b5f6);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3, #4fa0e0);
    }
    </style>
    """
