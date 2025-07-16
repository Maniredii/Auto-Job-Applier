"""
Glassdoor Job Scraper
Specialized scraper for Glassdoor platform with focus on job listings, company reviews, and salary insights
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

class GlassdoorScraper(BaseScraper):
    """Glassdoor job scraper with anti-detection features"""
    
    def __init__(self):
        """Initialize Glassdoor scraper"""
        super().__init__()
        self.base_url = "https://www.glassdoor.com"
        self.jobs_url = f"{self.base_url}/Job/jobs.htm"
        self.login_url = f"{self.base_url}/profile/login_input.htm"
        
        self.browser_manager = BrowserManager()
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        
        # Platform-specific selectors
        self.selectors = {
            'job_cards': '[data-test="job-listing"], .react-job-listing, .jobContainer',
            'job_title': '[data-test="job-title"], .jobTitle, h3 a',
            'company_name': '[data-test="employer-name"], .employerName, .companyName',
            'location': '[data-test="job-location"], .location, .jobLocation',
            'posted_date': '[data-test="job-age"], .jobAge, .posted',
            'job_type': '.jobType, .employmentType',
            'salary': '[data-test="salary-estimate"], .salaryEstimate, .salary',
            'rating': '.rating, .companyRating',
            'apply_button': '[data-test="apply-button"], .applyButton',
            'next_page': '[data-test="pagination-next"], .next',
            'login_email': '#userEmail, input[name="username"]',
            'login_password': '#userPassword, input[name="password"]',
            'login_submit': '[data-test="sign-in-button"], .signInBtn'
        }
    
    def initialize_driver(self) -> None:
        """Initialize browser driver"""
        if not self.driver:
            self.driver = self.browser_manager.get_driver(
                headless=config.HEADLESS_MODE,
                profile_name="glassdoor_profile"
            )
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Glassdoor scraper driver initialized")
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Glassdoor
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self.initialize_driver()
        
        try:
            logger.info("Attempting to login to Glassdoor")
            
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
                logger.info("Successfully logged in to Glassdoor")
                return True
            else:
                logger.error("Glassdoor login failed")
                return False
                
        except Exception as e:
            logger.error(f"Glassdoor login error: {str(e)}")
            return False
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            # Look for user profile or dashboard elements
            success_indicators = [
                '[data-test="user-menu"]',
                '.userMenu',
                '.profile-dropdown',
                '.user-profile'
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
        date_posted: str = "week",
        salary_min: int = None,
        company_rating_min: float = None
    ) -> List[JobListing]:
        """
        Scrape jobs from Glassdoor
        
        Args:
            job_title: Job title to search for
            location: Job location
            max_jobs: Maximum number of jobs to scrape
            experience_level: Experience level filter
            job_type: Job type filter
            date_posted: Date posted filter
            salary_min: Minimum salary filter
            company_rating_min: Minimum company rating filter
            
        Returns:
            List of JobListing objects
        """
        if not self.driver:
            self.initialize_driver()
        
        logger.info(f"Scraping Glassdoor jobs: {job_title} in {location}")
        
        jobs = []
        
        try:
            # Build search URL
            search_params = {
                'sc.keyword': job_title,
                'locT': 'C',
                'locId': location if location else '',
            }
            
            # Add filters
            if date_posted:
                date_map = {
                    'day': '1',
                    'week': '7',
                    'month': '30'
                }
                if date_posted in date_map:
                    search_params['fromAge'] = date_map[date_posted]
            
            if job_type:
                type_map = {
                    'full-time': 'fulltime',
                    'part-time': 'parttime',
                    'contract': 'contract',
                    'internship': 'internship'
                }
                if job_type.lower() in type_map:
                    search_params['jobType'] = type_map[job_type.lower()]
            
            search_url = f"{self.jobs_url}?{urlencode(search_params)}"
            logger.debug(f"Search URL: {search_url}")
            
            # Navigate to search results
            self.driver.get(search_url)
            self.human_delay(3, 5)
            
            # Handle popups
            self.handle_popup()
            self._handle_glassdoor_popups()
            
            # Scrape job listings
            page_count = 0
            max_pages = 10
            
            while len(jobs) < max_jobs and page_count < max_pages:
                page_count += 1
                logger.debug(f"Scraping page {page_count}")
                
                # Get job cards on current page
                page_jobs = self._scrape_job_cards(company_rating_min)
                
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
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from Glassdoor")
            return jobs
            
        except Exception as e:
            logger.error(f"Glassdoor scraping error: {str(e)}")
            return []
    
    def _handle_glassdoor_popups(self) -> None:
        """Handle Glassdoor-specific popups"""
        try:
            # Common Glassdoor popup selectors
            popup_selectors = [
                '[data-test="modal-close"]',
                '.modal-close',
                '.close-icon',
                '.CloseIcon'
            ]
            
            for selector in popup_selectors:
                try:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_button.is_displayed():
                        self.safe_click(close_button)
                        logger.debug(f"Dismissed Glassdoor popup: {selector}")
                        time.sleep(1)
                except NoSuchElementException:
                    continue
        except Exception as e:
            logger.debug(f"Error handling Glassdoor popups: {str(e)}")
    
    def _scrape_job_cards(self, company_rating_min: float = None) -> List[JobListing]:
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
                        # Apply company rating filter if specified
                        if company_rating_min and hasattr(job, 'company_rating'):
                            try:
                                rating = float(job.company_rating)
                                if rating < company_rating_min:
                                    continue
                            except (ValueError, TypeError):
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

            # Extract company rating
            company_rating = ""
            try:
                rating_element = card.find_element(By.CSS_SELECTOR, self.selectors['rating'])
                company_rating = rating_element.text.strip()
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
                posted_date=posted_date,
                platform="glassdoor",
                job_type="Full-time",  # Glassdoor doesn't always specify
                salary=salary,
                job_id=job_id,
                easy_apply=easy_apply,
                apply_url=job_url
            )

            # Add company rating as custom attribute
            if company_rating:
                job.company_rating = company_rating

            return job

        except Exception as e:
            logger.debug(f"Error extracting job data from card: {str(e)}")
            return None

    def _parse_posted_date(self, date_text: str) -> str:
        """Parse posted date from various formats"""
        try:
            # Common patterns in Glassdoor
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
                # Glassdoor URLs typically have format: /job-listing/job-title-company-JV_IC123456_KO0,10_IL.11,20_IM123.htm
                parts = url.split('_')
                for part in parts:
                    if part.startswith('IC') or part.startswith('KO'):
                        numbers = re.findall(r'\d+', part)
                        if numbers:
                            return numbers[0]
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
                    '[data-test="job-description"]',
                    '.jobDescriptionContent',
                    '.desc'
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

            # Extract company information and rating
            try:
                company_selectors = [
                    '.employerInfo',
                    '.companyHeader',
                    '.employer-info'
                ]

                for selector in company_selectors:
                    try:
                        company_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        details['company_info'] = company_element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
            except:
                details['company_info'] = ""

            # Extract benefits
            try:
                benefits_selectors = [
                    '.benefits',
                    '.jobBenefits',
                    '.perks'
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
        logger.info("Glassdoor scraper closed")
