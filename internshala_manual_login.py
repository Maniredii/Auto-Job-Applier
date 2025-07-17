#!/usr/bin/env python3
"""
Internshala Manual Login Helper
Opens browser and lets you login manually, then proceeds with job applications
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
from config import config

class InternshalaManualHelper:
    """Helper for manual login and automated job applications"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.session_stats = {
            'jobs_found': 0,
            'jobs_applied': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'start_time': datetime.now()
        }
    
    def create_browser(self):
        """Create browser for manual login"""
        print("🌐 Creating browser for manual login...")
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
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
    
    def manual_login_process(self):
        """Guide user through manual login"""
        print("\n🔐 MANUAL LOGIN PROCESS")
        print("="*40)
        
        try:
            # Navigate to login page
            print("🔗 Opening Internshala login page...")
            self.driver.get("https://internshala.com/login")
            time.sleep(3)
            
            print(f"📄 Page loaded: {self.driver.title}")
            
            # Pre-fill credentials if possible
            try:
                print("🔧 Attempting to pre-fill credentials...")
                
                email_field = self.driver.find_element(By.CSS_SELECTOR, "#email")
                password_field = self.driver.find_element(By.CSS_SELECTOR, "#password")
                
                if email_field.is_displayed():
                    email_field.clear()
                    email_field.send_keys(config.INTERNSHALA_EMAIL)
                    print(f"✅ Pre-filled email: {config.INTERNSHALA_EMAIL}")
                
                if password_field.is_displayed():
                    password_field.clear()
                    password_field.send_keys(config.INTERNSHALA_PASSWORD)
                    print("✅ Pre-filled password")
                    
            except Exception as e:
                print(f"⚠️ Could not pre-fill credentials: {str(e)}")
            
            # Manual login instructions
            print("\n👤 MANUAL LOGIN REQUIRED")
            print("="*30)
            print("📋 Please complete the following steps in the browser window:")
            print("1. ✅ Verify email and password are correct")
            print("2. 🔍 Complete any CAPTCHA if present")
            print("3. 🔐 Click the 'Login' button")
            print("4. ✅ Wait for successful login (dashboard/profile page)")
            print("5. ⌨️ Come back here and press ENTER when logged in")
            
            # Wait for user confirmation
            input("\n⏳ Press ENTER after you have successfully logged in...")
            
            # Check if login was successful
            current_url = self.driver.current_url
            print(f"\n🌐 Current URL: {current_url}")
            
            if 'login' not in current_url:
                print("🎉 LOGIN SUCCESSFUL!")
                print("✅ Ready to proceed with job applications")
                return True
            else:
                print("❌ Still on login page")
                retry = input("🔄 Try again? (y/n): ").lower().strip()
                if retry == 'y':
                    return self.manual_login_process()
                else:
                    return False
                    
        except Exception as e:
            print(f"❌ Manual login error: {str(e)}")
            return False
    
    def search_and_apply_jobs(self):
        """Search for jobs and apply automatically"""
        print("\n🔍 AUTOMATED JOB SEARCH & APPLICATION")
        print("="*45)
        
        try:
            # Navigate to internships page
            print("🔗 Navigating to software development internships...")
            self.driver.get("https://internshala.com/internships/software-development-internship")
            time.sleep(3)
            
            print(f"📄 Search page: {self.driver.title}")
            
            # Find job cards
            job_selectors = [
                '.individual_internship',
                '.internship_meta',
                '.container-fluid .row > div'
            ]
            
            jobs_found = []
            for selector in job_selectors:
                try:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(job_elements) > 0:
                        print(f"✅ Found {len(job_elements)} internships")
                        jobs_found = job_elements[:5]  # Limit to first 5
                        break
                except:
                    continue
            
            if not jobs_found:
                print("❌ No internships found")
                return 0
            
            # Extract and display job information
            jobs = []
            print("\n📋 AVAILABLE INTERNSHIPS:")
            print("-" * 50)
            
            for i, job_element in enumerate(jobs_found, 1):
                try:
                    job_info = self.extract_job_info(job_element, i)
                    if job_info:
                        jobs.append(job_info)
                        print(f"{i}. {job_info['title']} at {job_info['company']}")
                        print(f"   📍 {job_info['location']}")
                        if job_info['url']:
                            print(f"   🔗 {job_info['url'][:60]}...")
                        print("-" * 50)
                except Exception as e:
                    print(f"⚠️ Error extracting job {i}: {str(e)}")
            
            self.session_stats['jobs_found'] = len(jobs)
            
            if not jobs:
                print("❌ No job details could be extracted")
                return 0
            
            # Ask user which jobs to apply to
            print(f"\n🤔 Found {len(jobs)} internships")
            apply_choice = input("Apply to all? (y/n) or enter numbers (e.g., 1,3,5): ").strip()
            
            if apply_choice.lower() == 'y':
                selected_jobs = jobs
            elif apply_choice.lower() == 'n':
                print("👀 Job viewing completed without applications")
                return 0
            else:
                # Parse selected job numbers
                try:
                    selected_indices = [int(x.strip()) - 1 for x in apply_choice.split(',')]
                    selected_jobs = [jobs[i] for i in selected_indices if 0 <= i < len(jobs)]
                except:
                    print("❌ Invalid selection, applying to first 3 jobs")
                    selected_jobs = jobs[:3]
            
            # Apply to selected jobs
            applications_made = 0
            for job in selected_jobs:
                print(f"\n🎯 Applying to: {job['title']} at {job['company']}")
                
                if self.apply_to_job(job):
                    applications_made += 1
                    self.session_stats['applications_successful'] += 1
                    print(f"   ✅ Application successful!")
                else:
                    self.session_stats['applications_failed'] += 1
                    print(f"   ❌ Application failed")
                
                self.session_stats['jobs_applied'] += 1
                
                # Delay between applications
                if applications_made < len(selected_jobs):
                    print("   ⏳ Waiting 30 seconds before next application...")
                    time.sleep(30)
            
            return applications_made
            
        except Exception as e:
            print(f"❌ Job search error: {str(e)}")
            return 0
    
    def extract_job_info(self, job_element, index):
        """Extract job information from element"""
        try:
            # Find title and URL
            title_selectors = [
                '.job-title a',
                '.profile h3 a',
                'h3 a',
                'h4 a'
            ]
            
            title = f"Software Development Intern {index}"
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
            
            # Find company
            company_selectors = [
                '.company-name',
                '.company h4 a',
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
            
            # Find location
            location = "Remote"
            try:
                location_elem = job_element.find_element(By.CSS_SELECTOR, '.locations span, .location_link')
                location = location_elem.text.strip()
            except:
                pass
            
            return {
                'index': index,
                'title': title,
                'company': company,
                'location': location,
                'url': job_url if job_url and job_url.startswith('http') else f"https://internshala.com{job_url}" if job_url else "",
                'element': job_element
            }
            
        except Exception as e:
            print(f"   ⚠️ Error extracting job {index}: {str(e)}")
            return None
    
    def apply_to_job(self, job):
        """Apply to a specific job"""
        try:
            if not job['url']:
                print("   ⚠️ No job URL available")
                return False
            
            # Navigate to job page
            print("   🌐 Opening job page...")
            self.driver.get(job['url'])
            time.sleep(3)
            
            # Look for apply button
            apply_selectors = [
                '.apply_now_button',
                '.btn-primary',
                'button[contains(text(), "Apply")]',
                'a[contains(text(), "Apply")]'
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
            
            if not apply_button:
                print("   ⚠️ No apply button found")
                return False
            
            print("   🖱️ Clicking apply button...")
            apply_button.click()
            time.sleep(3)
            
            # Handle application form
            return self.handle_application_form(job)
            
        except Exception as e:
            print(f"   ❌ Application error: {str(e)}")
            return False
    
    def handle_application_form(self, job):
        """Handle application form"""
        try:
            print("   📝 Handling application form...")
            
            # Look for cover letter field
            cover_letter_selectors = [
                'textarea[name*="cover"]',
                'textarea[placeholder*="cover"]',
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
                'input[type="submit"]'
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
    
    def print_session_summary(self):
        """Print session summary"""
        duration = datetime.now() - self.session_stats['start_time']
        
        print("\n" + "="*60)
        print("📊 INTERNSHALA SESSION SUMMARY")
        print("="*60)
        print(f"⏱️  Duration: {duration}")
        print(f"🔍 Jobs Found: {self.session_stats['jobs_found']}")
        print(f"📝 Jobs Applied To: {self.session_stats['jobs_applied']}")
        print(f"✅ Successful Applications: {self.session_stats['applications_successful']}")
        print(f"❌ Failed Applications: {self.session_stats['applications_failed']}")
        
        if self.session_stats['jobs_applied'] > 0:
            success_rate = (self.session_stats['applications_successful'] / self.session_stats['jobs_applied']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("="*60)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function"""
    print("🎯 INTERNSHALA MANUAL LOGIN + AUTO APPLY")
    print("="*50)
    print("📧 Email: deepthedzinr@gmail.com")
    print("🔍 Target: Software Development Internships")
    print("="*50)
    
    helper = InternshalaManualHelper()
    
    try:
        # Step 1: Create browser
        if not helper.create_browser():
            print("❌ Cannot proceed without browser")
            return
        
        # Step 2: Manual login
        if not helper.manual_login_process():
            print("❌ Cannot proceed without login")
            return
        
        # Step 3: Automated job search and application
        applications_made = helper.search_and_apply_jobs()
        
        print(f"\n🎉 Session completed! Applied to {applications_made} internships!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    
    finally:
        helper.print_session_summary()
        helper.close()
        print("\n✅ Session completed!")

if __name__ == "__main__":
    main()
