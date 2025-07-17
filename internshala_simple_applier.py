#!/usr/bin/env python3
"""
Simple Internshala Job Applier
Simplified version that works with current Chrome setup
"""

import time
import json
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import config

class SimpleInternshalaApplier:
    """Simple Internshala job applier"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.applied_jobs = set()
        self.session_stats = {
            'jobs_found': 0,
            'jobs_applied': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'start_time': datetime.now()
        }
    
    def create_simple_browser(self):
        """Create a simple Chrome browser"""
        print("🌐 Creating Chrome browser...")
        
        options = Options()
        
        # Basic options that work with all Chrome versions
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        
        # User agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Browser created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Browser creation failed: {str(e)}")
            return False
    
    def login_to_internshala(self):
        """Login to Internshala"""
        print("🔐 Logging into Internshala...")
        print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
        
        try:
            # Navigate to Internshala
            self.driver.get("https://internshala.com/login")
            time.sleep(3)
            
            print(f"📄 Page title: {self.driver.title}")
            
            # Find email field
            email_selectors = [
                '#email',
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="email"]'
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if email_field.is_displayed():
                        break
                except:
                    continue
            
            if not email_field:
                print("❌ Email field not found")
                return False
            
            print("✅ Email field found, typing email...")
            email_field.clear()
            email_field.send_keys(config.INTERNSHALA_EMAIL)
            time.sleep(1)
            
            # Find password field
            password_selectors = [
                '#password',
                'input[name="password"]',
                'input[type="password"]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if password_field.is_displayed():
                        break
                except:
                    continue
            
            if not password_field:
                print("❌ Password field not found")
                return False
            
            print("✅ Password field found, typing password...")
            password_field.clear()
            password_field.send_keys(config.INTERNSHALA_PASSWORD)
            time.sleep(1)
            
            # Find and click login button
            login_selectors = [
                'button[type="submit"]',
                '#login_submit',
                '.login-btn',
                'input[type="submit"]',
                'button[contains(text(), "Login")]'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button.is_displayed() and login_button.is_enabled():
                        break
                except:
                    continue
            
            if not login_button:
                print("❌ Login button not found")
                return False
            
            print("✅ Login button found, clicking...")
            login_button.click()
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            print(f"🌐 After login URL: {current_url}")
            
            if 'dashboard' in current_url or 'student' in current_url or 'internshala.com' in current_url and 'login' not in current_url:
                print("🎉 LOGIN SUCCESSFUL!")
                return True
            else:
                print("❌ Login failed - still on login page")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def search_for_jobs(self):
        """Search for internships on Internshala"""
        print("\n🔍 Searching for internships...")
        
        try:
            # Navigate to internships page
            self.driver.get("https://internshala.com/internships/software-development-internship")
            time.sleep(3)
            
            print(f"📄 Search page title: {self.driver.title}")
            
            # Look for job/internship cards
            job_selectors = [
                '.individual_internship',
                '.internship_meta',
                '.job-card',
                '.internship-card',
                '.container-fluid .row > div'
            ]
            
            jobs_found = []
            for selector in job_selectors:
                try:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(job_elements) > 0:
                        print(f"✅ Found {len(job_elements)} internships with selector: {selector}")
                        jobs_found = job_elements
                        break
                except:
                    continue
            
            if not jobs_found:
                print("❌ No internships found")
                return []
            
            # Extract job information
            jobs = []
            for i, job_element in enumerate(jobs_found[:10], 1):  # Limit to first 10
                try:
                    job_info = self.extract_job_info(job_element, i)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    print(f"⚠️ Error extracting job {i}: {str(e)}")
                    continue
            
            self.session_stats['jobs_found'] = len(jobs)
            print(f"\n✅ Successfully extracted {len(jobs)} internship details!")
            
            return jobs
            
        except Exception as e:
            print(f"❌ Job search error: {str(e)}")
            return []
    
    def extract_job_info(self, job_element, index):
        """Extract job information from element"""
        try:
            # Try to find title
            title_selectors = [
                '.job-title a',
                '.profile h3 a',
                'h3 a',
                'h4 a',
                '.heading-4-5 a'
            ]
            
            title = "Software Development Intern"
            job_url = ""
            
            for selector in title_selectors:
                try:
                    title_elem = job_element.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    job_url = title_elem.get_attribute('href')
                    if title and job_url:
                        break
                except:
                    continue
            
            # Try to find company
            company_selectors = [
                '.company-name',
                '.company h4 a',
                '.heading-6 a',
                'a[href*="company"]'
            ]
            
            company = "Company"
            for selector in company_selectors:
                try:
                    company_elem = job_element.find_element(By.CSS_SELECTOR, selector)
                    company = company_elem.text.strip()
                    if company:
                        break
                except:
                    continue
            
            # Try to find location
            location_selectors = [
                '.locations span',
                '.location_link',
                '.individual_internship_details .location'
            ]
            
            location = "Remote"
            for selector in location_selectors:
                try:
                    location_elem = job_element.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
            job_info = {
                'index': index,
                'title': title,
                'company': company,
                'location': location,
                'url': job_url if job_url and job_url.startswith('http') else f"https://internshala.com{job_url}" if job_url else "",
                'element': job_element
            }
            
            print(f"   {index}. {title} at {company} ({location})")
            return job_info
            
        except Exception as e:
            print(f"   ⚠️ Could not extract job {index}: {str(e)}")
            return None
    
    def apply_to_jobs(self, jobs, max_applications=3):
        """Apply to selected jobs"""
        if not jobs:
            print("❌ No jobs to apply to")
            return 0
        
        print(f"\n📝 APPLYING TO INTERNSHIPS (Max: {max_applications})")
        print("="*60)
        
        applications_made = 0
        
        for job in jobs[:max_applications]:
            print(f"\n🎯 Applying to: {job['title']} at {job['company']}")
            
            try:
                if job['url']:
                    # Navigate to job page
                    print("   🌐 Opening job page...")
                    self.driver.get(job['url'])
                    time.sleep(3)
                    
                    # Look for apply button
                    apply_selectors = [
                        '.apply_now_button',
                        '.btn-primary',
                        'button[contains(text(), "Apply")]',
                        'a[contains(text(), "Apply")]',
                        '.apply-btn'
                    ]
                    
                    apply_button = None
                    for selector in apply_selectors:
                        try:
                            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for button in buttons:
                                if button.is_displayed() and 'apply' in button.text.lower():
                                    apply_button = button
                                    break
                            if apply_button:
                                break
                        except:
                            continue
                    
                    if apply_button:
                        print("   ✅ Apply button found!")
                        print("   🖱️ Clicking apply button...")
                        apply_button.click()
                        time.sleep(3)
                        
                        # Handle any application form
                        success = self.handle_application_form(job)
                        
                        if success:
                            print(f"   🎉 Successfully applied to {job['title']}!")
                            self.session_stats['applications_successful'] += 1
                            applications_made += 1
                            self.save_application_record(job, 'SUCCESS')
                        else:
                            print(f"   ❌ Application failed for {job['title']}")
                            self.session_stats['applications_failed'] += 1
                    else:
                        print("   ⚠️ No apply button found")
                        self.session_stats['applications_failed'] += 1
                else:
                    print("   ⚠️ No job URL available")
                    self.session_stats['applications_failed'] += 1
                
                self.session_stats['jobs_applied'] += 1
                
                # Delay between applications
                if applications_made < max_applications:
                    print("   ⏳ Waiting 30 seconds before next application...")
                    time.sleep(30)
                
            except Exception as e:
                print(f"   ❌ Application error: {str(e)}")
                self.session_stats['applications_failed'] += 1
        
        return applications_made
    
    def handle_application_form(self, job):
        """Handle application form if present"""
        try:
            print("   📝 Checking for application form...")
            time.sleep(2)
            
            # Look for form elements
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, 'form, .application-form, .modal')
            
            if form_elements:
                print("   📋 Application form detected")
                
                # Look for cover letter field
                cover_letter_selectors = [
                    'textarea[name*="cover"]',
                    'textarea[placeholder*="cover"]',
                    '#cover_letter',
                    'textarea'
                ]
                
                for selector in cover_letter_selectors:
                    try:
                        cover_letter_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if cover_letter_field.is_displayed():
                            print("   ✍️ Filling cover letter...")
                            cover_letter_text = f"Dear {job['company']} Team,\n\nI am excited to apply for the {job['title']} position. I am a motivated student eager to contribute and learn.\n\nThank you for considering my application.\n\nBest regards"
                            cover_letter_field.clear()
                            cover_letter_field.send_keys(cover_letter_text)
                            time.sleep(1)
                            break
                    except:
                        continue
                
                # Look for submit button
                submit_selectors = [
                    'button[type="submit"]',
                    '.submit-btn',
                    'input[type="submit"]',
                    'button[contains(text(), "Submit")]'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_button.is_displayed() and submit_button.is_enabled():
                            print("   🚀 Submitting application...")
                            submit_button.click()
                            time.sleep(3)
                            return True
                    except:
                        continue
            
            print("   ✅ Application completed")
            return True
            
        except Exception as e:
            print(f"   ❌ Form handling error: {str(e)}")
            return False
    
    def save_application_record(self, job, status):
        """Save application record"""
        try:
            record = {
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'url': job['url'],
                'applied_at': datetime.now().isoformat(),
                'status': status,
                'platform': 'internshala'
            }
            
            # Save to file
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
            print(f"   ⚠️ Could not save application record: {str(e)}")
    
    def print_session_summary(self):
        """Print session summary"""
        duration = datetime.now() - self.session_stats['start_time']
        
        print("\n" + "="*70)
        print("📊 INTERNSHALA APPLICATION SESSION SUMMARY")
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
        """Close browser"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function"""
    print("🎯 SIMPLE INTERNSHALA JOB APPLIER")
    print("="*50)
    print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
    print("🔍 Target: Software Development Internships")
    print("="*50)
    
    applier = SimpleInternshalaApplier()
    
    try:
        # Step 1: Create browser
        if not applier.create_simple_browser():
            print("❌ Cannot proceed without browser")
            return
        
        # Step 2: Login
        if not applier.login_to_internshala():
            print("❌ Cannot proceed without login")
            return
        
        # Step 3: Search for jobs
        jobs = applier.search_for_jobs()
        
        if not jobs:
            print("❌ No jobs found")
            return
        
        # Step 4: Apply to jobs
        print(f"\n🤔 Found {len(jobs)} internships. Applying to first 3...")
        applications_made = applier.apply_to_jobs(jobs, max_applications=3)
        
        print(f"\n🎉 Applied to {applications_made} internships!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    
    finally:
        applier.print_session_summary()
        applier.close()
        print("\n✅ Session completed!")

if __name__ == "__main__":
    main()
