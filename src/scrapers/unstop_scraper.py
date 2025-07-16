"""
Unstop (formerly Dare2Compete) Job Scraper
Specialized scraper for Unstop platform focusing on competitions, hackathons, and job opportunities
"""

import logging
import time
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper, JobListing
from ..automation.browser_manager import BrowserManager
from config import config

logger = logging.getLogger(__name__)

class UnstopScraper(BaseScraper):
    """Unstop job scraper with anti-detection features"""
    
    def __init__(self):
        """Initialize Unstop scraper"""
        super().__init__()
        self.base_url = "https://unstop.com"
        self.jobs_url = f"{self.base_url}/jobs"
        self.competitions_url = f"{self.base_url}/competitions"
        self.hackathons_url = f"{self.base_url}/hackathons"
        self.login_url = f"{self.base_url}/login"
        
        self.browser_manager = BrowserManager()
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        
        # Platform-specific selectors
        self.selectors = {
            'job_cards': '.opportunity-card, .job-card, .card-container',
            'job_title': '.opportunity-title, .job-title, h3 a, h4 a',
            'company_name': '.company-name, .organizer-name, .company',
            'location': '.location, .venue, .job-location',
            'posted_date': '.posted-date, .deadline, .registration-ends',
            'job_type': '.opportunity-type, .job-type, .category',
            'salary': '.salary, .prize, .stipend',
            'apply_button': '.apply-btn, .register-btn, .btn-primary',
            'description_link': '.view-details, .opportunity-link',
            'next_page': '.next, .pagination-next',
            'login_email': '#email, input[name="email"]',
            'login_password': '#password, input[name="password"]',
            'login_submit': '.login-btn, button[type="submit"]'
        }
    
    def initialize_driver(self) -> None:
        """Initialize browser driver"""
        if not self.driver:
            self.driver = self.browser_manager.get_driver(
                headless=config.HEADLESS_MODE,
                profile_name="unstop_profile"
            )
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Unstop scraper driver initialized")
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Unstop
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self.initialize_driver()
        
        try:
            logger.info("Attempting to login to Unstop")
            
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
                logger.info("Successfully logged in to Unstop")
                return True
            else:
                logger.error("Unstop login failed")
                return False
                
        except Exception as e:
            logger.error(f"Unstop login error: {str(e)}")
            return False
    
    def _check_login_success(self) -> bool:
        """Check if login was successful"""
        try:
            # Look for user profile or dashboard elements
            success_indicators = [
                '.user-profile',
                '.profile-dropdown',
                '.dashboard',
                '.user-menu'
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
        opportunity_type: str = "jobs",  # "jobs", "competitions", "hackathons", or "all"
        experience_level: str = None,
        date_posted: str = "week"
    ) -> List[JobListing]:
        """
        Scrape opportunities from Unstop
        
        Args:
            job_title: Job title or keyword to search for
            location: Job location
            max_jobs: Maximum number of opportunities to scrape
            opportunity_type: Type of opportunities to scrape
            experience_level: Experience level filter
            date_posted: Date posted filter
            
        Returns:
            List of JobListing objects
        """
        if not self.driver:
            self.initialize_driver()
        
        logger.info(f"Scraping Unstop: {job_title} in {location}")
        
        all_opportunities = []
        
        try:
            # Determine which types to scrape
            types_to_scrape = []
            if opportunity_type == "all":
                types_to_scrape = ["jobs", "competitions", "hackathons"]
            else:
                types_to_scrape = [opportunity_type]
            
            jobs_per_type = max_jobs // len(types_to_scrape)
            
            for opp_type in types_to_scrape:
                opportunities = self._scrape_opportunity_type(
                    job_title, location, jobs_per_type, opp_type, date_posted
                )
                all_opportunities.extend(opportunities)
            
            # Limit to requested number
            all_opportunities = all_opportunities[:max_jobs]
            
            logger.info(f"Successfully scraped {len(all_opportunities)} opportunities from Unstop")
            return all_opportunities
            
        except Exception as e:
            logger.error(f"Unstop scraping error: {str(e)}")
            return []
    
    def _scrape_opportunity_type(
        self,
        keyword: str,
        location: str,
        max_items: int,
        opp_type: str,
        date_posted: str
    ) -> List[JobListing]:
        """Scrape specific type of opportunities"""
        
        opportunities = []
        
        try:
            # Build search URL based on type
            if opp_type == "jobs":
                base_url = self.jobs_url
            elif opp_type == "competitions":
                base_url = self.competitions_url
            elif opp_type == "hackathons":
                base_url = self.hackathons_url
            else:
                base_url = self.jobs_url
            
            search_params = {
                'search': keyword,
                'location': location if location else '',
            }
            
            # Add filters based on opportunity type
            if opp_type == "jobs":
                search_params['type'] = 'job'
            elif opp_type == "competitions":
                search_params['type'] = 'competition'
            elif opp_type == "hackathons":
                search_params['type'] = 'hackathon'
            
            search_url = f"{base_url}?{urlencode(search_params)}"
            logger.debug(f"Search URL: {search_url}")
            
            # Navigate to search results
            self.driver.get(search_url)
            self.human_delay(3, 5)
            
            # Handle popups
            self.handle_popup()
            
            # Scrape opportunities
            page_count = 0
            max_pages = 10
            
            while len(opportunities) < max_items and page_count < max_pages:
                page_count += 1
                logger.debug(f"Scraping {opp_type} page {page_count}")
                
                # Get opportunity cards on current page
                page_opportunities = self._scrape_opportunity_cards(opp_type)
                
                if not page_opportunities:
                    logger.warning(f"No {opp_type} found on current page")
                    break
                
                opportunities.extend(page_opportunities)
                logger.info(f"Scraped {len(page_opportunities)} {opp_type} from page {page_count}")
                
                # Break if we have enough opportunities
                if len(opportunities) >= max_items:
                    break
                
                # Try to go to next page
                if not self._go_to_next_page():
                    logger.info(f"No more {opp_type} pages to scrape")
                    break
                
                # Random delay between pages
                self.human_delay(2, 4)
            
            return opportunities[:max_items]
            
        except Exception as e:
            logger.error(f"Error scraping {opp_type}: {str(e)}")
            return opportunities
    
    def _scrape_opportunity_cards(self, opp_type: str) -> List[JobListing]:
        """Scrape opportunity cards from current page"""
        opportunities = []
        
        try:
            # Wait for opportunity cards to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['job_cards']))
            )
            
            cards = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['job_cards'])
            logger.debug(f"Found {len(cards)} opportunity cards")
            
            for card in cards:
                try:
                    opportunity = self._extract_opportunity_data(card, opp_type)
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.debug(f"Error extracting opportunity data: {str(e)}")
                    continue
            
            return opportunities
            
        except TimeoutException:
            logger.warning("Timeout waiting for opportunity cards to load")
            return []
        except Exception as e:
            logger.error(f"Error scraping opportunity cards: {str(e)}")
            return []

    def _extract_opportunity_data(self, card, opp_type: str) -> Optional[JobListing]:
        """Extract opportunity data from a card"""
        try:
            # Extract title
            title_element = card.find_element(By.CSS_SELECTOR, self.selectors['job_title'])
            title = title_element.text.strip()

            # Get URL
            try:
                url = title_element.get_attribute('href')
                if url and not url.startswith('http'):
                    url = f"{self.base_url}{url}"
            except:
                url = ""

            # Extract company/organizer
            try:
                company_element = card.find_element(By.CSS_SELECTOR, self.selectors['company_name'])
                company = company_element.text.strip()
            except NoSuchElementException:
                company = "Not specified"

            # Extract location
            try:
                location_element = card.find_element(By.CSS_SELECTOR, self.selectors['location'])
                location = location_element.text.strip()
            except NoSuchElementException:
                location = "Online" if opp_type in ["competitions", "hackathons"] else "Not specified"

            # Extract posted date/deadline
            try:
                date_element = card.find_element(By.CSS_SELECTOR, self.selectors['posted_date'])
                posted_date = self._parse_date(date_element.text.strip())
            except NoSuchElementException:
                posted_date = "Not specified"

            # Extract salary/prize
            try:
                salary_element = card.find_element(By.CSS_SELECTOR, self.selectors['salary'])
                salary = salary_element.text.strip()
            except NoSuchElementException:
                salary = "Not specified"

            # Extract type
            try:
                type_element = card.find_element(By.CSS_SELECTOR, self.selectors['job_type'])
                job_type = type_element.text.strip()
            except NoSuchElementException:
                job_type = opp_type.title()

            # Check for easy apply/register
            easy_apply = False
            try:
                apply_button = card.find_element(By.CSS_SELECTOR, self.selectors['apply_button'])
                easy_apply = apply_button.is_displayed()
            except NoSuchElementException:
                pass

            # Get opportunity ID from URL
            opp_id = self._extract_opportunity_id(url)

            # Create job listing
            opportunity = JobListing(
                title=title,
                company=company,
                location=location,
                description="",  # Will be filled by detailed scraping if needed
                url=url,
                posted_date=posted_date,
                platform="unstop",
                job_type=job_type,
                salary=salary,
                job_id=opp_id,
                easy_apply=easy_apply,
                apply_url=url
            )

            return opportunity

        except Exception as e:
            logger.debug(f"Error extracting opportunity data from card: {str(e)}")
            return None

    def _parse_date(self, date_text: str) -> str:
        """Parse date from various formats"""
        try:
            # Common patterns in Unstop
            if 'deadline' in date_text.lower():
                return date_text
            elif 'ends' in date_text.lower():
                return date_text
            elif 'ago' in date_text.lower():
                return date_text
            else:
                return date_text
        except:
            return "Not specified"

    def _extract_opportunity_id(self, url: str) -> str:
        """Extract opportunity ID from URL"""
        try:
            if url:
                # Unstop URLs typically have format: /opportunities/job-title-123456
                parts = url.split('/')
                if len(parts) > 2:
                    # Look for numeric ID
                    for part in reversed(parts):
                        numbers = re.findall(r'\d+', part)
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

    def get_opportunity_details(self, opportunity_url: str) -> Dict[str, Any]:
        """
        Get detailed opportunity information from opportunity page

        Args:
            opportunity_url: URL of the opportunity

        Returns:
            Dictionary with detailed opportunity information
        """
        if not self.driver:
            self.initialize_driver()

        try:
            logger.debug(f"Getting opportunity details from: {opportunity_url}")

            # Navigate to opportunity page
            self.driver.get(opportunity_url)
            self.human_delay(2, 4)

            details = {}

            # Extract detailed description
            try:
                desc_selectors = [
                    '.opportunity-description',
                    '.job-description',
                    '.description',
                    '.details'
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

            # Extract requirements/eligibility
            try:
                req_selectors = [
                    '.requirements',
                    '.eligibility',
                    '.criteria'
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

            # Extract prizes/benefits
            try:
                benefits_selectors = [
                    '.prizes',
                    '.benefits',
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
            logger.error(f"Error getting opportunity details: {str(e)}")
            return {}

    def close(self) -> None:
        """Close the scraper and browser"""
        if self.browser_manager:
            self.browser_manager.close_driver()
        logger.info("Unstop scraper closed")
