"""
Auto Application System Module
Central orchestrator for automated job applications
"""

import logging
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import json

from ..scrapers.job_scraper import JobScraper, SearchCriteria, JobPlatform
from ..scrapers.linkedin_scraper import LinkedInScraper
from ..parsers.resume_parser import ResumeParser, ResumeData
from ..parsers.job_description_parser import JobDescriptionParser, JobRequirements
from ..ai.resume_modifier import ResumeModifier, ResumeModification
from ..ai.cover_letter_generator import CoverLetterGenerator, CoverLetterData
from ..automation.browser_manager import BrowserManager
from config import config

logger = logging.getLogger(__name__)

class ApplicationStatus(Enum):
    """Application status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPLIED = "applied"
    FAILED = "failed"
    SKIPPED = "skipped"
    DUPLICATE = "duplicate"

@dataclass
class ApplicationConfig:
    """Configuration for auto application system"""
    # Search criteria
    job_titles: List[str]
    locations: List[str] = field(default_factory=lambda: ["Remote"])
    max_applications_per_day: int = 20
    max_applications_total: int = 100
    platforms: List[str] = field(default_factory=lambda: ["linkedin"])
    
    # Filtering criteria
    min_match_score: float = 0.6
    max_experience_years: int = 10
    min_salary: Optional[int] = None
    exclude_companies: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    
    # Application settings
    resume_strategy: str = "moderate"  # conservative, moderate, aggressive
    cover_letter_template: str = "professional"
    personalization_level: str = "high"
    apply_immediately: bool = False
    review_before_apply: bool = True
    
    # Timing settings
    delay_between_applications: Tuple[int, int] = (300, 600)  # 5-10 minutes
    daily_application_window: Tuple[int, int] = (9, 17)  # 9 AM - 5 PM
    weekend_applications: bool = False
    
    # File paths
    resume_path: str = ""
    output_directory: str = "applications"

@dataclass
class JobApplication:
    """Individual job application data"""
    job_id: str
    job_title: str
    company_name: str
    job_url: str
    platform: str
    
    # Analysis results
    job_requirements: Optional[JobRequirements] = None
    match_score: float = 0.0
    
    # Generated materials
    modified_resume: Optional[ResumeModification] = None
    cover_letter: Optional[CoverLetterData] = None
    
    # Application tracking
    status: ApplicationStatus = ApplicationStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    applied_at: Optional[str] = None
    error_message: Optional[str] = None
    
    # Metadata
    application_method: str = ""  # online, email, etc.
    required_documents: List[str] = field(default_factory=list)
    notes: str = ""

class AutoApplicationSystem:
    """Central auto application system"""
    
    def __init__(self, config: ApplicationConfig):
        """
        Initialize auto application system
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.applications: List[JobApplication] = []
        self.daily_application_count = 0
        self.total_application_count = 0
        self.last_application_date = None
        
        # Initialize components
        self.job_scraper = JobScraper()
        self.resume_parser = ResumeParser()
        self.job_parser = JobDescriptionParser(use_ai=True)
        self.resume_modifier = ResumeModifier()
        self.cover_letter_generator = CoverLetterGenerator()
        self.browser_manager = BrowserManager()
        
        # Load base resume
        self.base_resume = None
        if self.config.resume_path:
            self._load_base_resume()
        
        # Setup output directory
        self.output_dir = Path(self.config.output_directory)
        self.output_dir.mkdir(exist_ok=True)
        
        # Application tracking
        self.session_stats = {
            'jobs_found': 0,
            'jobs_analyzed': 0,
            'applications_created': 0,
            'applications_submitted': 0,
            'applications_failed': 0,
            'session_start': datetime.now().isoformat()
        }
    
    def _load_base_resume(self) -> None:
        """Load and parse base resume"""
        try:
            resume_path = Path(self.config.resume_path)
            if resume_path.exists():
                self.base_resume = self.resume_parser.parse_resume(str(resume_path))
                logger.info(f"Base resume loaded: {self.base_resume.name}")
            else:
                logger.error(f"Resume file not found: {resume_path}")
        except Exception as e:
            logger.error(f"Failed to load base resume: {str(e)}")
    
    async def run_application_cycle(self) -> Dict[str, Any]:
        """
        Run complete application cycle
        
        Returns:
            Dictionary with cycle results and statistics
        """
        logger.info("Starting auto application cycle")
        
        if not self.base_resume:
            raise ValueError("Base resume not loaded. Please provide a valid resume path.")
        
        # Check daily limits
        if not self._check_daily_limits():
            logger.warning("Daily application limits reached")
            return self._get_cycle_results()
        
        try:
            # Step 1: Search for jobs
            jobs = await self._search_jobs()
            self.session_stats['jobs_found'] = len(jobs)
            
            if not jobs:
                logger.info("No jobs found matching criteria")
                return self._get_cycle_results()
            
            # Step 2: Analyze and filter jobs
            qualified_jobs = await self._analyze_jobs(jobs)
            self.session_stats['jobs_analyzed'] = len(qualified_jobs)
            
            # Step 3: Create applications
            applications = await self._create_applications(qualified_jobs)
            self.session_stats['applications_created'] = len(applications)
            
            # Step 4: Submit applications (if enabled)
            if self.config.apply_immediately and not self.config.review_before_apply:
                submitted = await self._submit_applications(applications)
                self.session_stats['applications_submitted'] = submitted
            
            # Step 5: Save results
            await self._save_session_results()
            
            logger.info(f"Application cycle completed: {len(applications)} applications created")
            return self._get_cycle_results()
            
        except Exception as e:
            logger.error(f"Application cycle failed: {str(e)}")
            raise
        finally:
            # Cleanup
            self.job_scraper.close_all_scrapers()
    
    async def _search_jobs(self) -> List[Any]:
        """Search for jobs based on configuration"""
        logger.info("Searching for jobs...")
        
        all_jobs = []
        
        for job_title in self.config.job_titles:
            for location in self.config.locations:
                try:
                    # Create search criteria
                    criteria = SearchCriteria(
                        job_title=job_title,
                        location=location,
                        max_jobs=50,  # Limit per search to avoid overwhelming
                        platforms=[JobPlatform(platform) for platform in self.config.platforms]
                    )
                    
                    # Search jobs
                    jobs = self.job_scraper.scrape_jobs(criteria)
                    
                    # Filter out duplicates and excluded companies
                    filtered_jobs = self._filter_jobs(jobs)
                    all_jobs.extend(filtered_jobs)
                    
                    logger.info(f"Found {len(filtered_jobs)} jobs for '{job_title}' in '{location}'")
                    
                    # Add delay between searches
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Job search failed for '{job_title}' in '{location}': {str(e)}")
                    continue
        
        # Remove duplicates based on URL
        unique_jobs = self._remove_duplicate_jobs(all_jobs)
        logger.info(f"Total unique jobs found: {len(unique_jobs)}")
        
        return unique_jobs
    
    def _filter_jobs(self, jobs: List[Any]) -> List[Any]:
        """Filter jobs based on configuration criteria"""
        filtered_jobs = []
        
        for job in jobs:
            # Check excluded companies
            if job.company.lower() in [company.lower() for company in self.config.exclude_companies]:
                logger.debug(f"Skipping job at excluded company: {job.company}")
                continue
            
            # Check excluded keywords
            job_text = f"{job.title} {job.description}".lower()
            if any(keyword.lower() in job_text for keyword in self.config.exclude_keywords):
                logger.debug(f"Skipping job with excluded keywords: {job.title}")
                continue
            
            # Check if already applied (basic URL check)
            if self._already_applied(job.url):
                logger.debug(f"Already applied to: {job.title} at {job.company}")
                continue
            
            filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _remove_duplicate_jobs(self, jobs: List[Any]) -> List[Any]:
        """Remove duplicate jobs based on URL and title+company"""
        seen_urls = set()
        seen_jobs = set()
        unique_jobs = []
        
        for job in jobs:
            # Check URL duplicates
            if job.url in seen_urls:
                continue
            
            # Check title+company duplicates
            job_key = f"{job.title.lower()}_{job.company.lower()}"
            if job_key in seen_jobs:
                continue
            
            seen_urls.add(job.url)
            seen_jobs.add(job_key)
            unique_jobs.append(job)
        
        return unique_jobs
    
    def _already_applied(self, job_url: str) -> bool:
        """Check if already applied to this job"""
        # Check current session applications
        for app in self.applications:
            if app.job_url == job_url:
                return True
        
        # Check historical applications (if tracking file exists)
        history_file = self.output_dir / "application_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    return job_url in history.get('applied_urls', [])
            except Exception:
                pass
        
        return False
    
    async def _analyze_jobs(self, jobs: List[Any]) -> List[Tuple[Any, JobRequirements, float]]:
        """Analyze jobs and calculate match scores"""
        logger.info(f"Analyzing {len(jobs)} jobs...")
        
        qualified_jobs = []
        
        for job in jobs:
            try:
                # Parse job requirements
                job_requirements = self.job_parser.parse_job_description(
                    job.description, job.title
                )
                
                # Calculate match score
                match_score = self._calculate_job_match(job_requirements)
                
                # Check if meets minimum requirements
                if match_score >= self.config.min_match_score:
                    qualified_jobs.append((job, job_requirements, match_score))
                    logger.debug(f"Qualified job: {job.title} at {job.company} (score: {match_score:.1%})")
                else:
                    logger.debug(f"Job below threshold: {job.title} at {job.company} (score: {match_score:.1%})")
                
                # Add small delay between analyses
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Job analysis failed for {job.title}: {str(e)}")
                continue
        
        # Sort by match score (highest first)
        qualified_jobs.sort(key=lambda x: x[2], reverse=True)
        
        logger.info(f"Found {len(qualified_jobs)} qualified jobs")
        return qualified_jobs
    
    def _calculate_job_match(self, job_requirements: JobRequirements) -> float:
        """Calculate how well the candidate matches job requirements"""
        if not self.base_resume:
            return 0.0
        
        # Use text processor to calculate skill relevance
        skill_match = self.resume_modifier.text_processor.calculate_skill_relevance(
            self.base_resume.skills,
            job_requirements.required_skills + job_requirements.preferred_skills
        )
        
        # Additional factors
        experience_match = self._calculate_experience_match(job_requirements)
        education_match = self._calculate_education_match(job_requirements)
        
        # Weighted score
        total_score = (
            skill_match * 0.6 +
            experience_match * 0.3 +
            education_match * 0.1
        )
        
        return min(total_score, 1.0)
    
    def _calculate_experience_match(self, job_requirements: JobRequirements) -> float:
        """Calculate experience level match"""
        # Simple heuristic based on job level and candidate experience
        job_level_scores = {
            'Entry': 0.9,
            'Mid-Level': 0.8,
            'Senior': 0.7,
            'Lead': 0.6,
            'Principal': 0.5,
            'Director': 0.3
        }
        
        return job_level_scores.get(job_requirements.job_level, 0.7)
    
    def _calculate_education_match(self, job_requirements: JobRequirements) -> float:
        """Calculate education requirement match"""
        if not job_requirements.education_requirements:
            return 1.0
        
        if not self.base_resume.education:
            return 0.5
        
        # Simple check for degree presence
        candidate_education = ' '.join([
            edu.get('degree', '') for edu in self.base_resume.education
        ]).lower()
        
        for req in job_requirements.education_requirements:
            req_lower = req.lower()
            if any(keyword in candidate_education for keyword in ['bachelor', 'master', 'phd']):
                return 1.0
        
        return 0.7  # Partial match

    async def _create_applications(self, qualified_jobs: List[Tuple[Any, JobRequirements, float]]) -> List[JobApplication]:
        """Create applications for qualified jobs"""
        logger.info(f"Creating applications for {len(qualified_jobs)} jobs...")

        applications = []

        for job, job_requirements, match_score in qualified_jobs:
            # Check daily limits
            if not self._check_daily_limits():
                logger.info("Daily application limit reached")
                break

            try:
                # Create application
                application = await self._create_single_application(
                    job, job_requirements, match_score
                )

                if application:
                    applications.append(application)
                    self.applications.append(application)
                    self._increment_application_count()

                    logger.info(f"Created application: {job.title} at {job.company}")

                    # Add delay between applications
                    delay = self._get_application_delay()
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"Failed to create application for {job.title}: {str(e)}")
                continue

        logger.info(f"Created {len(applications)} applications")
        return applications

    async def _create_single_application(
        self,
        job: Any,
        job_requirements: JobRequirements,
        match_score: float
    ) -> Optional[JobApplication]:
        """Create a single job application"""

        try:
            # Generate unique job ID
            job_id = f"{job.company}_{job.title}_{int(time.time())}"
            job_id = job_id.replace(" ", "_").replace("/", "_")

            # Create application object
            application = JobApplication(
                job_id=job_id,
                job_title=job.title,
                company_name=job.company,
                job_url=job.url,
                platform=getattr(job, 'platform', 'unknown'),
                job_requirements=job_requirements,
                match_score=match_score
            )

            # Modify resume for this job
            logger.debug(f"Modifying resume for {job.title}")
            modified_resume = self.resume_modifier.modify_resume_for_job(
                self.base_resume,
                job_requirements,
                strategy=self.config.resume_strategy,
                preserve_truthfulness=True
            )
            application.modified_resume = modified_resume

            # Generate cover letter
            logger.debug(f"Generating cover letter for {job.title}")
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                resume_data=self.base_resume,
                job_requirements=job_requirements,
                company_name=job.company,
                job_title=job.title,
                template=self.config.cover_letter_template,
                personalization_level=self.config.personalization_level
            )
            application.cover_letter = cover_letter

            # Extract application instructions
            app_instructions = self.cover_letter_generator.groq_client.text_processor.extract_application_instructions(
                job.description
            ) if hasattr(self.cover_letter_generator.groq_client, 'text_processor') else {}

            application.application_method = app_instructions.get('application_method', 'Unknown')
            application.required_documents = app_instructions.get('required_documents', [])

            # Save application materials
            await self._save_application_materials(application)

            application.status = ApplicationStatus.IN_PROGRESS
            return application

        except Exception as e:
            logger.error(f"Failed to create application: {str(e)}")
            return None

    async def _save_application_materials(self, application: JobApplication) -> None:
        """Save application materials to files"""
        try:
            # Create application directory
            app_dir = self.output_dir / application.job_id
            app_dir.mkdir(exist_ok=True)

            # Save modified resume
            if application.modified_resume:
                resume_path = app_dir / "resume.txt"
                self.resume_modifier.export_modified_resume(
                    application.modified_resume,
                    resume_path,
                    format_type='text'
                )

                # Also save as JSON with metadata
                resume_json_path = app_dir / "resume_analysis.json"
                self.resume_modifier.export_modified_resume(
                    application.modified_resume,
                    resume_json_path,
                    format_type='json'
                )

            # Save cover letter
            if application.cover_letter:
                cover_letter_path = app_dir / "cover_letter.txt"
                self.cover_letter_generator.export_cover_letter(
                    application.cover_letter,
                    cover_letter_path,
                    format_type='text'
                )

                # Also save as JSON with metadata
                cover_letter_json_path = app_dir / "cover_letter_analysis.json"
                self.cover_letter_generator.export_cover_letter(
                    application.cover_letter,
                    cover_letter_json_path,
                    format_type='json'
                )

            # Save application summary
            summary_path = app_dir / "application_summary.json"
            summary_data = {
                'job_id': application.job_id,
                'job_title': application.job_title,
                'company_name': application.company_name,
                'job_url': application.job_url,
                'platform': application.platform,
                'match_score': application.match_score,
                'status': application.status.value,
                'created_at': application.created_at,
                'application_method': application.application_method,
                'required_documents': application.required_documents,
                'resume_improvements': {
                    'match_score_before': application.modified_resume.match_score_before if application.modified_resume else 0,
                    'match_score_after': application.modified_resume.match_score_after if application.modified_resume else 0,
                    'improvement_percentage': application.modified_resume.improvement_percentage if application.modified_resume else 0
                },
                'cover_letter_quality': {
                    'personalization_score': application.cover_letter.personalization_score if application.cover_letter else 0,
                    'word_count': application.cover_letter.word_count if application.cover_letter else 0
                }
            }

            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved application materials to {app_dir}")

        except Exception as e:
            logger.error(f"Failed to save application materials: {str(e)}")

    async def _submit_applications(self, applications: List[JobApplication]) -> int:
        """Submit applications (placeholder for actual submission logic)"""
        logger.info(f"Submitting {len(applications)} applications...")

        submitted_count = 0

        for application in applications:
            try:
                # This is where actual application submission would happen
                # For now, we'll simulate the process

                # Route to platform-specific application handler
                platform = application.platform.lower()
                if platform == 'linkedin':
                    success = await self._submit_linkedin_application(application)
                elif platform == 'indeed':
                    success = await self._submit_indeed_application(application)
                elif platform == 'glassdoor':
                    success = await self._submit_glassdoor_application(application)
                elif platform == 'naukri':
                    success = await self._submit_naukri_application(application)
                elif platform == 'internshala':
                    success = await self._submit_internshala_application(application)
                elif platform == 'unstop':
                    success = await self._submit_unstop_application(application)
                elif platform == 'angellist':
                    success = await self._submit_angellist_application(application)
                elif platform == 'dice':
                    success = await self._submit_dice_application(application)
                elif platform == 'monster':
                    success = await self._submit_monster_application(application)
                elif platform == 'ziprecruiter':
                    success = await self._submit_ziprecruiter_application(application)
                else:
                    success = await self._submit_generic_application(application)

                if success:
                    application.status = ApplicationStatus.APPLIED
                    application.applied_at = datetime.now().isoformat()
                    submitted_count += 1
                    logger.info(f"Successfully applied to {application.job_title} at {application.company_name}")
                else:
                    application.status = ApplicationStatus.FAILED
                    application.error_message = "Submission failed"
                    logger.error(f"Failed to apply to {application.job_title} at {application.company_name}")

                # Add delay between submissions
                delay = self._get_application_delay()
                await asyncio.sleep(delay)

            except Exception as e:
                application.status = ApplicationStatus.FAILED
                application.error_message = str(e)
                logger.error(f"Application submission error: {str(e)}")

        logger.info(f"Submitted {submitted_count} applications successfully")
        return submitted_count

    async def _submit_linkedin_application(self, application: JobApplication) -> bool:
        """Submit application via LinkedIn (placeholder)"""
        # This would implement actual LinkedIn application submission
        # For now, return True to simulate success
        logger.debug(f"Simulating LinkedIn application submission for {application.job_title}")

        # In a real implementation, this would:
        # 1. Navigate to the job URL
        # 2. Click apply button
        # 3. Fill out application form
        # 4. Upload resume and cover letter
        # 5. Submit application

        return True

    async def _submit_indeed_application(self, application: JobApplication) -> bool:
        """Submit application via Indeed"""
        logger.debug(f"Simulating Indeed application submission for {application.job_title}")
        # Implementation would use Indeed's application system
        return True

    async def _submit_glassdoor_application(self, application: JobApplication) -> bool:
        """Submit application via Glassdoor"""
        logger.debug(f"Simulating Glassdoor application submission for {application.job_title}")
        # Implementation would use Glassdoor's application system
        return True

    async def _submit_naukri_application(self, application: JobApplication) -> bool:
        """Submit application via Naukri"""
        logger.debug(f"Simulating Naukri application submission for {application.job_title}")
        # Implementation would use Naukri's application system
        return True

    async def _submit_internshala_application(self, application: JobApplication) -> bool:
        """Submit application via Internshala"""
        logger.debug(f"Simulating Internshala application submission for {application.job_title}")
        # Implementation would use Internshala's application system
        return True

    async def _submit_unstop_application(self, application: JobApplication) -> bool:
        """Submit application via Unstop"""
        logger.debug(f"Simulating Unstop application submission for {application.job_title}")
        # Implementation would use Unstop's application system
        return True

    async def _submit_angellist_application(self, application: JobApplication) -> bool:
        """Submit application via AngelList"""
        logger.debug(f"Simulating AngelList application submission for {application.job_title}")
        # Implementation would use AngelList's application system
        return True

    async def _submit_dice_application(self, application: JobApplication) -> bool:
        """Submit application via Dice"""
        logger.debug(f"Simulating Dice application submission for {application.job_title}")
        # Implementation would use Dice's application system
        return True

    async def _submit_monster_application(self, application: JobApplication) -> bool:
        """Submit application via Monster"""
        logger.debug(f"Simulating Monster application submission for {application.job_title}")
        # Implementation would use Monster's application system
        return True

    async def _submit_ziprecruiter_application(self, application: JobApplication) -> bool:
        """Submit application via ZipRecruiter"""
        logger.debug(f"Simulating ZipRecruiter application submission for {application.job_title}")
        # Implementation would use ZipRecruiter's application system
        return True

    async def _submit_generic_application(self, application: JobApplication) -> bool:
        """Submit application via generic method (placeholder)"""
        # This would implement email or other application methods
        logger.debug(f"Simulating generic application submission for {application.job_title}")

        # In a real implementation, this would:
        # 1. Send email with resume and cover letter
        # 2. Or navigate to company website and fill form
        # 3. Handle different application methods

        return True

    def _check_daily_limits(self) -> bool:
        """Check if daily application limits are reached"""
        current_date = datetime.now().date()

        # Reset daily count if new day
        if self.last_application_date != current_date:
            self.daily_application_count = 0
            self.last_application_date = current_date

        # Check daily limit
        if self.daily_application_count >= self.config.max_applications_per_day:
            return False

        # Check total limit
        if self.total_application_count >= self.config.max_applications_total:
            return False

        # Check time window
        current_hour = datetime.now().hour
        start_hour, end_hour = self.config.daily_application_window

        if not (start_hour <= current_hour < end_hour):
            return False

        # Check weekend policy
        if not self.config.weekend_applications and datetime.now().weekday() >= 5:
            return False

        return True

    def _increment_application_count(self) -> None:
        """Increment application counters"""
        self.daily_application_count += 1
        self.total_application_count += 1

    def _get_application_delay(self) -> int:
        """Get random delay between applications"""
        import random
        min_delay, max_delay = self.config.delay_between_applications
        return random.randint(min_delay, max_delay)

    async def _save_session_results(self) -> None:
        """Save session results and statistics"""
        try:
            # Update session stats
            self.session_stats['session_end'] = datetime.now().isoformat()
            self.session_stats['total_applications'] = len(self.applications)

            # Save session summary
            session_file = self.output_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            session_data = {
                'config': {
                    'job_titles': self.config.job_titles,
                    'locations': self.config.locations,
                    'platforms': self.config.platforms,
                    'min_match_score': self.config.min_match_score,
                    'resume_strategy': self.config.resume_strategy,
                    'cover_letter_template': self.config.cover_letter_template
                },
                'statistics': self.session_stats,
                'applications': [
                    {
                        'job_id': app.job_id,
                        'job_title': app.job_title,
                        'company_name': app.company_name,
                        'match_score': app.match_score,
                        'status': app.status.value,
                        'created_at': app.created_at,
                        'applied_at': app.applied_at
                    }
                    for app in self.applications
                ]
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # Update application history
            await self._update_application_history()

            logger.info(f"Session results saved to {session_file}")

        except Exception as e:
            logger.error(f"Failed to save session results: {str(e)}")

    async def _update_application_history(self) -> None:
        """Update application history file"""
        try:
            history_file = self.output_dir / "application_history.json"

            # Load existing history
            history = {'applied_urls': [], 'total_applications': 0}
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)

            # Add new applications
            for app in self.applications:
                if app.status == ApplicationStatus.APPLIED and app.job_url not in history['applied_urls']:
                    history['applied_urls'].append(app.job_url)

            history['total_applications'] = len(history['applied_urls'])
            history['last_updated'] = datetime.now().isoformat()

            # Save updated history
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to update application history: {str(e)}")

    def _get_cycle_results(self) -> Dict[str, Any]:
        """Get cycle results and statistics"""
        return {
            'session_stats': self.session_stats,
            'applications_created': len(self.applications),
            'applications_by_status': {
                status.value: len([app for app in self.applications if app.status == status])
                for status in ApplicationStatus
            },
            'average_match_score': sum(app.match_score for app in self.applications) / len(self.applications) if self.applications else 0,
            'top_matches': sorted(
                [(app.job_title, app.company_name, app.match_score) for app in self.applications],
                key=lambda x: x[2],
                reverse=True
            )[:5]
        }

    def get_application_status(self, job_id: str) -> Optional[JobApplication]:
        """Get status of specific application"""
        for app in self.applications:
            if app.job_id == job_id:
                return app
        return None

    def get_applications_by_status(self, status: ApplicationStatus) -> List[JobApplication]:
        """Get applications by status"""
        return [app for app in self.applications if app.status == status]

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            **self.session_stats,
            'daily_application_count': self.daily_application_count,
            'total_application_count': self.total_application_count,
            'applications_in_session': len(self.applications)
        }

    async def review_pending_applications(self) -> List[JobApplication]:
        """Get pending applications for manual review"""
        pending_apps = self.get_applications_by_status(ApplicationStatus.IN_PROGRESS)

        # Sort by match score (highest first)
        pending_apps.sort(key=lambda x: x.match_score, reverse=True)

        return pending_apps

    async def approve_application(self, job_id: str) -> bool:
        """Approve application for submission"""
        application = self.get_application_status(job_id)
        if not application:
            return False

        try:
            success = await self._submit_applications([application])
            return success > 0
        except Exception as e:
            logger.error(f"Failed to approve application {job_id}: {str(e)}")
            return False

    async def reject_application(self, job_id: str, reason: str = "") -> bool:
        """Reject application"""
        application = self.get_application_status(job_id)
        if not application:
            return False

        application.status = ApplicationStatus.SKIPPED
        application.notes = f"Rejected: {reason}"
        return True

    def export_applications_report(self, output_path: Path) -> bool:
        """Export applications report"""
        try:
            report_data = {
                'generated_at': datetime.now().isoformat(),
                'session_statistics': self.get_session_statistics(),
                'applications': []
            }

            for app in self.applications:
                app_data = {
                    'job_id': app.job_id,
                    'job_title': app.job_title,
                    'company_name': app.company_name,
                    'job_url': app.job_url,
                    'platform': app.platform,
                    'match_score': app.match_score,
                    'status': app.status.value,
                    'created_at': app.created_at,
                    'applied_at': app.applied_at,
                    'error_message': app.error_message,
                    'application_method': app.application_method,
                    'required_documents': app.required_documents,
                    'notes': app.notes
                }

                # Add resume modification details
                if app.modified_resume:
                    app_data['resume_analysis'] = {
                        'match_score_before': app.modified_resume.match_score_before,
                        'match_score_after': app.modified_resume.match_score_after,
                        'improvement_percentage': app.modified_resume.improvement_percentage,
                        'modifications_made': app.modified_resume.modifications_made,
                        'keyword_additions': app.modified_resume.keyword_additions
                    }

                # Add cover letter details
                if app.cover_letter:
                    app_data['cover_letter_analysis'] = {
                        'personalization_score': app.cover_letter.personalization_score,
                        'word_count': app.cover_letter.word_count,
                        'template_used': app.cover_letter.template_used,
                        'key_points': app.cover_letter.key_points
                    }

                report_data['applications'].append(app_data)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Applications report exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export applications report: {str(e)}")
            return False

