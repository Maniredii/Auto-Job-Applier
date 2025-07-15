"""
LinkedIn Job Scraper with Advanced Anti-Detection
"""

import time
import random
import logging
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper, JobListing
from ..automation.browser_manager import BrowserManager
from config import config

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper with stealth capabilities"""
    
    def __init__(self):
        """Initialize LinkedIn scraper"""
        self.browser_manager = BrowserManager()
        self.driver = None
        self.is_logged_in = False
        
        # LinkedIn URLs
        self.base_url = "https://www.linkedin.com"
        self.login_url = f"{self.base_url}/login"
        self.jobs_url = f"{self.base_url}/jobs/search"
        
        # Selectors (updated for current LinkedIn)
        self.selectors = {
            'login': {
                'email': '#username',
                'password': '#password',
                'submit': 'button[type="submit"]',
                'captcha': '.captcha-container',
                'error': '.alert--error'
            },
            'jobs': {
                'search_box': '.jobs-search-box__text-input',
                'location_box': '.jobs-search-box__text-input[aria-label*="location"]',
                'search_button': '.jobs-search-box__submit-button',
                'job_cards': '.job-search-card',
                'job_title': '.job-search-card__title',
                'company_name': '.job-search-card__subtitle-link',
                'location': '.job-search-card__location',
                'posted_date': '.job-search-card__listdate',
                'job_link': '.job-search-card__title-link',
                'description': '.job-search__job-description',
                'load_more': '.infinite-scroller__show-more-button',
                'easy_apply': '.jobs-apply-button--top-card'
            },
            'filters': {
                'experience_level': 'button[aria-label*="Experience level"]',
                'job_type': 'button[aria-label*="Job type"]',
                'remote': 'button[aria-label*="Remote"]',
                'date_posted': 'button[aria-label*="Date posted"]'
            }
        }
    
    def initialize_driver(self, headless: bool = None, profile_name: str = "linkedin") -> None:
        """
        Initialize browser driver
        
        Args:
            headless: Run in headless mode
            profile_name: Browser profile name
        """
        self.driver = self.browser_manager.get_driver(headless, profile_name)
        super().__init__(self.driver)
        logger.info("LinkedIn scraper initialized")
    
    def login(self, email: str = None, password: str = None, phone: str = None) -> bool:
        """
        Login to LinkedIn with stealth measures
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            phone: LinkedIn phone number
            
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self.initialize_driver()
        
        # Use config credentials if not provided
        email = email or config.LINKEDIN_EMAIL
        password = password or config.LINKEDIN_PASSWORD
        phone = phone or config.LINKEDIN_PHONE
        
        if not email or not password:
            logger.error("LinkedIn credentials not provided")
            return False
        
        logger.info("Attempting LinkedIn login...")
        
        try:
            # Navigate to login page
            self.driver.get(self.login_url)
            self.human_delay(2, 4)
            
            # Handle any popups
            self.handle_popup()
            
            # Wait for login form
            email_field = self.wait_for_element(By.CSS_SELECTOR, self.selectors['login']['email'])
            if not email_field:
                logger.error("Email field not found")
                return False
            
            # Enter email with human-like typing
            logger.debug("Entering email...")
            self.human_type(email_field, email)
            self.human_delay(1, 2)
            
            # Enter password
            password_field = self.wait_for_element(By.CSS_SELECTOR, self.selectors['login']['password'])
            if not password_field:
                logger.error("Password field not found")
                return False
            
            logger.debug("Entering password...")
            self.human_type(password_field, password)
            self.human_delay(1, 2)
            
            # Random mouse movement
            self.random_mouse_movement()
            
            # Submit form
            submit_button = self.wait_for_clickable(By.CSS_SELECTOR, self.selectors['login']['submit'])
            if not submit_button:
                logger.error("Submit button not found")
                return False
            
            logger.debug("Submitting login form...")
            self.safe_click(submit_button)
            
            # Wait for login to complete
            self.human_delay(3, 6)
            
            # Check for CAPTCHA
            if self.check_for_captcha():
                logger.warning("CAPTCHA detected during login. Manual intervention required.")
                input("Please solve the CAPTCHA and press Enter to continue...")
            
            # Check for phone verification
            if phone and "challenge" in self.driver.current_url.lower():
                logger.info("Phone verification required")
                if not self._handle_phone_verification(phone):
                    return False
            
            # Verify login success
            self.human_delay(2, 4)
            if self._verify_login():
                logger.info("LinkedIn login successful")
                self.is_logged_in = True
                return True
            else:
                logger.error("LinkedIn login failed")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def _handle_phone_verification(self, phone: str) -> bool:
        """
        Handle phone verification challenge
        
        Args:
            phone: Phone number for verification
            
        Returns:
            True if verification successful, False otherwise
        """
        try:
            # Look for phone input field
            phone_selectors = [
                'input[name="phoneNumber"]',
                'input[id*="phone"]',
                'input[type="tel"]'
            ]
            
            phone_field = None
            for selector in phone_selectors:
                phone_field = self.wait_for_element(By.CSS_SELECTOR, selector, timeout=5)
                if phone_field:
                    break
            
            if phone_field:
                logger.info("Entering phone number for verification...")
                self.human_type(phone_field, phone)
                
                # Submit phone number
                submit_selectors = [
                    'button[type="submit"]',
                    'button[data-test-id="submit-btn"]',
                    '.challenge-form button'
                ]
                
                for selector in submit_selectors:
                    submit_btn = self.wait_for_clickable(By.CSS_SELECTOR, selector, timeout=5)
                    if submit_btn:
                        self.safe_click(submit_btn)
                        break
                
                # Wait for verification code input
                logger.warning("SMS verification code required. Please check your phone.")
                input("Enter the verification code on the page and press Enter to continue...")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Phone verification error: {str(e)}")
            return False
    
    def _verify_login(self) -> bool:
        """
        Verify if login was successful
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for login indicators
            login_indicators = [
                '.global-nav__me',  # Profile menu
                '.global-nav__primary-link-me',  # Me link
                'nav[aria-label="Primary Navigation"]',  # Main navigation
                '.feed-container'  # Feed container
            ]
            
            for indicator in login_indicators:
                if self.wait_for_element(By.CSS_SELECTOR, indicator, timeout=5):
                    return True
            
            # Check if still on login page or error page
            if "login" in self.driver.current_url or "challenge" in self.driver.current_url:
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Login verification error: {str(e)}")
            return False
    
    def scrape_jobs(
        self,
        job_title: str,
        location: str = "Remote",
        max_jobs: int = 50,
        experience_level: str = None,
        job_type: str = None,
        date_posted: str = "week"
    ) -> List[JobListing]:
        """
        Scrape jobs from LinkedIn
        
        Args:
            job_title: Job title to search for
            location: Job location
            max_jobs: Maximum number of jobs to scrape
            experience_level: Experience level filter
            job_type: Job type filter (Full-time, Part-time, etc.)
            date_posted: Date posted filter (day, week, month)
            
        Returns:
            List of JobListing objects
        """
        if not self.driver:
            self.initialize_driver()
        
        if not self.is_logged_in:
            logger.warning("Not logged in to LinkedIn. Some features may be limited.")
        
        logger.info(f"Scraping LinkedIn jobs: {job_title} in {location}")
        
        jobs = []
        
        try:
            # Build search URL
            search_params = {
                'keywords': job_title,
                'location': location,
                'f_TPR': self._get_date_filter(date_posted),
                'f_JT': self._get_job_type_filter(job_type) if job_type else None,
                'f_E': self._get_experience_filter(experience_level) if experience_level else None
            }
            
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            search_url = f"{self.jobs_url}?{urlencode(search_params)}"
            logger.debug(f"Search URL: {search_url}")
            
            # Navigate to search results
            self.driver.get(search_url)
            self.human_delay(3, 5)
            
            # Handle popups
            self.handle_popup()
            
            # Scrape job listings
            page_count = 0
            max_pages = 10  # Limit to prevent infinite scrolling
            
            while len(jobs) < max_jobs and page_count < max_pages:
                page_count += 1
                logger.debug(f"Scraping page {page_count}")
                
                # Get job cards on current page
                page_jobs = self._scrape_job_cards()
                
                if not page_jobs:
                    logger.warning("No jobs found on current page")
                    break
                
                jobs.extend(page_jobs)
                logger.info(f"Scraped {len(page_jobs)} jobs from page {page_count}")
                
                # Break if we have enough jobs
                if len(jobs) >= max_jobs:
                    break
                
                # Try to load more jobs
                if not self._load_more_jobs():
                    logger.info("No more jobs to load")
                    break
                
                # Random delay between pages
                self.human_delay(2, 4)
            
            # Limit to requested number of jobs
            jobs = jobs[:max_jobs]
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn jobs: {str(e)}")
            return jobs
    
    def _scrape_job_cards(self) -> List[JobListing]:
        """
        Scrape job cards from current page
        
        Returns:
            List of JobListing objects
        """
        jobs = []
        
        try:
            # Wait for job cards to load
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['jobs']['job_cards'])
            
            if not job_cards:
                logger.warning("No job cards found")
                return jobs
            
            for card in job_cards:
                try:
                    job = self._extract_job_data(card)
                    if job:
                        jobs.append(job)
                        
                except Exception as e:
                    logger.debug(f"Error extracting job data: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping job cards: {str(e)}")
            return jobs
    
    def _extract_job_data(self, card) -> Optional[JobListing]:
        """
        Extract job data from job card element
        
        Args:
            card: Job card WebElement
            
        Returns:
            JobListing object or None
        """
        try:
            # Extract basic information
            title_element = card.find_element(By.CSS_SELECTOR, self.selectors['jobs']['job_title'])
            title = self.get_text_safe(title_element)
            
            company_element = card.find_element(By.CSS_SELECTOR, self.selectors['jobs']['company_name'])
            company = self.get_text_safe(company_element)
            
            location_element = card.find_element(By.CSS_SELECTOR, self.selectors['jobs']['location'])
            location = self.get_text_safe(location_element)
            
            # Get job URL
            link_element = card.find_element(By.CSS_SELECTOR, self.selectors['jobs']['job_link'])
            job_url = self.get_attribute_safe(link_element, 'href')
            
            # Get posted date
            try:
                date_element = card.find_element(By.CSS_SELECTOR, self.selectors['jobs']['posted_date'])
                posted_date = self.get_text_safe(date_element)
            except NoSuchElementException:
                posted_date = ""
            
            # Basic validation
            if not title or not company:
                logger.debug("Missing required job data")
                return None
            
            # Create job listing
            job = JobListing(
                title=title,
                company=company,
                location=location,
                description="",  # Will be filled when clicking on job
                url=job_url,
                posted_date=posted_date,
                job_type="",
                experience_level="",
                salary=""
            )
            
            return job
            
        except Exception as e:
            logger.debug(f"Error extracting job data: {str(e)}")
            return None
    
    def _load_more_jobs(self) -> bool:
        """
        Try to load more jobs by scrolling or clicking load more button
        
        Returns:
            True if more jobs loaded, False otherwise
        """
        try:
            # First try scrolling to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.human_delay(2, 3)
            
            # Look for "Show more" button
            load_more_selectors = [
                self.selectors['jobs']['load_more'],
                '.infinite-scroller__show-more-button',
                'button[aria-label*="more results"]',
                '.jobs-search-results__pagination button'
            ]
            
            for selector in load_more_selectors:
                try:
                    load_more_btn = self.wait_for_clickable(By.CSS_SELECTOR, selector, timeout=3)
                    if load_more_btn and load_more_btn.is_displayed():
                        self.safe_click(load_more_btn)
                        self.human_delay(3, 5)
                        return True
                except Exception:
                    continue
            
            # Try pagination
            next_page_selectors = [
                'button[aria-label="Next"]',
                '.artdeco-pagination__button--next',
                'button[data-test-pagination-page-btn="next"]'
            ]
            
            for selector in next_page_selectors:
                try:
                    next_btn = self.wait_for_clickable(By.CSS_SELECTOR, selector, timeout=3)
                    if next_btn and next_btn.is_enabled():
                        self.safe_click(next_btn)
                        self.human_delay(3, 5)
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.debug(f"Error loading more jobs: {str(e)}")
            return False
    
    def _get_date_filter(self, date_posted: str) -> str:
        """Get LinkedIn date filter parameter"""
        date_filters = {
            'day': 'r86400',
            'week': 'r604800',
            'month': 'r2592000'
        }
        return date_filters.get(date_posted, 'r604800')  # Default to week
    
    def _get_job_type_filter(self, job_type: str) -> str:
        """Get LinkedIn job type filter parameter"""
        job_type_filters = {
            'full-time': 'F',
            'part-time': 'P',
            'contract': 'C',
            'temporary': 'T',
            'internship': 'I'
        }
        return job_type_filters.get(job_type.lower() if job_type else '')
    
    def _get_experience_filter(self, experience_level: str) -> str:
        """Get LinkedIn experience filter parameter"""
        experience_filters = {
            'internship': '1',
            'entry': '2',
            'associate': '3',
            'mid': '4',
            'director': '5',
            'executive': '6'
        }
        return experience_filters.get(experience_level.lower() if experience_level else '')
    
    def close(self) -> None:
        """Close the scraper and browser"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("LinkedIn scraper closed")
