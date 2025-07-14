# Author: Enhanced by AI Assistant
# Smart Application Strategy Module
# Implements intelligent job application logic with priority scoring and success tracking

import json
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from modules.helpers import print_lg

@dataclass
class JobScore:
    """Data class for job scoring metrics."""
    relevance_score: float = 0.0
    company_score: float = 0.0
    salary_score: float = 0.0
    location_score: float = 0.0
    experience_match: float = 0.0
    skills_match: float = 0.0
    total_score: float = 0.0
    priority_level: str = "medium"

@dataclass
class ApplicationMetrics:
    """Data class for tracking application success metrics."""
    total_applications: int = 0
    successful_applications: int = 0
    failed_applications: int = 0
    response_rate: float = 0.0
    interview_rate: float = 0.0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    last_updated: str = ""

class SmartApplicationStrategy:
    """
    Intelligent application strategy that prioritizes jobs and optimizes success rates.
    """
    
    def __init__(self, config_path: str = "config/application_strategy.json"):
        self.config_path = config_path
        self.metrics_path = "data/application_metrics.json"
        self.job_scores_path = "data/job_scores.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Load configuration and metrics
        self.config = self._load_config()
        self.metrics = self._load_metrics()
        self.job_scores_history = self._load_job_scores()
        
        # Application rate limiting
        self.daily_application_limit = self.config.get("daily_application_limit", 50)
        self.hourly_application_limit = self.config.get("hourly_application_limit", 10)
        self.applications_today = self._count_applications_today()
        self.applications_this_hour = self._count_applications_this_hour()
        
        # Success tracking
        self.min_success_rate = self.config.get("min_success_rate", 0.05)  # 5%
        self.target_response_rate = self.config.get("target_response_rate", 0.15)  # 15%
        
    def _load_config(self) -> Dict:
        """Load application strategy configuration."""
        default_config = {
            "daily_application_limit": 50,
            "hourly_application_limit": 10,
            "min_success_rate": 0.05,
            "target_response_rate": 0.15,
            "priority_weights": {
                "relevance": 0.3,
                "company": 0.2,
                "salary": 0.15,
                "location": 0.1,
                "experience_match": 0.15,
                "skills_match": 0.1
            },
            "company_preferences": {
                "preferred_companies": [],
                "blacklisted_companies": [],
                "company_size_preference": "any",  # startup, medium, large, any
                "industry_preferences": []
            },
            "application_timing": {
                "preferred_hours": [9, 10, 11, 14, 15, 16],  # Business hours
                "avoid_weekends": True,
                "peak_application_times": [10, 15]  # 10 AM and 3 PM
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create default config file
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print_lg(f"Error loading config: {e}, using defaults")
            return default_config
    
    def _load_metrics(self) -> ApplicationMetrics:
        """Load application metrics from file."""
        try:
            if os.path.exists(self.metrics_path):
                with open(self.metrics_path, 'r') as f:
                    data = json.load(f)
                return ApplicationMetrics(**data)
            else:
                return ApplicationMetrics()
        except Exception as e:
            print_lg(f"Error loading metrics: {e}")
            return ApplicationMetrics()
    
    def _load_job_scores(self) -> Dict:
        """Load historical job scores."""
        try:
            if os.path.exists(self.job_scores_path):
                with open(self.job_scores_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print_lg(f"Error loading job scores: {e}")
            return {}
    
    def _save_metrics(self):
        """Save application metrics to file."""
        try:
            with open(self.metrics_path, 'w') as f:
                json.dump(asdict(self.metrics), f, indent=2)
        except Exception as e:
            print_lg(f"Error saving metrics: {e}")
    
    def _save_job_scores(self):
        """Save job scores to file."""
        try:
            with open(self.job_scores_path, 'w') as f:
                json.dump(self.job_scores_history, f, indent=2)
        except Exception as e:
            print_lg(f"Error saving job scores: {e}")
    
    def _count_applications_today(self) -> int:
        """Count applications submitted today."""
        # This would integrate with the existing CSV tracking
        # For now, return a placeholder
        return 0
    
    def _count_applications_this_hour(self) -> int:
        """Count applications submitted in the current hour."""
        # This would integrate with the existing CSV tracking
        # For now, return a placeholder
        return 0
    
    def should_apply_to_job(self, job_data: Dict) -> Tuple[bool, str, JobScore]:
        """
        Determines if we should apply to a job based on intelligent criteria.
        """
        # Check rate limits
        if self.applications_today >= self.daily_application_limit:
            return False, "Daily application limit reached", JobScore()
        
        if self.applications_this_hour >= self.hourly_application_limit:
            return False, "Hourly application limit reached", JobScore()
        
        # Check timing
        if not self._is_optimal_application_time():
            return False, "Not optimal application time", JobScore()
        
        # Calculate job score
        job_score = self.calculate_job_score(job_data)
        
        # Determine if we should apply based on score
        should_apply = self._should_apply_based_on_score(job_score)
        
        reason = f"Job score: {job_score.total_score:.2f}, Priority: {job_score.priority_level}"
        
        return should_apply, reason, job_score
    
    def calculate_job_score(self, job_data: Dict) -> JobScore:
        """
        Calculates a comprehensive score for a job posting.
        """
        score = JobScore()
        weights = self.config["priority_weights"]
        
        # Relevance score (based on job title and description keywords)
        score.relevance_score = self._calculate_relevance_score(job_data)
        
        # Company score (based on preferences and reputation)
        score.company_score = self._calculate_company_score(job_data)
        
        # Salary score (based on salary expectations)
        score.salary_score = self._calculate_salary_score(job_data)
        
        # Location score (based on location preferences)
        score.location_score = self._calculate_location_score(job_data)
        
        # Experience match score
        score.experience_match = self._calculate_experience_match(job_data)
        
        # Skills match score
        score.skills_match = self._calculate_skills_match(job_data)
        
        # Calculate total weighted score
        score.total_score = (
            score.relevance_score * weights["relevance"] +
            score.company_score * weights["company"] +
            score.salary_score * weights["salary"] +
            score.location_score * weights["location"] +
            score.experience_match * weights["experience_match"] +
            score.skills_match * weights["skills_match"]
        )
        
        # Determine priority level
        if score.total_score >= 0.8:
            score.priority_level = "high"
        elif score.total_score >= 0.6:
            score.priority_level = "medium"
        else:
            score.priority_level = "low"
        
        return score
    
    def _calculate_relevance_score(self, job_data: Dict) -> float:
        """Calculate relevance score based on job title and description."""
        # Placeholder implementation - would use NLP/ML for better matching
        title = job_data.get("title", "").lower()
        description = job_data.get("description", "").lower()
        
        # Simple keyword matching (would be enhanced with ML)
        relevant_keywords = ["python", "data", "engineer", "developer", "analyst"]
        
        score = 0.0
        for keyword in relevant_keywords:
            if keyword in title:
                score += 0.3
            if keyword in description:
                score += 0.1
        
        return min(1.0, score)
    
    def _calculate_company_score(self, job_data: Dict) -> float:
        """Calculate company score based on preferences."""
        company = job_data.get("company", "").lower()
        
        # Check preferences
        preferred = self.config["company_preferences"]["preferred_companies"]
        blacklisted = self.config["company_preferences"]["blacklisted_companies"]
        
        if any(pref.lower() in company for pref in preferred):
            return 1.0
        elif any(black.lower() in company for black in blacklisted):
            return 0.0
        else:
            return 0.5  # Neutral score for unknown companies
    
    def _calculate_salary_score(self, job_data: Dict) -> float:
        """Calculate salary score based on expectations."""
        # Placeholder - would parse salary information from job posting
        return 0.7  # Default neutral score
    
    def _calculate_location_score(self, job_data: Dict) -> float:
        """Calculate location score based on preferences."""
        location = job_data.get("work_location", "").lower()
        work_style = job_data.get("work_style", "").lower()
        
        # Prefer remote work
        if "remote" in work_style or "remote" in location:
            return 1.0
        elif "hybrid" in work_style:
            return 0.8
        else:
            return 0.6  # On-site
    
    def _calculate_experience_match(self, job_data: Dict) -> float:
        """Calculate experience match score."""
        required_exp = job_data.get("experience_required", 0)
        
        # Placeholder - would compare with user's actual experience
        user_experience = 3  # Would come from config
        
        if required_exp <= user_experience:
            return 1.0
        elif required_exp <= user_experience + 2:
            return 0.7
        else:
            return 0.3
    
    def _calculate_skills_match(self, job_data: Dict) -> float:
        """Calculate skills match score."""
        # Placeholder - would use AI to extract and match skills
        return 0.8  # Default good match
    
    def _should_apply_based_on_score(self, job_score: JobScore) -> bool:
        """Determine if we should apply based on the job score."""
        # Apply to high priority jobs immediately
        if job_score.priority_level == "high":
            return True
        
        # Apply to medium priority jobs with some probability
        elif job_score.priority_level == "medium":
            return random.random() < 0.7  # 70% chance
        
        # Apply to low priority jobs only if we have capacity
        else:
            return random.random() < 0.3 and self.applications_today < self.daily_application_limit * 0.8
    
    def _is_optimal_application_time(self) -> bool:
        """Check if current time is optimal for applications."""
        now = datetime.now()
        
        # Check if it's weekend and we want to avoid weekends
        if self.config["application_timing"]["avoid_weekends"] and now.weekday() >= 5:
            return False
        
        # Check if it's within preferred hours
        preferred_hours = self.config["application_timing"]["preferred_hours"]
        if now.hour not in preferred_hours:
            return False
        
        return True
    
    def record_application_result(self, job_id: str, result: str, response_time: Optional[float] = None):
        """Record the result of a job application."""
        self.metrics.total_applications += 1
        
        if result == "success":
            self.metrics.successful_applications += 1
        elif result == "failed":
            self.metrics.failed_applications += 1
        
        if response_time:
            # Update average response time
            total_time = self.metrics.avg_response_time * (self.metrics.total_applications - 1)
            self.metrics.avg_response_time = (total_time + response_time) / self.metrics.total_applications
        
        # Update rates
        if self.metrics.total_applications > 0:
            self.metrics.success_rate = self.metrics.successful_applications / self.metrics.total_applications
            self.metrics.response_rate = self.metrics.successful_applications / self.metrics.total_applications
        
        self.metrics.last_updated = datetime.now().isoformat()
        self._save_metrics()
    
    def get_application_recommendations(self) -> Dict:
        """Get recommendations for improving application success."""
        recommendations = []
        
        if self.metrics.success_rate < self.min_success_rate:
            recommendations.append("Consider improving resume quality or targeting more relevant jobs")
        
        if self.metrics.response_rate < self.target_response_rate:
            recommendations.append("Consider personalizing cover letters more or targeting smaller companies")
        
        if self.applications_today > self.daily_application_limit * 0.8:
            recommendations.append("Consider slowing down application rate to maintain quality")
        
        return {
            "recommendations": recommendations,
            "current_metrics": asdict(self.metrics),
            "daily_progress": f"{self.applications_today}/{self.daily_application_limit}",
            "hourly_progress": f"{self.applications_this_hour}/{self.hourly_application_limit}"
        }
