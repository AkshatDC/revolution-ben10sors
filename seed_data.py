"""
Dummy Data Seeder
Populates the database with realistic dummy data for testing and demo purposes
"""

import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import firebase_admin
from firebase_admin import credentials, db as firebase_db
from auth_manager import AuthManager

# Initialize Firebase if not already done
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://revolution-7a48d-default-rtdb.firebaseio.com/'
    })

fake = Faker()
auth_manager = AuthManager()

# ==================== Configuration ====================

NUM_USERS = 50
NUM_ORGANIZATIONS = 8
NUM_OPPORTUNITIES = 30
NUM_TEMPLATES = 20
NUM_MESSAGES_PER_COMMUNITY = 100

# Skill categories
SKILLS = {
    "technical": ["Python", "JavaScript", "React", "Node.js", "Django", "FastAPI", "Machine Learning", 
                  "Data Science", "AWS", "Docker", "Kubernetes", "SQL", "MongoDB", "TensorFlow", "PyTorch"],
    "business": ["Project Management", "Business Development", "Marketing", "Sales", "Strategy", 
                 "Finance", "Accounting", "HR", "Operations", "Product Management"],
    "creative": ["UI/UX Design", "Graphic Design", "Content Writing", "Video Editing", "Photography",
                 "Branding", "Copywriting", "Animation", "3D Modeling"],
    "soft": ["Leadership", "Communication", "Team Management", "Problem Solving", "Critical Thinking",
             "Negotiation", "Public Speaking", "Time Management"]
}

# Interest categories
INTERESTS = ["AI & Machine Learning", "Startups", "Innovation", "Technology", "Business Growth",
             "Entrepreneurship", "Networking", "Community Building", "Education", "Sustainability",
             "Healthcare", "Finance", "E-commerce", "SaaS", "Mobile Apps", "Web Development",
             "Data Analytics", "Blockchain", "Cybersecurity", "Cloud Computing"]

# Industries
INDUSTRIES = ["Technology", "Healthcare", "Finance", "Education", "E-commerce", "Manufacturing",
              "Consulting", "Marketing", "Real Estate", "Retail", "Transportation", "Energy"]

# Job titles
JOB_TITLES = ["Software Engineer", "Product Manager", "Data Scientist", "Business Analyst",
              "Marketing Manager", "Sales Director", "UX Designer", "DevOps Engineer",
              "Entrepreneur", "Consultant", "Founder", "CTO", "CEO", "VP of Engineering"]


# ==================== Helper Functions ====================

def random_date(start_days_ago=90, end_days_ago=0):
    """Generate random datetime within range"""
    start = datetime.utcnow() - timedelta(days=start_days_ago)
    end = datetime.utcnow() - timedelta(days=end_days_ago)
    return start + (end - start) * random.random()


def random_skills(count=5):
    """Get random skills from different categories"""
    all_skills = []
    for category in SKILLS.values():
        all_skills.extend(category)
    return random.sample(all_skills, min(count, len(all_skills)))


def random_interests(count=4):
    """Get random interests"""
    return random.sample(INTERESTS, min(count, len(INTERESTS)))


# ==================== Seeding Functions ====================

