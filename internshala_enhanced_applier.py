#!/usr/bin/env python3
"""
Enhanced Internshala Job Applier
Handles login issues, error popups, scrolling, and user-recommended searches
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import config

class EnhancedInternshalaApplier:
    """Enhanced Internshala job applier with robust error handling"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.actions = None
        self.session_stats = {
            'jobs_found': 0,
            'jobs_applied': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'start_time': datetime.now()
        }
    
    def create_browser(self):
        """Create browser with enhanced settings"""
        print("🌐 Creating enhanced browser...")
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")  # Start maximized for better visibility
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)  # Increased timeout
            self.actions = ActionChains(self.driver)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Enhanced browser created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Browser creation failed: {str(e)}")
            return False
    
    def enhanced_login(self, max_retries=3):
        """Enhanced login with error handling and retries"""
        print("\n🔐 ENHANCED LOGIN PROCESS")
        print("="*40)
        print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
        print(f"🔄 Max retries: {max_retries}")
        
        for attempt in range(1, max_retries + 1):
            print(f"\n🎯 Login attempt {attempt}/{max_retries}")
            
            try:
                # Navigate to login page
                print("🔗 Navigating to Internshala login...")
                self.driver.get("https://internshala.com/login")
                time.sleep(3)
                
                # Scroll to top first
                print("📜 Scrolling to top...")
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                # Handle any initial popups
                self.handle_popups()
                
                # Find and fill email field
                print("📧 Finding email field...")
                email_field = self.find_element_with_retry([
                    '#email',
                    'input[name="email"]',
                    'input[type="email"]'
                ])
                
                if not email_field:
                    print("❌ Email field not found")
                    continue
                
                print("⌨️ Filling email...")
                self.slow_type(email_field, config.INTERNSHALA_EMAIL)
                time.sleep(1)
                
                # Find and fill password field
                print("🔒 Finding password field...")
                password_field = self.find_element_with_retry([
                    '#password',
                    'input[name="password"]',
                    'input[type="password"]'
                ])
                
                if not password_field:
                    print("❌ Password field not found")
                    continue
                
                print("⌨️ Filling password...")
                self.slow_type(password_field, config.INTERNSHALA_PASSWORD)
                time.sleep(1)
                
                # Scroll to make sure login button is visible
                print("📜 Scrolling to login button...")
                self.driver.execute_script("window.scrollTo(0, 300);")
                time.sleep(1)
                
                # Find and click login button with multiple methods
                print("🔍 Finding login button...")
                login_success = self.click_login_button()
                
                if not login_success:
                    print("❌ Could not click login button")
                    continue
                
                # Wait for page response
                print("⏳ Waiting for login response...")
                time.sleep(5)
                
                # Handle any error popups
                self.handle_error_popups()
                
                # Scroll page from top to bottom as requested
                print("📜 Scrolling page from top to bottom...")
                self.scroll_page_full()
                
                # Check login result
                if self.check_login_success():
                    print("🎉 LOGIN SUCCESSFUL!")
                    return True
                else:
                    print(f"❌ Login attempt {attempt} failed")
                    if attempt < max_retries:
                        print("🔄 Retrying login...")
                        time.sleep(3)
                    
            except Exception as e:
                print(f"❌ Login attempt {attempt} error: {str(e)}")
                if attempt < max_retries:
                    time.sleep(3)
        
        print("❌ All login attempts failed")
        return False
    
    def find_element_with_retry(self, selectors, timeout=10):
        """Find element with multiple selectors and retry"""
        for selector in selectors:
            try:
                element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if element.is_displayed():
                    print(f"✅ Found element with selector: {selector}")
                    return element
            except:
                continue
        return None
    
    def slow_type(self, element, text):
        """Type text slowly like a human"""
        element.clear()
        time.sleep(0.5)
        for char in text:
            element.send_keys(char)
            time.sleep(0.1)  # Small delay between characters
    
    def click_login_button(self):
        """Enhanced login button clicking with multiple methods"""
        login_selectors = [
            'button[type="submit"]',
            '#login_submit',
            '.login-btn',
            'input[type="submit"]',
            'button:contains("Login")',
            '.btn-primary'
        ]
        
        # Method 1: Try normal click
        for selector in login_selectors:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed() and button.is_enabled():
                    print(f"🖱️ Clicking login button with selector: {selector}")
                    button.click()
                    return True
            except:
                continue
        
        # Method 2: Try JavaScript click
        print("🔧 Trying JavaScript click...")
        for selector in login_selectors:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed():
                    print(f"⚡ JavaScript clicking: {selector}")
                    self.driver.execute_script("arguments[0].click();", button)
                    return True
            except:
                continue
        
        # Method 3: Try ActionChains click
        print("🔧 Trying ActionChains click...")
        for selector in login_selectors:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed():
                    print(f"🎯 ActionChains clicking: {selector}")
                    self.actions.move_to_element(button).click().perform()
                    return True
            except:
                continue
        
        # Method 4: Try Enter key on form
        print("🔧 Trying Enter key submission...")
        try:
            password_field = self.driver.find_element(By.CSS_SELECTOR, '#password')
            password_field.send_keys(Keys.RETURN)
            return True
        except:
            pass
        
        return False
    
    def handle_popups(self):
        """Handle initial popups"""
        popup_selectors = [
            '.close',
            '.modal-close',
            '.popup-close',
            '[data-dismiss="modal"]',
            '.fa-times'
        ]
        
        for selector in popup_selectors:
            try:
                popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                if popup.is_displayed():
                    print(f"🔧 Closing popup: {selector}")
                    popup.click()
                    time.sleep(1)
            except:
                continue
    
    def handle_error_popups(self):
        """Handle error message popups and click OK"""
        print("🔍 Checking for error popups...")
        
        # Look for error messages and OK buttons
        error_ok_selectors = [
            'button:contains("OK")',
            'button:contains("Ok")',
            '.btn:contains("OK")',
            '.swal-button',
            '.alert button',
            '[data-dismiss="alert"]'
        ]
        
        # Check for error text first
        error_text_selectors = [
            '.error',
            '.alert-danger',
            '.invalid-feedback',
            '.swal-text',
            '[class*="error"]'
        ]
        
        error_found = False
        for selector in error_text_selectors:
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for error in error_elements:
                    if error.is_displayed() and error.text.strip():
                        print(f"⚠️ Error message found: {error.text}")
                        error_found = True
            except:
                continue
        
        # Click OK buttons
        for selector in error_ok_selectors:
            try:
                ok_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in ok_buttons:
                    if button.is_displayed() and 'ok' in button.text.lower():
                        print(f"🖱️ Clicking OK button: {button.text}")
                        button.click()
                        time.sleep(1)
                        error_found = True
            except:
                continue
        
        # Try JavaScript method for SweetAlert or similar
        try:
            self.driver.execute_script("""
                if (typeof swal !== 'undefined') {
                    swal.close();
                }
                $('.swal-button').click();
                $('.alert .close').click();
            """)
        except:
            pass
        
        if error_found:
            print("✅ Handled error popups")
        else:
            print("ℹ️ No error popups found")
    
    def scroll_page_full(self):
        """Scroll page from top to bottom slowly"""
        print("📜 Performing full page scroll...")
        
        # Scroll to top first
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Get page height
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Scroll down in steps
        scroll_step = 200
        current_position = 0
        
        while current_position < page_height:
            current_position += scroll_step
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(0.5)  # Slow scroll
        
        # Scroll back to top
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        print("✅ Full page scroll completed")
    
    def check_login_success(self):
        """Check if login was successful"""
        current_url = self.driver.current_url
        page_title = self.driver.title
        
        print(f"🌐 Current URL: {current_url}")
        print(f"📄 Page title: {page_title}")
        
        # Success indicators
        success_indicators = [
            'dashboard' in current_url,
            'student' in current_url,
            'profile' in current_url,
            'login' not in current_url and 'internshala.com' in current_url
        ]
        
        return any(success_indicators)
    
    def search_user_recommended_jobs(self):
        """Search for user-recommended jobs with slow navigation"""
        print("\n🔍 SEARCHING FOR USER-RECOMMENDED JOBS")
        print("="*45)
        
        # Ask user for search preferences
        print("🤔 What type of jobs would you like to search for?")
        job_preferences = input("Enter job title/field (e.g., 'Software Development', 'Data Science', 'Marketing'): ").strip()
        
        if not job_preferences:
            job_preferences = "Software Development"
            print(f"📝 Using default: {job_preferences}")
        
        location_preference = input("Enter preferred location (or 'Remote'): ").strip()
        if not location_preference:
            location_preference = "Remote"
            print(f"📍 Using default: {location_preference}")
        
        try:
            # Navigate to internships page slowly
            print("🔗 Slowly navigating to internships page...")
            self.driver.get("https://internshala.com/internships")
            time.sleep(3)
            
            # Scroll to search area
            print("📜 Scrolling to search area...")
            self.driver.execute_script("window.scrollTo(0, 200);")
            time.sleep(2)
            
            # Find search box
            print("🔍 Finding search box...")
            search_selectors = [
                '#search_internships',
                'input[placeholder*="search"]',
                'input[name*="search"]',
                '.search-input'
            ]
            
            search_box = self.find_element_with_retry(search_selectors)
            
            if search_box:
                print(f"⌨️ Searching for: {job_preferences}")
                self.slow_type(search_box, job_preferences)
                time.sleep(1)
                
                # Press Enter or click search button
                search_box.send_keys(Keys.RETURN)
                time.sleep(3)
            else:
                # Try direct URL search
                search_url = f"https://internshala.com/internships/{job_preferences.lower().replace(' ', '-')}-internship"
                print(f"🔗 Trying direct search URL: {search_url}")
                self.driver.get(search_url)
                time.sleep(3)
            
            # Apply location filter if needed
            if location_preference.lower() != 'all':
                self.apply_location_filter(location_preference)
            
            # Find and process jobs
            return self.find_and_process_jobs(job_preferences, location_preference)
            
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            return []
    
    def apply_location_filter(self, location):
        """Apply location filter"""
        try:
            print(f"📍 Applying location filter: {location}")
            
            # Look for location filter
            location_selectors = [
                '#location_filter',
                'input[placeholder*="location"]',
                '.location-filter'
            ]
            
            location_field = self.find_element_with_retry(location_selectors)
            
            if location_field:
                self.slow_type(location_field, location)
                time.sleep(1)
                location_field.send_keys(Keys.RETURN)
                time.sleep(2)
                print("✅ Location filter applied")
            else:
                print("⚠️ Location filter not found")
                
        except Exception as e:
            print(f"⚠️ Location filter error: {str(e)}")
    
    def find_and_process_jobs(self, job_type, location):
        """Find and process job listings"""
        print("🔍 Finding job listings...")
        
        try:
            # Wait for jobs to load
            time.sleep(3)
            
            # Find job cards
            job_selectors = [
                '.individual_internship',
                '.internship_meta',
                '.job-card',
                '.container-fluid .row > div'
            ]
            
            jobs_found = []
            for selector in job_selectors:
                try:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(job_elements) > 0:
                        print(f"✅ Found {len(job_elements)} job listings")
                        jobs_found = job_elements[:10]  # Limit to first 10
                        break
                except:
                    continue
            
            if not jobs_found:
                print("❌ No job listings found")
                return []
            
            # Extract job information
            jobs = []
            print(f"\n📋 FOUND {len(jobs_found)} {job_type.upper()} OPPORTUNITIES:")
            print("="*60)
            
            for i, job_element in enumerate(jobs_found, 1):
                try:
                    job_info = self.extract_job_info(job_element, i)
                    if job_info:
                        jobs.append(job_info)
                        print(f"{i}. {job_info['title']}")
                        print(f"   🏢 Company: {job_info['company']}")
                        print(f"   📍 Location: {job_info['location']}")
                        print(f"   🔗 URL: {job_info['url'][:50]}..." if job_info['url'] else "   🔗 URL: Not available")
                        print("-" * 60)
                except Exception as e:
                    print(f"⚠️ Error extracting job {i}: {str(e)}")
            
            self.session_stats['jobs_found'] = len(jobs)
            return jobs
            
        except Exception as e:
            print(f"❌ Job processing error: {str(e)}")
            return []
    
    def extract_job_info(self, job_element, index):
        """Extract job information from element"""
        try:
            # Find title and URL
            title_selectors = [
                '.job-title a',
                '.profile h3 a',
                'h3 a',
                'h4 a',
                '.heading-4-5 a'
            ]
            
            title = f"Internship {index}"
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
            
            # Find location
            location_selectors = [
                '.locations span',
                '.location_link',
                '.individual_internship_details .location'
            ]
            
            location = "Not specified"
            for selector in location_selectors:
                try:
                    location_elem = job_element.find_element(By.CSS_SELECTOR, selector)
                    location = location_elem.text.strip()
                    if location:
                        break
                except:
                    continue
            
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
    
    def apply_to_selected_jobs(self, jobs):
        """Apply to user-selected jobs"""
        if not jobs:
            print("❌ No jobs available for application")
            return 0
        
        print(f"\n📝 JOB APPLICATION PROCESS")
        print("="*40)
        
        # Let user select jobs
        print("🤔 Which jobs would you like to apply to?")
        print("Options:")
        print("  - 'all' for all jobs")
        print("  - '1,3,5' for specific jobs")
        print("  - 'first 3' for first 3 jobs")
        
        selection = input("Your choice: ").strip().lower()
        
        if selection == 'all':
            selected_jobs = jobs
        elif 'first' in selection:
            try:
                num = int(selection.split()[-1])
                selected_jobs = jobs[:num]
            except:
                selected_jobs = jobs[:3]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_jobs = [jobs[i] for i in indices if 0 <= i < len(jobs)]
            except:
                print("⚠️ Invalid selection, using first 3 jobs")
                selected_jobs = jobs[:3]
        
        print(f"📝 Applying to {len(selected_jobs)} jobs...")
        
        applications_made = 0
        for i, job in enumerate(selected_jobs, 1):
            print(f"\n🎯 Applying to job {i}/{len(selected_jobs)}: {job['title']}")
            
            if self.apply_to_job(job):
                applications_made += 1
                self.session_stats['applications_successful'] += 1
                print(f"   ✅ Application successful!")
            else:
                self.session_stats['applications_failed'] += 1
                print(f"   ❌ Application failed")
            
            self.session_stats['jobs_applied'] += 1
            
            # Delay between applications
            if i < len(selected_jobs):
                print("   ⏳ Waiting 30 seconds before next application...")
                time.sleep(30)
        
        return applications_made
    
    def apply_to_job(self, job):
        """Apply to a specific job with enhanced error handling"""
        try:
            if not job['url']:
                print("   ⚠️ No job URL available")
                return False
            
            # Navigate to job page slowly
            print("   🌐 Opening job page...")
            self.driver.get(job['url'])
            time.sleep(3)
            
            # Scroll to see apply button
            self.driver.execute_script("window.scrollTo(0, 400);")
            time.sleep(1)
            
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
        """Handle application form with enhanced error handling"""
        try:
            print("   📝 Handling application form...")
            time.sleep(2)
            
            # Handle any popups first
            self.handle_popups()
            
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
                        cover_letter_text = f"""Dear {job['company']} Team,

I am excited to apply for the {job['title']} position. As a motivated and dedicated individual, I am eager to contribute to your team and gain valuable experience in this field.

My skills and enthusiasm make me a great fit for this role, and I am committed to delivering high-quality work while learning from your experienced team.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {job['company']}.

Best regards"""
                        
                        self.slow_type(cover_letter_field, cover_letter_text)
                        time.sleep(1)
                        break
                except:
                    continue
            
            # Scroll to submit button
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Look for submit button
            submit_selectors = [
                'button[type="submit"]',
                '.submit-btn',
                'input[type="submit"]',
                'button[contains(text(), "Submit")]',
                '.btn-primary'
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        print("   🚀 Submitting application...")
                        self.driver.execute_script("arguments[0].click();", submit_button)
                        time.sleep(3)
                        
                        # Handle any confirmation popups
                        self.handle_popups()
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
        print("📊 ENHANCED INTERNSHALA SESSION SUMMARY")
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
    print("🚀 ENHANCED INTERNSHALA JOB APPLIER")
    print("="*50)
    print("✨ Features:")
    print("  - Enhanced login with error handling")
    print("  - Popup management and page scrolling")
    print("  - User-recommended job search")
    print("  - Robust application process")
    print("="*50)
    
    applier = EnhancedInternshalaApplier()
    
    try:
        # Step 1: Create browser
        if not applier.create_browser():
            print("❌ Cannot proceed without browser")
            return
        
        # Step 2: Enhanced login
        if not applier.enhanced_login():
            print("❌ Cannot proceed without login")
            return
        
        # Step 3: Search for user-recommended jobs
        jobs = applier.search_user_recommended_jobs()
        
        if not jobs:
            print("❌ No jobs found")
            return
        
        # Step 4: Apply to selected jobs
        applications_made = applier.apply_to_selected_jobs(jobs)
        
        print(f"\n🎉 Session completed! Applied to {applications_made} jobs!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    
    finally:
        applier.print_session_summary()
        applier.close()
        print("\n✅ Enhanced session completed!")

if __name__ == "__main__":
    main()
