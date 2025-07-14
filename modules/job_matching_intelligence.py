# Author: Enhanced by AI Assistant
# Job Matching Intelligence Module
# Smart job filtering and matching based on skills, experience, and preferences

import re
import json
import os
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.helpers import print_lg

# Import Groq AI for job matching
try:
    from modules.ai.groqConnections import groq_create_client
    from config.secrets import groq_api_key, groq_model
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print_lg("⚠️ Groq AI not available for job matching")

@dataclass
class JobMatch:
    """Data class for job matching results."""
    job_id: str
    title: str
    company: str
    match_score: float
    skill_match: float
    experience_match: float
    location_match: float
    salary_match: float
    culture_match: float
    reasons: List[str]
    red_flags: List[str]
    recommendation: str

@dataclass
class UserProfile:
    """Data class for user profile and preferences."""
    skills: List[str]
    experience_years: int
    education_level: str
    preferred_locations: List[str]
    preferred_companies: List[str]
    salary_range: Tuple[int, int]
    work_style_preference: str  # remote, hybrid, onsite
    industry_preferences: List[str]
    job_level_preference: str  # entry, mid, senior, executive
    career_goals: List[str]
    deal_breakers: List[str]

class JobMatchingIntelligence:
    """
    Advanced job matching system that uses AI to find the best job matches.
    """
    
    def __init__(self, profile_path: str = "config/user_profile.json"):
        self.profile_path = profile_path
        self.user_profile = self._load_user_profile()
        self.job_history_path = "data/job_matching_history.json"
        self.matching_history = self._load_matching_history()
        
        # Initialize ML components
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Skill synonyms and mappings
        self.skill_synonyms = self._load_skill_synonyms()
        
        # Company intelligence
        self.company_intelligence = self._load_company_intelligence()

        # Initialize Groq AI client for job matching
        self.groq_client = None
        if GROQ_AVAILABLE and groq_api_key:
            try:
                self.groq_client = groq_create_client(groq_api_key, groq_model)
                if self.groq_client:
                    print_lg("🚀 Groq AI enabled for job matching")
            except Exception as e:
                print_lg(f"⚠️ Failed to initialize Groq AI: {e}")
                self.groq_client = None
        
    def _load_user_profile(self) -> UserProfile:
        """Load user profile from configuration."""
        default_profile = {
            "skills": ["python", "data analysis", "machine learning"],
            "experience_years": 3,
            "education_level": "bachelor",
            "preferred_locations": ["remote", "san francisco", "new york"],
            "preferred_companies": [],
            "salary_range": [70000, 120000],
            "work_style_preference": "remote",
            "industry_preferences": ["technology", "fintech"],
            "job_level_preference": "mid",
            "career_goals": ["data scientist", "ml engineer"],
            "deal_breakers": ["no remote work", "unpaid overtime"]
        }
        
        try:
            if os.path.exists(self.profile_path):
                with open(self.profile_path, 'r') as f:
                    profile_data = json.load(f)
                return UserProfile(**profile_data)
            else:
                # Create default profile
                os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
                with open(self.profile_path, 'w') as f:
                    json.dump(default_profile, f, indent=2)
                return UserProfile(**default_profile)
        except Exception as e:
            print_lg(f"Error loading user profile: {e}")
            return UserProfile(**default_profile)
    
    def _load_matching_history(self) -> Dict:
        """Load job matching history."""
        try:
            if os.path.exists(self.job_history_path):
                with open(self.job_history_path, 'r') as f:
                    return json.load(f)
            else:
                return {"matches": [], "feedback": {}}
        except Exception as e:
            print_lg(f"Error loading matching history: {e}")
            return {"matches": [], "feedback": {}}
    
    def _save_matching_history(self):
        """Save job matching history."""
        try:
            os.makedirs(os.path.dirname(self.job_history_path), exist_ok=True)
            with open(self.job_history_path, 'w') as f:
                json.dump(self.matching_history, f, indent=2)
        except Exception as e:
            print_lg(f"Error saving matching history: {e}")
    
    def _load_skill_synonyms(self) -> Dict:
        """Load skill synonyms for better matching."""
        default_synonyms = {
            "python": ["python", "py", "python3", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "react", "vue", "angular"],
            "machine learning": ["ml", "machine learning", "ai", "artificial intelligence", "deep learning"],
            "data science": ["data science", "data analysis", "analytics", "statistics"],
            "sql": ["sql", "mysql", "postgresql", "database", "rdbms"],
            "cloud": ["aws", "azure", "gcp", "google cloud", "cloud computing"],
            "docker": ["docker", "containerization", "kubernetes", "k8s"]
        }
        
        try:
            synonyms_path = "config/skill_synonyms.json"
            if os.path.exists(synonyms_path):
                with open(synonyms_path, 'r') as f:
                    return json.load(f)
            else:
                with open(synonyms_path, 'w') as f:
                    json.dump(default_synonyms, f, indent=2)
                return default_synonyms
        except Exception as e:
            print_lg(f"Error loading skill synonyms: {e}")
            return default_synonyms
    
    def _load_company_intelligence(self) -> Dict:
        """Load company intelligence data."""
        default_intelligence = {
            "google": {
                "culture": "innovative, fast-paced, data-driven",
                "benefits": "excellent", 
                "work_life_balance": "good",
                "growth_opportunities": "excellent",
                "reputation_score": 9.0
            },
            "microsoft": {
                "culture": "collaborative, inclusive, growth-mindset",
                "benefits": "excellent",
                "work_life_balance": "very good",
                "growth_opportunities": "excellent", 
                "reputation_score": 8.5
            },
            "amazon": {
                "culture": "customer-obsessed, high-performance",
                "benefits": "good",
                "work_life_balance": "challenging",
                "growth_opportunities": "excellent",
                "reputation_score": 7.5
            }
        }
        
        try:
            intelligence_path = "config/company_intelligence.json"
            if os.path.exists(intelligence_path):
                with open(intelligence_path, 'r') as f:
                    return json.load(f)
            else:
                with open(intelligence_path, 'w') as f:
                    json.dump(default_intelligence, f, indent=2)
                return default_intelligence
        except Exception as e:
            print_lg(f"Error loading company intelligence: {e}")
            return default_intelligence
    
    def analyze_job_match(self, job_data: Dict) -> JobMatch:
        """
        Analyzes how well a job matches the user's profile using AI and traditional methods.
        """
        job_id = job_data.get('job_id', 'unknown')
        title = job_data.get('title', 'Unknown')
        company = job_data.get('company', 'Unknown')
        description = job_data.get('description', '')

        print_lg(f"🔍 AI-analyzing job match: {title} at {company}")

        # Use AI analysis if available
        if self.groq_client and description:
            ai_analysis = self._ai_analyze_job_match(job_data)
            if ai_analysis:
                return self._create_job_match_from_ai_analysis(job_data, ai_analysis)

        # Fallback to traditional analysis
        print_lg("🔄 Using traditional job matching analysis")

        # Calculate individual match scores
        skill_match = self._calculate_skill_match(description, title)
        experience_match = self._calculate_experience_match(description)
        location_match = self._calculate_location_match(job_data)
        salary_match = self._calculate_salary_match(job_data)
        culture_match = self._calculate_culture_match(company, description)

        # Calculate overall match score
        weights = {
            'skill': 0.35,
            'experience': 0.20,
            'location': 0.15,
            'salary': 0.15,
            'culture': 0.15
        }

        overall_score = (
            skill_match * weights['skill'] +
            experience_match * weights['experience'] +
            location_match * weights['location'] +
            salary_match * weights['salary'] +
            culture_match * weights['culture']
        )

        # Generate reasons and red flags
        reasons = self._generate_match_reasons(
            skill_match, experience_match, location_match, salary_match, culture_match
        )
        red_flags = self._identify_red_flags(job_data, description)

        # Generate recommendation
        recommendation = self._generate_recommendation(overall_score, red_flags)

        job_match = JobMatch(
            job_id=job_id,
            title=title,
            company=company,
            match_score=overall_score,
            skill_match=skill_match,
            experience_match=experience_match,
            location_match=location_match,
            salary_match=salary_match,
            culture_match=culture_match,
            reasons=reasons,
            red_flags=red_flags,
            recommendation=recommendation
        )

        # Save to history
        self._save_match_to_history(job_match)

        return job_match

    def _ai_analyze_job_match(self, job_data: Dict) -> Optional[Dict]:
        """
        Use Groq AI to analyze job match compatibility.
        """
        try:
            print_lg("🤖 Using Groq AI for job match analysis...")

            # Prepare user profile for AI
            user_profile_dict = {
                'skills': self.user_profile.skills,
                'experience_years': self.user_profile.experience_years,
                'education_level': self.user_profile.education_level,
                'preferred_locations': self.user_profile.preferred_locations,
                'salary_range': self.user_profile.salary_range,
                'work_style_preference': self.user_profile.work_style_preference,
                'industry_preferences': self.user_profile.industry_preferences,
                'career_goals': self.user_profile.career_goals
            }

            # Use Groq AI to analyze job match
            ai_analysis = self.groq_client.analyze_job_match(
                job_data.get('description', ''), user_profile_dict
            )

            print_lg("✅ AI job match analysis completed")
            return ai_analysis

        except Exception as e:
            print_lg(f"⚠️ AI job analysis failed: {e}")
            return None

    def _create_job_match_from_ai_analysis(self, job_data: Dict, ai_analysis: Dict) -> JobMatch:
        """
        Create JobMatch object from AI analysis results.
        """
        job_id = job_data.get('job_id', 'unknown')
        title = job_data.get('title', 'Unknown')
        company = job_data.get('company', 'Unknown')

        # Extract AI analysis results
        match_percentage = ai_analysis.get('match_percentage', 70) / 100.0
        matching_skills = ai_analysis.get('matching_skills', [])
        missing_requirements = ai_analysis.get('missing_requirements', [])
        recommendation_text = ai_analysis.get('recommendation', 'consider')

        # Convert AI recommendation to our format
        recommendation_mapping = {
            'highly_recommended': 'HIGHLY RECOMMENDED: Excellent match',
            'recommended': 'RECOMMENDED: Good match',
            'consider': 'CONSIDER: Moderate match',
            'not_recommended': 'NOT RECOMMENDED: Poor match'
        }

        recommendation = recommendation_mapping.get(recommendation_text, 'CONSIDER: Moderate match')

        # Generate reasons from AI analysis
        reasons = []
        if matching_skills:
            reasons.append(f"Strong skill alignment: {', '.join(matching_skills[:3])}")
        if ai_analysis.get('experience_match') == 'good':
            reasons.append("Experience level matches requirements")
        if ai_analysis.get('cultural_fit') in ['excellent', 'good']:
            reasons.append("Good cultural fit indicators")

        # Generate red flags from missing requirements
        red_flags = []
        if missing_requirements:
            red_flags.extend([f"Missing: {req}" for req in missing_requirements[:3]])

        # Create JobMatch object
        job_match = JobMatch(
            job_id=job_id,
            title=title,
            company=company,
            match_score=match_percentage,
            skill_match=len(matching_skills) / max(len(self.user_profile.skills), 1),
            experience_match=0.8 if ai_analysis.get('experience_match') == 'good' else 0.6,
            location_match=0.8,  # Default, could be enhanced
            salary_match=0.7 if ai_analysis.get('salary_compatibility') == 'high' else 0.6,
            culture_match=0.9 if ai_analysis.get('cultural_fit') == 'excellent' else 0.7,
            reasons=reasons,
            red_flags=red_flags,
            recommendation=recommendation
        )

        # Save to history
        self._save_match_to_history(job_match)

        return job_match
    
    def _calculate_skill_match(self, description: str, title: str) -> float:
        """Calculate how well job requirements match user skills."""
        # Extract required skills from job description
        job_skills = self._extract_skills_from_text(description + " " + title)
        
        # Expand user skills with synonyms
        expanded_user_skills = set()
        for skill in self.user_profile.skills:
            expanded_user_skills.add(skill.lower())
            if skill.lower() in self.skill_synonyms:
                expanded_user_skills.update(self.skill_synonyms[skill.lower()])
        
        # Calculate overlap
        matched_skills = job_skills.intersection(expanded_user_skills)
        
        if not job_skills:
            return 0.5  # Neutral score if no skills detected
        
        skill_match_ratio = len(matched_skills) / len(job_skills)
        
        # Bonus for having more skills than required
        if len(matched_skills) > len(job_skills) * 0.8:
            skill_match_ratio = min(1.0, skill_match_ratio * 1.2)
        
        return skill_match_ratio
    
    def _extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract technical skills from job description."""
        skills = set()
        text_lower = text.lower()
        
        # Common technical skills patterns
        skill_patterns = [
            r'\b(python|java|javascript|c\+\+|c#|ruby|go|rust|swift)\b',
            r'\b(react|angular|vue|django|flask|spring|express)\b',
            r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git)\b',
            r'\b(machine learning|deep learning|ai|data science|analytics)\b',
            r'\b(agile|scrum|devops|ci/cd|microservices|api)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            skills.update(matches)
        
        # Also check against known skill synonyms
        for skill_category, synonyms in self.skill_synonyms.items():
            for synonym in synonyms:
                if synonym in text_lower:
                    skills.add(skill_category)
        
        return skills
    
    def _calculate_experience_match(self, description: str) -> float:
        """Calculate experience level match."""
        # Extract experience requirements
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\s*to\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        required_experience = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, description.lower())
            for match in matches:
                if isinstance(match, tuple):
                    required_experience.extend([int(x) for x in match if x.isdigit()])
                else:
                    required_experience.append(int(match))
        
        if not required_experience:
            return 0.8  # Neutral score if no experience mentioned
        
        min_required = min(required_experience)
        max_required = max(required_experience) if len(required_experience) > 1 else min_required
        
        user_exp = self.user_profile.experience_years
        
        # Perfect match if within range
        if min_required <= user_exp <= max_required + 2:
            return 1.0
        # Good match if close
        elif abs(user_exp - min_required) <= 1:
            return 0.8
        # Penalty for being under-qualified
        elif user_exp < min_required:
            return max(0.2, 1.0 - (min_required - user_exp) * 0.2)
        # Slight penalty for being over-qualified
        else:
            return max(0.6, 1.0 - (user_exp - max_required) * 0.1)
    
    def _calculate_location_match(self, job_data: Dict) -> float:
        """Calculate location preference match."""
        work_location = job_data.get('work_location', '').lower()
        work_style = job_data.get('work_style', '').lower()
        
        # Check for remote work
        if 'remote' in work_style or 'remote' in work_location:
            if 'remote' in [loc.lower() for loc in self.user_profile.preferred_locations]:
                return 1.0
            elif self.user_profile.work_style_preference == 'remote':
                return 1.0
        
        # Check for hybrid
        if 'hybrid' in work_style:
            if self.user_profile.work_style_preference in ['hybrid', 'remote']:
                return 0.8
        
        # Check specific locations
        for preferred_loc in self.user_profile.preferred_locations:
            if preferred_loc.lower() in work_location:
                return 0.9
        
        # Default score for on-site if no preference match
        return 0.4 if self.user_profile.work_style_preference == 'remote' else 0.6
    
    def _calculate_salary_match(self, job_data: Dict) -> float:
        """Calculate salary expectation match."""
        # This would need to parse salary information from job posting
        # For now, return a neutral score
        return 0.7
    
    def _calculate_culture_match(self, company: str, description: str) -> float:
        """Calculate culture and company fit."""
        company_lower = company.lower()
        
        # Check company intelligence
        if company_lower in self.company_intelligence:
            company_info = self.company_intelligence[company_lower]
            reputation_score = company_info.get('reputation_score', 5.0) / 10.0
            return reputation_score
        
        # Check if company is in preferred list
        if company in self.user_profile.preferred_companies:
            return 1.0
        
        # Analyze culture keywords in description
        positive_culture_keywords = [
            'collaborative', 'innovative', 'inclusive', 'growth', 'learning',
            'work-life balance', 'flexible', 'supportive', 'diverse'
        ]
        
        negative_culture_keywords = [
            'fast-paced', 'high-pressure', 'demanding', 'overtime',
            'aggressive', 'competitive'
        ]
        
        description_lower = description.lower()
        positive_count = sum(1 for keyword in positive_culture_keywords if keyword in description_lower)
        negative_count = sum(1 for keyword in negative_culture_keywords if keyword in description_lower)
        
        culture_score = 0.5 + (positive_count * 0.1) - (negative_count * 0.1)
        return max(0.0, min(1.0, culture_score))
    
    def _generate_match_reasons(self, skill_match: float, experience_match: float,
                               location_match: float, salary_match: float, culture_match: float) -> List[str]:
        """Generate reasons why this job is a good match."""
        reasons = []
        
        if skill_match >= 0.8:
            reasons.append("Strong technical skills alignment")
        elif skill_match >= 0.6:
            reasons.append("Good skills match with room to grow")
        
        if experience_match >= 0.8:
            reasons.append("Experience level is a perfect fit")
        elif experience_match >= 0.6:
            reasons.append("Experience level is suitable")
        
        if location_match >= 0.8:
            reasons.append("Location/work style matches preferences")
        
        if culture_match >= 0.8:
            reasons.append("Company culture aligns with preferences")
        
        if salary_match >= 0.8:
            reasons.append("Salary range meets expectations")
        
        return reasons
    
    def _identify_red_flags(self, job_data: Dict, description: str) -> List[str]:
        """Identify potential red flags in the job posting."""
        red_flags = []
        description_lower = description.lower()
        
        # Check deal breakers
        for deal_breaker in self.user_profile.deal_breakers:
            if deal_breaker.lower() in description_lower:
                red_flags.append(f"Deal breaker: {deal_breaker}")
        
        # Common red flags
        red_flag_patterns = [
            (r'unpaid\s+overtime', "Mentions unpaid overtime"),
            (r'fast.paced\s+environment', "High-pressure environment"),
            (r'wear\s+many\s+hats', "Role may lack focus"),
            (r'urgent\s+hiring', "Urgent hiring (possible high turnover)"),
            (r'no\s+remote', "No remote work options"),
            (r'long\s+hours', "Mentions long working hours")
        ]
        
        for pattern, flag_message in red_flag_patterns:
            if re.search(pattern, description_lower):
                red_flags.append(flag_message)
        
        return red_flags
    
    def _generate_recommendation(self, overall_score: float, red_flags: List[str]) -> str:
        """Generate application recommendation."""
        if red_flags:
            return "CAUTION: Review red flags before applying"
        elif overall_score >= 0.8:
            return "HIGHLY RECOMMENDED: Excellent match"
        elif overall_score >= 0.6:
            return "RECOMMENDED: Good match"
        elif overall_score >= 0.4:
            return "CONSIDER: Moderate match"
        else:
            return "NOT RECOMMENDED: Poor match"
    
    def _save_match_to_history(self, job_match: JobMatch):
        """Save job match to history for learning."""
        match_data = asdict(job_match)
        match_data['timestamp'] = datetime.now().isoformat()
        
        self.matching_history['matches'].append(match_data)
        
        # Keep only last 1000 matches
        if len(self.matching_history['matches']) > 1000:
            self.matching_history['matches'] = self.matching_history['matches'][-1000:]
        
        self._save_matching_history()
    
    def get_job_recommendations(self, job_list: List[Dict]) -> List[JobMatch]:
        """Get ranked job recommendations from a list of jobs."""
        print_lg(f"🎯 Analyzing {len(job_list)} jobs for recommendations...")
        
        job_matches = []
        for job_data in job_list:
            try:
                match = self.analyze_job_match(job_data)
                job_matches.append(match)
            except Exception as e:
                print_lg(f"Error analyzing job {job_data.get('job_id', 'unknown')}: {e}")
        
        # Sort by match score
        job_matches.sort(key=lambda x: x.match_score, reverse=True)
        
        print_lg(f"✅ Generated {len(job_matches)} job recommendations")
        return job_matches
    
    def update_user_feedback(self, job_id: str, applied: bool, outcome: str = None):
        """Update user feedback for learning."""
        feedback_data = {
            'applied': applied,
            'outcome': outcome,
            'timestamp': datetime.now().isoformat()
        }
        
        self.matching_history['feedback'][job_id] = feedback_data
        self._save_matching_history()
    
    def get_matching_insights(self) -> Dict:
        """Get insights about matching performance."""
        matches = self.matching_history.get('matches', [])
        feedback = self.matching_history.get('feedback', {})
        
        if not matches:
            return {"message": "No matching history available"}
        
        # Calculate average scores
        avg_match_score = np.mean([m['match_score'] for m in matches])
        avg_skill_match = np.mean([m['skill_match'] for m in matches])
        
        # Count recommendations
        recommendations = [m['recommendation'] for m in matches]
        rec_counts = {rec: recommendations.count(rec) for rec in set(recommendations)}
        
        return {
            "total_jobs_analyzed": len(matches),
            "average_match_score": f"{avg_match_score:.2f}",
            "average_skill_match": f"{avg_skill_match:.2f}",
            "recommendation_breakdown": rec_counts,
            "jobs_with_feedback": len(feedback)
        }
