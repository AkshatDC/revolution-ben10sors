"""
Participation Analytics Module
Tracks community engagement, top contributors, and content reach metrics.
"""

from firebase_admin import db
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, Counter
import json


# ============================================================
# Activity Tracking
# ============================================================

def track_engagement(
    community: str,
    username: str,
    activity_type: str,
    metadata: Dict = None
):
    """
    Track user engagement activity.
    
    Args:
        community: Community name
        username: User performing the activity
        activity_type: Type of activity (message, question, answer, share, reaction, etc.)
        metadata: Additional activity metadata
    """
    if metadata is None:
        metadata = {}
    
    engagement = {
        "username": username,
        "community": community,
        "type": activity_type,
        "metadata": metadata,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        ref = db.reference(f'analytics/engagement/{community}')
        ref.push(engagement)
    except Exception as e:
        print(f"❌ Error tracking engagement: {e}")


def track_content_view(
    community: str,
    content_id: str,
    content_type: str,
    viewer_username: str
):
    """Track when content is viewed."""
    view = {
        "content_id": content_id,
        "content_type": content_type,
        "viewer": viewer_username,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        ref = db.reference(f'analytics/content_views/{community}/{content_id}')
        ref.push(view)
    except Exception as e:
        print(f"❌ Error tracking view: {e}")


# ============================================================
# Analytics Queries
# ============================================================

def get_community_stats(community: str, days: int = 30) -> Dict:
    """
    Get overall community statistics.
    
    Args:
        community: Community name
        days: Number of days to analyze
    
    Returns:
        Dictionary with various stats
    """
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    stats = {
        "total_messages": 0,
        "total_users": 0,
        "active_users": 0,
        "total_kb_entries": 0,
        "total_opportunities": 0,
        "avg_messages_per_user": 0,
        "period_days": days
    }
    
    try:
        # Get messages
        msg_ref = db.reference(f'chats/{community}')
        messages = msg_ref.get()
        
        if messages:
            stats["total_messages"] = len(messages)
            
            # Count unique users
            users = set()
            recent_users = set()
            
            for msg in messages.values():
                username = msg.get("username", "")
                if username:
                    users.add(username)
                    
                    # Check if message is recent
                    timestamp = msg.get("timestamp", 0)
                    if isinstance(timestamp, (int, float)):
                        msg_date = datetime.fromtimestamp(timestamp).isoformat()
                        if msg_date >= cutoff_date:
                            recent_users.add(username)
            
            stats["total_users"] = len(users)
            stats["active_users"] = len(recent_users)
            
            if stats["total_users"] > 0:
                stats["avg_messages_per_user"] = round(stats["total_messages"] / stats["total_users"], 2)
        
        # Get KB size
        kb_ref = db.reference(f'knowledgebase/{community}/store')
        kb_data = kb_ref.get()
        if kb_data:
            stats["total_kb_entries"] = len(kb_data)
        
        # Get opportunities
        opp_ref = db.reference(f'opportunities/{community}')
        opp_data = opp_ref.get()
        if opp_data:
            stats["total_opportunities"] = len(opp_data)
        
    except Exception as e:
        print(f"❌ Error getting community stats: {e}")
    
    return stats


def get_top_contributors(community: str, days: int = 30, limit: int = 10) -> List[Dict]:
    """
    Get top contributors by message count.
    
    Args:
        community: Community name
        days: Number of days to analyze
        limit: Number of top contributors to return
    
    Returns:
        List of contributors with stats
    """
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    try:
        msg_ref = db.reference(f'chats/{community}')
        messages = msg_ref.get()
        
        if not messages:
            return []
        
        # Count messages per user
        user_stats = defaultdict(lambda: {
            "username": "",
            "message_count": 0,
            "question_count": 0,
            "last_active": ""
        })
        
        for msg in messages.values():
            username = msg.get("username", "")
            if not username or username in ["KB-Bot", "KB-Summary", "system"]:
                continue
            
            timestamp = msg.get("timestamp", 0)
            if isinstance(timestamp, (int, float)):
                msg_date = datetime.fromtimestamp(timestamp).isoformat()
                
                # Only count recent messages
                if msg_date >= cutoff_date:
                    user_stats[username]["username"] = username
                    user_stats[username]["message_count"] += 1
                    
                    # Check if it's a question
                    content = msg.get("content", "").lower()
                    if "?" in content or content.startswith(("what", "how", "why", "when", "where", "who")):
                        user_stats[username]["question_count"] += 1
                    
                    # Update last active
                    if msg_date > user_stats[username]["last_active"]:
                        user_stats[username]["last_active"] = msg_date
        
        # Sort by message count
        contributors = sorted(
            user_stats.values(),
            key=lambda x: x["message_count"],
            reverse=True
        )
        
        return contributors[:limit]
        
    except Exception as e:
        print(f"❌ Error getting top contributors: {e}")
        return []


def get_engagement_trends(community: str, days: int = 30) -> Dict:
    """
    Get engagement trends over time.
    
    Args:
        community: Community name
        days: Number of days to analyze
    
    Returns:
        Dictionary with daily engagement data
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    trends = {
        "daily_messages": defaultdict(int),
        "daily_active_users": defaultdict(set),
        "activity_types": Counter()
    }
    
    try:
        # Analyze messages
        msg_ref = db.reference(f'chats/{community}')
        messages = msg_ref.get()
        
        if messages:
            for msg in messages.values():
                timestamp = msg.get("timestamp", 0)
                if isinstance(timestamp, (int, float)):
                    msg_datetime = datetime.fromtimestamp(timestamp)
                    
                    if msg_datetime >= cutoff_date:
                        date_key = msg_datetime.strftime("%Y-%m-%d")
                        trends["daily_messages"][date_key] += 1
                        
                        username = msg.get("username", "")
                        if username:
                            trends["daily_active_users"][date_key].add(username)
        
        # Analyze engagement activities
        eng_ref = db.reference(f'analytics/engagement/{community}')
        engagements = eng_ref.get()
        
        if engagements:
            for eng in engagements.values():
                activity_type = eng.get("type", "unknown")
                trends["activity_types"][activity_type] += 1
        
        # Convert sets to counts
        trends["daily_active_users"] = {
            date: len(users) for date, users in trends["daily_active_users"].items()
        }
        
        # Convert to regular dicts for JSON serialization
        trends["daily_messages"] = dict(trends["daily_messages"])
        trends["activity_types"] = dict(trends["activity_types"])
        
    except Exception as e:
        print(f"❌ Error getting engagement trends: {e}")
    
    return trends


def get_content_reach(community: str, content_id: str) -> Dict:
    """
    Get reach metrics for specific content.
    
    Args:
        community: Community name
        content_id: Content identifier
    
    Returns:
        Dictionary with reach metrics
    """
    reach = {
        "total_views": 0,
        "unique_viewers": 0,
        "viewers": []
    }
    
    try:
        ref = db.reference(f'analytics/content_views/{community}/{content_id}')
        views = ref.get()
        
        if views:
            reach["total_views"] = len(views)
            
            viewers = set()
            for view in views.values():
                viewer = view.get("viewer", "")
                if viewer:
                    viewers.add(viewer)
            
            reach["unique_viewers"] = len(viewers)
            reach["viewers"] = list(viewers)
    
    except Exception as e:
        print(f"❌ Error getting content reach: {e}")
    
    return reach


def get_user_engagement_score(username: str, community: str, days: int = 30) -> Dict:
    """
    Calculate engagement score for a user.
    
    Args:
        username: User's name
        community: Community name
        days: Number of days to analyze
    
    Returns:
        Dictionary with engagement metrics and score
    """
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    metrics = {
        "username": username,
        "messages_sent": 0,
        "questions_asked": 0,
        "kb_contributions": 0,
        "opportunities_posted": 0,
        "engagement_score": 0
    }
    
    try:
        # Count messages
        msg_ref = db.reference(f'chats/{community}')
        messages = msg_ref.get()
        
        if messages:
            for msg in messages.values():
                if msg.get("username") == username:
                    timestamp = msg.get("timestamp", 0)
                    if isinstance(timestamp, (int, float)):
                        msg_date = datetime.fromtimestamp(timestamp).isoformat()
                        
                        if msg_date >= cutoff_date:
                            metrics["messages_sent"] += 1
                            
                            content = msg.get("content", "").lower()
                            if "?" in content:
                                metrics["questions_asked"] += 1
        
        # Count KB contributions
        kb_ref = db.reference(f'knowledgebase/{community}/store')
        kb_data = kb_ref.get()
        
        if kb_data:
            for entry in kb_data.values():
                if entry.get("metadata", {}).get("added_by") == username:
                    metrics["kb_contributions"] += 1
        
        # Count opportunities posted
        opp_ref = db.reference(f'opportunities/{community}')
        opp_data = opp_ref.get()
        
        if opp_data:
            for opp in opp_data.values():
                if opp.get("posted_by") == username:
                    metrics["opportunities_posted"] += 1
        
        # Calculate engagement score (weighted)
        score = (
            metrics["messages_sent"] * 1 +
            metrics["questions_asked"] * 2 +
            metrics["kb_contributions"] * 5 +
            metrics["opportunities_posted"] * 3
        )
        
        metrics["engagement_score"] = score
        
    except Exception as e:
        print(f"❌ Error calculating engagement score: {e}")
    
    return metrics


def generate_analytics_report(community: str, days: int = 30) -> str:
    """
    Generate a comprehensive analytics report.
    
    Args:
        community: Community name
        days: Number of days to analyze
    
    Returns:
        Formatted report string
    """
    stats = get_community_stats(community, days)
    contributors = get_top_contributors(community, days, limit=5)
    trends = get_engagement_trends(community, days)
    
    report = f"""
# Analytics Report: {community}
**Period:** Last {days} days
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Community Overview
- **Total Messages:** {stats['total_messages']}
- **Total Users:** {stats['total_users']}
- **Active Users (period):** {stats['active_users']}
- **Knowledge Base Entries:** {stats['total_kb_entries']}
- **Active Opportunities:** {stats['total_opportunities']}
- **Avg Messages/User:** {stats['avg_messages_per_user']}

---

## Top Contributors
"""
    
    for i, contributor in enumerate(contributors, 1):
        report += f"\n{i}. **{contributor['username']}**\n"
        report += f"   - Messages: {contributor['message_count']}\n"
        report += f"   - Questions: {contributor['question_count']}\n"
        report += f"   - Last Active: {contributor['last_active'][:10]}\n"
    
    report += "\n---\n\n## Activity Breakdown\n"
    
    for activity_type, count in trends['activity_types'].items():
        report += f"- **{activity_type.title()}:** {count}\n"
    
    return report
