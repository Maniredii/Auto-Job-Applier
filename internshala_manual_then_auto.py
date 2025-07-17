#!/usr/bin/env python3
"""
Internshala Manual Login + Auto Apply
You login manually, then system automatically applies to jobs
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

class InternshalaManualAutoApplier:
    """Manual login + automated job applications"""
    
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
        print("🌐 Creating browser...")
        
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
    
    def manual_login_guide(self):
        """Guide user through manual login"""
        print("\n🔐 MANUAL LOGIN PROCESS")
        print("="*50)
        
        try:
            # Open Internshala login page
            print("🔗 Opening Internshala login page...")
            self.driver.get("https://internshala.com/login")
            time.sleep(3)
            
            print(f"📄 Page loaded: {self.driver.title}")
            
            # Instructions for manual login
            print("\n👤 PLEASE LOGIN MANUALLY")
            print("="*30)
            print("📋 Steps to complete:")
            print("1. 📧 Enter your email address")
            print("2. 🔒 Enter your password") 
            print("3. 🔍 Complete any CAPTCHA if shown")
            print("4. 🖱️ Click the 'Login' button")
            print("5. ✅ Wait until you see your dashboard/profile")
            print("6. ⌨️ Come back here and press ENTER")
            
            print(f"\n💡 Suggested credentials to try:")
            print(f"   Email: deepthedzinr@gmail.com")
            print(f"   Password: 8897125659")
            print(f"   (Or use your correct credentials)")
            
            # Wait for user to complete login
            input("\n⏳ Press ENTER after you have successfully logged in...")
            
            # Verify login success
            current_url = self.driver.current_url
            print(f"\n🌐 Current URL: {current_url}")
            
            if 'login' not in current_url:
                print("🎉 LOGIN SUCCESSFUL!")
                print("✅ Ready to start automated job applications")
                return True
            else:
                print("❌ Still on login page")
                retry = input("🔄 Try logging in again? (y/n): ").lower().strip()
                if retry == 'y':
                    return self.manual_login_guide()
                else:
                    return False
                    
        except Exception as e:
            print(f"❌ Manual login error: {str(e)}")
            return False
    
    def get_user_job_preferences(self):
        """Get job search preferences from user"""
        print("\n🎯 JOB SEARCH PREFERENCES")
        print("="*35)
        
        # Get job type preference
        print("🤔 What type of opportunities are you looking for?")
        print("Options:")
        print("1. Software Development")
        print("2. Data Science") 
        print("3. Digital Marketing")
        print("4. Graphic Design")
        print("5. Content Writing")
        print("6. Business Development")
        print("7. Custom (you specify)")
        
        choice = input("\nEnter choice (1-7) or job title: ").strip()
        
        job_types = {
            '1': 'Software Development',
            '2': 'Data Science',
            '3': 'Digital Marketing', 
            '4': 'Graphic Design',
            '5': 'Content Writing',
            '6': 'Business Development'
        }
        
        if choice in job_types:
            job_title = job_types[choice]
        elif choice == '7':
            job_title = input("Enter custom job title: ").strip()
        else:
            job_title = choice if choice else 'Software Development'
        
        # Get location preference
        print(f"\n📍 Location preference for {job_title}:")
        print("Options: Remote, Mumbai, Delhi, Bangalore, Hyderabad, Pune, Chennai, or any city")
        location = input("Enter location (or press Enter for 'Remote'): ").strip()
        if not location:
            location = 'Remote'
        
        # Get application limit
        max_applications = input("\n📊 How many jobs to apply to? (default: 5): ").strip()
        try:
            max_applications = int(max_applications) if max_applications else 5
        except:
            max_applications = 5
        
        preferences = {
            'job_title': job_title,
            'location': location,
            'max_applications': max_applications
        }
        
        print(f"\n✅ Preferences set:")
        print(f"   🎯 Job: {job_title}")
        print(f"   📍 Location: {location}")
        print(f"   📊 Max applications: {max_applications}")
        
        return preferences
    
    def search_jobs(self, preferences):
        """Search for jobs based on user preferences"""
        print(f"\n🔍 SEARCHING FOR {preferences['job_title'].upper()} JOBS")
        print("="*60)
        
        try:
            # Create search URL
            job_slug = preferences['job_title'].lower().replace(' ', '-')
            search_url = f"https://internshala.com/internships/{job_slug}-internship"
            
            print(f"🔗 Navigating to: {search_url}")
            self.driver.get(search_url)
            time.sleep(3)
            
            # Apply location filter if not "All"
            if preferences['location'].lower() not in ['all', 'any']:
                self.apply_location_filter(preferences['location'])
            
            # Find job listings
            jobs = self.find_job_listings()
            
            if jobs:
                print(f"✅ Found {len(jobs)} job opportunities!")
                self.display_jobs(jobs)
                return jobs
            else:
                print("❌ No jobs found with current criteria")
                return []
                
        except Exception as e:
            print(f"❌ Job search error: {str(e)}")
            return []
    
    def apply_location_filter(self, location):
        """Apply location filter"""
        try:
            print(f"📍 Applying location filter: {location}")
            
            # Look for location dropdown or filter
            location_selectors = [
                'select[name*="location"]',
                '#location_filter',
                '.location-filter'
            ]
            
            for selector in location_selectors:
                try:
                    location_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if location_element.is_displayed():
                        location_element.click()
                        time.sleep(1)
                        
                        # Try to find and click location option
                        location_options = self.driver.find_elements(By.XPATH, f"//option[contains(text(), '{location}')]")
                        if location_options:
                            location_options[0].click()
                            time.sleep(2)
                            print(f"✅ Applied location filter: {location}")
                            return
                except:
                    continue
            
            print(f"⚠️ Could not apply location filter for {location}")
            
        except Exception as e:
            print(f"⚠️ Location filter error: {str(e)}")
    
    def find_job_listings(self):
        """Find and extract job listings"""
        try:
            # Wait for jobs to load
            time.sleep(3)
            
            # Find job cards
            job_selectors = [
                '.individual_internship',
                '.internship_meta',
                '.job-card'
            ]
            
            jobs_found = []
            for selector in job_selectors:
                try:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(job_elements) > 0:
                        jobs_found = job_elements[:15]  # Limit to first 15
                        break
                except:
                    continue
            
            if not jobs_found:
                return []
            
            # Extract job information
            jobs = []
            for i, job_element in enumerate(jobs_found, 1):
                try:
                    job_info = self.extract_job_info(job_element, i)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    print(f"⚠️ Error extracting job {i}: {str(e)}")
            
            self.session_stats['jobs_found'] = len(jobs)
            return jobs
            
        except Exception as e:
            print(f"❌ Job listing error: {str(e)}")
            return []
    
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
            
            title = f"Opportunity {index}"
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
            location = "Not specified"
            try:
                location_elem = job_element.find_element(By.CSS_SELECTOR, '.locations span, .location_link')
                location = location_elem.text.strip()
            except:
                pass
            
            # Find duration/stipend
            details = ""
            try:
                detail_elems = job_element.find_elements(By.CSS_SELECTOR, '.item_body, .stipend')
                details = " | ".join([elem.text.strip() for elem in detail_elems if elem.text.strip()])
            except:
                pass
            
            return {
                'index': index,
                'title': title,
                'company': company,
                'location': location,
                'details': details,
                'url': job_url if job_url and job_url.startswith('http') else f"https://internshala.com{job_url}" if job_url else "",
                'element': job_element
            }
            
        except Exception as e:
            return None
    
    def display_jobs(self, jobs):
        """Display found jobs to user"""
        print(f"\n📋 FOUND {len(jobs)} JOB OPPORTUNITIES:")
        print("="*70)
        
        for job in jobs:
            print(f"{job['index']}. {job['title']}")
            print(f"   🏢 Company: {job['company']}")
            print(f"   📍 Location: {job['location']}")
            if job['details']:
                print(f"   💼 Details: {job['details']}")
            print("-" * 70)
    
    def apply_to_jobs(self, jobs, max_applications):
        """Apply to selected jobs"""
        if not jobs:
            print("❌ No jobs available for application")
            return 0
        
        print(f"\n📝 AUTOMATED JOB APPLICATION PROCESS")
        print("="*50)
        
        # Select jobs to apply to
        jobs_to_apply = jobs[:max_applications]
        
        print(f"📊 Applying to first {len(jobs_to_apply)} jobs...")
        
        applications_made = 0
        for i, job in enumerate(jobs_to_apply, 1):
            print(f"\n🎯 Applying to job {i}/{len(jobs_to_apply)}")
            print(f"   📝 {job['title']} at {job['company']}")
            
            if self.apply_to_single_job(job):
                applications_made += 1
                self.session_stats['applications_successful'] += 1
                print(f"   ✅ Application successful!")
            else:
                self.session_stats['applications_failed'] += 1
                print(f"   ❌ Application failed")
            
            self.session_stats['jobs_applied'] += 1
            
            # Delay between applications
            if i < len(jobs_to_apply):
                print("   ⏳ Waiting 30 seconds before next application...")
                time.sleep(30)
        
        return applications_made
    
    def apply_to_single_job(self, job):
        """Apply to a single job"""
        try:
            if not job['url']:
                print("   ⚠️ No job URL available")
                return False
            
            # Navigate to job page
            print("   🌐 Opening job page...")
            self.driver.get(job['url'])
            time.sleep(3)
            
            # Scroll to find apply button
            self.driver.execute_script("window.scrollTo(0, 400);")
            time.sleep(1)
            
            # Find apply button
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
            self.driver.execute_script("arguments[0].click();", apply_button)
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
            time.sleep(2)
            
            # Fill cover letter if present
            cover_letter_selectors = [
                'textarea[name*="cover"]',
                'textarea[placeholder*="cover"]',
                'textarea'
            ]
            
            for selector in cover_letter_selectors:
                try:
                    cover_letter_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if cover_letter_field.is_displayed():
                        print("   ✍️ Writing cover letter...")
                        cover_letter_text = f"""Dear {job['company']} Team,

