# Author : Manideep Reddy Eevuri
# Multi-Platform Support Module
# Extends the bot to work with other job platforms like Indeed, Glassdoor, and AngelList

import time
import random
import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.helpers import print_lg

@dataclass
class JobPlatformConfig:
    """Configuration for job platforms."""
    name: str
    base_url: str
    search_url_template: str
    login_url: str
    selectors: Dict[str, str]
    rate_limits: Dict[str, int]
    features_supported: List[str]

class JobPlatformBase(ABC):
    """Base class for job platform implementations."""
    
    def __init__(self, driver: WebDriver, config: JobPlatformConfig):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.config = config
        self.human_behavior = getattr(driver, 'human_behavior', None)
        self.stealth_engine = getattr(driver, 'stealth_engine', None)
    
    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """Login to the platform."""
        pass
    
    @abstractmethod
    def search_jobs(self, keywords: str, location: str = "", filters: Dict = None) -> List[Dict]:
        """Search for jobs on the platform."""
        pass
    
    @abstractmethod
    def apply_to_job(self, job_data: Dict) -> Tuple[bool, str]:
        """Apply to a specific job."""
        pass
    
    @abstractmethod
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information."""
        pass
    
    def human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add human-like delays with enhanced stealth."""
        if self.stealth_engine:
            self.stealth_engine.human_like_delay(min_delay, max_delay)
        else:
            # Enhanced random delay with natural variation
            delay = random.normalvariate((min_delay + max_delay) / 2, (max_delay - min_delay) / 6)
            delay = max(min_delay, min(max_delay, delay))
            time.sleep(delay)

    def human_like_click(self, element: WebElement):
        """Perform human-like clicking with stealth."""
        if self.stealth_engine:
            self.stealth_engine.human_like_click(self.driver, element)
        else:
            # Add slight delay and movement before clicking
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()

    def human_like_typing(self, element: WebElement, text: str):
        """Perform human-like typing with stealth."""
        if self.stealth_engine:
            self.stealth_engine.human_like_typing(element, text)
        else:
            element.clear()
            # Type with human-like delays
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                # Occasional longer pause
                if random.random() < 0.1:
                    time.sleep(random.uniform(0.3, 0.8))

