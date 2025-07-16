"""
Internshala Job Scraper
Specialized scraper for Internshala platform focusing on internships and entry-level jobs
"""

import logging
import time
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode, urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper, JobListing
from ..automation.browser_manager import BrowserManager
from config import config

logger = logging.getLogger(__name__)

class IntershalaScraper(BaseScraper):
    """Internshala job scraper with anti-detection features"""
    
    def __init__(self):
        """Initialize Internshala scraper"""
        super().__init__()
        self.base_url = "https://internshala.com"
        self.jobs_url = f"{self.base_url}/jobs"
        self.internships_url = f"{self.base_url}/internships"
        self.login_url = f"{self.base_url}/login"
        
        self.browser_manager = BrowserManager()
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        
        # Platform-specific selectors
        self.selectors = {
            'job_cards': '.individual_internship',
            'job_title': '.job-title a, .profile h3 a',
            'company_name': '.company-name, .company h4 a',
            'location': '.location_link, .locations span',
            'posted_date': '.status, .posted_by_container',
            'job_type': '.internship_type, .job_type',
            'salary': '.stipend, .salary',
            'apply_button': '.apply_now_button, .btn-primary',
            'description_link': '.view_detail_button, .view-details',
            'next_page': '.next, .pagination .next',
            'login_email': '#email',
            'login_password': '#password',
            'login_submit': '#login_submit'
        }
    
    def initialize_driver(self) -> None:
        """Initialize browser driver"""
        if not self.driver:
            self.driver = self.browser_manager.get_driver(
                headless=config.HEADLESS_MODE,
                profile_name="internshala_profile"
            )
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Internshala scraper driver initialized")
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Internshala
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self.initialize_driver()
        
        try:
            logger.info("Attempting to login to Internshala")
            
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
                logger.info("Successfully logged in to Internshala")
                return True
            else:
                logger.error("Internshala login failed")
                return False
                
        except Exception as e:
            logger.error(f"Internshala login error: {str(e)}")
            return False
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            # Look for user profile or dashboard elements
            success_indicators = [
                '.user_name',
                '.profile-dropdown',
                '.dashboard',
                '[data-toggle="dropdown"]'
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
        job_type: str = "both",  # "internship", "job", or "both"
        experience_level: str = None,
        date_posted: str = "week"
    ) -> List[JobListing]:
        """
        Scrape jobs from Internshala
        
        Args:
            job_title: Job title to search for
            location: Job location
            max_jobs: Maximum number of jobs to scrape
            job_type: Type of opportunities ("internship", "job", or "both")
            experience_level: Experience level filter
            date_posted: Date posted filter
            
        Returns:
            List of JobListing objects
        """
        if not self.driver:
            self.initialize_driver()
        
        logger.info(f"Scraping Internshala: {job_title} in {location}")
        
        all_jobs = []
        
        try:
            # Scrape internships if requested
            if job_type in ["internship", "both"]:
                internships = self._scrape_opportunities(
                    job_title, location, max_jobs // 2 if job_type == "both" else max_jobs,
                    "internship", date_posted
                )
                all_jobs.extend(internships)
            
            # Scrape jobs if requested
            if job_type in ["job", "both"]:
                jobs = self._scrape_opportunities(
                    job_title, location, max_jobs // 2 if job_type == "both" else max_jobs,
                    "job", date_posted
                )
                all_jobs.extend(jobs)
            
            # Limit to requested number
            all_jobs = all_jobs[:max_jobs]
            
            logger.info(f"Successfully scraped {len(all_jobs)} opportunities from Internshala")
            return all_jobs
            
        except Exception as e:
            logger.error(f"Internshala scraping error: {str(e)}")
            return []
    
    def _scrape_opportunities(
        self,
        job_title: str,
        location: str,
        max_jobs: int,
        opportunity_type: str,
        date_posted: str
    ) -> List[JobListing]:
        """Scrape specific type of opportunities (internships or jobs)"""
        
        jobs = []
        
        try:
            # Build search URL
            base_url = self.internships_url if opportunity_type == "internship" else self.jobs_url
            search_params = {
                'search': job_title,
                'location': location if location else '',
            }
            
            # Add date filter
            if date_posted == "day":
                search_params['posted'] = '1'
            elif date_posted == "week":
                search_params['posted'] = '7'
            elif date_posted == "month":
                search_params['posted'] = '30'
            
            search_url = f"{base_url}?{urlencode(search_params)}"
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
                logger.debug(f"Scraping {opportunity_type} page {page_count}")
                
                # Get job cards on current page
                page_jobs = self._scrape_job_cards(opportunity_type)
                
                if not page_jobs:
                    logger.warning(f"No {opportunity_type}s found on current page")
                    break
                
                jobs.extend(page_jobs)
                logger.info(f"Scraped {len(page_jobs)} {opportunity_type}s from page {page_count}")
                
                # Break if we have enough jobs
                if len(jobs) >= max_jobs:
                    break
                
                # Try to go to next page
                if not self._go_to_next_page():
                    logger.info(f"No more {opportunity_type} pages to scrape")
                    break
                
                # Random delay between pages
                self.human_delay(2, 4)
            
            return jobs[:max_jobs]
            
        except Exception as e:
            logger.error(f"Error scraping {opportunity_type}s: {str(e)}")
            return jobs
    
    def _scrape_job_cards(self, opportunity_type: str) -> List[JobListing]:
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
                    job = self._extract_job_data(card, opportunity_type)
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

    def _extract_job_data(self, card, opportunity_type: str) -> Optional[JobListing]:
        """Extract job data from a job card"""
        try:
            # Extract title
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
                location = "Not specified"

            # Extract posted date
            try:
                date_element = card.find_element(By.CSS_SELECTOR, self.selectors['posted_date'])
                posted_date = self._parse_posted_date(date_element.text.strip())
            except NoSuchElementException:
                posted_date = "Not specified"

            # Extract salary/stipend
            try:
                salary_element = card.find_element(By.CSS_SELECTOR, self.selectors['salary'])
                salary = salary_element.text.strip()
            except NoSuchElementException:
                salary = "Not specified"

            # Extract job type
            try:
                type_element = card.find_element(By.CSS_SELECTOR, self.selectors['job_type'])
                job_type = type_element.text.strip()
            except NoSuchElementException:
                job_type = opportunity_type.title()

            # Check for easy apply
            easy_apply = False
            try:
                apply_button = card.find_element(By.CSS_SELECTOR, self.selectors['apply_button'])
                easy_apply = 'apply_now' in apply_button.get_attribute('class').lower()
            except NoSuchElementException:
                pass

            # Get job ID from URL
            job_id = self._extract_job_id(job_url)

            # Create job listing
            job = JobListing(
                title=title,
                company=company,
                location=location,
                description="",  # Will be filled by detailed scraping if needed
                url=job_url,
                posted_date=posted_date,
                platform="internshala",
                job_type=job_type,
                salary=salary,
                job_id=job_id,
                easy_apply=easy_apply,
                apply_url=job_url
            )

            return job

        except Exception as e:
            logger.debug(f"Error extracting job data from card: {str(e)}")
            return None

    def _parse_posted_date(self, date_text: str) -> str:
        """Parse posted date from various formats"""
        try:
            # Common patterns in Internshala
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
                # Internshala URLs typically have format: /internships/detail/job-title-123456
                parts = url.split('/')
                if len(parts) > 2:
                    # Look for numeric ID at the end
                    last_part = parts[-1]
                    numbers = re.findall(r'\d+', last_part)
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
                    '.internship_details',
                    '.job_description',
                    '.description',
                    '.detail_view'
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

            # Extract requirements
            try:
                req_selectors = [
                    '.requirements',
                    '.skills_required',
                    '.eligibility'
                ]

                requirements = []
                for selector in req_selectors:
                    try:
                        req_elements = self.driver.find_elements(By.CSS_SELECTOR, f"{selector} li, {selector} p")
                        for elem in req_elements:
                            req_text = elem.text.strip()
                            if req_text:
                                requirements.append(req_text)
                    except NoSuchElementException:
                        continue

                details['requirements'] = requirements
            except:
                details['requirements'] = []

            # Extract benefits/perks
            try:
                benefits_selectors = [
                    '.perks',
                    '.benefits',
                    '.additional_info'
                ]

                benefits = []
                for selector in benefits_selectors:
                    try:
                        benefit_elements = self.driver.find_elements(By.CSS_SELECTOR, f"{selector} li, {selector} span")
                        for elem in benefit_elements:
                            benefit_text = elem.text.strip()
                            if benefit_text:
                                benefits.append(benefit_text)
                    except NoSuchElementException:
                        continue

                details['benefits'] = benefits
            except:
                details['benefits'] = []

            return details

        except Exception as e:
            logger.error(f"Error getting job details: {str(e)}")
            return {}

    def close(self) -> None:
        """Close the scraper and browser"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("Internshala scraper closed")
