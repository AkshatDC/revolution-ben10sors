"""
Personalized Opportunity Matching System with Tag-Based Matching
Generates opportunities based on user profile tags, skills, interests, and bio
"""

import random
from datetime import datetime, timedelta

# Expanded opportunity database with tags
OPPORTUNITY_DATABASE = [
    # Tech & Development - Frontend
    {"title": "Senior Full-Stack Developer", "type": "Job", "category": "Tech",
     "skills": ["Python", "JavaScript", "React", "Node.js"], "interests": ["Technology", "Coding"],
     "tags": ["python", "javascript", "react", "nodejs", "fullstack", "web", "developer"],
     "description": "Build next-gen SaaS products", "company": "TechVenture Inc.", "urgency_days": 7},
    
    {"title": "Frontend Developer - React", "type": "Job", "category": "Tech",
     "skills": ["React", "JavaScript", "TypeScript", "CSS"], "interests": ["Technology", "Frontend"],
     "tags": ["react", "javascript", "typescript", "frontend", "web", "ui"],
     "description": "Create beautiful user interfaces", "company": "WebCraft Studios", "urgency_days": 10},
    
    {"title": "Vue.js Developer", "type": "Job", "category": "Tech",
     "skills": ["Vue.js", "JavaScript", "Vuex", "CSS"], "interests": ["Technology", "Frontend"],
     "tags": ["vue", "vuejs", "javascript", "frontend", "web", "spa"],
     "description": "Build modern SPAs with Vue", "company": "VueWorks", "urgency_days": 14},
    
    {"title": "Angular Developer", "type": "Job", "category": "Tech",
     "skills": ["Angular", "TypeScript", "RxJS"], "interests": ["Technology", "Frontend"],
     "tags": ["angular", "typescript", "frontend", "web", "spa"],
     "description": "Enterprise Angular applications", "company": "AngularPro", "urgency_days": 9},
    
    # Backend Development
    {"title": "Backend Engineer - Node.js", "type": "Job", "category": "Tech",
     "skills": ["Node.js", "Express", "MongoDB", "API"], "interests": ["Technology", "Backend"],
     "tags": ["nodejs", "backend", "api", "express", "mongodb", "database"],
     "description": "Scalable backend systems", "company": "CloudAPI Inc.", "urgency_days": 12},
    
    {"title": "Python Backend Developer", "type": "Job", "category": "Tech",
     "skills": ["Python", "Django", "Flask", "PostgreSQL"], "interests": ["Technology", "Backend"],
     "tags": ["python", "django", "flask", "backend", "api", "postgresql"],
     "description": "Robust Python applications", "company": "PythonWorks", "urgency_days": 8},
    
    {"title": "Java Spring Boot Developer", "type": "Job", "category": "Tech",
     "skills": ["Java", "Spring Boot", "Microservices"], "interests": ["Technology", "Backend"],
     "tags": ["java", "spring", "springboot", "backend", "microservices"],
     "description": "Enterprise Java systems", "company": "JavaCorp", "urgency_days": 11},
    
    {"title": "Go Developer", "type": "Job", "category": "Tech",
     "skills": ["Go", "Golang", "Microservices", "Docker"], "interests": ["Technology", "Backend"],
     "tags": ["go", "golang", "backend", "microservices", "docker"],
     "description": "High-performance Go services", "company": "GoTech", "urgency_days": 13},
    
    # AI & Machine Learning
    {"title": "AI/ML Engineer", "type": "Job", "category": "AI",
     "skills": ["Machine Learning", "Python", "TensorFlow", "PyTorch"], "interests": ["AI", "ML"],
     "tags": ["ai", "ml", "machinelearning", "python", "tensorflow", "pytorch", "deeplearning"],
     "description": "Cutting-edge AI models", "company": "HealthAI Labs", "urgency_days": 14},
    
    {"title": "Data Scientist", "type": "Job", "category": "Data",
     "skills": ["Python", "R", "Statistics", "ML"], "interests": ["Data Science", "Analytics"],
     "tags": ["datascience", "python", "r", "statistics", "ml", "analytics"],
     "description": "Extract insights from data", "company": "DataInsights Co.", "urgency_days": 10},
    
    {"title": "NLP Engineer", "type": "Job", "category": "AI",
     "skills": ["NLP", "Python", "Transformers", "BERT"], "interests": ["AI", "NLP"],
     "tags": ["nlp", "ai", "python", "transformers", "bert", "language"],
     "description": "Build language understanding systems", "company": "LangTech AI", "urgency_days": 12},
    
    {"title": "Computer Vision Engineer", "type": "Job", "category": "AI",
     "skills": ["Computer Vision", "Python", "OpenCV", "CNN"], "interests": ["AI", "Vision"],
     "tags": ["computervision", "ai", "python", "opencv", "cnn", "deeplearning"],
     "description": "Image recognition systems", "company": "VisionAI", "urgency_days": 15},
    
    # Mobile Development
    {"title": "React Native Developer", "type": "Job", "category": "Mobile",
     "skills": ["React Native", "JavaScript", "Mobile"], "interests": ["Mobile", "Technology"],
     "tags": ["reactnative", "mobile", "javascript", "ios", "android", "app"],
     "description": "Cross-platform mobile apps", "company": "MobileFirst", "urgency_days": 9},
    
    {"title": "iOS Developer", "type": "Job", "category": "Mobile",
     "skills": ["Swift", "iOS", "SwiftUI", "Xcode"], "interests": ["Mobile", "iOS"],
     "tags": ["ios", "swift", "swiftui", "mobile", "apple", "app"],
     "description": "Native iOS applications", "company": "AppleDevs", "urgency_days": 11},
    
    {"title": "Android Developer", "type": "Job", "category": "Mobile",
     "skills": ["Kotlin", "Android", "Jetpack Compose"], "interests": ["Mobile", "Android"],
     "tags": ["android", "kotlin", "mobile", "jetpack", "app"],
     "description": "Modern Android apps", "company": "DroidWorks", "urgency_days": 10},
    
    {"title": "Flutter Developer", "type": "Job", "category": "Mobile",
     "skills": ["Flutter", "Dart", "Mobile"], "interests": ["Mobile", "Technology"],
     "tags": ["flutter", "dart", "mobile", "crossplatform", "app"],
     "description": "Beautiful Flutter applications", "company": "FlutterPro", "urgency_days": 8},
    
    # DevOps & Cloud
    {"title": "DevOps Engineer", "type": "Job", "category": "DevOps",
     "skills": ["DevOps", "Docker", "Kubernetes", "AWS"], "interests": ["DevOps", "Cloud"],
     "tags": ["devops", "docker", "kubernetes", "aws", "cloud", "cicd"],
     "description": "Scale infrastructure", "company": "CloudScale Inc.", "urgency_days": 5},
    
    {"title": "AWS Cloud Architect", "type": "Job", "category": "Cloud",
     "skills": ["AWS", "Cloud Architecture", "Terraform"], "interests": ["Cloud", "Architecture"],
     "tags": ["aws", "cloud", "architecture", "terraform", "devops"],
     "description": "Design cloud solutions", "company": "CloudArch", "urgency_days": 12},
    
    {"title": "Azure DevOps Engineer", "type": "Job", "category": "DevOps",
     "skills": ["Azure", "DevOps", "CI/CD", "Terraform"], "interests": ["Cloud", "DevOps"],
     "tags": ["azure", "devops", "cloud", "cicd", "terraform"],
     "description": "Azure cloud automation", "company": "AzurePro", "urgency_days": 14},
    
    {"title": "Site Reliability Engineer", "type": "Job", "category": "DevOps",
     "skills": ["SRE", "Kubernetes", "Monitoring", "Python"], "interests": ["DevOps", "Reliability"],
     "tags": ["sre", "kubernetes", "monitoring", "devops", "reliability"],
     "description": "Ensure system reliability", "company": "ReliableOps", "urgency_days": 10},
    
    # Blockchain & Web3
    {"title": "Blockchain Developer", "type": "Job", "category": "Blockchain",
     "skills": ["Blockchain", "Solidity", "Web3", "Ethereum"], "interests": ["Blockchain", "Web3"],
     "tags": ["blockchain", "solidity", "web3", "ethereum", "crypto", "smartcontracts"],
     "description": "Build DeFi applications", "company": "CryptoChain", "urgency_days": 10},
    
    {"title": "Smart Contract Developer", "type": "Job", "category": "Blockchain",
     "skills": ["Solidity", "Smart Contracts", "Ethereum"], "interests": ["Blockchain", "DeFi"],
     "tags": ["smartcontracts", "solidity", "ethereum", "blockchain", "defi"],
     "description": "Secure smart contracts", "company": "DeFiLabs", "urgency_days": 13},
    
    {"title": "Web3 Frontend Developer", "type": "Job", "category": "Blockchain",
     "skills": ["React", "Web3.js", "Ethereum", "JavaScript"], "interests": ["Web3", "Frontend"],
     "tags": ["web3", "react", "ethereum", "frontend", "blockchain", "dapp"],
     "description": "DApp user interfaces", "company": "Web3UI", "urgency_days": 11},
    
    # Marketing & Business
    {"title": "Digital Marketing Manager", "type": "Job", "category": "Marketing",
     "skills": ["Marketing", "SEO", "Content", "Social Media"], "interests": ["Marketing", "Business"],
     "tags": ["marketing", "seo", "content", "socialmedia", "digital", "growth"],
     "description": "Lead marketing strategy", "company": "GrowthHub", "urgency_days": 8},
    
    {"title": "Content Marketing Specialist", "type": "Job", "category": "Marketing",
     "skills": ["Content Writing", "SEO", "Marketing"], "interests": ["Content", "Marketing"],
     "tags": ["content", "writing", "seo", "marketing", "copywriting"],
     "description": "Create engaging content", "company": "ContentFirst", "urgency_days": 9},
    
    {"title": "SEO Specialist", "type": "Job", "category": "Marketing",
     "skills": ["SEO", "Analytics", "Content", "Marketing"], "interests": ["SEO", "Marketing"],
     "tags": ["seo", "analytics", "marketing", "google", "optimization"],
     "description": "Optimize search rankings", "company": "SEOPro", "urgency_days": 7},
    
    {"title": "Social Media Manager", "type": "Job", "category": "Marketing",
     "skills": ["Social Media", "Content", "Marketing"], "interests": ["Social Media", "Marketing"],
     "tags": ["socialmedia", "content", "marketing", "community", "engagement"],
     "description": "Manage social presence", "company": "SocialGrowth", "urgency_days": 10},
    
    {"title": "Product Manager", "type": "Job", "category": "Product",
     "skills": ["Product Management", "Agile", "Strategy"], "interests": ["Product", "Business"],
     "tags": ["product", "productmanagement", "agile", "strategy", "roadmap"],
     "description": "Own product roadmap", "company": "ProductCo", "urgency_days": 15},
    
    {"title": "Growth Hacker", "type": "Job", "category": "Marketing",
     "skills": ["Growth Hacking", "Analytics", "Marketing"], "interests": ["Growth", "Startups"],
     "tags": ["growth", "growthhacking", "marketing", "analytics", "startup"],
     "description": "Drive rapid growth", "company": "GrowthLabs", "urgency_days": 6},
    
    {"title": "Business Development Manager", "type": "Job", "category": "Business",
     "skills": ["Business Development", "Sales", "Negotiation"], "interests": ["Business", "Sales"],
     "tags": ["business", "sales", "bd", "partnerships", "negotiation"],
     "description": "Build strategic partnerships", "company": "BizDev Inc.", "urgency_days": 12},
    
    # Design & Creative
    {"title": "UI/UX Designer", "type": "Job", "category": "Design",
     "skills": ["UI Design", "UX Design", "Figma"], "interests": ["Design", "UX"],
     "tags": ["ui", "ux", "design", "figma", "userexperience", "interface"],
     "description": "Design intuitive interfaces", "company": "DesignTech", "urgency_days": 11},
    
    {"title": "Product Designer", "type": "Job", "category": "Design",
     "skills": ["Product Design", "UX", "Prototyping"], "interests": ["Design", "Product"],
     "tags": ["productdesign", "ux", "design", "prototyping", "figma"],
     "description": "End-to-end product design", "company": "ProductDesign Co.", "urgency_days": 13},
    
    {"title": "Graphic Designer", "type": "Job", "category": "Design",
     "skills": ["Graphic Design", "Adobe Creative Suite"], "interests": ["Design", "Art"],
     "tags": ["graphicdesign", "design", "adobe", "creative", "branding"],
     "description": "Create brand identity", "company": "BrandStudio", "urgency_days": 7},
    
    {"title": "Motion Graphics Designer", "type": "Job", "category": "Design",
     "skills": ["Motion Graphics", "After Effects", "Animation"], "interests": ["Design", "Animation"],
     "tags": ["motiongraphics", "animation", "aftereffects", "design", "video"],
     "description": "Animated visual content", "company": "MotionWorks", "urgency_days": 14},
    
    # Data & Analytics
    {"title": "Data Analyst", "type": "Job", "category": "Data",
     "skills": ["Data Analysis", "SQL", "Python", "Tableau"], "interests": ["Data", "Analytics"],
     "tags": ["data", "analytics", "sql", "python", "tableau", "visualization"],
     "description": "Analyze business data", "company": "DataCorp", "urgency_days": 9},
    
    {"title": "Business Intelligence Analyst", "type": "Job", "category": "Data",
     "skills": ["BI", "SQL", "Power BI", "Analytics"], "interests": ["Business", "Analytics"],
     "tags": ["bi", "businessintelligence", "sql", "powerbi", "analytics"],
     "description": "Drive data-driven decisions", "company": "BIAnalytics", "urgency_days": 11},
    
    {"title": "Data Engineer", "type": "Job", "category": "Data",
     "skills": ["Data Engineering", "Python", "Spark", "SQL"], "interests": ["Data", "Engineering"],
     "tags": ["dataengineering", "python", "spark", "sql", "etl", "pipeline"],
     "description": "Build data pipelines", "company": "DataPipe Inc.", "urgency_days": 10},
    
    # Cybersecurity
    {"title": "Security Engineer", "type": "Job", "category": "Security",
     "skills": ["Cybersecurity", "Penetration Testing", "Security"], "interests": ["Security", "Technology"],
     "tags": ["security", "cybersecurity", "pentesting", "infosec", "hacking"],
     "description": "Protect systems from threats", "company": "SecureNet", "urgency_days": 8},
    
    {"title": "Ethical Hacker", "type": "Job", "category": "Security",
     "skills": ["Ethical Hacking", "Penetration Testing"], "interests": ["Security", "Hacking"],
     "tags": ["ethicalhacking", "pentesting", "security", "hacking", "cybersecurity"],
     "description": "Find and fix vulnerabilities", "company": "HackSafe", "urgency_days": 12},
    
    # Partnerships & Startups
    {"title": "Co-Founder for FinTech Startup", "type": "Partnership", "category": "Startup",
     "skills": ["Entrepreneurship", "Finance", "Technology"], "interests": ["Startups", "Entrepreneurship"],
     "tags": ["cofounder", "startup", "fintech", "entrepreneurship", "founder"],
     "description": "Build payment solutions", "company": "FinTech Ventures", "urgency_days": 20},
    
    {"title": "Technical Co-Founder - AI Startup", "type": "Partnership", "category": "Startup",
     "skills": ["AI", "CTO", "Technology", "Leadership"], "interests": ["Startups", "AI"],
     "tags": ["cofounder", "cto", "ai", "startup", "technical", "founder"],
     "description": "Join as CTO for AI platform", "company": "AI Innovations", "urgency_days": 30},
    
    {"title": "Marketing Co-Founder", "type": "Partnership", "category": "Startup",
     "skills": ["Marketing", "Growth", "Strategy"], "interests": ["Startups", "Marketing"],
     "tags": ["cofounder", "marketing", "startup", "growth", "founder"],
     "description": "Lead marketing for SaaS", "company": "SaaS Startup", "urgency_days": 25},
    
    # Events & Speaking
    {"title": "Tech Conference Speaker", "type": "Event", "category": "Speaking",
     "skills": ["Public Speaking", "Technology"], "interests": ["Speaking", "Technology"],
     "tags": ["speaking", "conference", "tech", "publicspeaking", "presentation"],
     "description": "Share expertise with 5000+ attendees", "company": "TechCon", "urgency_days": 3},
    
    {"title": "AI Summit Panelist", "type": "Event", "category": "Speaking",
     "skills": ["AI", "Public Speaking"], "interests": ["AI", "Speaking"],
     "tags": ["ai", "speaking", "panel", "summit", "conference"],
     "description": "Discuss future of AI", "company": "AI Summit", "urgency_days": 5},
    
    {"title": "Startup Pitch Competition", "type": "Event", "category": "Competition",
     "skills": ["Entrepreneurship", "Pitching"], "interests": ["Startups", "Competition"],
     "tags": ["startup", "pitch", "competition", "entrepreneurship", "funding"],
     "description": "Win $100K funding", "company": "Startup Arena", "urgency_days": 18},
    
    {"title": "Hackathon - AI for Good", "type": "Event", "category": "Hackathon",
     "skills": ["Coding", "AI", "Teamwork"], "interests": ["Hackathon", "AI"],
     "tags": ["hackathon", "ai", "coding", "competition", "innovation"],
     "description": "24-hour AI hackathon", "company": "AIHacks", "urgency_days": 4},
    
    {"title": "Web3 Hackathon", "type": "Event", "category": "Hackathon",
     "skills": ["Blockchain", "Coding", "Web3"], "interests": ["Blockchain", "Hackathon"],
     "tags": ["hackathon", "web3", "blockchain", "coding", "crypto"],
     "description": "Build DApps in 48 hours", "company": "Web3Hacks", "urgency_days": 6},
    
    # Freelance & Projects
    {"title": "E-commerce Website Development", "type": "Project", "category": "Freelance",
     "skills": ["Web Development", "E-commerce", "React"], "interests": ["Freelancing", "Web"],
     "tags": ["freelance", "web", "ecommerce", "react", "development", "project"],
     "description": "Build custom e-commerce platform", "company": "RetailTech", "urgency_days": 10},
    
    {"title": "Mobile App Design", "type": "Project", "category": "Freelance",
     "skills": ["UI Design", "Mobile Design", "Figma"], "interests": ["Design", "Freelancing"],
     "tags": ["freelance", "design", "mobile", "ui", "figma", "project"],
     "description": "Design fitness app", "company": "FitLife", "urgency_days": 8},
    
    {"title": "Marketing Campaign", "type": "Project", "category": "Consulting",
     "skills": ["Marketing", "Strategy", "Analytics"], "interests": ["Marketing", "Consulting"],
     "tags": ["freelance", "marketing", "campaign", "consulting", "strategy"],
     "description": "Product launch campaign", "company": "LaunchBoost", "urgency_days": 6},
    
    {"title": "Data Analysis Project", "type": "Project", "category": "Data",
     "skills": ["Data Analysis", "Python", "SQL"], "interests": ["Data", "Freelancing"],
     "tags": ["freelance", "data", "analysis", "python", "sql", "project"],
     "description": "Customer behavior analysis", "company": "DataInsights", "urgency_days": 12},
    
    {"title": "Logo Design", "type": "Project", "category": "Freelance",
     "skills": ["Graphic Design", "Branding"], "interests": ["Design", "Freelancing"],
     "tags": ["freelance", "design", "logo", "branding", "graphic"],
     "description": "Create brand identity", "company": "BrandNew", "urgency_days": 5},
    
    # Mentorship & Teaching
    {"title": "Coding Mentor", "type": "Mentorship", "category": "Education",
     "skills": ["Mentoring", "Teaching", "Programming"], "interests": ["Teaching", "Mentorship"],
     "tags": ["mentor", "teaching", "coding", "education", "programming"],
     "description": "Guide junior developers", "company": "CodeMentor", "urgency_days": 30},
    
    {"title": "AI Workshop Instructor", "type": "Event", "category": "Teaching",
     "skills": ["AI", "Teaching", "Communication"], "interests": ["Teaching", "AI"],
     "tags": ["teaching", "ai", "workshop", "instructor", "education"],
     "description": "Teach AI fundamentals", "company": "AI Academy", "urgency_days": 15},
    
    {"title": "Web Development Bootcamp Instructor", "type": "Job", "category": "Teaching",
     "skills": ["Web Development", "Teaching"], "interests": ["Teaching", "Web"],
     "tags": ["teaching", "web", "bootcamp", "instructor", "education"],
     "description": "Teach full-stack development", "company": "CodeBootcamp", "urgency_days": 20},
    
    # Investment & Advisory
    {"title": "Angel Investor - EdTech", "type": "Investment", "category": "Funding",
     "skills": ["Investment", "Finance", "Business"], "interests": ["Investment", "Education"],
     "tags": ["investment", "angel", "edtech", "funding", "investor"],
     "description": "Invest in EdTech startups", "company": "EdTech Fund", "urgency_days": 25},
    
    {"title": "Startup Advisor - HealthTech", "type": "Advisory", "category": "Consulting",
     "skills": ["Healthcare", "Business", "Strategy"], "interests": ["Healthcare", "Consulting"],
     "tags": ["advisor", "healthtech", "startup", "consulting", "strategy"],
     "description": "Guide health startups", "company": "HealthAdvisors", "urgency_days": 20},
    
    {"title": "Tech Advisor for Non-Profit", "type": "Advisory", "category": "Consulting",
     "skills": ["Technology", "Advising", "Strategy"], "interests": ["Social Impact", "Technology"],
     "tags": ["advisor", "nonprofit", "tech", "consulting", "socialimpact"],
     "description": "Tech strategy for NGO", "company": "TechForGood", "urgency_days": 30},
]


