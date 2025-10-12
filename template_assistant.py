"""
AI-Powered Template Assistance
Helps users fill standard business templates like proposals, reports, and documents
using AI suggestions based on context and user data.
"""

import os
from typing import Dict, List, Optional
import httpx
from dotenv import load_dotenv
from firebase_admin import db
from datetime import datetime
import uuid
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# ============================================================
# Template Storage
# ============================================================

TEMPLATE_LIBRARY = {
    "business_proposal": {
        "name": "Business Proposal",
        "fields": [
            {"name": "executive_summary", "label": "Executive Summary", "type": "text", "required": True},
            {"name": "problem_statement", "label": "Problem Statement", "type": "text", "required": True},
            {"name": "proposed_solution", "label": "Proposed Solution", "type": "text", "required": True},
            {"name": "market_analysis", "label": "Market Analysis", "type": "text", "required": False},
            {"name": "financial_projections", "label": "Financial Projections", "type": "text", "required": False},
            {"name": "timeline", "label": "Timeline", "type": "text", "required": False},
            {"name": "team", "label": "Team Information", "type": "text", "required": False},
        ],
        "description": "Standard business proposal template"
    },
    "project_report": {
        "name": "Project Report",
        "fields": [
            {"name": "project_title", "label": "Project Title", "type": "text", "required": True},
            {"name": "objectives", "label": "Objectives", "type": "text", "required": True},
            {"name": "methodology", "label": "Methodology", "type": "text", "required": True},
            {"name": "results", "label": "Results", "type": "text", "required": True},
            {"name": "challenges", "label": "Challenges Faced", "type": "text", "required": False},
            {"name": "conclusion", "label": "Conclusion", "type": "text", "required": True},
            {"name": "recommendations", "label": "Recommendations", "type": "text", "required": False},
        ],
        "description": "Project status or completion report"
    },
    "meeting_minutes": {
        "name": "Meeting Minutes",
        "fields": [
            {"name": "meeting_title", "label": "Meeting Title", "type": "text", "required": True},
            {"name": "date", "label": "Date", "type": "date", "required": True},
            {"name": "attendees", "label": "Attendees", "type": "text", "required": True},
            {"name": "agenda", "label": "Agenda", "type": "text", "required": True},
            {"name": "discussion_points", "label": "Discussion Points", "type": "text", "required": True},
            {"name": "action_items", "label": "Action Items", "type": "text", "required": True},
            {"name": "next_meeting", "label": "Next Meeting", "type": "text", "required": False},
        ],
        "description": "Meeting minutes documentation"
    },
    "grant_application": {
        "name": "Grant Application",
        "fields": [
            {"name": "organization_name", "label": "Organization Name", "type": "text", "required": True},
            {"name": "project_description", "label": "Project Description", "type": "text", "required": True},
            {"name": "funding_amount", "label": "Funding Amount Requested", "type": "text", "required": True},
            {"name": "impact", "label": "Expected Impact", "type": "text", "required": True},
            {"name": "budget_breakdown", "label": "Budget Breakdown", "type": "text", "required": True},
            {"name": "sustainability", "label": "Sustainability Plan", "type": "text", "required": False},
        ],
        "description": "Grant or funding application"
    },
    "partnership_agreement": {
        "name": "Partnership Agreement",
        "fields": [
            {"name": "parties", "label": "Parties Involved", "type": "text", "required": True},
            {"name": "purpose", "label": "Purpose of Partnership", "type": "text", "required": True},
            {"name": "responsibilities", "label": "Responsibilities", "type": "text", "required": True},
            {"name": "benefits", "label": "Benefits", "type": "text", "required": True},
            {"name": "duration", "label": "Duration", "type": "text", "required": True},
            {"name": "terms", "label": "Terms and Conditions", "type": "text", "required": False},
        ],
        "description": "Partnership or collaboration agreement"
    }
}


def get_available_templates() -> Dict:
    """Return all available templates."""
    return TEMPLATE_LIBRARY


def get_template(template_id: str) -> Optional[Dict]:
    """Get a specific template by ID."""
    return TEMPLATE_LIBRARY.get(template_id)


# ============================================================
# AI-Powered Field Suggestions
# ============================================================

