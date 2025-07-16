"""
AngelList (Wellfound) Job Scraper
Specialized scraper for AngelList/Wellfound platform focusing on startup jobs
"""

import logging
import time
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode, quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper, JobListing
from ..automation.browser_manager import BrowserManager
from config import config

logger = logging.getLogger(__name__)

class AngelListScraper(BaseScraper):
    """AngelList job scraper with anti-detection features"""
    
    def __init__(self):
        """Initialize AngelList scraper"""
        super().__init__()
        self.base_url = "https://wellfound.com"  # AngelList rebranded to Wellfound
        self.jobs_url = f"{self.base_url}/jobs"
        self.login_url = f"{self.base_url}/login"
        
        self.browser_manager = BrowserManager()
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        
        # Platform-specific selectors
        self.selectors = {
            'job_cards': '[data-test="StartupResult"], .startup-link, .job-listing',
            'job_title': '[data-test="JobTitle"], .job-title, h3 a',
            'company_name': '[data-test="StartupNameLink"], .startup-name, .company-name',
            'location': '[data-test="LocationLink"], .location, .job-location',
            'posted_date': '.posted-date, .job-age',
            'job_type': '.job-type, .employment-type',
            'salary': '[data-test="SalaryRange"], .salary-range, .compensation',
            'equity': '.equity, .equity-range',
            'company_size': '.company-size, .team-size',
            'apply_button': '[data-test="ApplyButton"], .apply-button',
            'next_page': '.next, .pagination-next',
            'login_email': 'input[name="user[email]"], #user_email',
            'login_password': 'input[name="user[password]"], #user_password',
            'login_submit': 'input[type="submit"], .login-button'
        }
    
    def initialize_driver(self) -> None:
        """Initialize browser driver"""
        if not self.driver:
            self.driver = self.browser_manager.get_driver(
                headless=config.HEADLESS_MODE,
                profile_name="angellist_profile"
            )
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("AngelList scraper driver initialized")
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to AngelList
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self.initialize_driver()
        
        try:
            logger.info("Attempting to login to AngelList")
            
            # Navigate to login page
            self.driver.get(self.login_url)
            self.human_delay(2, 4)
            
            # Handle any popups
            self.handle_popup()
            
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
            
            # Wait for login to complete
            self.human_delay(3, 5)
            
            # Check if login was successful
            if self._check_login_success():
                self.is_logged_in = True
                logger.info("Successfully logged in to AngelList")
                return True
            else:
                logger.error("AngelList login failed")
                return False
                
        except Exception as e:
            logger.error(f"AngelList login error: {str(e)}")
            return False
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            # Look for user profile or dashboard elements
            success_indicators = [
                '.user-menu',
                '.profile-dropdown',
                '.user-avatar',
                '[data-test="UserMenu"]'
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        return True
                except NoSuchElementException:
                    continue
            
            # Check if still on login page
            current_url = self.driver.current_url
            if 'login' in current_url.lower():
                return False
                
            return True
            
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
        company_size: str = None,
        equity_min: float = None
    ) -> List[JobListing]:
        """
        Scrape jobs from AngelList
        
        Args:
            job_title: Job title to search for
            location: Job location
            max_jobs: Maximum number of jobs to scrape
            experience_level: Experience level filter
            job_type: Job type filter
            company_size: Company size filter (startup, small, medium, large)
            equity_min: Minimum equity percentage
            
        Returns:
            List of JobListing objects
        """
        if not self.driver:
            self.initialize_driver()
        
        logger.info(f"Scraping AngelList jobs: {job_title} in {location}")
        
        jobs = []
        
        try:
            # Build search URL
            search_params = {
                'role': job_title,
                'location': location if location else '',
            }
            
            # Add filters
            if experience_level:
                exp_map = {
                    'intern': 'intern',
                    'entry-level': 'junior',
                    'mid-level': 'mid',
                    'senior-level': 'senior',
                    'lead': 'lead'
                }
                if experience_level.lower() in exp_map:
                    search_params['experience'] = exp_map[experience_level.lower()]
            
            if job_type:
                type_map = {
                    'full-time': 'full-time',
                    'part-time': 'part-time',
                    'contract': 'contract',
                    'internship': 'internship'
                }
                if job_type.lower() in type_map:
                    search_params['type'] = type_map[job_type.lower()]
            
            if company_size:
                size_map = {
                    'startup': '1-10',
                    'small': '11-50',
                    'medium': '51-200',
                    'large': '201+'
                }
                if company_size.lower() in size_map:
                    search_params['company_size'] = size_map[company_size.lower()]
            
            search_url = f"{self.jobs_url}?{urlencode(search_params)}"
            logger.debug(f"Search URL: {search_url}")
            
            # Navigate to search results
            self.driver.get(search_url)
            self.human_delay(3, 5)
            
            # Handle popups
            self.handle_popup()
            
            # Scrape job listings
            page_count = 0
            max_pages = 10
            
            while len(jobs) < max_jobs and page_count < max_pages:
                page_count += 1
                logger.debug(f"Scraping page {page_count}")
                
                # Get job cards on current page
                page_jobs = self._scrape_job_cards(equity_min)
                
                if not page_jobs:
                    logger.warning("No jobs found on current page")
                    break
                
                jobs.extend(page_jobs)
                logger.info(f"Scraped {len(page_jobs)} jobs from page {page_count}")
                
                # Break if we have enough jobs
                if len(jobs) >= max_jobs:
                    break
                
                # Try to go to next page
                if not self._go_to_next_page():
                    logger.info("No more pages to scrape")
                    break
                
                # Random delay between pages
                self.human_delay(2, 4)
            
            # Limit to requested number of jobs
            jobs = jobs[:max_jobs]
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from AngelList")
            return jobs
            
        except Exception as e:
            logger.error(f"AngelList scraping error: {str(e)}")
            return []
    
    def _scrape_job_cards(self, equity_min: float = None) -> List[JobListing]:
        """Scrape job cards from current page"""
        jobs = []
        
        try:
            # Wait for job cards to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['job_cards']))
            )
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['job_cards'])
            logger.debug(f"Found {len(job_cards)} job cards")
            
            for card in job_cards:
                try:
                    job = self._extract_job_data(card)
                    if job:
                        # Apply equity filter if specified
                        if equity_min and hasattr(job, 'equity_percentage'):
                            try:
                                equity = float(job.equity_percentage.replace('%', ''))
                                if equity < equity_min:
                                    continue
                            except (ValueError, TypeError, AttributeError):
                                pass
                        
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

            # Make URL absolute
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
                location = "Remote"  # Many startup jobs are remote

            # Extract salary
            try:
                salary_element = card.find_element(By.CSS_SELECTOR, self.selectors['salary'])
                salary = salary_element.text.strip()
            except NoSuchElementException:
                salary = "Not disclosed"

            # Extract equity
            equity = ""
            try:
                equity_element = card.find_element(By.CSS_SELECTOR, self.selectors['equity'])
                equity = equity_element.text.strip()
            except NoSuchElementException:
                pass

            # Extract company size
            company_size = ""
            try:
                size_element = card.find_element(By.CSS_SELECTOR, self.selectors['company_size'])
                company_size = size_element.text.strip()
            except NoSuchElementException:
                pass

            # Check for easy apply
            easy_apply = False
            try:
                apply_button = card.find_element(By.CSS_SELECTOR, self.selectors['apply_button'])
                easy_apply = apply_button.is_displayed()
            except NoSuchElementException:
                pass

            # Extract job ID from URL
            job_id = self._extract_job_id(job_url)

            # Create job listing
            job = JobListing(
                title=title,
                company=company,
                location=location,
                description="",  # Will be filled by detailed scraping if needed
                url=job_url,
                posted_date="Not specified",  # AngelList doesn't always show posted date
                platform="angellist",
                job_type="Full-time",  # Most startup jobs are full-time
                salary=salary,
                job_id=job_id,
                easy_apply=easy_apply,
                apply_url=job_url,
                company_size=company_size
            )

            # Add equity as custom attribute
            if equity:
                job.equity_percentage = equity

            return job

        except Exception as e:
            logger.debug(f"Error extracting job data from card: {str(e)}")
            return None

    def _extract_job_id(self, url: str) -> str:
        """Extract job ID from URL"""
        try:
            if url:
                # AngelList URLs typically have format: /jobs/123456-job-title-at-company
                parts = url.split('/')
                for part in parts:
                    if part and part[0].isdigit():
                        # Extract numeric part before the dash
                        job_id = part.split('-')[0]
                        if job_id.isdigit():
                            return job_id
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
        """
        Get detailed job information from job page

        Args:
            job_url: URL of the job posting

        Returns:
            Dictionary with detailed job information
        """
        if not self.driver:
            self.initialize_driver()

        try:
            logger.debug(f"Getting job details from: {job_url}")

            # Navigate to job page
            self.driver.get(job_url)
            self.human_delay(2, 4)

            details = {}

            # Extract detailed description
            try:
                desc_selectors = [
                    '.job-description',
                    '.description',
                    '.job-details'
                ]

                for selector in desc_selectors:
                    try:
                        desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        details['description'] = desc_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
            except:
                details['description'] = ""

            # Extract startup information
            try:
                startup_selectors = [
                    '.startup-info',
                    '.company-info',
                    '.startup-details'
                ]

                for selector in startup_selectors:
                    try:
                        startup_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        details['company_info'] = startup_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
            except:
                details['company_info'] = ""

            # Extract requirements/skills
            try:
                req_selectors = [
                    '.requirements',
                    '.skills',
                    '.qualifications'
                ]

                requirements = []
                for selector in req_selectors:
                    try:
                        req_elements = self.driver.find_elements(By.CSS_SELECTOR, f"{selector} li, {selector} span")
                        for elem in req_elements:
                            req_text = elem.text.strip()
                            if req_text:
                                requirements.append(req_text)
                    except NoSuchElementException:
                        continue

                details['requirements'] = requirements
            except:
                details['requirements'] = []

            return details

        except Exception as e:
            logger.error(f"Error getting job details: {str(e)}")
            return {}

    def close(self) -> None:
        """Close the scraper and browser"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("AngelList scraper closed")