def seed_users():
    """Create 50+ realistic users"""
    print("🌱 Seeding users...")
    
    users_ref = firebase_db.reference('users')
    profiles_ref = firebase_db.reference('user_profiles')
    
    users = []
    
    for i in range(NUM_USERS):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{fake.free_email_domain()}"
        
        # Create user account
        user_data = {
            "username": username,
            "email": email,
            "password_hash": auth_manager.hash_password("password123"),  # Default password
            "full_name": f"{first_name} {last_name}",
            "created_at": random_date(90, 1).isoformat(),
            "is_active": True,
            "is_verified": random.choice([True, True, True, False]),  # 75% verified
            "avatar_url": f"https://ui-avatars.com/api/?name={first_name}+{last_name}&background=random",
            "bio": fake.text(max_nb_chars=200),
            "last_login": random_date(7, 0).isoformat() if random.random() > 0.2 else None
        }
        
        users_ref.child(username).set(user_data)
        
        # Create user profile
        profile_data = {
            "username": username,
            "skills": random_skills(random.randint(3, 8)),
            "interests": random_interests(random.randint(2, 6)),
            "bio": user_data["bio"],
            "job_title": random.choice(JOB_TITLES),
            "industry": random.choice(INDUSTRIES),
            "location": f"{fake.city()}, {fake.country()}",
            "linkedin_url": f"https://linkedin.com/in/{username}",
            "twitter_handle": f"@{username}",
            "metadata": {
                "years_experience": random.randint(0, 20),
                "education": random.choice(["Bachelor's", "Master's", "PhD", "Bootcamp", "Self-taught"]),
                "availability": random.choice(["Full-time", "Part-time", "Freelance", "Not looking"])
            },
            "updated_at": random_date(30, 0).isoformat()
        }
        
        profiles_ref.child(username).set(profile_data)
        users.append(username)
    
    print(f"✅ Created {NUM_USERS} users")
    return users


def seed_organizations(users):
    """Create realistic organizations"""
    print("🌱 Seeding organizations...")
    
    orgs_ref = firebase_db.reference('organizations')
    members_ref = firebase_db.reference('organization_members')
    
    org_names = [
        "AI Innovators Hub",
        "Startup Founders Network",
        "Tech Entrepreneurs Alliance",
        "Data Science Community",
        "Product Management Guild",
        "Digital Marketing Collective",
        "FinTech Pioneers",
        "HealthTech Innovators"
    ]
    
    organizations = []
    
    for i, org_name in enumerate(org_names[:NUM_ORGANIZATIONS]):
        org_id = org_name.lower().replace(" ", "_")
        admin = random.choice(users)
        
        # Select random members (10-20 per org)
        num_members = random.randint(10, 20)
        org_members = random.sample(users, num_members)
        if admin not in org_members:
            org_members.append(admin)
        
        # Create organization
        org_data = {
            "id": org_id,
            "name": org_name,
            "description": fake.text(max_nb_chars=300),
            "admin": admin,
            "members": org_members,
            "settings": {
                "is_private": random.choice([True, False]),
                "require_approval": random.choice([True, False]),
                "max_members": random.choice([50, 100, 500, 1000]),
                "features_enabled": {
                    "chat": True,
                    "kb": True,
                    "opportunities": True,
                    "templates": True,
                    "analytics": True
                }
            },
            "created_at": random_date(180, 30).isoformat(),
            "updated_at": random_date(30, 0).isoformat(),
            "member_count": len(org_members),
            "category": random.choice(INDUSTRIES),
            "logo_url": f"https://ui-avatars.com/api/?name={org_name}&background=random&size=200"
        }
        
        orgs_ref.child(org_id).set(org_data)
        
        # Create member roles
        for member in org_members:
            if member == admin:
                role = "admin"
            elif random.random() < 0.2:  # 20% moderators
                role = "moderator"
            else:
                role = "member"
            
            member_data = {
                "username": member,
                "role": role,
                "joined_at": random_date(150, 5).isoformat()
            }
            
            members_ref.child(f"{org_id}/{member}").set(member_data)
        
        organizations.append(org_id)
    
    print(f"✅ Created {len(organizations)} organizations")
    return organizations


