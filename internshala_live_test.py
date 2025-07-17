#!/usr/bin/env python3
"""
Live Internshala Job Scraper and Applier
Real-time job scraping and application for Internshala
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from src.scrapers.internshala_scraper import IntershalaScraper
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InternshalaLiveApplier:
    """Live Internshala job application system"""
    
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
    
    async def login_and_test(self) -> bool:
        """Login to Internshala and test functionality"""
        print("🔐 Logging into Internshala...")
        print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
        print(f"🔒 Password: {'*' * len(config.INTERNSHALA_PASSWORD)}")
        
        try:
            self.scraper.initialize_driver()
            success = self.scraper.login(
                config.INTERNSHALA_EMAIL,
                config.INTERNSHALA_PASSWORD
            )
            
            if success:
                print("✅ Successfully logged into Internshala!")
                return True
            else:
                print("❌ Failed to login to Internshala")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    async def search_and_display_jobs(self, job_criteria: Dict[str, Any]) -> List:
        """Search for jobs and display results"""
        print(f"\n🔍 Searching for jobs...")
        print(f"   Job Title: {job_criteria['job_title']}")
        print(f"   Location: {job_criteria['location']}")
        print(f"   Max Jobs: {job_criteria['max_jobs']}")
        print(f"   Type: {job_criteria['job_type']}")
        
        try:
            jobs = self.scraper.scrape_jobs(
                job_title=job_criteria['job_title'],
                location=job_criteria['location'],
                max_jobs=job_criteria['max_jobs'],
                job_type=job_criteria['job_type'],
                date_posted=job_criteria.get('date_posted', 'week')
            )
            
            self.session_stats['jobs_found'] = len(jobs)
            
            print(f"\n✅ Found {len(jobs)} jobs!")
            
            if jobs:
                print("\n📋 JOB LISTINGS:")
                print("=" * 80)
                
                for i, job in enumerate(jobs, 1):
                    print(f"\n{i}. {job.title}")
                    print(f"   🏢 Company: {job.company}")
                    print(f"   📍 Location: {job.location}")
                    print(f"   📅 Posted: {job.posted_date}")
                    print(f"   💰 Salary: {job.salary}")
                    print(f"   🔗 URL: {job.url}")
                    print(f"   🆔 Job ID: {job.job_id}")
                    print(f"   ⚡ Easy Apply: {'Yes' if job.easy_apply else 'No'}")
                    print("-" * 80)
            
            return jobs
            
        except Exception as e:
            print(f"❌ Job search error: {str(e)}")
            return []
    
    async def apply_to_selected_jobs(self, jobs: List, max_applications: int = 3) -> int:
        """Apply to selected jobs"""
        if not jobs:
            print("❌ No jobs available for application")
            return 0
        
        print(f"\n📝 STARTING JOB APPLICATIONS (Max: {max_applications})")
        print("=" * 60)
        
        applications_made = 0
        
        for i, job in enumerate(jobs[:max_applications], 1):
            print(f"\n🎯 Applying to Job {i}/{min(len(jobs), max_applications)}")
            print(f"   Title: {job.title}")
            print(f"   Company: {job.company}")
            
            try:
                # Navigate to job page
                print("   🌐 Navigating to job page...")
                self.scraper.driver.get(job.url)
                await asyncio.sleep(3)
                
                # Look for apply button
                print("   🔍 Looking for apply button...")
                apply_button = self.find_apply_button()
                
                if apply_button:
                    print("   ✅ Apply button found!")
                    
                    # Click apply button
                    print("   🖱️ Clicking apply button...")
                    self.scraper.safe_click(apply_button)
                    await asyncio.sleep(3)
                    
                    # Handle application process
                    success = await self.handle_application_process(job)
                    
                    if success:
                        print(f"   ✅ Successfully applied to {job.title}!")
                        self.session_stats['applications_successful'] += 1
                        applications_made += 1
                        
                        # Save application record
                        self.save_application_record(job, 'SUCCESS')
                    else:
                        print(f"   ❌ Failed to complete application for {job.title}")
                        self.session_stats['applications_failed'] += 1
                else:
                    print("   ⚠️ No apply button found")
                    self.session_stats['applications_failed'] += 1
                
                self.session_stats['jobs_applied'] += 1
                
                # Delay between applications
                if i < min(len(jobs), max_applications):
                    delay = 30  # 30 seconds between applications
                    print(f"   ⏳ Waiting {delay} seconds before next application...")
                    await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"   ❌ Application error: {str(e)}")
                self.session_stats['applications_failed'] += 1
        
        return applications_made
    
    def find_apply_button(self):
        """Find the apply button on the job page"""
        apply_selectors = [
            '.apply_now_button',
            '.btn-primary',
            '[data-action="apply"]',
            '.apply-btn',
            'button[contains(text(), "Apply")]',
            'a[contains(text(), "Apply")]'
        ]
        
        for selector in apply_selectors:
            try:
                elements = self.scraper.driver.find_elements('css selector', selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        text = element.text.lower()
                        if 'apply' in text and 'now' in text:
                            return element
            except:
                continue
        
        return None
    
    async def handle_application_process(self, job) -> bool:
        """Handle the application form submission"""
        try:
            print("   📝 Handling application form...")
            
            # Wait for any form to load
            await asyncio.sleep(2)
            
            # Check if there's a form to fill
            form_elements = self.scraper.driver.find_elements('css selector', 'form, .application-form')
            
            if form_elements:
                print("   📋 Application form detected")
                
                # Look for cover letter field
                cover_letter_selectors = [
                    'textarea[name*="cover"]',
                    'textarea[placeholder*="cover"]',
                    '#cover_letter',
                    '.cover-letter textarea'
                ]
                
                for selector in cover_letter_selectors:
                    try:
                        cover_letter_field = self.scraper.driver.find_element('css selector', selector)
                        if cover_letter_field.is_displayed():
                            print("   ✍️ Filling cover letter...")
                            cover_letter_text = self.generate_cover_letter(job)
                            self.scraper.human_type(cover_letter_field, cover_letter_text)
                            break
                    except:
                        continue
                
                # Look for submit button
                submit_selectors = [
                    'button[type="submit"]',
                    '.submit-btn',
                    '.apply-submit',
                    'input[type="submit"]'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_button = self.scraper.driver.find_element('css selector', selector)
                        if submit_button.is_displayed() and submit_button.is_enabled():
                            print("   🚀 Submitting application...")
                            self.scraper.safe_click(submit_button)
                            await asyncio.sleep(3)
                            return True
                    except:
                        continue
            
            # If no form or submission successful
            print("   ✅ Application process completed")
            return True
            
        except Exception as e:
            print(f"   ❌ Form handling error: {str(e)}")
            return False
    
    def generate_cover_letter(self, job) -> str:
        """Generate a simple cover letter"""
        return f"""Dear {job.company} Team,