class ApplicationManager:
    """High-level application manager for easy usage"""

    def __init__(self, resume_path: str, output_directory: str = "applications"):
        """
        Initialize application manager

        Args:
            resume_path: Path to base resume file
            output_directory: Directory for application outputs
        """
        self.resume_path = resume_path
        self.output_directory = output_directory
        self.system = None

    def create_config(
        self,
        job_titles: List[str],
        locations: List[str] = None,
        max_applications_per_day: int = 20,
        platforms: List[str] = None,
        min_match_score: float = 0.6,
        **kwargs
    ) -> ApplicationConfig:
        """
        Create application configuration

        Args:
            job_titles: List of job titles to search for
            locations: List of locations (default: ["Remote"])
            max_applications_per_day: Maximum applications per day
            platforms: List of platforms (default: ["linkedin"])
            min_match_score: Minimum match score threshold
            **kwargs: Additional configuration options

        Returns:
            ApplicationConfig object
        """
        if locations is None:
            locations = ["Remote"]
        if platforms is None:
            platforms = ["linkedin"]

        config = ApplicationConfig(
            job_titles=job_titles,
            locations=locations,
            max_applications_per_day=max_applications_per_day,
            platforms=platforms,
            min_match_score=min_match_score,
            resume_path=self.resume_path,
            output_directory=self.output_directory,
            **kwargs
        )

        return config

    async def run_auto_application(self, config: ApplicationConfig) -> Dict[str, Any]:
        """
        Run auto application process

        Args:
            config: Application configuration

        Returns:
            Results dictionary
        """
        self.system = AutoApplicationSystem(config)

        try:
            results = await self.system.run_application_cycle()
            return results
        except Exception as e:
            logger.error(f"Auto application failed: {str(e)}")
            raise

    async def run_with_review(self, config: ApplicationConfig) -> Dict[str, Any]:
        """
        Run application process with manual review step

        Args:
            config: Application configuration

        Returns:
            Results dictionary
        """
        # Disable immediate application
        config.apply_immediately = False
        config.review_before_apply = True

        self.system = AutoApplicationSystem(config)

        # Run application creation cycle
        results = await self.system.run_application_cycle()

        # Get pending applications for review
        pending_apps = await self.system.review_pending_applications()

        results['pending_applications'] = [
            {
                'job_id': app.job_id,
                'job_title': app.job_title,
                'company_name': app.company_name,
                'match_score': app.match_score,
                'job_url': app.job_url
            }
            for app in pending_apps
        ]

        return results

    async def approve_and_submit(self, job_ids: List[str]) -> Dict[str, bool]:
        """
        Approve and submit specific applications

        Args:
            job_ids: List of job IDs to approve

        Returns:
            Dictionary mapping job IDs to success status
        """
        if not self.system:
            raise ValueError("No active application system. Run application process first.")

        results = {}
        for job_id in job_ids:
            success = await self.system.approve_application(job_id)
            results[job_id] = success

        return results

    def get_application_summary(self) -> Dict[str, Any]:
        """Get summary of current application session"""
        if not self.system:
            return {}

        return self.system.get_session_statistics()

    def export_report(self, output_path: str) -> bool:
        """Export detailed application report"""
        if not self.system:
            return False

        return self.system.export_applications_report(Path(output_path))
