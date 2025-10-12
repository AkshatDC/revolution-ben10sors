"""
Opportunity Matching Engine
Matches users with relevant business opportunities, events, and collaborations
based on their profile, activity, and interests.
"""

from firebase_admin import db
from datetime import datetime
from typing import List, Dict, Optional
import uuid
from difflib import SequenceMatcher


# ============================================================
# Opportunity Storage & Retrieval
# ============================================================

def add_opportunity(
    community: str,
    title: str,
    description: str,
    category: str,
    tags: List[str] = None,
    requirements: List[str] = None,
    deadline: str = None,
    posted_by: str = None,
    metadata: dict = None
) -> str:
    """
    Add a new opportunity to the community.
    
    Args:
        community: Community name
        title: Opportunity title
        description: Detailed description
        category: Type (e.g., 'event', 'collaboration', 'job', 'funding')
        tags: List of relevant tags
        requirements: List of requirements/skills needed
        deadline: Deadline date (ISO format)
        posted_by: Username who posted
        metadata: Additional metadata
    
    Returns:
        Opportunity ID
    """
    if tags is None:
        tags = []
    if requirements is None:
        requirements = []
    if metadata is None:
        metadata = {}
    
    opportunity = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "category": category,
        "tags": tags,
        "requirements": requirements,
        "deadline": deadline,
        "posted_by": posted_by,
        "metadata": metadata,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    try:
        ref = db.reference(f'opportunities/{community}')
        ref.push(opportunity)
        print(f"✅ Opportunity added: {title} in {community}")
        return opportunity["id"]
    except Exception as e:
        print(f"❌ Error adding opportunity: {e}")
        return None


def get_opportunities(community: str, status: str = "active", limit: int = 50) -> List[Dict]:
    """
    Fetch opportunities for a community.
    
    Args:
        community: Community name
        status: Filter by status ('active', 'closed', 'all')
        limit: Maximum number to return
    
    Returns:
        List of opportunity dictionaries
    """
    try:
        ref = db.reference(f'opportunities/{community}')
        data = ref.order_by_key().limit_to_last(limit).get()
        
        if not data:
            return []
        
        opportunities = list(data.values())
        
        if status != "all":
            opportunities = [opp for opp in opportunities if opp.get("status") == status]
        
        # Sort by created_at descending
        opportunities.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return opportunities
    except Exception as e:
        print(f"❌ Error fetching opportunities: {e}")
        return []


def update_opportunity_status(community: str, opportunity_id: str, status: str):
    """Update the status of an opportunity (active/closed)."""
    try:
        ref = db.reference(f'opportunities/{community}')
        data = ref.get()
        
        if not data:
            return False
        
        for key, opp in data.items():
            if opp.get("id") == opportunity_id:
                ref.child(key).update({"status": status})
                print(f"✅ Updated opportunity {opportunity_id} status to {status}")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Error updating opportunity: {e}")
        return False


# ============================================================
# User Profile & Interest Tracking
# ============================================================