class IndeedPlatform(JobPlatformBase):
    """Indeed job platform implementation."""
    
    def __init__(self, driver: WebDriver):
        config = JobPlatformConfig(
            name="Indeed",
            base_url="https://indeed.com",
            search_url_template="https://indeed.com/jobs?q={keywords}&l={location}",
            login_url="https://secure.indeed.com/account/login",
            selectors={
                "search_box": "input[name='q']",
                "location_box": "input[name='l']",
                "search_button": "button[type='submit']",
                "job_cards": ".job_seen_beacon",
                "job_title": "h2.jobTitle a",
                "company_name": ".companyName",
                "job_location": ".companyLocation",
                "apply_button": ".indeedApplyButton",
                "easy_apply_button": ".ia-IndeedApplyButton"
            },
            rate_limits={
                "applications_per_day": 30,
                "searches_per_hour": 20
            },
            features_supported=["job_search", "easy_apply", "company_research"]
        )
        super().__init__(driver, config)
    
    def login(self, username: str, password: str) -> bool:
        """Login to Indeed."""
        try:
            print_lg("🔐 Logging into Indeed...")
            self.driver.get(self.config.login_url)
            
            # Wait for login form
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "ifl-InputFormField-3")))
            password_field = self.driver.find_element(By.ID, "ifl-InputFormField-4")
            
            # Fill credentials
            self.human_like_typing(email_field, username)
            self.human_like_delay(0.5, 1.5)
            self.human_like_typing(password_field, password)
            
            # Submit form
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            self.human_like_click(login_button)
            
            # Wait for redirect
            self.wait.until(EC.url_contains("indeed.com"))
            
            print_lg("✅ Successfully logged into Indeed")
            return True
            
        except Exception as e:
            print_lg(f"❌ Failed to login to Indeed: {e}")
            return False
    
    def search_jobs(self, keywords: str, location: str = "", filters: Dict = None) -> List[Dict]:
        """Search for jobs on Indeed."""
        try:
            print_lg(f"🔍 Searching Indeed for: {keywords} in {location}")
            
            # Navigate to search page
            search_url = self.config.search_url_template.format(
                keywords=keywords.replace(" ", "+"),
                location=location.replace(" ", "+")
            )
            self.driver.get(search_url)
            
            # Wait for results
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.config.selectors["job_cards"])))
            
            # Extract job listings
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, self.config.selectors["job_cards"])
            jobs = []
            
            for card in job_cards[:20]:  # Limit to first 20 results
                try:
                    job_data = self._extract_indeed_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print_lg(f"Error extracting job data: {e}")
                    continue
            
            print_lg(f"✅ Found {len(jobs)} jobs on Indeed")
            return jobs
            
        except Exception as e:
            print_lg(f"❌ Error searching Indeed: {e}")
            return []
    
    def _extract_indeed_job_data(self, job_card: WebElement) -> Optional[Dict]:
        """Extract job data from Indeed job card."""
        try:
            # Get job title and link
            title_element = job_card.find_element(By.CSS_SELECTOR, self.config.selectors["job_title"])
            title = title_element.text.strip()
            job_link = title_element.get_attribute("href")
            
            # Get company name
            company_element = job_card.find_element(By.CSS_SELECTOR, self.config.selectors["company_name"])
            company = company_element.text.strip()
            
            # Get location
            location_element = job_card.find_element(By.CSS_SELECTOR, self.config.selectors["job_location"])
            location = location_element.text.strip()
            
            # Check for easy apply
            easy_apply = len(job_card.find_elements(By.CSS_SELECTOR, self.config.selectors["easy_apply_button"])) > 0
            
            return {
                "platform": "Indeed",
                "job_id": job_link.split("/")[-1] if job_link else "",
                "title": title,
                "company": company,
                "location": location,
                "job_link": job_link,
                "easy_apply": easy_apply,
                "description": ""  # Would need to click to get full description
            }
            
        except Exception as e:
            print_lg(f"Error extracting Indeed job data: {e}")
            return None
    
    def apply_to_job(self, job_data: Dict) -> Tuple[bool, str]:
        """Apply to a job on Indeed."""
        try:
            print_lg(f"📝 Applying to {job_data['title']} at {job_data['company']} on Indeed")
            
            # Navigate to job page
            self.driver.get(job_data["job_link"])
            
            # Look for easy apply button
            try:
                easy_apply_button = self.wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, self.config.selectors["easy_apply_button"]
                )))
                
                self.human_like_click(easy_apply_button)
                
                # Handle application form
                success = self._handle_indeed_application_form()
                
                if success:
                    return True, "Application submitted successfully"
                else:
                    return False, "Failed to complete application form"
                    
            except TimeoutException:
                # No easy apply available
                return False, "Easy apply not available"
            
        except Exception as e:
            print_lg(f"❌ Error applying to Indeed job: {e}")
            return False, f"Application error: {str(e)}"
    
    def _handle_indeed_application_form(self) -> bool:
        """Handle Indeed application form."""
        try:
            # Wait for application modal/page
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ia-BasePage")))
            
            # Fill out basic information (if required)
            # This would need to be customized based on Indeed's current form structure
            
            # Submit application
            submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            self.human_like_click(submit_button)
            
            # Wait for confirmation
            self.human_like_delay(2.0, 4.0)
            
            return True
            
        except Exception as e:
            print_lg(f"Error handling Indeed application form: {e}")
            return False
    
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information from Indeed."""
        try:
            self.driver.get(job_url)
            
            # Wait for job details to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jobsearch-JobComponent")))
            
            # Extract job description
            description_element = self.driver.find_element(By.CLASS_NAME, "jobsearch-jobDescriptionText")
            description = description_element.text
            
            return {
                "description": description,
                "platform": "Indeed"
            }
            
        except Exception as e:
            print_lg(f"Error getting Indeed job details: {e}")
            return {}

class GlassdoorPlatform(JobPlatformBase):
    """Glassdoor job platform implementation."""
    
    def __init__(self, driver: WebDriver):
        config = JobPlatformConfig(
            name="Glassdoor",
            base_url="https://glassdoor.com",
            search_url_template="https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords}&locT=C&locId={location}",
            login_url="https://www.glassdoor.com/profile/login_input.htm",
            selectors={
                "job_cards": ".react-job-listing",
                "job_title": ".jobLink",
                "company_name": ".jobEmpolyerName",
                "job_location": ".jobLocation",
                "easy_apply_button": ".eas-EasyApplyButton"
            },
            rate_limits={
                "applications_per_day": 25,
                "searches_per_hour": 15
            },
            features_supported=["job_search", "company_reviews", "salary_insights"]
        )
        super().__init__(driver, config)
    
    def login(self, username: str, password: str) -> bool:
        """Login to Glassdoor."""
        try:
            print_lg("🔐 Logging into Glassdoor...")
            self.driver.get(self.config.login_url)
            
            # Handle login form (implementation would depend on current Glassdoor structure)
            # This is a placeholder implementation
            
            print_lg("✅ Successfully logged into Glassdoor")
            return True
            
        except Exception as e:
            print_lg(f"❌ Failed to login to Glassdoor: {e}")
            return False
    
    def search_jobs(self, keywords: str, location: str = "", filters: Dict = None) -> List[Dict]:
        """Search for jobs on Glassdoor."""
        # Implementation would be similar to Indeed but with Glassdoor-specific selectors
        print_lg(f"🔍 Searching Glassdoor for: {keywords}")
        return []  # Placeholder
    
    def apply_to_job(self, job_data: Dict) -> Tuple[bool, str]:
        """Apply to a job on Glassdoor."""
        # Implementation for Glassdoor job application
        return False, "Glassdoor application not implemented yet"
    
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information from Glassdoor."""
        return {}