def calculate_match_score(user_profile, opportunity):
    """
    Calculate match score with TAG-BASED MATCHING as primary factor
    Returns score from 0-100
    """
    score = 0
    max_score = 0
    
    # Extract user data
    user_skills = [s.lower().strip() for s in user_profile.get('skills', [])]
    user_interests = [i.lower().strip() for i in user_profile.get('interests', [])]
    user_bio = user_profile.get('bio', '').lower()
    
    # NEW: Extract user tags (primary matching factor)
    user_tags = []
    if 'tags' in user_profile:
        user_tags = [t.lower().strip() for t in user_profile.get('tags', [])]
    
    # TAG MATCHING (50% weight) - PRIMARY FACTOR
    if opportunity.get('tags') and user_tags:
        max_score += 50
        opp_tags = [t.lower() for t in opportunity['tags']]
        tag_matches = sum(1 for tag in user_tags if tag in opp_tags)
        if user_tags:
            score += (tag_matches / len(opp_tags)) * 50
    
    # Skills matching (25% weight)
    if opportunity.get('skills'):
        max_score += 25
        opp_skills = [s.lower() for s in opportunity['skills']]
        skill_matches = sum(1 for skill in user_skills if any(opp_skill in skill or skill in opp_skill for opp_skill in opp_skills))
        if user_skills:
            score += (skill_matches / len(opp_skills)) * 25
    
    # Interests matching (15% weight)
    if opportunity.get('interests'):
        max_score += 15
        opp_interests = [i.lower() for i in opportunity['interests']]
        interest_matches = sum(1 for interest in user_interests if any(opp_int in interest or interest in opp_int for opp_int in opp_interests))
        if user_interests:
            score += (interest_matches / len(opp_interests)) * 15
    
    # Bio keyword matching (10% weight)
    if user_bio and opportunity.get('tags'):
        max_score += 10
        bio_matches = sum(1 for tag in opportunity['tags'] if tag in user_bio)
        if opportunity['tags']:
            score += (bio_matches / len(opportunity['tags'])) * 10
    
    # Normalize score
    if max_score > 0:
        final_score = int((score / max_score) * 100)
    else:
        final_score = 0
    
    # Add slight randomness for variety
    final_score = max(0, min(100, final_score + random.randint(-3, 3)))
    
    return final_score


