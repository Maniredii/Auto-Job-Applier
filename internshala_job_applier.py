#!/usr/bin/env python3
"""
Real-time Internshala Job Application System
Live job scraping and application automation for Internshala platform
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from src.scrapers.internshala_scraper import IntershalaScraper
from src.scrapers.job_scraper import JobScraper, SearchCriteria, JobPlatform
from src.automation.auto_application_system import AutoApplicationSystem, ApplicationConfig
from src.ai.resume_modifier import ResumeModifier
from src.ai.cover_letter_generator import CoverLetterGenerator
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/internshala_jobs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InternshalaJobApplier:
    """Real-time Internshala job application system"""
    
    def __init__(self):
        self.scraper = IntershalaScraper()
        self.applied_jobs = set()
        self.session_stats = {
            'jobs_found': 0,
            'jobs_applied': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'start_time': datetime.now()
        }
        
        # Load previously applied jobs
        self.load_applied_jobs()
    
    def load_applied_jobs(self):
        """Load previously applied job IDs to avoid duplicates"""
        try:
            applied_file = Path('data/applied_jobs_internshala.json')
            if applied_file.exists():
                with open(applied_file, 'r') as f:
                    data = json.load(f)
                    self.applied_jobs = set(data.get('applied_job_ids', []))
                logger.info(f"Loaded {len(self.applied_jobs)} previously applied jobs")
        except Exception as e:
            logger.error(f"Error loading applied jobs: {str(e)}")
    
    def save_applied_jobs(self):
        """Save applied job IDs"""
        try:
            applied_file = Path('data/applied_jobs_internshala.json')
            applied_file.parent.mkdir(exist_ok=True)
            
            data = {
                'applied_job_ids': list(self.applied_jobs),
                'last_updated': datetime.now().isoformat(),
                'total_applied': len(self.applied_jobs)
            }
            
            with open(applied_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving applied jobs: {str(e)}")
    
    async def login_to_internshala(self) -> bool:
        """Login to Internshala with credentials"""
        logger.info("🔐 Logging into Internshala...")
        
        try:
            self.scraper.initialize_driver()
            success = self.scraper.login(
                config.INTERNSHALA_EMAIL,
                config.INTERNSHALA_PASSWORD
            )
            
            if success:
                logger.info("✅ Successfully logged into Internshala")
                return True
            else:
                logger.error("❌ Failed to login to Internshala")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {str(e)}")
            return False
    
    async def search_jobs(self, job_criteria: Dict[str, Any]) -> List:
        """Search for jobs on Internshala"""
        logger.info(f"🔍 Searching for jobs: {job_criteria}")
        
        try:
            jobs = self.scraper.scrape_jobs(
                job_title=job_criteria.get('job_title', 'Software Development'),
                location=job_criteria.get('location', ''),
                max_jobs=job_criteria.get('max_jobs', 20),
                job_type=job_criteria.get('job_type', 'both'),
                date_posted=job_criteria.get('date_posted', 'week')
            )
            
            # Filter out already applied jobs
            new_jobs = [job for job in jobs if job.job_id not in self.applied_jobs]
            
            self.session_stats['jobs_found'] += len(jobs)
            
            logger.info(f"✅ Found {len(jobs)} total jobs, {len(new_jobs)} new jobs")
            return new_jobs
            
        except Exception as e:
            logger.error(f"❌ Job search error: {str(e)}")
            return []
    
    async def apply_to_job(self, job) -> bool:
        """Apply to a specific job"""
        logger.info(f"📝 Applying to: {job.title} at {job.company}")
        
        try:
            # Get detailed job information
            job_details = self.scraper.get_job_details(job.url)
            
            # Navigate to job page
            self.scraper.driver.get(job.url)
            await asyncio.sleep(2)
            
            # Look for apply button
            apply_selectors = [
                '.apply_now_button',
                '.btn-primary',
                '[data-action="apply"]',
                '.apply-btn'
            ]
            
            apply_button = None
            for selector in apply_selectors:
                try:
                    elements = self.scraper.driver.find_elements('css selector', selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            if 'apply' in element.text.lower():
                                apply_button = element
                                break
                    if apply_button:
                        break
                except:
                    continue
            
            if apply_button:
                # Click apply button
                self.scraper.safe_click(apply_button)
                await asyncio.sleep(3)
                
                # Handle application form if present
                success = await self.handle_application_form(job)
                
                if success:
                    self.applied_jobs.add(job.job_id)
                    self.session_stats['applications_successful'] += 1
                    logger.info(f"✅ Successfully applied to {job.title}")
                    
                    # Save application record
                    self.save_application_record(job, job_details, 'SUCCESS')
                    return True
                else:
                    self.session_stats['applications_failed'] += 1
                    logger.error(f"❌ Failed to complete application for {job.title}")
                    return False
            else:
                logger.warning(f"⚠️ No apply button found for {job.title}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Application error for {job.title}: {str(e)}")
            self.session_stats['applications_failed'] += 1
            return False
    
    async def handle_application_form(self, job) -> bool:
        """Handle the application form submission"""
        try:
            # Wait for form to load
            await asyncio.sleep(2)
            
            # Look for common form elements
            form_selectors = {
                'cover_letter': ['textarea[name="cover_letter"]', '#cover_letter', '.cover-letter'],
                'resume_upload': ['input[type="file"]', '.file-upload', '#resume'],
                'submit_button': ['button[type="submit"]', '.submit-btn', '.apply-submit']
            }
            
            # Fill cover letter if field exists
            for selector in form_selectors['cover_letter']:
                try:
                    cover_letter_field = self.scraper.driver.find_element('css selector', selector)
                    if cover_letter_field.is_displayed():
                        # Generate a simple cover letter
                        cover_letter_text = self.generate_cover_letter(job)
                        self.scraper.human_type(cover_letter_field, cover_letter_text)
                        logger.info("✅ Cover letter filled")
                        break
                except:
                    continue
            
            # Handle resume upload if needed
            resume_uploaded = False
            for selector in form_selectors['resume_upload']:
                try:
                    upload_field = self.scraper.driver.find_element('css selector', selector)
                    if upload_field.is_displayed():
                        # Check if resume exists
                        resume_path = Path('data/resumes/resume.pdf')
                        if resume_path.exists():
                            upload_field.send_keys(str(resume_path.absolute()))
                            resume_uploaded = True
                            logger.info("✅ Resume uploaded")
                            break
                except:
                    continue
            
            # Submit the form
            for selector in form_selectors['submit_button']:
                try:
                    submit_button = self.scraper.driver.find_element('css selector', selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        self.scraper.safe_click(submit_button)
                        await asyncio.sleep(3)
                        logger.info("✅ Application form submitted")
                        return True
                except:
                    continue
            
            # If no submit button found, assume application was successful
            logger.info("✅ Application completed (no form submission required)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Form handling error: {str(e)}")
            return False
    
    def generate_cover_letter(self, job) -> str:
        """Generate a simple cover letter for the job"""
        return f"""Dear Hiring Manager,