def seed_chat_messages(users, organizations):
    """Create realistic chat messages"""
    print("🌱 Seeding chat messages...")
    
    chats_ref = firebase_db.reference('chats')
    
    message_templates = [
        "Hey everyone! {topic}",
        "I'm working on {topic}. Anyone interested in collaborating?",
        "Does anyone have experience with {topic}?",
        "Just finished {topic}. Happy to share insights!",
        "Looking for recommendations on {topic}",
        "Great discussion today about {topic}!",
        "Can someone help me with {topic}?",
        "Excited to announce {topic}!",
        "What do you all think about {topic}?",
        "Has anyone tried {topic}?"
    ]
    
    topics = [
        "AI integration", "machine learning models", "startup funding", "product launches",
        "user acquisition", "team building", "remote work", "productivity tools",
        "market research", "customer feedback", "growth strategies", "tech stacks"
    ]
    
    total_messages = 0
    
    for org_id in organizations:
        # Get org members
        members_ref = firebase_db.reference(f'organization_members/{org_id}')
        members_data = members_ref.get() or {}
        org_members = list(members_data.keys())
        
        if not org_members:
            continue
        
        for _ in range(NUM_MESSAGES_PER_COMMUNITY):
            sender = random.choice(org_members)
            template = random.choice(message_templates)
            topic = random.choice(topics)
            content = template.format(topic=topic)
            
            message_id = str(uuid.uuid4())
            message_data = {
                "role": "user",
                "user_id": str(uuid.uuid4()),
                "username": sender,
                "content": content,
                "timestamp": random_date(30, 0).timestamp(),
                "reactions": {},
                "thread_count": 0,
                "edited": False
            }
            
            # Add random reactions (20% chance)
            if random.random() < 0.2:
                reactions = ["👍", "❤️", "🎉", "🚀", "💡"]
                for _ in range(random.randint(1, 3)):
                    reactor = random.choice(org_members)
                    reaction = random.choice(reactions)
                    if reaction not in message_data["reactions"]:
                        message_data["reactions"][reaction] = []
                    if reactor not in message_data["reactions"][reaction]:
                        message_data["reactions"][reaction].append(reactor)
            
            chats_ref.child(f"{org_id}/{message_id}").set(message_data)
            total_messages += 1
    
    print(f"✅ Created {total_messages} chat messages")


def seed_opportunities(users, organizations):
    """Create realistic opportunities"""
    print("🌱 Seeding opportunities...")
    
    opps_ref = firebase_db.reference('opportunities')
    
    opp_templates = {
        "job": [
            "Senior {role} - {company}",
            "{role} Position at {company}",
            "Hiring: {role} for {company}"
        ],
        "event": [
            "{event_type} on {topic}",
            "Join us for {event_type}: {topic}",
            "Upcoming {event_type} - {topic}"
        ],
        "collaboration": [
            "Looking for co-founder with {skill} expertise",
            "Seeking {role} for new project",
            "Partnership opportunity in {industry}"
        ],
        "funding": [
            "Seed funding available for {industry} startups",
            "Grant opportunity: {topic}",
            "Investment opportunity in {industry}"
        ]
    }
    
    roles = ["Software Engineer", "Product Manager", "Data Scientist", "Designer", "Marketing Manager"]
    companies = [fake.company() for _ in range(20)]
    event_types = ["Workshop", "Webinar", "Conference", "Meetup", "Hackathon"]
    topics_list = ["AI & ML", "Blockchain", "SaaS", "FinTech", "HealthTech", "EdTech"]
    
    total_opps = 0
    
    for org_id in organizations:
        # Get org members
        members_ref = firebase_db.reference(f'organization_members/{org_id}')
        members_data = members_ref.get() or {}
        org_members = list(members_data.keys())
        
        if not org_members:
            continue
        
        num_opps = random.randint(2, 5)
        
        for _ in range(num_opps):
            category = random.choice(list(opp_templates.keys()))
            template = random.choice(opp_templates[category])
            
            title = template.format(
                role=random.choice(roles),
                company=random.choice(companies),
                event_type=random.choice(event_types),
                topic=random.choice(topics_list),
                skill=random.choice(random_skills(1)),
                industry=random.choice(INDUSTRIES)
            )
            
            opp_id = str(uuid.uuid4())
            opp_data = {
                "id": opp_id,
                "title": title,
                "description": fake.text(max_nb_chars=500),
                "category": category,
                "tags": random.sample(INTERESTS, random.randint(2, 5)),
                "requirements": random_skills(random.randint(2, 4)),
                "deadline": (datetime.utcnow() + timedelta(days=random.randint(7, 90))).isoformat(),
                "posted_by": random.choice(org_members),
                "status": random.choice(["active", "active", "active", "closed"]),  # 75% active
                "created_at": random_date(60, 0).isoformat(),
                "views": random.randint(10, 200),
                "applicants": random.randint(0, 20)
            }
            
            opps_ref.child(f"{org_id}/{opp_id}").set(opp_data)
            total_opps += 1
    
    print(f"✅ Created {total_opps} opportunities")