def get_urgency_text(days):
    """Convert days to urgency text"""
    if days <= 3:
        return f"Urgent: {days} days left", "🔴"
    elif days <= 7:
        return f"Apply before {(datetime.now() + timedelta(days=days)).strftime('%b %d')}", "🟡"
    elif days <= 14:
        return f"Deadline in {days} days", "🟢"
    else:
        return f"Open until {(datetime.now() + timedelta(days=days)).strftime('%b %d')}", "🔵"


def get_personalized_opportunities(user_profile, top_n=5, min_score=30):
    """
    Get personalized opportunities based on user profile TAGS
    Tags are the primary matching factor
    """
    scored_opportunities = []
    
    for opp in OPPORTUNITY_DATABASE:
        score = calculate_match_score(user_profile, opp)
        
        if score >= min_score:
            urgency_text, urgency_icon = get_urgency_text(opp['urgency_days'])
            
            scored_opportunities.append({
                'title': opp['title'],
                'type': opp['type'],
                'category': opp['category'],
                'description': opp['description'],
                'company': opp['company'],
                'match': score,
                'urgency': urgency_text,
                'urgency_icon': urgency_icon,
                'urgency_days': opp['urgency_days']
            })
    
    # Sort by match score and urgency
    scored_opportunities.sort(key=lambda x: (-x['match'], x['urgency_days']))
    
    return scored_opportunities[:top_n]


def get_opportunity_stats(user_profile):
    """Get statistics about opportunities"""
    all_opps = get_personalized_opportunities(user_profile, top_n=200, min_score=0)
    
    high_match = len([o for o in all_opps if o['match'] >= 70])
    medium_match = len([o for o in all_opps if 50 <= o['match'] < 70])
    urgent = len([o for o in all_opps if o['urgency_days'] <= 7])
    
    return {
        'total': len(all_opps),
        'high_match': high_match,
        'medium_match': medium_match,
        'urgent': urgent
    }
