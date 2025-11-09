"""
Multi-Tenant Architecture & Security
Allows multiple communities/organizations to manage their own spaces securely.
"""

from firebase_admin import db
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
import hashlib
import secrets


# ============================================================
# Organization/Tenant Management
# ============================================================

def create_organization(
    org_name: str,
    admin_username: str,
    description: str = "",
    settings: Dict = None
) -> str:
    """
    Create a new organization/tenant.
    
    Args:
        org_name: Organization name (will be used as community ID)
        admin_username: Username of the organization admin
        description: Organization description
        settings: Custom organization settings
    
    Returns:
        Organization ID
    """
    if settings is None:
        settings = {}
    
    org_id = org_name.lower().replace(" ", "_")
    
    organization = {
        "id": org_id,
        "name": org_name,
        "description": description,
        "admin": admin_username,
        "members": [admin_username],
        "settings": {
            "is_private": settings.get("is_private", False),
            "require_approval": settings.get("require_approval", True),
            "max_members": settings.get("max_members", 1000),
            "features_enabled": settings.get("features_enabled", {
                "chat": True,
                "kb": True,
                "opportunities": True,
                "templates": True,
                "analytics": True
            })
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        ref = db.reference(f'organizations/{org_id}')
        existing = ref.get()
        
        if existing:
            print(f"⚠️ Organization {org_name} already exists")
            return None
        
        ref.set(organization)
        print(f"✅ Organization created: {org_name}")
        return org_id
    except Exception as e:
        print(f"❌ Error creating organization: {e}")
        return None





def update_organization_settings(org_id: str, settings: Dict) -> bool:
    """Update organization settings."""
    try:
        ref = db.reference(f'organizations/{org_id}')
        org = ref.get()
        
        if not org:
            return False
        
        current_settings = org.get("settings", {})
        current_settings.update(settings)
        
        ref.update({
            "settings": current_settings,
            "updated_at": datetime.now().isoformat()
        })
        
        print(f"✅ Organization settings updated: {org_id}")
        return True
    except Exception as e:
        print(f"❌ Error updating organization: {e}")
        return False


# ============================================================
# Member Management & Access Control
# ============================================================

def add_member_to_organization(org_id: str, username: str, role: str = "member") -> bool:
    """
    Add a member to an organization.
    
    Args:
        org_id: Organization ID
        username: Username to add
        role: Member role (admin, moderator, member)
    
    Returns:
        Success status
    """
    try:
        org_ref = db.reference(f'organizations/{org_id}')
        org = org_ref.get()
        
        if not org:
            print(f"⚠️ Organization {org_id} not found")
            return False
        
        members = org.get("members", [])
        
        if username in members:
            print(f"⚠️ User {username} already a member of {org_id}")
            return False
        
        members.append(username)
        org_ref.update({"members": members})
        
        # Store member role
        member_ref = db.reference(f'organization_members/{org_id}/{username}')
        member_ref.set({
            "username": username,
            "role": role,
            "joined_at": datetime.now().isoformat()
        })
        
        print(f"✅ Added {username} to {org_id} as {role}")
        return True
    except Exception as e:
        print(f"❌ Error adding member: {e}")
        return False


def remove_member_from_organization(org_id: str, username: str) -> bool:
    """Remove a member from an organization."""
    try:
        org_ref = db.reference(f'organizations/{org_id}')
        org = org_ref.get()
        
        if not org:
            return False
        
        members = org.get("members", [])
        
        if username not in members:
            return False
        
        # Don't allow removing the admin
        if username == org.get("admin"):
            print(f"⚠️ Cannot remove admin from organization")
            return False
        
        members.remove(username)
        org_ref.update({"members": members})
        
        # Remove member role
        member_ref = db.reference(f'organization_members/{org_id}/{username}')
        member_ref.delete()
        
        print(f"✅ Removed {username} from {org_id}")
        return True
    except Exception as e:
        print(f"❌ Error removing member: {e}")
        return False


def get_member_role(org_id: str, username: str) -> Optional[str]:
    """Get a member's role in an organization."""
    try:
        ref = db.reference(f'organization_members/{org_id}/{username}')
        member = ref.get()
        
        if member:
            return member.get("role", "member")
        
        return None
    except Exception as e:
        print(f"❌ Error getting member role: {e}")
        return None


def is_member(org_id: str, username: str) -> bool:
    """Check if a user is a member of an organization."""
    try:
        org_ref = db.reference(f'organizations/{org_id}')
        org = org_ref.get()
        
        if not org:
            return False
        
        members = org.get("members", [])
        return username in members
    except Exception as e:
        print(f"❌ Error checking membership: {e}")
        return False


def is_admin(org_id: str, username: str) -> bool:
    """Check if a user is an admin of an organization."""
    try:
        org_ref = db.reference(f'organizations/{org_id}')
        org = org_ref.get()
        
        if not org:
            return False
        
        return org.get("admin") == username
    except Exception as e:
        print(f"❌ Error checking admin status: {e}")
        return False


def get_user_organizations(username: str) -> List[Dict]:
    """Get all organizations a user is a member of."""
    try:
        orgs_ref = db.reference('organizations')
        all_orgs = orgs_ref.get()
        
        if not all_orgs:
            return []
        
        user_orgs = []
        for org in all_orgs.values():
            members = org.get("members", [])
            if username in members:
                user_orgs.append(org)
        
        return user_orgs
    except Exception as e:
        print(f"❌ Error getting user organizations: {e}")
        return []


# ============================================================
# Access Control & Permissions
# ============================================================

def check_permission(org_id: str, username: str, action: str) -> bool:
    """
    Check if a user has permission to perform an action.
    
    Args:
        org_id: Organization ID
        username: Username
        action: Action to check (read, write, delete, admin)
    
    Returns:
        True if user has permission
    """
    # Check if user is a member
    if not is_member(org_id, username):
        return False
    
    # Get user role
    role = get_member_role(org_id, username)
    
    if not role:
        return False
    
    # Define permissions by role
    permissions = {
        "admin": ["read", "write", "delete", "admin", "moderate"],
        "moderator": ["read", "write", "moderate"],
        "member": ["read", "write"]
    }
    
    allowed_actions = permissions.get(role, [])
    return action in allowed_actions


def create_invite_code(org_id: str, created_by: str, max_uses: int = 1, expires_in_days: int = 7) -> str:
    """
    Create an invite code for an organization.
    
    Args:
        org_id: Organization ID
        created_by: Username who created the invite
        max_uses: Maximum number of times the code can be used
        expires_in_days: Number of days until expiration
    
    Returns:
        Invite code
    """
    code = secrets.token_urlsafe(16)
    
    invite = {
        "code": code,
        "org_id": org_id,
        "created_by": created_by,
        "max_uses": max_uses,
        "uses": 0,
        "expires_at": (datetime.now() + timedelta(days=expires_in_days)).isoformat(),
        "created_at": datetime.now().isoformat()
    }
    
    try:
        ref = db.reference(f'invite_codes/{code}')
        ref.set(invite)
        print(f"✅ Invite code created: {code}")
        return code
    except Exception as e:
        print(f"❌ Error creating invite code: {e}")
        return None


def use_invite_code(code: str, username: str) -> bool:
    """
    Use an invite code to join an organization.
    
    Args:
        code: Invite code
        username: Username joining
    
    Returns:
        Success status
    """
    try:
        ref = db.reference(f'invite_codes/{code}')
        invite = ref.get()
        
        if not invite:
            print(f"⚠️ Invalid invite code")
            return False
        
        # Check expiration
        expires_at = datetime.fromisoformat(invite["expires_at"])
        if datetime.now() > expires_at:
            print(f"⚠️ Invite code expired")
            return False
        
        # Check max uses
        if invite["uses"] >= invite["max_uses"]:
            print(f"⚠️ Invite code already used maximum times")
            return False
        
        # Add member to organization
        org_id = invite["org_id"]
        success = add_member_to_organization(org_id, username, role="member")
        
        if success:
            # Increment uses
            ref.update({"uses": invite["uses"] + 1})
            return True
        
        return False
    except Exception as e:
        print(f"❌ Error using invite code: {e}")
        return False


# ============================================================
# Data Isolation
# ============================================================

def get_organization_data_path(org_id: str, data_type: str) -> str:
    """
    Get the Firebase path for organization-specific data.
    Ensures data isolation between organizations.
    
    Args:
        org_id: Organization ID
        data_type: Type of data (chats, kb, opportunities, etc.)
    
    Returns:
        Firebase path
    """
    valid_types = ["chats", "knowledgebase", "opportunities", "templates", "analytics"]
    
    if data_type not in valid_types:
        raise ValueError(f"Invalid data type: {data_type}")
    
    return f"{data_type}/{org_id}"


def verify_data_access(org_id: str, username: str, data_type: str, action: str = "read") -> bool:
    """
    Verify that a user has access to specific organization data.
    
    Args:
        org_id: Organization ID
        username: Username
        data_type: Type of data being accessed
        action: Action being performed (read, write, delete)
    
    Returns:
        True if access is allowed
    """
    # Check if organization exists
    org = get_organization(org_id)
    if not org:
        return False
    
    # Check if organization is private
    is_private = org.get("settings", {}).get("is_private", False)
    
    # If private, user must be a member
    if is_private and not is_member(org_id, username):
        return False
    
    # Check specific permissions for write/delete actions
    if action in ["write", "delete"]:
        return check_permission(org_id, username, action)
    
    # Read access allowed for members (or everyone if public)
    return True if not is_private else is_member(org_id, username)