def update_user_profile(
    username: str,
    skills: List[str] = None,
    interests: List[str] = None,
    bio: str = None,
    tags: List[str] = None,
    metadata: dict = None
):
    """
    Update or create a user profile with skills, interests, and tags.
    Tags are the primary factor for opportunity matching.
    """
    if skills is None:
        skills = []
    if interests is None:
        interests = []
    if tags is None:
        tags = []
    if metadata is None:
        metadata = {}
    
    profile = {
        "username": username,
        "skills": skills,
        "interests": interests,
        "tags": tags,
        "bio": bio or "",
        "metadata": metadata,
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        ref = db.reference(f'user_profiles/{username}')
        ref.set(profile)
        print(f"✅ Profile updated for {username} with {len(tags)} tags")
        return True
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        return False


def get_user_profile(username: str) -> Optional[Dict]:
    """Fetch user profile."""
    try:
        ref = db.reference(f'user_profiles/{username}')
        profile = ref.get()
        return profile
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")
        return None


def track_user_activity(username: str, community: str, activity_type: str, content: str):
    """
    Track user activity for better matching.
    
    Args:
        username: User's name
        community: Community name
        activity_type: Type of activity (message, question, share, etc.)
        content: Activity content
    """
    activity = {
        "username": username,
        "community": community,
        "type": activity_type,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        ref = db.reference(f'user_activity/{username}')
        ref.push(activity)
    except Exception as e:
        print(f"❌ Error tracking activity: {e}")


# ============================================================
# Matching Algorithm
# ============================================================

def calculate_match_score(opportunity: Dict, user_profile: Dict, user_activity: List[Dict]) -> float:
    """
    Calculate match score between opportunity and user.
    
    Returns:
        Score between 0 and 1
    """
    score = 0.0
    
    # Extract opportunity data
    opp_tags = set([tag.lower() for tag in opportunity.get("tags", [])])
    opp_requirements = set([req.lower() for req in opportunity.get("requirements", [])])
    opp_description = opportunity.get("description", "").lower()
    
    # Extract user data
    user_skills = set([skill.lower() for skill in user_profile.get("skills", [])])
    user_interests = set([interest.lower() for interest in user_profile.get("interests", [])])
    
    # 1. Skills match (40% weight)
    if opp_requirements:
        skills_overlap = len(user_skills & opp_requirements)
        skills_score = skills_overlap / len(opp_requirements)
        score += skills_score * 0.4
    
    # 2. Interest match (30% weight)
    if opp_tags:
        interest_overlap = len(user_interests & opp_tags)
        interest_score = interest_overlap / len(opp_tags) if opp_tags else 0
        score += interest_score * 0.3
    
    # 3. Activity relevance (20% weight)
    if user_activity:
        activity_texts = " ".join([act.get("content", "") for act in user_activity[-20:]]).lower()
        activity_score = SequenceMatcher(None, activity_texts, opp_description).ratio()
        score += activity_score * 0.2
    
    # 4. Bio relevance (10% weight)
    user_bio = user_profile.get("bio", "").lower()
    if user_bio:
        bio_score = SequenceMatcher(None, user_bio, opp_description).ratio()
        score += bio_score * 0.1
    
    return min(score, 1.0)


def match_opportunities(username: str, community: str, top_k: int = 5) -> List[Dict]:
    """
    Find and rank opportunities for a user based on their profile and activity.
    
    Args:
        username: User's name
        community: Community name
        top_k: Number of top matches to return
    
    Returns:
        List of opportunities with match scores
    """
    # Get user profile
    user_profile = get_user_profile(username)
    if not user_profile:
        print(f"⚠️ No profile found for {username}, using empty profile")
        user_profile = {"skills": [], "interests": [], "bio": ""}
    
    # Get user activity
    try:
        ref = db.reference(f'user_activity/{username}')
        activity_data = ref.order_by_key().limit_to_last(50).get()
        user_activity = list(activity_data.values()) if activity_data else []
    except:
        user_activity = []
    
    # Get active opportunities
    opportunities = get_opportunities(community, status="active")
    
    if not opportunities:
        return []
    
    # Calculate match scores
    scored_opportunities = []
    for opp in opportunities:
        score = calculate_match_score(opp, user_profile, user_activity)
        scored_opportunities.append({
            "opportunity": opp,
            "match_score": round(score, 3)
        })
    
    # Sort by score descending
    scored_opportunities.sort(key=lambda x: x["match_score"], reverse=True)
    
    return scored_opportunities[:top_k]


def get_opportunity_recommendations(username: str, community: str, min_score: float = 0.3) -> List[Dict]:
    """
    Get personalized opportunity recommendations for a user.
    Only returns opportunities with match score above threshold.
    """
    matches = match_opportunities(username, community, top_k=10)
    
    # Filter by minimum score
    recommendations = [m for m in matches if m["match_score"] >= min_score]
    
    print(f"🎯 Found {len(recommendations)} recommendations for {username} in {community}")
    
    return recommendations