async def generate_field_suggestion(
    field_name: str,
    field_label: str,
    template_context: Dict,
    user_context: Dict,
    community_context: str = ""
) -> str:
    """
    Generate AI suggestion for a template field.
    
    Args:
        field_name: Field identifier
        field_label: Human-readable field label
        template_context: Other filled fields in the template
        user_context: User profile and activity data
        community_context: Relevant community discussions/KB
    
    Returns:
        AI-generated suggestion
    """
    if not GEMINI_API_KEY:
        return "⚠️ AI suggestions unavailable (API key not configured)"
    
    # Build context-aware prompt
    prompt = f"""You are an AI assistant helping to fill a business document template.

Field to fill: {field_label}

Context from other fields:
{json.dumps(template_context, indent=2)}

User information:
{json.dumps(user_context, indent=2)}

Community context:
{community_context}

Please provide a professional, concise suggestion for the "{field_label}" field.
Make it specific and actionable based on the context provided.
Keep it between 2-4 sentences unless more detail is clearly needed.
"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            suggestion = data["candidates"][0]["content"]["parts"][0]["text"]
            return suggestion.strip()
    except Exception as e:
        print(f"❌ Error generating suggestion: {e}")
        return f"⚠️ Could not generate suggestion: {str(e)}"


def generate_field_suggestion_sync(
    field_name: str,
    field_label: str,
    template_context: Dict,
    user_context: Dict,
    community_context: str = ""
) -> str:
    """Synchronous version of generate_field_suggestion."""
    if not GEMINI_API_KEY:
        return "⚠️ AI suggestions unavailable (API key not configured)"
    
    prompt = f"""You are an AI assistant helping to fill a business document template.

Field to fill: {field_label}

Context from other fields:
{json.dumps(template_context, indent=2)}

User information:
{json.dumps(user_context, indent=2)}

Community context:
{community_context}

Please provide a professional, concise suggestion for the "{field_label}" field.
Make it specific and actionable based on the context provided.
Keep it between 2-4 sentences unless more detail is clearly needed.
"""
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        import requests
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        suggestion = data["candidates"][0]["content"]["parts"][0]["text"]
        return suggestion.strip()
    except Exception as e:
        print(f"❌ Error generating suggestion: {e}")
        return f"⚠️ Could not generate suggestion: {str(e)}"


# ============================================================
# Template Instance Management
# ============================================================

def save_template_instance(
    community: str,
    username: str,
    template_id: str,
    filled_data: Dict,
    status: str = "draft"
) -> str:
    """
    Save a filled template instance.
    
    Args:
        community: Community name
        username: User who created it
        template_id: Template type
        filled_data: Dictionary of field values
        status: 'draft' or 'completed'
    
    Returns:
        Instance ID
    """
    instance = {
        "id": str(uuid.uuid4()),
        "template_id": template_id,
        "username": username,
        "community": community,
        "data": filled_data,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        ref = db.reference(f'template_instances/{community}/{username}')
        ref.push(instance)
        print(f"✅ Template instance saved: {template_id} for {username}")
        return instance["id"]
    except Exception as e:
        print(f"❌ Error saving template instance: {e}")
        return None


def get_user_templates(community: str, username: str) -> List[Dict]:
    """Get all template instances created by a user."""
    try:
        ref = db.reference(f'template_instances/{community}/{username}')
        data = ref.get()
        
        if not data:
            return []
        
        instances = list(data.values())
        instances.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return instances
    except Exception as e:
        print(f"❌ Error fetching templates: {e}")
        return []


def update_template_instance(
    community: str,
    username: str,
    instance_id: str,
    filled_data: Dict,
    status: str = None
) -> bool:
    """Update an existing template instance."""
    try:
        ref = db.reference(f'template_instances/{community}/{username}')
        data = ref.get()
        
        if not data:
            return False
        
        for key, instance in data.items():
            if instance.get("id") == instance_id:
                updates = {
                    "data": filled_data,
                    "updated_at": datetime.now().isoformat()
                }
                if status:
                    updates["status"] = status
                
                ref.child(key).update(updates)
                print(f"✅ Template instance updated: {instance_id}")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Error updating template: {e}")
        return False


def export_template_to_markdown(instance: Dict, template: Dict) -> str:
    """
    Export a filled template to markdown format.
    
    Args:
        instance: Template instance with filled data
        template: Template definition
    
    Returns:
        Markdown formatted document
    """
    md = f"# {template['name']}\n\n"
    md += f"**Created by:** {instance.get('username', 'Unknown')}\n"
    md += f"**Date:** {instance.get('created_at', 'N/A')}\n"
    md += f"**Status:** {instance.get('status', 'draft').upper()}\n\n"
    md += "---\n\n"
    
    filled_data = instance.get("data", {})
    
    for field in template["fields"]:
        field_name = field["name"]
        field_label = field["label"]
        value = filled_data.get(field_name, "")
        
        md += f"## {field_label}\n\n"
        if value:
            md += f"{value}\n\n"
        else:
            md += "*Not filled*\n\n"
    
    return md


def export_template_to_json(instance: Dict) -> str:
    """Export template instance to JSON."""
    return json.dumps(instance, indent=2)