def seed_analytics(users, organizations):
    """Create analytics engagement data"""
    print("🌱 Seeding analytics data...")
    
    engagement_ref = firebase_db.reference('analytics/engagement')
    
    activity_types = ["message_sent", "question_asked", "opportunity_posted", 
                     "template_created", "kb_contribution", "content_viewed"]
    
    total_activities = 0
    
    for org_id in organizations:
        # Get org members
        members_ref = firebase_db.reference(f'organization_members/{org_id}')
        members_data = members_ref.get() or {}
        org_members = list(members_data.keys())
        
        if not org_members:
            continue
        
        # Create 200-500 engagement events per org
        num_events = random.randint(200, 500)
        
        for _ in range(num_events):
            activity_id = str(uuid.uuid4())
            activity_data = {
                "username": random.choice(org_members),
                "community": org_id,
                "type": random.choice(activity_types),
                "metadata": {},
                "timestamp": random_date(90, 0).isoformat()
            }
            
            engagement_ref.child(f"{org_id}/{activity_id}").set(activity_data)
            total_activities += 1
    
    print(f"✅ Created {total_activities} analytics events")


def seed_knowledge_base(organizations):
    """Create KB entries"""
    print("🌱 Seeding knowledge base...")
    
    kb_ref = firebase_db.reference('knowledgebase')
    
    kb_topics = [
        "Best practices for {topic}",
        "How to implement {topic}",
        "Guide to {topic}",
        "Tips for {topic}",
        "Understanding {topic}"
    ]
    
    topics = ["team collaboration", "product development", "customer acquisition",
              "fundraising", "scaling startups", "remote work", "agile methodology"]
    
    total_entries = 0
    
    for org_id in organizations:
        num_entries = random.randint(5, 15)
        
        for _ in range(num_entries):
            entry_id = str(uuid.uuid4())
            topic = random.choice(topics)
            title_template = random.choice(kb_topics)
            
            entry_data = {
                "id": entry_id,
                "content": f"{title_template.format(topic=topic)}\n\n{fake.text(max_nb_chars=800)}",
                "metadata": {
                    "source": "chat_summary",
                    "topic": topic
                },
                "timestamp": random_date(90, 0).isoformat()
            }
            
            kb_ref.child(f"{org_id}/store/{entry_id}").set(entry_data)
            total_entries += 1
    
    print(f"✅ Created {total_entries} KB entries")


# ==================== Main Seeding Function ====================

def seed_all_data():
    """Seed all dummy data"""
    print("\n" + "="*60)
    print("🌱 STARTING DATA SEEDING")
    print("="*60 + "\n")
    
    try:
        # Seed in order (dependencies matter)
        users = seed_users()
        organizations = seed_organizations(users)
        seed_chat_messages(users, organizations)
        seed_opportunities(users, organizations)
        seed_analytics(users, organizations)
        seed_knowledge_base(organizations)
        
        print("\n" + "="*60)
        print("✅ DATA SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  - Users: {NUM_USERS}")
        print(f"  - Organizations: {len(organizations)}")
        print(f"  - Messages: ~{NUM_MESSAGES_PER_COMMUNITY * len(organizations)}")
        print(f"  - Opportunities: ~{NUM_OPPORTUNITIES}")
        print(f"  - Analytics Events: ~{len(organizations) * 300}")
        print(f"\nDefault password for all users: password123")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR during seeding: {str(e)}")
        raise


if __name__ == "__main__":
    seed_all_data()
