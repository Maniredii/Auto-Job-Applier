"""
Monster Job Scraper
Comprehensive scraper for Monster platform
"""

import logging
import time
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper, JobListing
from ..automation.browser_manager import BrowserManager
from config import config

logger = logging.getLogger(__name__)

class MonsterScraper(BaseScraper):
    """Monster job scraper with anti-detection features"""
    
    def __init__(self):
        """Initialize Monster scraper"""
        super().__init__()
        self.base_url = "https://www.monster.com"
        self.jobs_url = f"{self.base_url}/jobs/search"
        self.login_url = f"{self.base_url}/account/sign-in"
        
        self.browser_manager = BrowserManager()
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        
        # Platform-specific selectors
        self.selectors = {
            'job_cards': '[data-testid="job-card"], .job-card, .search-result',
            'job_title': '[data-testid="job-title"] a, .job-title a, h3 a',
            'company_name': '[data-testid="company-name"], .company-name, .company',
            'location': '[data-testid="job-location"], .location, .job-location',
            'posted_date': '.posted-date, .job-date, .date-posted',
            'job_type': '.job-type, .employment-type',
            'salary': '.salary, .compensation, .pay-range',
            'apply_button': '.apply-button, .btn-apply, .apply-now',
            'next_page': '.next, .pagination-next, [aria-label="Next"]',
            'login_email': '#email, input[name="email"]',
            'login_password': '#password, input[name="password"]',
            'login_submit': 'button[type="submit"], .btn-primary, .sign-in-btn'
        }
    
    def initialize_driver(self) -> None:
        """Initialize browser driver"""
        if not self.driver:
            self.driver = self.browser_manager.get_driver(
                headless=config.HEADLESS_MODE,
                profile_name="monster_profile"
            )
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Monster scraper driver initialized")
    
    def login(self, email: str, password: str) -> bool:
        """Login to Monster"""
        if not self.driver:
            self.initialize_driver()
        
        try:
            logger.info("Attempting to login to Monster")
            self.driver.get(self.login_url)
            self.human_delay(2, 4)
            
            # Fill login form
            email_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['login_email']))
            )
            self.human_type(email_field, email)
            
            password_field = self.driver.find_element(By.CSS_SELECTOR, self.selectors['login_password'])
            self.human_type(password_field, password)
            
            # Submit login
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors['login_submit'])
            self.safe_click(login_button)
            self.human_delay(3, 5)
            
            if self._check_login_success():
                self.is_logged_in = True
                logger.info("Successfully logged in to Monster")
                return True
            else:
                logger.error("Monster login failed")
                return False
                
        except Exception as e:
            logger.error(f"Monster login error: {str(e)}")
            return False
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            success_indicators = ['.user-menu', '.profile-dropdown', '.account-menu']
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        return True
                except NoSuchElementException:
                    continue
            return 'sign-in' not in self.driver.current_url.lower()
        except Exception as e:
            logger.debug(f"Login check error: {str(e)}")
            return False
    
    def scrape_jobs(
        self,
        job_title: str,
        location: str = "",
        max_jobs: int = 50,
        experience_level: str = None,
        job_type: str = None,
        date_posted: str = "week"
    ) -> List[JobListing]:
        """Scrape jobs from Monster"""
        if not self.driver:
            self.initialize_driver()
        
        logger.info(f"Scraping Monster jobs: {job_title} in {location}")
        jobs = []
        
        try:
            # Build search URL
            search_params = {
                'q': job_title,
                'where': location if location else '',
            }
            
            search_url = f"{self.jobs_url}?{urlencode(search_params)}"
            logger.debug(f"Search URL: {search_url}")
            
            # Navigate to search results
            self.driver.get(search_url)
            self.human_delay(3, 5)
            self.handle_popup()
            
            # Scrape job listings
            page_count = 0
            max_pages = 10
            
            while len(jobs) < max_jobs and page_count < max_pages:
                page_count += 1
                logger.debug(f"Scraping page {page_count}")
                
                page_jobs = self._scrape_job_cards()
                if not page_jobs:
                    break
                
                jobs.extend(page_jobs)
                logger.info(f"Scraped {len(page_jobs)} jobs from page {page_count}")
                
                if len(jobs) >= max_jobs or not self._go_to_next_page():
                    break
                
                self.human_delay(2, 4)
            
            jobs = jobs[:max_jobs]
            logger.info(f"Successfully scraped {len(jobs)} jobs from Monster")
            return jobs
            
        except Exception as e:
            logger.error(f"Monster scraping error: {str(e)}")
            return []
    
    def _scrape_job_cards(self) -> List[JobListing]:
        """Scrape job cards from current page"""
        jobs = []
        
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['job_cards']))
            )
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['job_cards'])
            logger.debug(f"Found {len(job_cards)} job cards")
            
            for card in job_cards:
                try:
                    job = self._extract_job_data(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error extracting job data: {str(e)}")
                    continue
            
            return jobs
            
        except TimeoutException:
            logger.warning("Timeout waiting for job cards to load")
            return []
        except Exception as e:
            logger.error(f"Error scraping job cards: {str(e)}")
            return []
    
    def _extract_job_data(self, card) -> Optional[JobListing]:
        """Extract job data from a job card"""
        try:
            # Extract title and URL
            title_element = card.find_element(By.CSS_SELECTOR, self.selectors['job_title'])
            title = title_element.text.strip()
            job_url = title_element.get_attribute('href')
            
            if job_url and not job_url.startswith('http'):
                job_url = f"{self.base_url}{job_url}"
            
            # Extract company
            company_element = card.find_element(By.CSS_SELECTOR, self.selectors['company_name'])
            company = company_element.text.strip()
            
            # Extract location
            try:
                location_element = card.find_element(By.CSS_SELECTOR, self.selectors['location'])
                location = location_element.text.strip()
            except NoSuchElementException:
                location = "Not specified"
            
            # Extract posted date
            try:
                date_element = card.find_element(By.CSS_SELECTOR, self.selectors['posted_date'])
                posted_date = self._parse_posted_date(date_element.text.strip())
            except NoSuchElementException:
                posted_date = "Not specified"
            
            # Extract salary
            try:
                salary_element = card.find_element(By.CSS_SELECTOR, self.selectors['salary'])
                salary = salary_element.text.strip()
            except NoSuchElementException:
                salary = "Not disclosed"
            
            # Extract job ID from URL
            job_id = self._extract_job_id(job_url)
            
            # Create job listing
            job = JobListing(
                title=title,
                company=company,
                location=location,
                description="",
                url=job_url,
                posted_date=posted_date,
                platform="monster",
                job_type="Full-time",
                salary=salary,
                job_id=job_id,
                apply_url=job_url
            )
            
            return job
            
        except Exception as e:
            logger.debug(f"Error extracting job data from card: {str(e)}")
            return None
    
    def _parse_posted_date(self, date_text: str) -> str:
        """Parse posted date from various formats"""
        try:
            if 'ago' in date_text.lower():
                return date_text
            elif 'today' in date_text.lower():
                return 'Today'
            elif 'yesterday' in date_text.lower():
                return 'Yesterday'
            else:
                return date_text
        except:
            return "Not specified"
    
    def _extract_job_id(self, url: str) -> str:
        """Extract job ID from URL"""
        try:
            if url:
                numbers = re.findall(r'\d+', url)
                if numbers:
                    return numbers[-1]
            return ""
        except:
            return ""
    
    def _go_to_next_page(self) -> bool:
        """Navigate to next page of results"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors['next_page'])
            if next_button.is_enabled() and next_button.is_displayed():
                self.safe_click(next_button)
                self.human_delay(2, 4)
                return True
            return False
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.debug(f"Error navigating to next page: {str(e)}")
            return False
    
    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """Get detailed job information from job page"""
        if not self.driver:
            self.initialize_driver()
        
        try:
            self.driver.get(job_url)
            self.human_delay(2, 4)
            
            details = {}
            
            # Extract description
            try:
                desc_selectors = ['.job-description', '.description', '.job-details']
                for selector in desc_selectors:
                    try:
                        desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        details['description'] = desc_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
            except:
                details['description'] = ""
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting job details: {str(e)}")
            return {}
    
    def close(self) -> None:
        """Close the scraper and browser"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("Monster scraper closed")