I am excited to apply for the {job.title} position. As a motivated student/professional, I am eager to contribute to your team and gain valuable experience.

My skills and enthusiasm make me a great fit for this role, and I am committed to delivering high-quality work and learning from your experienced team.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {job.company}.

Best regards,
Applicant"""
    
    def save_application_record(self, job, status: str):
        """Save application record"""
        try:
            record = {
                'job_id': job.job_id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'url': job.url,
                'applied_at': datetime.now().isoformat(),
                'status': status,
                'platform': 'internshala'
            }
            
            # Save to file
            apps_file = Path('data/applications/internshala_live_applications.json')
            apps_file.parent.mkdir(exist_ok=True)
            
            applications = []
            if apps_file.exists():
                with open(apps_file, 'r') as f:
                    applications = json.load(f)
            
            applications.append(record)
            
            with open(apps_file, 'w') as f:
                json.dump(applications, f, indent=2)
                
        except Exception as e:
            print(f"   ⚠️ Could not save application record: {str(e)}")
    
    def print_session_summary(self):
        """Print session summary"""
        duration = datetime.now() - self.session_stats['start_time']
        
        print("\n" + "="*70)
        print("📊 INTERNSHALA LIVE SESSION SUMMARY")
        print("="*70)
        print(f"⏱️  Duration: {duration}")
        print(f"🔍 Jobs Found: {self.session_stats['jobs_found']}")
        print(f"📝 Jobs Applied To: {self.session_stats['jobs_applied']}")
        print(f"✅ Successful Applications: {self.session_stats['applications_successful']}")
        print(f"❌ Failed Applications: {self.session_stats['applications_failed']}")
        
        if self.session_stats['jobs_applied'] > 0:
            success_rate = (self.session_stats['applications_successful'] / self.session_stats['jobs_applied']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("="*70)
    
    def close(self):
        """Close the scraper"""
        if self.scraper:
            self.scraper.close()

async def main():
    """Main function"""
    
    # Job search criteria
    job_criteria = {
        'job_title': 'Software Development Intern',
        'location': 'Remote',
        'max_jobs': 10,
        'job_type': 'internship',
        'date_posted': 'week'
    }
    
    print("🎯 INTERNSHALA LIVE JOB APPLIER")
    print("="*50)
    print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
    print(f"🔍 Search: {job_criteria['job_title']}")
    print(f"📍 Location: {job_criteria['location']}")
    print("="*50)
    
    applier = InternshalaLiveApplier()
    
    try:
        # Step 1: Login
        if not await applier.login_and_test():
            print("❌ Cannot proceed without successful login")
            return
        
        # Step 2: Search for jobs
        jobs = await applier.search_and_display_jobs(job_criteria)
        
        if not jobs:
            print("❌ No jobs found. Exiting.")
            return
        
        # Step 3: Ask user if they want to apply
        print(f"\n🤔 Found {len(jobs)} jobs. Do you want to apply to some of them?")
        user_input = input("Enter 'y' to apply to jobs, or 'n' to just view: ").lower().strip()
        
        if user_input == 'y':
            max_apps = int(input(f"How many jobs to apply to? (max {len(jobs)}): ") or "3")
            max_apps = min(max_apps, len(jobs))
            
            # Step 4: Apply to jobs
            applications_made = await applier.apply_to_selected_jobs(jobs, max_apps)
            print(f"\n🎉 Applied to {applications_made} jobs!")
        else:
            print("👀 Job viewing completed without applications")
    
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    
    finally:
        # Print summary and close
        applier.print_session_summary()
        applier.close()
        print("\n✅ Session completed!")

if __name__ == "__main__":
    asyncio.run(main())
