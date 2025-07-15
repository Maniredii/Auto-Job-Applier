"""
Main Job Scraper Module
Coordinates multiple job platforms and provides unified interface
"""

import logging
from typing import List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass

from .linkedin_scraper import LinkedInScraper
from .base_scraper import JobListing
from config import config

logger = logging.getLogger(__name__)

class JobPlatform(Enum):
    """Supported job platforms"""
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    NAUKRI = "naukri"

@dataclass
class SearchCriteria:
    """Job search criteria"""
    job_title: str
    location: str = "Remote"
    max_jobs: int = 50
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    date_posted: str = "week"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_only: bool = False
    platforms: List[JobPlatform] = None
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = [JobPlatform.LINKEDIN]

class JobScraper:
    """Main job scraper that coordinates multiple platforms"""
    
    def __init__(self):
        """Initialize job scraper"""
        self.scrapers = {}
        self.active_scrapers = []
        
        # Initialize available scrapers
        self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> None:
        """Initialize platform-specific scrapers"""
        try:
            # LinkedIn scraper
            self.scrapers[JobPlatform.LINKEDIN] = LinkedInScraper()
            logger.info("LinkedIn scraper initialized")
            
            # TODO: Add other platform scrapers
            # self.scrapers[JobPlatform.INDEED] = IndeedScraper()
            # self.scrapers[JobPlatform.GLASSDOOR] = GlassdoorScraper()
            
        except Exception as e:
            logger.error(f"Error initializing scrapers: {str(e)}")
    
    def scrape_jobs(self, criteria: SearchCriteria) -> List[JobListing]:
        """
        Scrape jobs from multiple platforms based on criteria
        
        Args:
            criteria: Search criteria
            
        Returns:
            List of JobListing objects from all platforms
        """
        logger.info(f"Starting job scraping: {criteria.job_title} in {criteria.location}")
        
        all_jobs = []
        jobs_per_platform = criteria.max_jobs // len(criteria.platforms)
        
        for platform in criteria.platforms:
            if platform not in self.scrapers:
                logger.warning(f"Scraper not available for platform: {platform.value}")
                continue
            
            try:
                logger.info(f"Scraping from {platform.value}...")
                
                scraper = self.scrapers[platform]
                self.active_scrapers.append(scraper)
                
                # Platform-specific scraping
                if platform == JobPlatform.LINKEDIN:
                    jobs = self._scrape_linkedin(scraper, criteria, jobs_per_platform)
                else:
                    # TODO: Add other platform implementations
                    jobs = []
                
                # Add platform info to jobs
                for job in jobs:
                    job.platform = platform.value
                
                all_jobs.extend(jobs)
                logger.info(f"Scraped {len(jobs)} jobs from {platform.value}")
                
            except Exception as e:
                logger.error(f"Error scraping from {platform.value}: {str(e)}")
                continue
        
        # Remove duplicates and sort
        unique_jobs = self._remove_duplicates(all_jobs)
        sorted_jobs = self._sort_jobs(unique_jobs)
        
        logger.info(f"Total unique jobs scraped: {len(sorted_jobs)}")
        return sorted_jobs[:criteria.max_jobs]
    
    def _scrape_linkedin(
        self, 
        scraper: LinkedInScraper, 
        criteria: SearchCriteria, 
        max_jobs: int
    ) -> List[JobListing]:
        """
        Scrape jobs from LinkedIn
        
        Args:
            scraper: LinkedIn scraper instance
            criteria: Search criteria
            max_jobs: Maximum jobs to scrape
            
        Returns:
            List of JobListing objects
        """
        try:
            # Initialize driver if needed
            if not scraper.driver:
                scraper.initialize_driver()
            
            # Login if credentials are available
            if config.LINKEDIN_EMAIL and config.LINKEDIN_PASSWORD:
                if not scraper.is_logged_in:
                    login_success = scraper.login()
                    if not login_success:
                        logger.warning("LinkedIn login failed, continuing without login")
            
            # Scrape jobs
            jobs = scraper.scrape_jobs(
                job_title=criteria.job_title,
                location=criteria.location,
                max_jobs=max_jobs,
                experience_level=criteria.experience_level,
                job_type=criteria.job_type,
                date_posted=criteria.date_posted
            )
            
            return jobs
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {str(e)}")
            return []
    
    def _remove_duplicates(self, jobs: List[JobListing]) -> List[JobListing]:
        """
        Remove duplicate job listings
        
        Args:
            jobs: List of job listings
            
        Returns:
            List of unique job listings
        """
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a unique identifier for the job
            job_id = f"{job.title.lower()}_{job.company.lower()}_{job.location.lower()}"
            
            if job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)
        
        logger.debug(f"Removed {len(jobs) - len(unique_jobs)} duplicate jobs")
        return unique_jobs
    
    def _sort_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """
        Sort jobs by relevance and date
        
        Args:
            jobs: List of job listings
            
        Returns:
            Sorted list of job listings
        """
        def sort_key(job):
            # Sort by posted date (newer first), then by title
            date_score = self._get_date_score(job.posted_date)
            return (-date_score, job.title.lower())
        
        return sorted(jobs, key=sort_key)
    
    def _get_date_score(self, posted_date: str) -> int:
        """
        Convert posted date to numeric score for sorting
        
        Args:
            posted_date: Posted date string
            
        Returns:
            Numeric score (higher = more recent)
        """
        posted_date_lower = posted_date.lower()
        
        if "hour" in posted_date_lower or "minute" in posted_date_lower:
            return 100
        elif "day" in posted_date_lower:
            # Extract number of days
            import re
            match = re.search(r'(\d+)', posted_date_lower)
            if match:
                days = int(match.group(1))
                return max(0, 50 - days)
            return 50
        elif "week" in posted_date_lower:
            match = re.search(r'(\d+)', posted_date_lower)
            if match:
                weeks = int(match.group(1))
                return max(0, 20 - weeks * 7)
            return 20
        elif "month" in posted_date_lower:
            return 5
        else:
            return 0
    
    def get_job_details(self, job: JobListing, platform: JobPlatform = None) -> JobListing:
        """
        Get detailed information for a specific job
        
        Args:
            job: Job listing to get details for
            platform: Platform to use (auto-detect if None)
            
        Returns:
            JobListing with detailed information
        """
        if platform is None:
            platform = JobPlatform(job.platform) if hasattr(job, 'platform') else JobPlatform.LINKEDIN
        
        if platform not in self.scrapers:
            logger.warning(f"Scraper not available for platform: {platform.value}")
            return job
        
        try:
            scraper = self.scrapers[platform]
            
            if platform == JobPlatform.LINKEDIN:
                return self._get_linkedin_job_details(scraper, job)
            else:
                # TODO: Add other platform implementations
                return job
                
        except Exception as e:
            logger.error(f"Error getting job details: {str(e)}")
            return job
    
    def _get_linkedin_job_details(self, scraper: LinkedInScraper, job: JobListing) -> JobListing:
        """
        Get detailed job information from LinkedIn
        
        Args:
            scraper: LinkedIn scraper instance
            job: Job listing
            
        Returns:
            JobListing with detailed information
        """
        try:
            if not scraper.driver:
                scraper.initialize_driver()
            
            # Navigate to job page
            scraper.driver.get(job.url)
            scraper.human_delay(2, 4)
            
            # Extract job description
            description_selectors = [
                '.job-search__job-description',
                '.jobs-description-content__text',
                '.jobs-box__html-content'
            ]
            
            description = ""
            for selector in description_selectors:
                try:
                    desc_element = scraper.wait_for_element(By.CSS_SELECTOR, selector, timeout=5)
                    if desc_element:
                        description = scraper.get_text_safe(desc_element)
                        break
                except Exception:
                    continue
            
            # Extract additional details
            job.description = description
            
            # Extract skills from description
            if description:
                from ..parsers.text_processor import TextProcessor
                processor = TextProcessor()
                skills_dict = processor.extract_skills_advanced(description)
                job.skills = []
                for skill_list in skills_dict.values():
                    job.skills.extend(skill_list)
            
            return job
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn job details: {str(e)}")
            return job
    
    def close_all_scrapers(self) -> None:
        """Close all active scrapers"""
        for scraper in self.active_scrapers:
            try:
                if hasattr(scraper, 'close'):
                    scraper.close()
            except Exception as e:
                logger.error(f"Error closing scraper: {str(e)}")
        
        self.active_scrapers.clear()
        logger.info("All scrapers closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all_scrapers()

# Convenience functions
def scrape_jobs_simple(
    job_title: str,
    location: str = "Remote",
    max_jobs: int = 50,
    platforms: List[str] = None
) -> List[JobListing]:
    """
    Simple function to scrape jobs
    
    Args:
        job_title: Job title to search for
        location: Job location
        max_jobs: Maximum number of jobs
        platforms: List of platform names
        
    Returns:
        List of JobListing objects
    """
    if platforms is None:
        platforms = ["linkedin"]
    
    platform_enums = []
    for platform in platforms:
        try:
            platform_enums.append(JobPlatform(platform.lower()))
        except ValueError:
            logger.warning(f"Unknown platform: {platform}")
    
    criteria = SearchCriteria(
        job_title=job_title,
        location=location,
        max_jobs=max_jobs,
        platforms=platform_enums
    )
    
    with JobScraper() as scraper:
        return scraper.scrape_jobs(criteria)