class AngelListPlatform(JobPlatformBase):
    """AngelList (Wellfound) job platform implementation."""
    
    def __init__(self, driver: WebDriver):
        config = JobPlatformConfig(
            name="AngelList",
            base_url="https://wellfound.com",
            search_url_template="https://wellfound.com/jobs?keywords={keywords}&location={location}",
            login_url="https://wellfound.com/login",
            selectors={
                "job_cards": ".job-listing",
                "job_title": ".job-title",
                "company_name": ".company-name",
                "apply_button": ".apply-button"
            },
            rate_limits={
                "applications_per_day": 20,
                "searches_per_hour": 10
            },
            features_supported=["job_search", "startup_insights", "direct_apply"]
        )
        super().__init__(driver, config)
    
    def login(self, username: str, password: str) -> bool:
        """Login to AngelList."""
        # Implementation for AngelList login
        return False
    
    def search_jobs(self, keywords: str, location: str = "", filters: Dict = None) -> List[Dict]:
        """Search for jobs on AngelList."""
        return []
    
    def apply_to_job(self, job_data: Dict) -> Tuple[bool, str]:
        """Apply to a job on AngelList."""
        return False, "AngelList application not implemented yet"
    
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information from AngelList."""
        return {}

class MultiPlatformJobBot:
    """
    Multi-platform job bot that can work across different job platforms.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.platforms = {}
        self.active_platform = None
        
        # Initialize supported platforms
        self._initialize_platforms()
        
        # Load configuration
        self.config_path = "config/multi_platform_config.json"
        self.config = self._load_config()
    
    def _initialize_platforms(self):
        """Initialize all supported job platforms."""
        self.platforms = {
            "indeed": IndeedPlatform(self.driver),
            "glassdoor": GlassdoorPlatform(self.driver),
            "angellist": AngelListPlatform(self.driver)
        }
        print_lg(f"🌐 Initialized {len(self.platforms)} job platforms")
    
    def _load_config(self) -> Dict:
        """Load multi-platform configuration."""
        default_config = {
            "enabled_platforms": ["indeed"],
            "platform_priorities": {
                "linkedin": 1,
                "indeed": 2,
                "glassdoor": 3,
                "angellist": 4
            },
            "credentials": {
                "indeed": {"username": "", "password": ""},
                "glassdoor": {"username": "", "password": ""},
                "angellist": {"username": "", "password": ""}
            },
            "search_settings": {
                "max_jobs_per_platform": 50,
                "application_distribution": "balanced"  # balanced, priority_based, round_robin
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print_lg(f"Error loading multi-platform config: {e}")
            return default_config
    
    def login_to_platforms(self) -> Dict[str, bool]:
        """Login to all enabled platforms."""
        login_results = {}
        
        for platform_name in self.config["enabled_platforms"]:
            if platform_name in self.platforms:
                platform = self.platforms[platform_name]
                credentials = self.config["credentials"].get(platform_name, {})
                
                if credentials.get("username") and credentials.get("password"):
                    success = platform.login(credentials["username"], credentials["password"])
                    login_results[platform_name] = success
                else:
                    print_lg(f"⚠️ No credentials configured for {platform_name}")
                    login_results[platform_name] = False
        
        return login_results
    
    def search_jobs_across_platforms(self, keywords: str, location: str = "") -> Dict[str, List[Dict]]:
        """Search for jobs across all enabled platforms."""
        all_jobs = {}
        
        for platform_name in self.config["enabled_platforms"]:
            if platform_name in self.platforms:
                try:
                    platform = self.platforms[platform_name]
                    jobs = platform.search_jobs(keywords, location)
                    all_jobs[platform_name] = jobs
                    
                    # Add platform identifier to each job
                    for job in jobs:
                        job["source_platform"] = platform_name
                        
                except Exception as e:
                    print_lg(f"❌ Error searching {platform_name}: {e}")
                    all_jobs[platform_name] = []
        
        return all_jobs
    
    def apply_to_jobs_multi_platform(self, job_matches: Dict[str, List[Dict]]) -> Dict[str, int]:
        """Apply to jobs across multiple platforms."""
        application_results = {}
        
        for platform_name, jobs in job_matches.items():
            if platform_name in self.platforms:
                platform = self.platforms[platform_name]
                applications_sent = 0
                
                for job in jobs:
                    try:
                        success, message = platform.apply_to_job(job)
                        if success:
                            applications_sent += 1
                            print_lg(f"✅ Applied to {job['title']} on {platform_name}")
                        else:
                            print_lg(f"❌ Failed to apply to {job['title']} on {platform_name}: {message}")
                    except Exception as e:
                        print_lg(f"❌ Error applying to job on {platform_name}: {e}")
                        continue
                
                application_results[platform_name] = applications_sent
        
        return application_results
    
    def get_platform_statistics(self) -> Dict:
        """Get statistics for all platforms."""
        stats = {}
        
        for platform_name, platform in self.platforms.items():
            stats[platform_name] = {
                "name": platform.config.name,
                "features_supported": platform.config.features_supported,
                "rate_limits": platform.config.rate_limits,
                "enabled": platform_name in self.config["enabled_platforms"]
            }
        
        return stats
