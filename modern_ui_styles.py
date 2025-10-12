"""
Modern Neumorphic UI Styles
Ocean-inspired color palette with glassmorphism and neumorphic design
"""

def get_modern_ui_css():
    """Returns comprehensive CSS for modern neumorphic UI"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ==================== COLOR PALETTE ==================== */
    :root {
        --deep-ocean: #003459;
        --ocean-blue: #007EA7;
        --sky-blue: #00A8E8;
        --light-gray: #E8ECEF;
        --sand-beige: #C9B8A8;
        --white: #FFFFFF;
        --shadow-light: rgba(255, 255, 255, 0.7);
        --shadow-dark: rgba(0, 52, 89, 0.15);
    }
    
    /* ==================== GLOBAL STYLES ==================== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #E8ECEF 0%, #F5F7FA 100%);
    }
    
    /* ==================== NEUMORPHIC CARDS ==================== */
    .neuro-card {
        background: linear-gradient(145deg, #F5F7FA, #E8ECEF);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 
            12px 12px 24px var(--shadow-dark),
            -12px -12px 24px var(--shadow-light);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .neuro-card:hover {
        box-shadow: 
            16px 16px 32px var(--shadow-dark),
            -16px -16px 32px var(--shadow-light);
        transform: translateY(-2px);
    }
    
    /* ==================== GLASSMORPHIC PANELS ==================== */
    .glass-panel {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 24px;
        box-shadow: 
            0 8px 32px rgba(0, 52, 89, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    /* ==================== CHAT CONTAINER ==================== */
    .modern-chat-container {
        background: linear-gradient(145deg, #F5F7FA, #FFFFFF);
        border-radius: 24px;
        padding: 0;
        max-height: 700px;
        overflow: hidden;
        box-shadow: 
            12px 12px 24px var(--shadow-dark),
            -12px -12px 24px var(--shadow-light);
    }
    
    .chat-header {
        background: linear-gradient(135deg, var(--ocean-blue), var(--sky-blue));
        padding: 20px 24px;
        border-radius: 24px 24px 0 0;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 12px rgba(0, 122, 167, 0.2);
    }
    
    .chat-title {
        font-size: 1.1em;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    .chat-subtitle {
        font-size: 0.85em;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .chat-messages-area {
        height: 550px;
        overflow-y: auto;
        padding: 24px;
        background: linear-gradient(180deg, #F5F7FA 0%, #FFFFFF 100%);
        scroll-behavior: smooth;
    }
    
    /* Custom Scrollbar */
    .chat-messages-area::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages-area::-webkit-scrollbar-track {
        background: rgba(0, 52, 89, 0.05);
        border-radius: 10px;
    }
    
    .chat-messages-area::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--ocean-blue), var(--sky-blue));
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
        border-radius: 18px;
        position: relative;
        word-wrap: break-word;
        transition: all 0.2s ease;
    }
    
    .message-bubble:hover {
        transform: scale(1.02);
    }
    
    /* Sent Messages - Neumorphic Style */
    .message-sent {
        background: linear-gradient(135deg, var(--sky-blue), var(--ocean-blue));
        color: white;
        border-radius: 18px 18px 4px 18px;
        box-shadow: 
            6px 6px 12px rgba(0, 122, 167, 0.3),
            -2px -2px 8px rgba(255, 255, 255, 0.1);
    }
    
    /* Received Messages - Glass Style */
    .message-received {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        color: var(--deep-ocean);
        border-radius: 18px 18px 18px 4px;
        border: 1px solid rgba(0, 122, 167, 0.1);
        box-shadow: 
            4px 4px 12px rgba(0, 52, 89, 0.08),
            -2px -2px 8px rgba(255, 255, 255, 0.5);
    }
    
    .message-username {
        font-weight: 600;
        font-size: 0.8em;
        margin-bottom: 4px;
        color: var(--ocean-blue);
        letter-spacing: -0.01em;
    }
    
    .message-content {
        font-size: 0.95em;
        line-height: 1.5;
        font-weight: 400;
    }
    
    .message-time {
        font-size: 0.7em;
        opacity: 0.7;
        margin-top: 6px;
        text-align: right;
        font-weight: 300;
    }
    
    /* ==================== AVATAR ==================== */
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid white;
        box-shadow: 
            4px 4px 8px rgba(0, 52, 89, 0.15),
            -2px -2px 6px rgba(255, 255, 255, 0.7);
        flex-shrink: 0;
    }
    
    /* ==================== DATE DIVIDER ==================== */
    .chat-date-divider {
        text-align: center;
        margin: 32px 0 24px 0;
        position: relative;
    }
    
    .chat-date-divider::before,
    .chat-date-divider::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 35%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 122, 167, 0.2), transparent);
    }
    
    .chat-date-divider::before {
        left: 0;
    }
    
    .chat-date-divider::after {
        right: 0;
    }
    
    .chat-date-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(0, 168, 232, 0.1), rgba(0, 126, 167, 0.1));
        backdrop-filter: blur(10px);
        padding: 8px 16px;
        border-radius: 16px;
        font-size: 0.75em;
        font-weight: 500;
        color: var(--ocean-blue);
        border: 1px solid rgba(0, 122, 167, 0.15);
        box-shadow: 0 2px 8px rgba(0, 52, 89, 0.08);
        letter-spacing: 0.02em;
    }
    
    /* ==================== FILE ATTACHMENT ==================== */
    .file-attachment {
        background: rgba(0, 122, 167, 0.08);
        backdrop-filter: blur(10px);
        padding: 12px;
        border-radius: 12px;
        margin-top: 8px;
        border: 1px solid rgba(0, 122, 167, 0.15);
        transition: all 0.2s ease;
    }
    
    .file-attachment:hover {
        background: rgba(0, 122, 167, 0.12);
        transform: translateY(-1px);
    }
    
    .file-icon {
        font-size: 1.2em;
        margin-right: 8px;
    }
    
    .file-name {
        font-size: 0.85em;
        font-weight: 500;
        color: var(--ocean-blue);
    }
    
    /* ==================== INPUT AREA ==================== */
    .chat-input-area {
        background: linear-gradient(145deg, #FFFFFF, #F5F7FA);
        padding: 20px 24px;
        border-radius: 0 0 24px 24px;
        border-top: 1px solid rgba(0, 122, 167, 0.1);
        box-shadow: 
            inset 0 4px 12px rgba(0, 52, 89, 0.05),
            0 -2px 8px rgba(255, 255, 255, 0.5);
    }
    
    /* ==================== BUTTONS ==================== */
    .neuro-button {
        background: linear-gradient(135deg, var(--ocean-blue), var(--sky-blue));
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 16px;
        font-weight: 500;
        font-size: 0.95em;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            6px 6px 12px rgba(0, 122, 167, 0.3),
            -2px -2px 8px rgba(255, 255, 255, 0.1);
        letter-spacing: 0.02em;
    }
    
    .neuro-button:hover {
        transform: translateY(-2px);
        box-shadow: 
            8px 8px 16px rgba(0, 122, 167, 0.4),
            -3px -3px 10px rgba(255, 255, 255, 0.2);
    }
    
    .neuro-button:active {
        transform: translateY(0);
        box-shadow: 
            4px 4px 8px rgba(0, 122, 167, 0.3),
            -1px -1px 4px rgba(255, 255, 255, 0.1);
    }
    
    .neuro-button-secondary {
        background: linear-gradient(145deg, #F5F7FA, #E8ECEF);
        color: var(--ocean-blue);
        box-shadow: 
            6px 6px 12px var(--shadow-dark),
            -6px -6px 12px var(--shadow-light);
    }
    
    .neuro-button-secondary:hover {
        box-shadow: 
            8px 8px 16px var(--shadow-dark),
            -8px -8px 16px var(--shadow-light);
    }
    
    /* ==================== SIDEBAR ==================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--deep-ocean), var(--ocean-blue));
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* ==================== METRICS ==================== */
    .metric-card {
        background: linear-gradient(145deg, #FFFFFF, #F5F7FA);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 
            8px 8px 16px var(--shadow-dark),
            -8px -8px 16px var(--shadow-light);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            12px 12px 24px var(--shadow-dark),
            -12px -12px 24px var(--shadow-light);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 700;
        background: linear-gradient(135deg, var(--ocean-blue), var(--sky-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: var(--deep-ocean);
        font-weight: 500;
        margin-top: 8px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* ==================== TABS ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(145deg, #F5F7FA, #E8ECEF);
        padding: 8px;
        border-radius: 20px;
        box-shadow: 
            inset 4px 4px 8px var(--shadow-dark),
            inset -4px -4px 8px var(--shadow-light);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 14px;
        color: var(--ocean-blue);
        font-weight: 500;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--ocean-blue), var(--sky-blue));
        color: white;
        box-shadow: 
            4px 4px 8px rgba(0, 122, 167, 0.3),
            -2px -2px 6px rgba(255, 255, 255, 0.1);
    }
    
    /* ==================== EXPANDER ==================== */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #F5F7FA, #E8ECEF);
        border-radius: 16px;
        padding: 16px 20px;
        font-weight: 500;
        color: var(--ocean-blue);
        box-shadow: 
            6px 6px 12px var(--shadow-dark),
            -6px -6px 12px var(--shadow-light);
    }
    
    /* ==================== FORM INPUTS ==================== */
    .stTextInput input,
    .stTextArea textarea {
        background: linear-gradient(145deg, #FFFFFF, #F5F7FA);
        border: 1px solid rgba(0, 122, 167, 0.15);
        border-radius: 14px;
        padding: 14px 18px;
        color: var(--deep-ocean);
        font-weight: 400;
        box-shadow: 
            inset 3px 3px 6px var(--shadow-dark),
            inset -3px -3px 6px var(--shadow-light);
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--sky-blue);
        box-shadow: 
            inset 3px 3px 6px var(--shadow-dark),
            inset -3px -3px 6px var(--shadow-light),
            0 0 0 3px rgba(0, 168, 232, 0.1);
    }
    
    /* ==================== ANIMATIONS ==================== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* ==================== UTILITY CLASSES ==================== */
    .text-gradient {
        background: linear-gradient(135deg, var(--ocean-blue), var(--sky-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .shadow-soft {
        box-shadow: 
            8px 8px 16px var(--shadow-dark),
            -8px -8px 16px var(--shadow-light);
    }
    
    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {
        .message-bubble {
            max-width: 85%;
        }
        
        .neuro-card {
            padding: 20px;
        }
        
        .chat-messages-area {
            height: 450px;
        }
    }
    </style>
    """
