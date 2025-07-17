#!/usr/bin/env python3
"""
Simple LinkedIn Job Applier
Uses basic Chrome setup that works with current system
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
from selenium.webdriver.common.keys import Keys
from config import config

class SimpleLinkedInApplier:
    """Simple LinkedIn job applier"""
    
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
        """Create simple Chrome browser"""
        print("🌐 Creating LinkedIn browser...")
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            print("✅ Browser created successfully!")
            return True
        except Exception as e:
            print(f"❌ Browser creation failed: {str(e)}")
            return False
    
    def manual_linkedin_login(self):
        """Guide user through LinkedIn login"""
        print("\n🔐 LINKEDIN LOGIN PROCESS")
        print("="*40)
        
        try:
            # Navigate to LinkedIn login
            print("🔗 Opening LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            print(f"📄 Page loaded: {self.driver.title}")
            
            # Pre-fill credentials if possible
            try:
                print("🔧 Attempting to pre-fill credentials...")
                
                # Find email field
                email_selectors = ['#username', 'input[name="session_key"]', 'input[type="email"]']
                for selector in email_selectors:
                    try:
                        email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if email_field.is_displayed():
                            email_field.clear()
                            email_field.send_keys(config.LINKEDIN_EMAIL)
                            print(f"✅ Pre-filled email: {config.LINKEDIN_EMAIL}")
                            break
                    except:
                        continue
                
                # Find password field
                password_selectors = ['#password', 'input[name="session_password"]', 'input[type="password"]']
                for selector in password_selectors:
                    try:
                        password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if password_field.is_displayed():
                            password_field.clear()
                            password_field.send_keys(config.LINKEDIN_PASSWORD)
                            print("✅ Pre-filled password")
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Could not pre-fill credentials: {str(e)}")
            
            # Manual login instructions
            print("\n👤 MANUAL LINKEDIN LOGIN")
            print("="*30)
            print("📋 Please complete these steps in the browser:")
            print("1. ✅ Verify email and password are correct")
            print("2. 🔍 Complete any security verification if needed")
            print("3. 🖱️ Click the 'Sign in' button")
            print("4. ✅ Wait for LinkedIn homepage/feed to load")
            print("5. ⌨️ Come back here and press ENTER")
            
            print(f"\n💡 Your LinkedIn credentials:")
            print(f"   Email/Phone: {config.LINKEDIN_EMAIL}")
            print(f"   Password: {config.LINKEDIN_PASSWORD}")
            
            # Wait for user confirmation
            input("\n⏳ Press ENTER after you have successfully logged in...")
            
            # Check login success
            current_url = self.driver.current_url
            print(f"\n🌐 Current URL: {current_url}")
            
            if 'feed' in current_url or 'linkedin.com' in current_url and 'login' not in current_url:
                print("🎉 LINKEDIN LOGIN SUCCESSFUL!")
                return True
            else:
                print("❌ Still on login page")
                retry = input("🔄 Try logging in again? (y/n): ").lower().strip()
                if retry == 'y':
                    return self.manual_linkedin_login()
                else:
                    return False
                    
        except Exception as e:
            print(f"❌ LinkedIn login error: {str(e)}")
            return False
    
    def get_job_search_preferences(self):
        """Get job search preferences from user"""
        print("\n🎯 LINKEDIN JOB SEARCH PREFERENCES")
        print("="*40)
        
        # Get job title
        print("🤔 What job titles are you looking for?")
        print("Examples: Software Engineer, Data Analyst, Marketing Manager")
        job_title = input("Enter job title: ").strip()
        if not job_title:
            job_title = "Software Engineer"
            print(f"📝 Using default: {job_title}")
        
        # Get location
        print(f"\n📍 Location for {job_title} jobs:")
        print("Examples: Remote, New York, San Francisco, London")
        location = input("Enter location (or 'Remote'): ").strip()
        if not location:
            location = "Remote"
            print(f"📍 Using default: {location}")
        
        # Get experience level
        print(f"\n📊 Experience level:")
        print("1. Entry level")
        print("2. Associate")
        print("3. Mid-Senior level")
        print("4. Director")
        print("5. Any")
        
        exp_choice = input("Choose experience level (1-5): ").strip()
        exp_levels = {
            '1': 'Entry level',
            '2': 'Associate', 
            '3': 'Mid-Senior level',
            '4': 'Director',
            '5': 'Any'
        }
        experience = exp_levels.get(exp_choice, 'Any')
        
        # Get application limit
        max_apps = input("\n📊 How many jobs to apply to? (default: 10): ").strip()
        try:
            max_applications = int(max_apps) if max_apps else 10
        except:
            max_applications = 10
        
        preferences = {
            'job_title': job_title,
            'location': location,
            'experience': experience,
            'max_applications': max_applications
        }
        
        print(f"\n✅ LinkedIn job search preferences:")
        print(f"   🎯 Job: {job_title}")
        print(f"   📍 Location: {location}")
        print(f"   📊 Experience: {experience}")
        print(f"   📝 Max applications: {max_applications}")
        
        return preferences
    
    def search_linkedin_jobs(self, preferences):
        """Search for jobs on LinkedIn"""
        print(f"\n🔍 SEARCHING LINKEDIN JOBS")
        print("="*40)
        
        try:
            # Navigate to LinkedIn jobs
            print("🔗 Navigating to LinkedIn Jobs...")
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Search for jobs
            print(f"🔍 Searching for: {preferences['job_title']}")
            
            # Find search box
            search_selectors = [
                'input[aria-label*="Search by title"]',
                'input[placeholder*="Search by title"]',
                '#jobs-search-box-keyword-id-ember',
                '.jobs-search-box__text-input'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if search_box.is_displayed():
                        break
                except:
                    continue
            
            if search_box:
                print("✅ Found search box, entering job title...")
                search_box.clear()
                search_box.send_keys(preferences['job_title'])
                time.sleep(1)
            
            # Find location box
            location_selectors = [
                'input[aria-label*="City"]',
                'input[placeholder*="City"]',
                '#jobs-search-box-location-id-ember',
                '.jobs-search-box__text-input[placeholder*="City"]'
            ]
            
            location_box = None
            for selector in location_selectors:
                try:
                    location_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if location_box.is_displayed():
                        break
                except:
                    continue
            
            if location_box:
                print("✅ Found location box, entering location...")
                location_box.clear()
                location_box.send_keys(preferences['location'])
                time.sleep(1)
            
            # Click search button or press Enter
            search_button_selectors = [
                'button[aria-label*="Search"]',
                '.jobs-search-box__submit-button',
                'button[type="submit"]'
            ]
            
            search_clicked = False
            for selector in search_button_selectors:
                try:
                    search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if search_button.is_displayed():
                        print("🖱️ Clicking search button...")
                        search_button.click()
                        search_clicked = True
                        break
                except:
                    continue
            
            if not search_clicked and search_box:
                print("⌨️ Pressing Enter to search...")
                search_box.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Find job listings
            jobs = self.find_linkedin_job_listings()
            
            if jobs:
                print(f"✅ Found {len(jobs)} LinkedIn job opportunities!")
                self.display_linkedin_jobs(jobs)
                return jobs
            else:
                print("❌ No LinkedIn jobs found")
                return []
                
        except Exception as e:
            print(f"❌ LinkedIn job search error: {str(e)}")
            return []
    
    def find_linkedin_job_listings(self):
        """Find LinkedIn job listings"""
        try:
            print("🔍 Looking for job listings...")
            time.sleep(3)
            
            # Find job cards
            job_selectors = [
                '.job-card-container',
                '.jobs-search-results__list-item',
                '.job-card-list__entity',
                '.jobs-search-results-list'
            ]
            
            jobs_found = []
            for selector in job_selectors:
                try:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(job_elements) > 0:
                        print(f"✅ Found {len(job_elements)} job cards")
                        jobs_found = job_elements[:15]  # Limit to first 15
                        break
                except:
                    continue
            
            if not jobs_found:
                print("⚠️ No job cards found, trying alternative method...")
                # Try to find any clickable job links
                job_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/jobs/view/"]')
                if job_links:
                    print(f"✅ Found {len(job_links)} job links")
                    jobs_found = job_links[:15]
            
            if not jobs_found:
                return []
            
            # Extract job information
            jobs = []
            for i, job_element in enumerate(jobs_found, 1):
                try:
                    job_info = self.extract_linkedin_job_info(job_element, i)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    print(f"⚠️ Error extracting LinkedIn job {i}: {str(e)}")
            
            self.session_stats['jobs_found'] = len(jobs)
            return jobs
            
        except Exception as e:
            print(f"❌ LinkedIn job listing error: {str(e)}")
            return []
    
    def extract_linkedin_job_info(self, job_element, index):
        """Extract LinkedIn job information"""
        try:
            # Find job title and URL
            title_selectors = [
                '.job-card-list__title a',
                '.job-card-container__link',
                'a[data-control-name="job_card_title"]',
                'h3 a'
            ]
            
            title = f"LinkedIn Job {index}"
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
            
            # If job_element is a link itself
            if not job_url and job_element.tag_name == 'a':
                job_url = job_element.get_attribute('href')
                title = job_element.text.strip() or f"LinkedIn Job {index}"
            
            # Find company
            company_selectors = [
                '.job-card-container__company-name',
                '.job-card-list__company-name',
                'a[data-control-name="job_card_company_link"]'
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
            location_selectors = [
                '.job-card-container__metadata-item',
                '.job-card-list__location',
                '.job-card-container__location'
            ]
            
            location = "Location not specified"
            for selector in location_selectors:
                try:
                    location_elem = job_element.find_element(By.CSS_SELECTOR, selector)
                    location_text = location_elem.text.strip()
                    if location_text and 'ago' not in location_text.lower():
                        location = location_text
                        break
                except:
                    continue
            
            return {
                'index': index,
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'element': job_element
            }
            
        except Exception as e:
            return None
    
    def display_linkedin_jobs(self, jobs):
        """Display LinkedIn jobs"""
        print(f"\n📋 FOUND {len(jobs)} LINKEDIN JOBS:")
        print("="*60)
        
        for job in jobs:
            print(f"{job['index']}. {job['title']}")
            print(f"   🏢 Company: {job['company']}")
            print(f"   📍 Location: {job['location']}")
            if job['url']:
                print(f"   🔗 URL: {job['url'][:50]}...")
            print("-" * 60)
    
    def apply_to_linkedin_jobs(self, jobs, max_applications):
        """Apply to LinkedIn jobs"""
        if not jobs:
            print("❌ No LinkedIn jobs available")
            return 0
        
        print(f"\n📝 LINKEDIN JOB APPLICATION PROCESS")
        print("="*50)
        
        jobs_to_apply = jobs[:max_applications]
        print(f"📊 Applying to first {len(jobs_to_apply)} jobs...")
        
        applications_made = 0
        for i, job in enumerate(jobs_to_apply, 1):
            print(f"\n🎯 Applying to LinkedIn job {i}/{len(jobs_to_apply)}")
            print(f"   📝 {job['title']} at {job['company']}")
            
            if self.apply_to_linkedin_job(job):
                applications_made += 1
                self.session_stats['applications_successful'] += 1
                print(f"   ✅ LinkedIn application successful!")
            else:
                self.session_stats['applications_failed'] += 1
                print(f"   ❌ LinkedIn application failed")
            
            self.session_stats['jobs_applied'] += 1
            
            # Delay between applications
            if i < len(jobs_to_apply):
                print("   ⏳ Waiting 45 seconds before next application...")
                time.sleep(45)
        
        return applications_made
    
    def apply_to_linkedin_job(self, job):
        """Apply to a single LinkedIn job"""
        try:
            if not job['url']:
                print("   ⚠️ No LinkedIn job URL available")
                return False
            
            # Navigate to job page
            print("   🌐 Opening LinkedIn job page...")
            self.driver.get(job['url'])
            time.sleep(3)
            
            # Look for Easy Apply button
            easy_apply_selectors = [
                'button[aria-label*="Easy Apply"]',
                '.jobs-apply-button',
                'button[data-control-name="jobdetails_topcard_inapply"]'
            ]
            
            easy_apply_button = None
            for selector in easy_apply_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and 'easy apply' in button.text.lower():
                        easy_apply_button = button
                        break
                except:
                    continue
            
            if easy_apply_button:
                print("   🖱️ Clicking Easy Apply...")
                easy_apply_button.click()
                time.sleep(3)
                
                # Handle Easy Apply process
                return self.handle_linkedin_easy_apply(job)
            else:
                print("   ⚠️ No Easy Apply button found")
                return False
                
        except Exception as e:
            print(f"   ❌ LinkedIn application error: {str(e)}")
            return False
    
    def handle_linkedin_easy_apply(self, job):
        """Handle LinkedIn Easy Apply process"""
        try:
            print("   📝 Handling LinkedIn Easy Apply...")
            
            # Handle multiple steps of Easy Apply
            max_steps = 5
            current_step = 1
            
            while current_step <= max_steps:
                print(f"   📋 Easy Apply step {current_step}...")
                
                # Look for text areas (cover letter, additional info)
                text_areas = self.driver.find_elements(By.CSS_SELECTOR, 'textarea')
                for textarea in text_areas:
                    if textarea.is_displayed() and not textarea.get_attribute('value'):
                        print("   ✍️ Filling text area...")
                        cover_letter = f"I am excited to apply for the {job['title']} position at {job['company']}. I believe my skills and enthusiasm make me a great fit for this role."
                        textarea.send_keys(cover_letter)
                        time.sleep(1)
                
                # Look for Next button
                next_selectors = [
                    'button[aria-label="Continue to next step"]',
                    'button[data-control-name="continue_unify"]',
                    'button:contains("Next")',
                    '.artdeco-button--primary'
                ]
                
                next_clicked = False
                for selector in next_selectors:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if next_button.is_displayed() and next_button.is_enabled():
                            if 'next' in next_button.text.lower() or 'continue' in next_button.text.lower():
                                print(f"   🖱️ Clicking: {next_button.text}")
                                next_button.click()
                                time.sleep(2)
                                next_clicked = True
                                break
                    except:
                        continue
                
                # Look for Submit button
                submit_selectors = [
                    'button[aria-label*="Submit application"]',
                    'button[data-control-name="submit_unify"]',
                    'button:contains("Submit")'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_button.is_displayed() and submit_button.is_enabled():
                            if 'submit' in submit_button.text.lower():
                                print("   🚀 Submitting LinkedIn application...")
                                submit_button.click()
                                time.sleep(3)
                                return True
                    except:
                        continue
                
                if not next_clicked:
                    break
                
                current_step += 1
            
            print("   ✅ LinkedIn Easy Apply process completed")
            return True
            
        except Exception as e:
            print(f"   ❌ LinkedIn Easy Apply error: {str(e)}")
            return False
    
    def print_session_summary(self):
        """Print session summary"""
        duration = datetime.now() - self.session_stats['start_time']
        
        print("\n" + "="*60)
        print("📊 LINKEDIN SESSION SUMMARY")
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
    print("🚀 SIMPLE LINKEDIN JOB APPLIER")
    print("="*50)
    print("✨ Features:")
    print("  - Manual login (handles security)")
    print("  - Automated job search")
    print("  - Easy Apply automation")
    print("  - User-customized preferences")
    print("="*50)
    
    applier = SimpleLinkedInApplier()
    
    try:
        # Step 1: Create browser
        if not applier.create_browser():
            print("❌ Cannot proceed without browser")
            return
        
        # Step 2: Manual LinkedIn login
        if not applier.manual_linkedin_login():
            print("❌ Cannot proceed without LinkedIn login")
            return
        
        # Step 3: Get job preferences
        preferences = applier.get_job_search_preferences()
        
        # Step 4: Search for jobs
        jobs = applier.search_linkedin_jobs(preferences)
        
        if not jobs:
            print("❌ No LinkedIn jobs found")
            return
        
        # Step 5: Apply to jobs
        applications_made = applier.apply_to_linkedin_jobs(jobs, preferences['max_applications'])
        
        print(f"\n🎉 LinkedIn session completed!")
        print(f"✅ Successfully applied to {applications_made} LinkedIn jobs!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    
    finally:
        applier.print_session_summary()
        applier.close()
        print("\n✅ LinkedIn session completed!")

if __name__ == "__main__":
    main()
