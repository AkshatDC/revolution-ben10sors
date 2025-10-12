# fastapi_server.py

import os
import time
import json
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import asyncio

from db_utils import init_db, add_message, fetch_messages
from kb_utils import add_to_kb, search_kb
from config import DB_PATH
from opportunity_matcher import (
    add_opportunity, get_opportunities, match_opportunities,
    update_user_profile, get_user_profile, track_user_activity
)
from template_assistant import (
    get_available_templates, get_template, save_template_instance,
    get_user_templates, generate_field_suggestion_sync, export_template_to_markdown
)
from analytics import (
    get_community_stats, get_top_contributors, get_engagement_trends,
    get_user_engagement_score, generate_analytics_report, track_engagement
)
from multi_tenant import (
    create_organization, get_organization, add_member_to_organization,
    is_member, check_permission, create_invite_code, use_invite_code,
    get_user_organizations
)

# Import auth functions directly to avoid circular dependency
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from firebase_admin import db as firebase_db

# ------------------------------------------
# 🔰 Load environment
# ------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30


# ------------------------------------------
# 🔐 Auth Helper Functions
# ------------------------------------------
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------------------------------
# 🚀 FastAPI App Initialization
# ------------------------------------------
app = FastAPI(title="Community Chat Hub - Realtime AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize local SQLite
init_db()

# ------------------------------------------
# 💬 WebSocket Connection Manager
# ------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, community: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(community, []).append(websocket)
        print(f"🔗 {community}: client connected")

    def disconnect(self, community: str, websocket: WebSocket):
        conns = self.active_connections.get(community, [])
        if websocket in conns:
            conns.remove(websocket)
            print(f"❌ {community}: client disconnected")

    async def broadcast(self, community: str, message: dict):
        conns = self.active_connections.get(community, [])
        alive = []
        for ws in conns:
            try:
                await ws.send_json(message)
                alive.append(ws)
            except Exception:
                pass
        self.active_connections[community] = alive


manager = ConnectionManager()

# ------------------------------------------
# 📦 Request Schemas
# ------------------------------------------
class ChatIn(BaseModel):
    community: str
    username: str
    content: str
    role: str = "user"


class QueryIn(BaseModel):
    community: str
    question: str


class OpportunityIn(BaseModel):
    community: str
    title: str
    description: str
    category: str
    tags: List[str] = []
    requirements: List[str] = []
    deadline: str = None
    posted_by: str = None


class UserProfileIn(BaseModel):
    username: str
    skills: List[str] = []
    interests: List[str] = []
    bio: str = ""


class TemplateInstanceIn(BaseModel):
    community: str
    username: str
    template_id: str
    filled_data: Dict


class FieldSuggestionIn(BaseModel):
    field_name: str
    field_label: str
    template_context: Dict
    user_context: Dict
    community_context: str = ""


class OrganizationIn(BaseModel):
    org_name: str
    admin_username: str
    description: str = ""
    settings: Dict = {}


class RegisterIn(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = ""


class LoginIn(BaseModel):
    username: str
    password: str


class RefreshTokenIn(BaseModel):
    refresh_token: str


# ------------------------------------------
# 🔐 Authentication Endpoints
# ------------------------------------------
@app.get("/")
async def root():
    """Root endpoint to verify server is running"""
    return {
        "message": "AI Community Platform API",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "auth_login": "/api/auth/login",
            "auth_register": "/api/auth/register"
        }
    }


@app.post("/api/auth/register")
async def api_register(data: RegisterIn):
    """Register a new user"""
    try:
        ref = firebase_db.reference('users')
        
        # Check if user exists
        users = ref.get() or {}
        if data.username in users:
            return {"ok": False, "error": "Username already exists"}
        
        # Check email uniqueness
        for user_data in users.values():
            if user_data.get('email') == data.email:
                return {"ok": False, "error": "Email already registered"}
        
        # Create user
        user_data = {
            "username": data.username,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "full_name": data.full_name,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "is_verified": False,
            "avatar_url": f"https://ui-avatars.com/api/?name={data.username}&background=random",
            "bio": "",
            "last_login": None
        }
        
        ref.child(data.username).set(user_data)
        
        return {
            "ok": True,
            "username": data.username,
            "email": data.email,
            "full_name": data.full_name,
            "message": "User registered successfully"
        }
        
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/auth/login")
async def api_login(data: LoginIn):
    """Login user and return tokens"""
    try:
        ref = firebase_db.reference(f'users/{data.username}')
        user_data = ref.get()
        
        if not user_data:
            return {"ok": False, "error": "Invalid username or password"}
        
        if not user_data.get('is_active'):
            return {"ok": False, "error": "Account is deactivated"}
        
        # Verify password
        if not verify_password(data.password, user_data['password_hash']):
            return {"ok": False, "error": "Invalid username or password"}
        
        # Update last login
        ref.update({"last_login": datetime.utcnow().isoformat()})
        
        # Remove password hash from returned data
        user_data.pop('password_hash', None)
        
        # Create tokens
        access_token = create_access_token({"sub": data.username})
        refresh_token = create_refresh_token({"sub": data.username})
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "session_id": session_id,
            "username": data.username,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "is_active": True
        }
        firebase_db.reference(f'sessions/{session_id}').set(session_data)
        
        return {
            "ok": True,
            "user": user_data,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_id": session_id
        }
        
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/auth/logout")
async def api_logout():
    """Logout user"""
    try:
        return {"ok": True, "message": "Logged out successfully"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/auth/refresh")
async def api_refresh_token(data: RefreshTokenIn):
    """Refresh access token"""
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            return {"ok": False, "error": "Invalid refresh token"}
        
        username = payload.get("sub")
        access_token = create_access_token({"sub": username})
        
        return {"ok": True, "access_token": access_token}
        
    except jwt.ExpiredSignatureError:
        return {"ok": False, "error": "Token has expired"}
    except jwt.JWTError:
        return {"ok": False, "error": "Invalid token"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/auth/me")
async def api_get_current_user():
    """Get current user info - placeholder"""
    return {"ok": True, "message": "Auth endpoint available"}


# ------------------------------------------
# 🤖 Helper: Gemini API call
# ------------------------------------------
async def call_gemini(prompt: str, timeout: int = 40) -> str:
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API key not configured."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("❌ Gemini error:", e)
        return f"(Gemini error: {e})"


# ------------------------------------------
# 🧠 Background Task: Summarize + Add to KB
# ------------------------------------------
async def background_summarize_and_add(community: str):
    """Fetch recent messages, summarize them, and add summary to KB."""
    rows = fetch_messages(community, limit=200)
    if not rows:
        return

    chat_text = "\n".join(
        [f"{r['username']}: {r['content']}" for r in rows[-100:]]
    )

    prompt = (
        "Summarize the following community chat into short bullet points and key insights:\n\n"
        + chat_text
    )

    try:
        summary = await call_gemini(prompt, timeout=60)
        add_to_kb(community, summary)
        print(f"🧠 Summary added to KB for '{community}'")
        await manager.broadcast(
            community,
            {
                "id": f"summary-{int(time.time())}",
                "role": "system",
                "content": f"📘 Summary updated:\n{summary}",
            },
        )
    except Exception as e:
        print("⚠️ Background summarization failed:", e)


# ------------------------------------------
# 📩 API: Send message
# ------------------------------------------
@app.post("/api/send")
async def api_send(chat: ChatIn, background_tasks: BackgroundTasks):
    """Receive chat message, broadcast to all, and trigger summarization."""
    msg_id = add_message(chat.community, chat.username, chat.content, chat.role)
    payload = {"id": msg_id, "role": chat.role, "username": chat.username, "content": chat.content}

    # broadcast new message
    await manager.broadcast(chat.community, payload)

    # Schedule background summarization (async)
    background_tasks.add_task(background_summarize_and_add, chat.community)

    return {"ok": True, "id": msg_id}


# ------------------------------------------
# 📥 API: Fetch messages
# ------------------------------------------
@app.get("/api/messages/{community}")
async def api_get_messages(community: str, limit: int = 200):
    """Return recent messages for a given community."""
    rows = fetch_messages(community, limit=limit)
    return {"messages": rows}


# ------------------------------------------
# 💬 WebSocket: Realtime Chat
# ------------------------------------------
@app.websocket("/ws/{community}")
async def websocket_endpoint(websocket: WebSocket, community: str):
    """Open real-time connection for a community chat."""
    await manager.connect(community, websocket)
    try:
        # On connect, send history
        messages = fetch_messages(community, limit=100)
        for m in messages:
            await websocket.send_json(
                {
                    "id": m.get("id"),
                    "role": m.get("role"),
                    "username": m.get("username"),
                    "content": m.get("content"),
                }
            )

        # Keep the connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(community, websocket)
    except Exception:
        manager.disconnect(community, websocket)


# ------------------------------------------
# 🔍 Knowledge Base Query Endpoint
# ------------------------------------------
@app.post("/api/query")
async def api_query(data: QueryIn):
    """Ask the Knowledge Base a question."""
    community = data.community.strip()
    question = data.question.strip()

    if not question:
        return {"error": "Empty question."}

    results = search_kb(community, question, k=5)
    if not results:
        return {"answer": "⚠️ No relevant documents found in the knowledge base.", "context": ""}

    context = "\n".join(results)
    prompt = f"""
You are an assistant answering questions using the knowledge base.
Use ONLY the context below to answer the question concisely.

Question:
{question}

Knowledge Base Context:
{context}
"""

    answer = await call_gemini(prompt, timeout=60)

    # Store + broadcast the answer
    msg_id = add_message(community, "system", answer, role="system")
    await manager.broadcast(community, {"id": msg_id, "role": "system", "content": answer})

    return {"answer": answer, "context": context}


# ------------------------------------------
# 🏁 Root Endpoint
# ------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "Community Chat AI Backend is running ✅"}


# ------------------------------------------
# 🎯 Opportunity Matching Endpoints
# ------------------------------------------
@app.post("/api/opportunities/create")
async def api_create_opportunity(opp: OpportunityIn):
    """Create a new opportunity."""
    opp_id = add_opportunity(
        opp.community, opp.title, opp.description, opp.category,
        opp.tags, opp.requirements, opp.deadline, opp.posted_by
    )
    
    if opp_id:
        # Track engagement
        if opp.posted_by:
            track_engagement(opp.community, opp.posted_by, "opportunity_posted")
        
        return {"ok": True, "opportunity_id": opp_id}
    
    return {"ok": False, "error": "Failed to create opportunity"}


@app.get("/api/opportunities/{community}")
async def api_get_opportunities(community: str, status: str = "active"):
    """Get opportunities for a community."""
    opportunities = get_opportunities(community, status=status)
    return {"opportunities": opportunities}


@app.get("/api/opportunities/match/{community}/{username}")
async def api_match_opportunities(community: str, username: str, min_score: float = 0.3):
    """Get personalized opportunity matches for a user."""
    matches = match_opportunities(username, community, top_k=10)
    
    # Filter by minimum score
    filtered = [m for m in matches if m["match_score"] >= min_score]
    
    return {"matches": filtered}


@app.post("/api/profile/update")
async def api_update_profile(profile: UserProfileIn):
    """Update user profile."""
    success = update_user_profile(
        profile.username, profile.skills, profile.interests, profile.bio
    )
    return {"ok": success}


@app.get("/api/profile/{username}")
async def api_get_profile(username: str):
    """Get user profile."""
    profile = get_user_profile(username)
    if profile:
        return {"profile": profile}
    return {"profile": None}


# ------------------------------------------
# 📝 Template Assistant Endpoints
# ------------------------------------------
@app.get("/api/templates")
async def api_get_templates():
    """Get all available templates."""
    templates = get_available_templates()
    return {"templates": templates}


@app.get("/api/templates/{template_id}")
async def api_get_template(template_id: str):
    """Get a specific template."""
    template = get_template(template_id)
    if template:
        return {"template": template}
    return {"error": "Template not found"}


@app.post("/api/templates/save")
async def api_save_template(data: TemplateInstanceIn):
    """Save a template instance."""
    instance_id = save_template_instance(
        data.community, data.username, data.template_id, data.filled_data
    )
    
    if instance_id:
        track_engagement(data.community, data.username, "template_created")
        return {"ok": True, "instance_id": instance_id}
    
    return {"ok": False, "error": "Failed to save template"}


@app.get("/api/templates/user/{community}/{username}")
async def api_get_user_templates(community: str, username: str):
    """Get all templates created by a user."""
    templates = get_user_templates(community, username)
    return {"templates": templates}


@app.post("/api/templates/suggest")
async def api_suggest_field(data: FieldSuggestionIn):
    """Get AI suggestion for a template field."""
    suggestion = generate_field_suggestion_sync(
        data.field_name, data.field_label, data.template_context,
        data.user_context, data.community_context
    )
    return {"suggestion": suggestion}


# ------------------------------------------
# 📊 Analytics Endpoints
# ------------------------------------------
@app.get("/api/analytics/stats/{community}")
async def api_get_stats(community: str, days: int = 30):
    """Get community statistics."""
    stats = get_community_stats(community, days)
    return {"stats": stats}


@app.get("/api/analytics/contributors/{community}")
async def api_get_contributors(community: str, days: int = 30, limit: int = 10):
    """Get top contributors."""
    contributors = get_top_contributors(community, days, limit)
    return {"contributors": contributors}


@app.get("/api/analytics/trends/{community}")
async def api_get_trends(community: str, days: int = 30):
    """Get engagement trends."""
    trends = get_engagement_trends(community, days)
    return {"trends": trends}


@app.get("/api/analytics/user/{community}/{username}")
async def api_get_user_engagement(community: str, username: str, days: int = 30):
    """Get user engagement score."""
    score = get_user_engagement_score(username, community, days)
    return {"engagement": score}


@app.get("/api/analytics/report/{community}")
async def api_get_report(community: str, days: int = 30):
    """Generate analytics report."""
    report = generate_analytics_report(community, days)
    return {"report": report}


# ------------------------------------------
# 🏢 Multi-Tenant / Organization Endpoints
# ------------------------------------------
@app.post("/api/organizations/create")
async def api_create_organization(org: OrganizationIn):
    """Create a new organization."""
    org_id = create_organization(
        org.org_name, org.admin_username, org.description, org.settings
    )
    
    if org_id:
        return {"ok": True, "organization_id": org_id}
    
    return {"ok": False, "error": "Failed to create organization or already exists"}


@app.get("/api/organizations/{org_id}")
async def api_get_organization_info(org_id: str):
    """Get organization details."""
    org = get_organization(org_id)
    if org:
        return {"organization": org}
    return {"error": "Organization not found"}


@app.get("/api/organizations/user/{username}")
async def api_get_user_orgs(username: str):
    """Get all organizations a user belongs to."""
    orgs = get_user_organizations(username)
    return {"organizations": orgs}


@app.post("/api/organizations/{org_id}/members/add")
async def api_add_member(org_id: str, username: str, role: str = "member"):
    """Add a member to an organization."""
    success = add_member_to_organization(org_id, username, role)
    return {"ok": success}


@app.post("/api/organizations/{org_id}/invite")
async def api_create_invite(org_id: str, created_by: str, max_uses: int = 1):
    """Create an invite code for an organization."""
    code = create_invite_code(org_id, created_by, max_uses)
    
    if code:
        return {"ok": True, "invite_code": code}
    
    return {"ok": False, "error": "Failed to create invite code"}


@app.post("/api/organizations/join")
async def api_join_organization(code: str, username: str):
    """Join an organization using an invite code."""
    success = use_invite_code(code, username)
    return {"ok": success}


# ------------------------------------------
# 🚀 Run Server
# ------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server...")
    print("📍 API docs: http://localhost:8001/docs")
    print("🔐 Auth endpoints: /api/auth/login, /api/auth/register")
    uvicorn.run(app, host="0.0.0.0", port=8001)
