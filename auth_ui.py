"""
Authentication UI Components for Streamlit
Login, Signup, and Session Management
"""

import streamlit as st
import requests
from typing import Optional, Dict
import time

# Backend URL
BACKEND_URL = "http://localhost:8001"


# ==================== CSS Styles ====================

def inject_auth_css():
    """Inject authentication page CSS"""
    st.markdown("""
    <style>
    /* Auth Container */
    .auth-container {
        max-width: 450px;
        margin: 50px auto;
        padding: 40px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Auth Header */
    .auth-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .auth-header h1 {
        color: #667eea;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    
    .auth-header p {
        color: #64748b;
        font-size: 1.1em;
    }
    
    /* Auth Tabs */
    .auth-tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 30px;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .auth-tab {
        flex: 1;
        padding: 12px;
        text-align: center;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: all 0.3s;
        font-weight: 600;
        color: #64748b;
    }
    
    .auth-tab.active {
        color: #667eea;
        border-bottom-color: #667eea;
    }
    
    .auth-tab:hover {
        background: #f8fafc;
    }
    
    /* Form Styles */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 12px;
        font-size: 1em;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button Styles */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px;
        font-size: 1.1em;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Success/Error Messages */
    .success-message {
        background: #d1fae5;
        color: #065f46;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #10b981;
    }
    
    .error-message {
        background: #fee2e2;
        color: #991b1b;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #ef4444;
    }
    
    /* User Profile Badge */
    .user-badge {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: #f8fafc;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .user-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
    }
    
    .user-info {
        flex: 1;
    }
    
    .user-name {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 4px;
    }
    
    .user-email {
        font-size: 0.9em;
        color: #64748b;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== Session Management ====================

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None


def login_user(username: str, password: str) -> tuple[bool, str, Optional[Dict]]:
    """
    Login user and store session
    Returns: (success, message, user_data)
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        # Debug: print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:200]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError as e:
                return False, f"Server returned invalid JSON: {response.text[:100]}", None
            
            if not data.get('ok'):
                return False, data.get('error', 'Login failed'), None
            
            # Store in session state
            st.session_state.authenticated = True
            st.session_state.user = data.get('user')
            st.session_state.access_token = data.get('access_token')
            st.session_state.refresh_token = data.get('refresh_token')
            
            return True, "Login successful!", data.get('user')
        else:
            try:
                error_msg = response.json().get('detail', f'Server error: {response.status_code}')
            except:
                error_msg = f"Server error {response.status_code}: {response.text[:100]}"
            return False, error_msg, None
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please start backend: python -m uvicorn fastapi_server:app --port 8000", None
    except Exception as e:
        return False, f"Login error: {str(e)}", None


def register_user(username: str, email: str, password: str, full_name: str) -> tuple[bool, str]:
    """
    Register new user
    Returns: (success, message)
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "Registration successful! Please login."
        else:
            error_msg = response.json().get('detail', 'Registration failed')
            return False, error_msg
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please ensure the backend is running."
    except Exception as e:
        return False, f"Registration error: {str(e)}"


def logout_user():
    """Logout user and clear session"""
    try:
        if st.session_state.access_token:
            requests.post(
                f"{BACKEND_URL}/api/auth/logout",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                timeout=5
            )
    except:
        pass
    
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None


def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for API calls"""
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


# ==================== UI Components ====================

def render_login_page():
    """Render login/signup page"""
    inject_auth_css()
    init_session_state()
    
    # Add REVOLUTION branding header at the top
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div style="font-size: 48px; font-weight: 700; background: linear-gradient(90deg, #5C7CFF, #7FB8FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 2px;">REVOLUTION</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the auth container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Tagline only (no duplicate REVOLUTION)
        st.markdown("""
        <div class="auth-header">
            <p>Connect, Collaborate, Grow</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for Login/Signup
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_signup_form()


def render_login_form():
    """Render login form"""
    st.markdown("### Welcome Back!")
    st.markdown("Enter your credentials to access your account")
    
    with st.form("login_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            remember_me = st.checkbox("Remember me", value=True)
        with col2:
            st.markdown("<small>Forgot?</small>", unsafe_allow_html=True)
        
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                with st.spinner("Logging in..."):
                    success, message, user_data = login_user(username, password)
                    
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Demo credentials hint
    with st.expander("Demo Credentials"):
        st.info("""
        **For Testing:**
        - Username: Any seeded username (check Firebase)
        - Password: `password123`
        
        Run `python seed_data_standalone.py` to create test users.
        """)


def render_signup_form():
    """Render signup form"""
    st.markdown("### Create Account")
    st.markdown("Join our community today!")
    
    with st.form("signup_form"):
        full_name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            key="signup_fullname"
        )
        
        username = st.text_input(
            "Username",
            placeholder="johndoe",
            help="Unique username (no spaces or special characters)",
            key="signup_username"
        )
        
        email = st.text_input(
            "Email",
            placeholder="john@example.com",
            key="signup_email"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 8 characters",
                key="signup_password"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter password",
                key="signup_confirm"
            )
        
        agree_terms = st.checkbox("I agree to the Terms & Conditions")
        
        submit = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit:
            # Validation
            if not all([full_name, username, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters")
            elif not agree_terms:
                st.error("Please agree to the Terms & Conditions")
            else:
                with st.spinner("Creating account..."):
                    success, message = register_user(username, email, password, full_name)
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        time.sleep(2)
                        st.info("Please switch to the Login tab to sign in")
                    else:
                        st.error(message)


def render_user_profile_badge():
    """Render logged-in user profile badge in sidebar"""
    if st.session_state.authenticated and st.session_state.user:
        user = st.session_state.user
        
        st.markdown("---")
        
        # User info
        col1, col2 = st.columns([1, 3])
        
        with col1:
            avatar_url = user.get('avatar_url', 'https://ui-avatars.com/api/?name=User')
            st.image(avatar_url, width=50)
        
        with col2:
            st.markdown(f"**{user.get('full_name', user.get('username'))}**")
            st.caption(user.get('email', ''))
        
        # Logout button
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        st.markdown("---")


def require_authentication():
    """
    Decorator/function to require authentication
    Call this at the start of your app
    """
    init_session_state()
    
    if not st.session_state.authenticated:
        render_login_page()
        st.stop()
    
    # Render user badge in sidebar
    with st.sidebar:
        render_user_profile_badge()


# ==================== Helper Functions ====================

def get_current_user() -> Optional[Dict]:
    """Get current logged-in user"""
    return st.session_state.user if st.session_state.authenticated else None


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.authenticated


def get_username() -> Optional[str]:
    """Get current username"""
    user = get_current_user()
    return user.get('username') if user else None


# ==================== Testing ====================

if __name__ == "__main__":
    st.set_page_config(
        page_title="REVOLUTION",
        page_icon="🌊",
        layout="wide"
    )
    
    # Test the authentication UI
    require_authentication()
    
    # If authenticated, show main content
    st.title("Welcome to the Platform!")
    st.success(f"You are logged in as: {get_username()}")
    
    user = get_current_user()
    st.json(user)
