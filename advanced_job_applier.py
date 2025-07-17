#!/usr/bin/env python3
"""
Advanced Job Application Automation System
Handles error messages, anti-detection, and intelligent navigation
"""

import time
import random
import json
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from config import config

class AdvancedJobApplier:
    """Advanced job application automation with comprehensive error handling"""
    
    def __init__(self, platform="linkedin"):
        self.platform = platform.lower()
        self.driver = None
        self.wait = None
        self.actions = None
        self.logger = self.setup_logging()
        self.session_stats = {
            'jobs_found': 0,
            'jobs_applied': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'errors_handled': 0,
            'captchas_detected': 0,
            'start_time': datetime.now()
        }
        
        # Anti-detection settings
        self.human_delays = {
            'typing_speed': (0.05, 0.15),  # seconds between keystrokes
            'action_delay': (2, 5),        # seconds between major actions
            'scroll_delay': (0.5, 1.5),    # seconds between scroll steps
            'click_delay': (1, 3)          # seconds between clicks
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'{self.platform}_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {self.platform} job application automation")
        return logger
    
    def create_stealth_browser(self):
        """Create browser with advanced anti-detection measures"""
        print("🛡️ Creating stealth browser with anti-detection measures...")
        self.logger.info("Creating stealth browser")
        
        options = Options()
        
        # Basic stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Faster loading
        options.add_argument("--disable-javascript-harmony-shipping")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        
        # Realistic user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Window size randomization
        window_sizes = ["1366,768", "1920,1080", "1440,900", "1536,864"]
        options.add_argument(f"--window-size={random.choice(window_sizes)}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            self.actions = ActionChains(self.driver)
            
            # Execute anti-detection scripts
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}};
            """)
            
            print("✅ Stealth browser created successfully!")
            self.logger.info("Stealth browser created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Browser creation failed: {str(e)}")
            self.logger.error(f"Browser creation failed: {str(e)}")
            return False
    
    def human_delay(self, delay_type='action_delay'):
        """Add human-like delays"""
        min_delay, max_delay = self.human_delays[delay_type]
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        return delay
    
    def human_type(self, element, text, clear_first=True):
        """Type text with human-like speed and patterns"""
        if clear_first:
            element.clear()
            self.human_delay('click_delay')
        
        # Add some typing variations
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Occasional longer pauses (thinking)
            if random.random() < 0.1:  # 10% chance
                time.sleep(random.uniform(0.3, 0.8))
            else:
                self.human_delay('typing_speed')
            
            # Occasional backspace and retype (human error simulation)
            if random.random() < 0.02 and i > 0:  # 2% chance
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(char)
        
        self.logger.info(f"Typed text with human-like patterns: {text[:20]}...")
    
    def human_scroll(self, direction='down', steps=3):
        """Scroll page with human-like patterns"""
        scroll_amount = random.randint(200, 400)
        
        for _ in range(steps):
            if direction == 'down':
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            else:
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            
            self.human_delay('scroll_delay')
            scroll_amount = random.randint(150, 350)  # Vary scroll amount
    
    def detect_and_handle_popups(self, max_attempts=5):
        """Comprehensive popup and error message detection and handling"""
        print("🔍 Scanning for popups and error messages...")
        self.logger.info("Scanning for popups and error messages")
        
        popup_handled = False
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            # Common popup close button selectors
            close_selectors = [
                # Generic close buttons
                'button[aria-label*="close" i]',
                'button[aria-label*="dismiss" i]',
                'button[title*="close" i]',
                '[data-dismiss="modal"]',
                '[data-dismiss="alert"]',
                '.close',
                '.modal-close',
                '.popup-close',
                '.dialog-close',
                
                # X buttons
                'button:contains("×")',
                'span:contains("×")',
                '.fa-times',
                '.fa-close',
                '[aria-label="Close"]',
                
                # OK/Dismiss buttons
                'button:contains("OK")',
                'button:contains("Ok")',
                'button:contains("Dismiss")',
                'button:contains("Close")',
                'button:contains("Got it")',
                'button:contains("Continue")',
                
                # Platform-specific selectors
                '.artdeco-modal__dismiss',  # LinkedIn
                '.swal-button',             # SweetAlert
                '.alert .btn-close',        # Bootstrap alerts
                '.toast-close-button',      # Toast notifications
                
                # CAPTCHA close buttons
                'button[aria-label*="captcha" i]',
                '.captcha-close',
                
                # Error dialog buttons
                '.error-dialog button',
                '.alert-dialog button',
                '.notification-close'
            ]
            
            popup_found = False
            
            for selector in close_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Check if it's actually a close/dismiss button
                            element_text = element.text.lower()
                            element_aria = (element.get_attribute('aria-label') or '').lower()
                            element_title = (element.get_attribute('title') or '').lower()
                            
                            close_keywords = ['close', 'dismiss', 'ok', 'got it', 'continue', '×', 'x']
                            
                            if any(keyword in element_text or keyword in element_aria or keyword in element_title 
                                   for keyword in close_keywords):
                                
                                print(f"   🖱️ Closing popup: {element_text or element_aria or element_title or 'Unknown'}")
                                self.logger.info(f"Closing popup with selector: {selector}")
                                
                                # Try multiple click methods
                                try:
                                    element.click()
                                except:
                                    try:
                                        self.driver.execute_script("arguments[0].click();", element)
                                    except:
                                        self.actions.move_to_element(element).click().perform()
                                
                                popup_handled = True
                                popup_found = True
                                self.session_stats['errors_handled'] += 1
                                
                                # Wait for popup to close
                                time.sleep(2)
                                break
                    
                    if popup_found:
                        break
                        
                except Exception as e:
                    continue
            
            # Check for CAPTCHA
            captcha_detected = self.detect_captcha()
            if captcha_detected:
                popup_found = True
                break
            
            if not popup_found:
                break
            
            # Brief pause before next scan
            time.sleep(1)
        
        if popup_handled:
            print("✅ Popup handling completed")
            self.logger.info("Popup handling completed")
        else:
            print("ℹ️ No popups detected")
        
        return popup_handled
    
    def detect_captcha(self):
        """Detect CAPTCHA and handle appropriately"""
        captcha_selectors = [
            'iframe[src*="captcha"]',
            'iframe[src*="recaptcha"]',
            '.captcha',
            '.recaptcha',
            '#captcha',
            '[data-captcha]',
            'img[src*="captcha"]'
        ]
        
        for selector in captcha_selectors:
            try:
                captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if any(elem.is_displayed() for elem in captcha_elements):
                    print("🤖 CAPTCHA detected!")
                    self.logger.warning("CAPTCHA detected - pausing for manual completion")
                    self.session_stats['captchas_detected'] += 1
                    
                    print("⏸️ CAPTCHA DETECTED - Manual intervention required")
                    print("📋 Please complete the CAPTCHA in the browser window")
                    print("⌨️ Press ENTER after completing the CAPTCHA...")
                    
                    input()  # Wait for user to complete CAPTCHA
                    
                    print("✅ Continuing after CAPTCHA completion")
                    self.logger.info("Continuing after CAPTCHA completion")
                    return True
            except:
                continue
        
        return False
    
    def safe_navigate(self, url, max_retries=3):
        """Navigate to URL with error handling and retries"""
        for attempt in range(max_retries):
            try:
                print(f"🔗 Navigating to: {url} (attempt {attempt + 1})")
                self.logger.info(f"Navigating to: {url} (attempt {attempt + 1})")
                
                self.driver.get(url)
                self.human_delay('action_delay')
                
                # Handle any popups that appear after navigation
                self.detect_and_handle_popups()
                
                print(f"✅ Successfully navigated to: {self.driver.title}")
                self.logger.info(f"Successfully navigated to: {self.driver.title}")
                return True
                
            except WebDriverException as e:
                print(f"⚠️ Navigation attempt {attempt + 1} failed: {str(e)}")
                self.logger.warning(f"Navigation attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print("❌ All navigation attempts failed")
                    self.logger.error("All navigation attempts failed")
                    return False
        
        return False
    
    def safe_click(self, element, description="element", max_retries=3):
        """Click element with error handling and retries"""
        for attempt in range(max_retries):
            try:
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                self.human_delay('scroll_delay')
                
                # Wait for element to be clickable
                self.wait.until(EC.element_to_be_clickable(element))
                
                # Add human-like mouse movement
                self.actions.move_to_element(element).perform()
                self.human_delay('click_delay')
                
                # Try multiple click methods
                try:
                    element.click()
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                    except:
                        self.actions.move_to_element(element).click().perform()
                
                print(f"✅ Successfully clicked: {description}")
                self.logger.info(f"Successfully clicked: {description}")
                
                # Handle any popups that appear after clicking
                self.human_delay('action_delay')
                self.detect_and_handle_popups()
                
                return True
                
            except Exception as e:
                print(f"⚠️ Click attempt {attempt + 1} failed for {description}: {str(e)}")
                self.logger.warning(f"Click attempt {attempt + 1} failed for {description}: {str(e)}")
                
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    print(f"❌ All click attempts failed for {description}")
                    self.logger.error(f"All click attempts failed for {description}")
                    return False
        
        return False
    
    def find_element_safe(self, selectors, description="element", timeout=10):
        """Find element with multiple selectors and error handling"""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                if element.is_displayed():
                    print(f"✅ Found {description} with selector: {selector}")
                    self.logger.info(f"Found {description} with selector: {selector}")
                    return element
                    
            except TimeoutException:
                continue
            except Exception as e:
                self.logger.warning(f"Error finding {description} with selector {selector}: {str(e)}")
                continue
        
        print(f"❌ Could not find {description}")
        self.logger.error(f"Could not find {description}")
        return None
    
    def enhanced_login(self, platform_config):
        """Enhanced login with comprehensive error handling"""
        print(f"\n🔐 ENHANCED {platform_config['name'].upper()} LOGIN")
        print("="*50)
        
        # Navigate to login page
        if not self.safe_navigate(platform_config['login_url']):
            return False
        
        max_login_attempts = 3
        
        for attempt in range(max_login_attempts):
            print(f"\n🎯 Login attempt {attempt + 1}/{max_login_attempts}")
            
            try:
                # Handle initial popups
                self.detect_and_handle_popups()
                
                # Scroll to top
                self.driver.execute_script("window.scrollTo(0, 0);")
                self.human_delay('scroll_delay')
                
                # Find and fill email field
                email_field = self.find_element_safe(
                    platform_config['email_selectors'], 
                    "email field"
                )
                
                if not email_field:
                    continue
                
                print("📧 Filling email field...")
                self.human_type(email_field, platform_config['email'])
                
                # Find and fill password field
                password_field = self.find_element_safe(
                    platform_config['password_selectors'],
                    "password field"
                )
                
                if not password_field:
                    continue
                
                print("🔒 Filling password field...")
                self.human_type(password_field, platform_config['password'])
                
                # Find and click login button
                login_button = self.find_element_safe(
                    platform_config['login_button_selectors'],
                    "login button"
                )
                
                if not login_button:
                    continue
                
                print("🖱️ Clicking login button...")
                if not self.safe_click(login_button, "login button"):
                    continue
                
                # Wait for login response
                print("⏳ Waiting for login response...")
                time.sleep(5)
                
                # Handle any error messages or popups
                self.detect_and_handle_popups()
                
                # Check login success
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                print(f"🌐 Current URL: {current_url}")
                print(f"📄 Page title: {page_title}")
                
                # Check success indicators
                success_indicators = platform_config.get('success_indicators', [])
                login_successful = any(indicator in current_url.lower() for indicator in success_indicators)
                
                if login_successful:
                    print("🎉 LOGIN SUCCESSFUL!")
                    self.logger.info("Login successful")
                    return True
                else:
                    print(f"❌ Login attempt {attempt + 1} failed")
                    self.logger.warning(f"Login attempt {attempt + 1} failed")
                    
                    if attempt < max_login_attempts - 1:
                        print("🔄 Retrying login...")
                        time.sleep(3)
            
            except Exception as e:
                print(f"❌ Login attempt {attempt + 1} error: {str(e)}")
                self.logger.error(f"Login attempt {attempt + 1} error: {str(e)}")
                
                if attempt < max_login_attempts - 1:
                    time.sleep(3)
        
        print("❌ All login attempts failed")
        self.logger.error("All login attempts failed")
        return False
    
    def navigate_to_jobs_section(self, platform_config):
        """Navigate to jobs section with error handling"""
        print("\n🎯 NAVIGATING TO JOBS SECTION")
        print("="*40)
        
        try:
            # Handle any popups first
            self.detect_and_handle_popups()
            
            # Look for jobs navigation link
            jobs_nav = self.find_element_safe(
                platform_config['jobs_nav_selectors'],
                "jobs navigation"
            )
            
            if jobs_nav:
                print("🖱️ Clicking Jobs navigation...")
                if self.safe_click(jobs_nav, "jobs navigation"):
                    self.human_delay('action_delay')
                    print("✅ Successfully navigated to jobs section")
                    self.logger.info("Successfully navigated to jobs section")
                    return True
            
            # Alternative: direct navigation to jobs URL
            if 'jobs_url' in platform_config:
                print("🔗 Using direct jobs URL navigation...")
                return self.safe_navigate(platform_config['jobs_url'])
            
            return False
            
        except Exception as e:
            print(f"❌ Jobs navigation error: {str(e)}")
            self.logger.error(f"Jobs navigation error: {str(e)}")
            return False
    
    def apply_job_filters(self, search_preferences, platform_config):
        """Apply job search filters based on user preferences"""
        print("\n🔍 APPLYING JOB SEARCH FILTERS")
        print("="*40)
        
        try:
            # Handle popups
            self.detect_and_handle_popups()
            
            # Job title/keywords search
            if search_preferences.get('job_title'):
                print(f"🔍 Searching for: {search_preferences['job_title']}")
                
                search_box = self.find_element_safe(
                    platform_config['search_selectors'],
                    "job search box"
                )
                
                if search_box:
                    self.human_type(search_box, search_preferences['job_title'])
                    self.human_delay('action_delay')
            
            # Location filter
            if search_preferences.get('location'):
                print(f"📍 Setting location: {search_preferences['location']}")
                
                location_box = self.find_element_safe(
                    platform_config['location_selectors'],
                    "location search box"
                )
                
                if location_box:
                    self.human_type(location_box, search_preferences['location'])
                    self.human_delay('action_delay')
            
            # Apply search
            search_button = self.find_element_safe(
                platform_config['search_button_selectors'],
                "search button"
            )
            
            if search_button:
                print("🖱️ Applying search filters...")
                if self.safe_click(search_button, "search button"):
                    self.human_delay('action_delay')
                    print("✅ Search filters applied successfully")
                    return True
            
            # Alternative: press Enter in search box
            if search_preferences.get('job_title') and search_box:
                print("⌨️ Pressing Enter to search...")
                search_box.send_keys(Keys.RETURN)
                self.human_delay('action_delay')
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Filter application error: {str(e)}")
            self.logger.error(f"Filter application error: {str(e)}")
            return False
    
    def get_platform_config(self):
        """Get platform-specific configuration"""
        configs = {
            'linkedin': {
                'name': 'LinkedIn',
                'login_url': 'https://www.linkedin.com/login',
                'jobs_url': 'https://www.linkedin.com/jobs/',
                'email': config.LINKEDIN_EMAIL,
                'password': config.LINKEDIN_PASSWORD,
                'email_selectors': ['#username', 'input[name="session_key"]', 'input[type="email"]'],
                'password_selectors': ['#password', 'input[name="session_password"]', 'input[type="password"]'],
                'login_button_selectors': ['button[type="submit"]', '.btn__primary--large', 'button[aria-label*="Sign in"]'],
                'success_indicators': ['feed', 'mynetwork', 'jobs', 'messaging'],
                'jobs_nav_selectors': ['a[href*="/jobs"]', 'nav a:contains("Jobs")', '.global-nav__primary-link[href*="jobs"]'],
                'search_selectors': ['input[aria-label*="Search by title"]', '.jobs-search-box__text-input', '#jobs-search-box-keyword'],
                'location_selectors': ['input[aria-label*="City"]', '.jobs-search-box__text-input[placeholder*="City"]', '#jobs-search-box-location'],
                'search_button_selectors': ['button[aria-label*="Search"]', '.jobs-search-box__submit-button', 'button[type="submit"]']
            },
            'internshala': {
                'name': 'Internshala',
                'login_url': 'https://internshala.com/login',
                'jobs_url': 'https://internshala.com/internships',
                'email': config.INTERNSHALA_EMAIL,
                'password': config.INTERNSHALA_PASSWORD,
                'email_selectors': ['#email', 'input[name="email"]', 'input[type="email"]'],
                'password_selectors': ['#password', 'input[name="password"]', 'input[type="password"]'],
                'login_button_selectors': ['button[type="submit"]', '.login-btn', '#login_submit'],
                'success_indicators': ['dashboard', 'student', 'internships'],
                'jobs_nav_selectors': ['a[href*="internships"]', 'nav a:contains("Internships")'],
                'search_selectors': ['#search_internships', 'input[placeholder*="search"]', '.search-input'],
                'location_selectors': ['#location_filter', 'input[placeholder*="location"]', '.location-filter'],
                'search_button_selectors': ['button[type="submit"]', '.search-btn', 'input[type="submit"]']
            }
        }
        
        return configs.get(self.platform, configs['linkedin'])

    def find_jobs(self, platform_config, max_jobs=10):
        """Find job listings with error handling"""
        print(f"\n🔍 FINDING JOB LISTINGS (Max: {max_jobs})")
        print("="*50)

        try:
            # Handle popups
            self.detect_and_handle_popups()

            # Wait for jobs to load
            time.sleep(3)

            # Platform-specific job card selectors
            job_selectors = {
                'linkedin': [
                    '.job-card-container',
                    '.jobs-search-results__list-item',
                    '.job-card-list__entity',
                    'a[href*="/jobs/view/"]'
                ],
                'internshala': [
                    '.individual_internship',
                    '.internship_meta',
                    '.job-card',
                    'a[href*="/internship/detail/"]'
                ]
            }

            selectors = job_selectors.get(self.platform, job_selectors['linkedin'])

            jobs_found = []
            for selector in selectors:
                try:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(job_elements) > 0:
                        print(f"✅ Found {len(job_elements)} job listings")
                        jobs_found = job_elements[:max_jobs]
                        break
                except:
                    continue

            if not jobs_found:
                print("❌ No job listings found")
                return []

            # Extract job information
            jobs = []
            for i, job_element in enumerate(jobs_found, 1):
                try:
                    job_info = self.extract_job_info(job_element, i, platform_config)
                    if job_info:
                        jobs.append(job_info)
                        print(f"   {i}. {job_info['title']} at {job_info['company']}")
                except Exception as e:
                    self.logger.warning(f"Error extracting job {i}: {str(e)}")

            self.session_stats['jobs_found'] = len(jobs)
            print(f"\n✅ Successfully extracted {len(jobs)} job details")
            return jobs

        except Exception as e:
            print(f"❌ Job finding error: {str(e)}")
            self.logger.error(f"Job finding error: {str(e)}")
            return []

    def extract_job_info(self, job_element, index, platform_config):
        """Extract job information from element"""
        try:
            # Platform-specific extraction logic
            if self.platform == 'linkedin':
                return self.extract_linkedin_job_info(job_element, index)
            elif self.platform == 'internshala':
                return self.extract_internshala_job_info(job_element, index)
            else:
                return self.extract_generic_job_info(job_element, index)

        except Exception as e:
            self.logger.warning(f"Error extracting job info: {str(e)}")
            return None

    def extract_linkedin_job_info(self, job_element, index):
        """Extract LinkedIn job information"""
        try:
            # Find title and URL
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
            location = "Remote"
            try:
                location_elem = job_element.find_element(By.CSS_SELECTOR, '.job-card-container__metadata-item')
                location_text = location_elem.text.strip()
                if location_text and 'ago' not in location_text.lower():
                    location = location_text
            except:
                pass

            return {
                'index': index,
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'platform': 'linkedin',
                'element': job_element
            }

        except Exception as e:
            return None

    def extract_internshala_job_info(self, job_element, index):
        """Extract Internshala job information"""
        try:
            # Find title and URL
            title_selectors = [
                '.job-title a',
                '.profile h3 a',
                'h3 a',
                'h4 a'
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
                'platform': 'internshala',
                'element': job_element
            }

        except Exception as e:
            return None

    def extract_generic_job_info(self, job_element, index):
        """Extract generic job information"""
        try:
            title = job_element.text.strip()[:50] or f"Job {index}"
            job_url = job_element.get_attribute('href') if job_element.tag_name == 'a' else ""

            return {
                'index': index,
                'title': title,
                'company': "Company",
                'location': "Location",
                'url': job_url,
                'platform': self.platform,
                'element': job_element
            }

        except Exception as e:
            return None

    def apply_to_jobs(self, jobs, platform_config):
        """Apply to jobs with comprehensive error handling"""
        print(f"\n📝 APPLYING TO {len(jobs)} JOBS")
        print("="*50)

        applications_made = 0

        for i, job in enumerate(jobs, 1):
            print(f"\n🎯 Applying to job {i}/{len(jobs)}: {job['title']}")
            self.logger.info(f"Applying to job {i}: {job['title']} at {job['company']}")

            try:
                if self.apply_to_single_job(job, platform_config):
                    applications_made += 1
                    self.session_stats['applications_successful'] += 1
                    print(f"   ✅ Application successful!")
                else:
                    self.session_stats['applications_failed'] += 1
                    print(f"   ❌ Application failed")

                self.session_stats['jobs_applied'] += 1

                # Human-like delay between applications
                if i < len(jobs):
                    delay = random.randint(30, 60)
                    print(f"   ⏳ Waiting {delay} seconds before next application...")
                    time.sleep(delay)

            except Exception as e:
                print(f"   ❌ Application error: {str(e)}")
                self.logger.error(f"Application error for job {i}: {str(e)}")
                self.session_stats['applications_failed'] += 1

        return applications_made

    def apply_to_single_job(self, job, platform_config):
        """Apply to a single job with error handling"""
        try:
            if not job['url']:
                print("   ⚠️ No job URL available")
                return False

            # Navigate to job page
            print("   🌐 Opening job page...")
            if not self.safe_navigate(job['url']):
                return False

            # Platform-specific application logic
            if self.platform == 'linkedin':
                return self.apply_linkedin_job(job)
            elif self.platform == 'internshala':
                return self.apply_internshala_job(job)
            else:
                return self.apply_generic_job(job)

        except Exception as e:
            print(f"   ❌ Single job application error: {str(e)}")
            self.logger.error(f"Single job application error: {str(e)}")
            return False

    def apply_linkedin_job(self, job):
        """Apply to LinkedIn job"""
        try:
            # Look for Easy Apply button
            easy_apply_selectors = [
                'button[aria-label*="Easy Apply"]',
                '.jobs-apply-button',
                'button[data-control-name="jobdetails_topcard_inapply"]'
            ]

            easy_apply_button = self.find_element_safe(easy_apply_selectors, "Easy Apply button")

            if easy_apply_button and 'easy apply' in easy_apply_button.text.lower():
                print("   🖱️ Clicking Easy Apply...")
                if self.safe_click(easy_apply_button, "Easy Apply button"):
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
            print("   📝 Handling LinkedIn Easy Apply process...")

            max_steps = 5
            current_step = 1

            while current_step <= max_steps:
                print(f"   📋 Easy Apply step {current_step}...")

                # Handle popups
                self.detect_and_handle_popups()

                # Fill text areas
                text_areas = self.driver.find_elements(By.CSS_SELECTOR, 'textarea')
                for textarea in text_areas:
                    if textarea.is_displayed() and not textarea.get_attribute('value'):
                        print("   ✍️ Filling cover letter...")
                        cover_letter = f"Dear {job['company']} Team,\n\nI am excited to apply for the {job['title']} position. I believe my skills and enthusiasm make me a great fit for this role.\n\nThank you for considering my application.\n\nBest regards"
                        self.human_type(textarea, cover_letter)

                # Look for Next button
                next_selectors = [
                    'button[aria-label="Continue to next step"]',
                    'button[data-control-name="continue_unify"]',
                    'button:contains("Next")'
                ]

                next_button = self.find_element_safe(next_selectors, "Next button", timeout=5)
                if next_button and ('next' in next_button.text.lower() or 'continue' in next_button.text.lower()):
                    print(f"   🖱️ Clicking: {next_button.text}")
                    if self.safe_click(next_button, "Next button"):
                        current_step += 1
                        continue

                # Look for Submit button
                submit_selectors = [
                    'button[aria-label*="Submit application"]',
                    'button[data-control-name="submit_unify"]',
                    'button:contains("Submit")'
                ]

                submit_button = self.find_element_safe(submit_selectors, "Submit button", timeout=5)
                if submit_button and 'submit' in submit_button.text.lower():
                    print("   🚀 Submitting LinkedIn application...")
                    if self.safe_click(submit_button, "Submit button"):
                        time.sleep(3)
                        return True

                break

            print("   ✅ LinkedIn Easy Apply process completed")
            return True

        except Exception as e:
            print(f"   ❌ LinkedIn Easy Apply error: {str(e)}")
            return False

    def apply_internshala_job(self, job):
        """Apply to Internshala job"""
        try:
            # Look for apply button
            apply_selectors = [
                '.apply_now_button',
                '.btn-primary',
                'button[contains(text(), "Apply")]',
                'a[contains(text(), "Apply")]'
            ]

            apply_button = self.find_element_safe(apply_selectors, "Apply button")

            if apply_button and 'apply' in apply_button.text.lower():
                print("   🖱️ Clicking Apply button...")
                if self.safe_click(apply_button, "Apply button"):
                    return self.handle_internshala_application(job)
            else:
                print("   ⚠️ No Apply button found")
                return False

        except Exception as e:
            print(f"   ❌ Internshala application error: {str(e)}")
            return False

    def handle_internshala_application(self, job):
        """Handle Internshala application form"""
        try:
            print("   📝 Handling Internshala application form...")

            # Handle popups
            self.detect_and_handle_popups()

            # Fill cover letter
            cover_letter_selectors = [
                'textarea[name*="cover"]',
                'textarea[placeholder*="cover"]',
                'textarea'
            ]

            cover_letter_field = self.find_element_safe(cover_letter_selectors, "cover letter field", timeout=5)
            if cover_letter_field:
                print("   ✍️ Writing cover letter...")
                cover_letter_text = f"Dear {job['company']} Team,\n\nI am excited to apply for the {job['title']} position. As a motivated individual, I am eager to contribute to your team and gain valuable experience.\n\nThank you for considering my application.\n\nBest regards"
                self.human_type(cover_letter_field, cover_letter_text)

            # Submit application
            submit_selectors = [
                'button[type="submit"]',
                '.submit-btn',
                'input[type="submit"]',
                'button[contains(text(), "Submit")]'
            ]

            submit_button = self.find_element_safe(submit_selectors, "Submit button")
            if submit_button:
                print("   🚀 Submitting Internshala application...")
                if self.safe_click(submit_button, "Submit button"):
                    time.sleep(3)
                    return True

            print("   ✅ Internshala application process completed")
            return True

        except Exception as e:
            print(f"   ❌ Internshala application error: {str(e)}")
            return False

    def apply_generic_job(self, job):
        """Apply to generic job posting"""
        try:
            print("   📝 Attempting generic job application...")

            # Look for common apply button patterns
            apply_selectors = [
                'button[contains(text(), "Apply")]',
                'a[contains(text(), "Apply")]',
                '.apply-btn',
                '.apply-button',
                'input[value*="Apply"]'
            ]

            apply_button = self.find_element_safe(apply_selectors, "Apply button")
            if apply_button:
                print("   🖱️ Clicking Apply button...")
                return self.safe_click(apply_button, "Apply button")
            else:
                print("   ⚠️ No Apply button found")
                return False

        except Exception as e:
            print(f"   ❌ Generic application error: {str(e)}")
            return False

    def print_session_summary(self):
        """Print comprehensive session summary"""
        duration = datetime.now() - self.session_stats['start_time']
        
        print("\n" + "="*70)
        print(f"📊 {self.platform.upper()} AUTOMATION SESSION SUMMARY")
        print("="*70)
        print(f"⏱️  Duration: {duration}")
        print(f"🔍 Jobs Found: {self.session_stats['jobs_found']}")
        print(f"📝 Jobs Applied To: {self.session_stats['jobs_applied']}")
        print(f"✅ Successful Applications: {self.session_stats['applications_successful']}")
        print(f"❌ Failed Applications: {self.session_stats['applications_failed']}")
        print(f"🛡️ Errors Handled: {self.session_stats['errors_handled']}")
        print(f"🤖 CAPTCHAs Detected: {self.session_stats['captchas_detected']}")
        
        if self.session_stats['jobs_applied'] > 0:
            success_rate = (self.session_stats['applications_successful'] / self.session_stats['jobs_applied']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("="*70)
        self.logger.info(f"Session completed - {self.session_stats}")
    
    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")

def main():
    """Main function"""
    print("🚀 ADVANCED JOB APPLICATION AUTOMATION SYSTEM")
    print("="*60)
    print("✨ Features:")
    print("  - 🛡️ Advanced anti-detection measures")
    print("  - 🔧 Comprehensive error handling")
    print("  - 🤖 CAPTCHA detection and handling")
    print("  - 👤 Human-like behavior patterns")
    print("  - 📊 Intelligent retry logic")
    print("  - 📝 Detailed logging and monitoring")
    print("="*60)
    
    # Get platform choice
    platform = input("\nChoose platform (linkedin/internshala): ").strip().lower()
    if platform not in ['linkedin', 'internshala']:
        platform = 'linkedin'
        print(f"Using default platform: {platform}")
    
    applier = AdvancedJobApplier(platform)
    
    try:
        # Step 1: Create stealth browser
        if not applier.create_stealth_browser():
            print("❌ Cannot proceed without browser")
            return
        
        # Step 2: Get platform configuration
        platform_config = applier.get_platform_config()
        
        # Step 3: Enhanced login
        if not applier.enhanced_login(platform_config):
            print("❌ Cannot proceed without login")
            return
        
        # Step 4: Navigate to jobs section
        if not applier.navigate_to_jobs_section(platform_config):
            print("❌ Could not navigate to jobs section")
            return
        
        # Step 5: Get search preferences
        search_preferences = {
            'job_title': input("\nEnter job title/keywords: ").strip() or "Software Engineer",
            'location': input("Enter location (or 'Remote'): ").strip() or "Remote"
        }
        
        # Step 6: Apply search filters
        if applier.apply_job_filters(search_preferences, platform_config):
            print("✅ Search filters applied successfully!")

            # Step 7: Find and apply to jobs
            max_applications = int(input("\nHow many jobs to apply to? (default: 5): ").strip() or "5")

            jobs = applier.find_jobs(platform_config, max_applications)
            if jobs:
                applications_made = applier.apply_to_jobs(jobs, platform_config)
                print(f"\n🎉 Applied to {applications_made} jobs successfully!")
            else:
                print("❌ No jobs found to apply to")

            # Keep browser open for manual inspection
            input("\nPress ENTER to close the browser...")
        
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        applier.logger.error(f"Unexpected error: {str(e)}")
    
    finally:
        applier.print_session_summary()
        applier.close()
        print("\n✅ Advanced automation session completed!")

if __name__ == "__main__":
    main()