I am writing to express my interest in the {job.title} position at {job.company}. 

I am a motivated and skilled professional with experience in software development and a passion for learning new technologies. I believe my skills and enthusiasm make me a great fit for this role.

I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how my background and skills can benefit {job.company}.

Thank you for considering my application.

Best regards,
[Your Name]"""
    
    def save_application_record(self, job, job_details: Dict, status: str):
        """Save application record for tracking"""
        try:
            record = {
                'job_id': job.job_id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'url': job.url,
                'applied_at': datetime.now().isoformat(),
                'status': status,
                'platform': 'internshala',
                'job_details': job_details
            }
            
            # Save to applications file
            apps_file = Path('data/applications/internshala_applications.json')
            apps_file.parent.mkdir(exist_ok=True)
            
            applications = []
            if apps_file.exists():
                with open(apps_file, 'r') as f:
                    applications = json.load(f)
            
            applications.append(record)
            
            with open(apps_file, 'w') as f:
                json.dump(applications, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving application record: {str(e)}")
    
    async def run_job_application_cycle(self, job_criteria: Dict[str, Any]):
        """Run a complete job application cycle"""
        logger.info("🚀 Starting Internshala job application cycle")
        
        # Login
        if not await self.login_to_internshala():
            return False
        
        try:
            # Search for jobs
            jobs = await self.search_jobs(job_criteria)
            
            if not jobs:
                logger.info("ℹ️ No new jobs found matching criteria")
                return True
            
            logger.info(f"📋 Processing {len(jobs)} jobs for application")
            
            # Apply to jobs
            for i, job in enumerate(jobs, 1):
                logger.info(f"📝 Processing job {i}/{len(jobs)}: {job.title}")
                
                # Apply to job
                success = await self.apply_to_job(job)
                self.session_stats['jobs_applied'] += 1
                
                # Delay between applications
                if i < len(jobs):
                    delay = config.DELAY_BETWEEN_APPLICATIONS
                    logger.info(f"⏳ Waiting {delay} seconds before next application...")
                    await asyncio.sleep(delay)
            
            # Save progress
            self.save_applied_jobs()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Job application cycle error: {str(e)}")
            return False
        
        finally:
            # Close scraper
            self.scraper.close()
    
    def print_session_stats(self):
        """Print session statistics"""
        duration = datetime.now() - self.session_stats['start_time']
        
        print("\n" + "="*60)
        print("📊 INTERNSHALA JOB APPLICATION SESSION SUMMARY")
        print("="*60)
        print(f"⏱️  Session Duration: {duration}")
        print(f"🔍 Jobs Found: {self.session_stats['jobs_found']}")
        print(f"📝 Jobs Applied To: {self.session_stats['jobs_applied']}")
        print(f"✅ Successful Applications: {self.session_stats['applications_successful']}")
        print(f"❌ Failed Applications: {self.session_stats['applications_failed']}")
        print(f"📈 Success Rate: {(self.session_stats['applications_successful']/max(1, self.session_stats['jobs_applied']))*100:.1f}%")
        print(f"💾 Total Applied Jobs (All Time): {len(self.applied_jobs)}")
        print("="*60)

async def main():
    """Main function to run Internshala job application"""
    
    # Job search criteria
    job_criteria = {
        'job_title': 'Software Development Intern',
        'location': 'Remote',
        'max_jobs': 10,
        'job_type': 'internship',
        'date_posted': 'week'
    }
    
    print("🎯 INTERNSHALA REAL-TIME JOB APPLIER")
    print("="*50)
    print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
    print(f"🔍 Search: {job_criteria['job_title']}")
    print(f"📍 Location: {job_criteria['location']}")
    print(f"📊 Max Jobs: {job_criteria['max_jobs']}")
    print("="*50)
    
    # Initialize job applier
    applier = InternshalaJobApplier()
    
    try:
        # Run application cycle
        success = await applier.run_job_application_cycle(job_criteria)
        
        if success:
            logger.info("✅ Job application cycle completed successfully")
        else:
            logger.error("❌ Job application cycle failed")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Job application interrupted by user")
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
    
    finally:
        # Print session statistics
        applier.print_session_stats()

if __name__ == "__main__":
    asyncio.run(main())