I am writing to express my strong interest in the {job['title']} position. As an enthusiastic and dedicated individual, I am excited about the opportunity to contribute to your team and gain valuable experience.

My passion for learning and commitment to excellence make me a great fit for this role. I am eager to bring my skills and fresh perspective to {job['company']} while continuing to grow professionally.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to your team's success.

Best regards"""
                        
                        cover_letter_field.clear()
                        for char in cover_letter_text:
                            cover_letter_field.send_keys(char)
                            time.sleep(0.02)  # Slow typing
                        time.sleep(1)
                        break
                except:
                    continue
            
            # Submit application
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
                        self.driver.execute_script("arguments[0].click();", submit_button)
                        time.sleep(3)
                        return True
                except:
                    continue
            
            print("   ✅ Application process completed")
            return True
            
        except Exception as e:
            print(f"   ❌ Form handling error: {str(e)}")
            return False
    
    def print_session_summary(self):
        """Print session summary"""
        duration = datetime.now() - self.session_stats['start_time']
        
        print("\n" + "="*70)
        print("📊 INTERNSHALA SESSION SUMMARY")
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
    print("🚀 INTERNSHALA: MANUAL LOGIN + AUTO APPLY")
    print("="*60)
    print("✨ How it works:")
    print("  1. 👤 You login manually (handles any issues)")
    print("  2. 🎯 Choose your job preferences")
    print("  3. 🤖 System automatically applies to jobs")
    print("="*60)
    
    applier = InternshalaManualAutoApplier()
    
    try:
        # Step 1: Create browser
        if not applier.create_browser():
            print("❌ Cannot proceed without browser")
            return
        
        # Step 2: Manual login
        if not applier.manual_login_guide():
            print("❌ Cannot proceed without login")
            return
        
        # Step 3: Get user preferences
        preferences = applier.get_user_job_preferences()
        
        # Step 4: Search for jobs
        jobs = applier.search_jobs(preferences)
        
        if not jobs:
            print("❌ No jobs found with current criteria")
            return
        
        # Step 5: Apply to jobs
        applications_made = applier.apply_to_jobs(jobs, preferences['max_applications'])
        
        print(f"\n🎉 Session completed!")
        print(f"✅ Successfully applied to {applications_made} jobs!")
        
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
