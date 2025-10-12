"""
Authentication and Authorization Manager
Handles JWT tokens, session management, password hashing, and role-based access control
"""

import os
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from functools import wraps
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import db as firebase_db

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()


class AuthManager:
    """Manages authentication and authorization"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    # ==================== Password Management ====================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    # ==================== Token Management ====================
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    # ==================== User Management ====================
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str = "") -> Dict:
        """Register a new user"""
        try:
            ref = firebase_db.reference('users')
            
            # Check if user exists
            users = ref.get() or {}
            if username in users:
                raise HTTPException(status_code=400, detail="Username already exists")
            
            # Check email uniqueness
            for user_data in users.values():
                if user_data.get('email') == email:
                    raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create user
            user_data = {
                "username": username,
                "email": email,
                "password_hash": self.hash_password(password),
                "full_name": full_name,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "is_verified": False,
                "avatar_url": f"https://ui-avatars.com/api/?name={username}&background=random",
                "bio": "",
                "last_login": None
            }
            
            ref.child(username).set(user_data)
            
            return {
                "username": username,
                "email": email,
                "full_name": full_name,
                "message": "User registered successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user and return user data"""
        try:
            ref = firebase_db.reference(f'users/{username}')
            user_data = ref.get()
            
            if not user_data:
                return None
            
            if not user_data.get('is_active'):
                raise HTTPException(status_code=403, detail="Account is deactivated")
            
            # Verify password
            if not self.verify_password(password, user_data['password_hash']):
                return None
            
            # Update last login
            ref.update({"last_login": datetime.utcnow().isoformat()})
            
            # Remove password hash from returned data
            user_data.pop('password_hash', None)
            return user_data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user data by username"""
        try:
            ref = firebase_db.reference(f'users/{username}')
            user_data = ref.get()
            
            if user_data:
                user_data.pop('password_hash', None)
            
            return user_data
        except Exception:
            return None
    
    # ==================== Session Management ====================
    
    def create_session(self, username: str) -> Dict:
        """Create a new session for a user"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "session_id": session_id,
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "is_active": True
        }
        
        ref = firebase_db.reference(f'sessions/{session_id}')
        ref.set(session_data)
        
        return session_data
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate a session"""
        try:
            ref = firebase_db.reference(f'sessions/{session_id}')
            session_data = ref.get()
            
            if not session_data:
                return None
            
            if not session_data.get('is_active'):
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.utcnow() > expires_at:
                ref.update({"is_active": False})
                return None
            
            return session_data
        except Exception:
            return None
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session (logout)"""
        try:
            ref = firebase_db.reference(f'sessions/{session_id}')
            ref.update({"is_active": False})
        except Exception:
            pass


# ==================== Dependency Injection ====================

auth_manager = AuthManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = auth_manager.decode_token(token)
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = auth_manager.get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


async def get_current_active_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Dependency to get current active user"""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


# ==================== Role-Based Access Control ====================

class RoleChecker:
    """Check if user has required role"""
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: Dict = Depends(get_current_active_user)):
        # Get user's roles from organizations
        username = current_user.get("username")
        
        try:
            ref = firebase_db.reference('organization_members')
            all_memberships = ref.get() or {}
            
            user_roles = set()
            for org_id, members in all_memberships.items():
                if username in members:
                    role = members[username].get('role', 'member')
                    user_roles.add(role)
            
            # Check if user has any of the allowed roles
            if not user_roles.intersection(self.allowed_roles):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required roles: {self.allowed_roles}"
                )
            
            return current_user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Role check failed: {str(e)}")


def require_roles(*roles: str):
    """Decorator to require specific roles"""
    return RoleChecker(list(roles))


# Admin, Moderator, Member role checkers
require_admin = require_roles("admin")
require_moderator = require_roles("admin", "moderator")
require_member = require_roles("admin", "moderator", "member")


# ==================== Permission Checks ====================

def check_org_permission(username: str, org_id: str, required_permission: str) -> bool:
    """Check if user has specific permission in an organization"""
    try:
        ref = firebase_db.reference(f'organization_members/{org_id}/{username}')
        member_data = ref.get()
        
        if not member_data:
            return False
        
        role = member_data.get('role', 'member')
        
        # Define permissions for each role
        permissions = {
            'admin': ['read', 'write', 'delete', 'moderate', 'admin', 'manage_members'],
            'moderator': ['read', 'write', 'moderate', 'delete_own'],
            'member': ['read', 'write', 'delete_own']
        }
        
        role_permissions = permissions.get(role, [])
        return required_permission in role_permissions
        
    except Exception:
        return False


def verify_org_access(username: str, org_id: str, permission: str = "read"):
    """Verify user has access to organization (raises HTTPException if not)"""
    if not check_org_permission(username, org_id, permission):
        raise HTTPException(
            status_code=403,
            detail=f"You don't have '{permission}' permission in this organization"
        )
