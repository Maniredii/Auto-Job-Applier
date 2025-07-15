"""
Base Scraper Class with Anti-Detection Features
"""

import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Data class for job listing information"""
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: str
    job_type: str = ""
    experience_level: str = ""
    salary: str = ""
    skills: List[str] = None
    scraped_at: str = ""
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if not self.scraped_at:
            self.scraped_at = time.strftime("%Y-%m-%d %H:%M:%S")

class BaseScraper(ABC):
    """Base class for job scrapers with anti-detection features"""
    
    def __init__(self, driver=None):
        """
        Initialize base scraper
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) if driver else None
        self.actions = ActionChains(driver) if driver else None
        
        # Anti-detection settings
        self.min_delay = 2
        self.max_delay = 5
        self.typing_delay = 0.1
        self.scroll_delay = 1
        
        # User agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    def human_delay(self, min_seconds: float = None, max_seconds: float = None) -> None:
        """
        Add human-like delay between actions
        
        Args:
            min_seconds: Minimum delay time
            max_seconds: Maximum delay time
        """
        min_delay = min_seconds or self.min_delay
        max_delay = max_seconds or self.max_delay
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Human delay: {delay:.2f} seconds")
        time.sleep(delay)
    
    def human_type(self, element, text: str, clear_first: bool = True) -> None:
        """
        Type text with human-like timing
        
        Args:
            element: WebElement to type into
            text: Text to type
            clear_first: Whether to clear element first
        """
        if clear_first:
            element.clear()
            time.sleep(0.5)
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, self.typing_delay))
    
    def human_scroll(self, pixels: int = None) -> None:
        """
        Scroll page with human-like behavior
        
        Args:
            pixels: Number of pixels to scroll (random if None)
        """
        if pixels is None:
            pixels = random.randint(300, 800)
        
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(random.uniform(0.5, self.scroll_delay))
    
    def random_mouse_movement(self) -> None:
        """Perform random mouse movements to appear human"""
        try:
            # Get random element to move to
            elements = self.driver.find_elements(By.TAG_NAME, "div")
            if elements:
                random_element = random.choice(elements[:10])  # Choose from first 10 elements
                self.actions.move_to_element(random_element).perform()
                time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            logger.debug(f"Random mouse movement failed: {str(e)}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """
        Wait for element with timeout
        
        Args:
            by: Selenium By locator
            value: Locator value
            timeout: Timeout in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        """
        Wait for element to be clickable
        
        Args:
            by: Selenium By locator
            value: Locator value
            timeout: Timeout in seconds
            
        Returns:
            WebElement if clickable, None otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable((by, value)))
        except TimeoutException:
            logger.warning(f"Element not clickable: {by}={value}")
            return None
    
    def safe_click(self, element) -> bool:
        """
        Safely click element with retry logic
        
        Args:
            element: WebElement to click
            
        Returns:
            True if successful, False otherwise
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # Try regular click first
                element.click()
                return True
                
            except Exception as e:
                logger.debug(f"Click attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    try:
                        # Try JavaScript click as fallback
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    except Exception:
                        continue
        
        logger.warning("All click attempts failed")
        return False
    
    def get_text_safe(self, element) -> str:
        """
        Safely get text from element
        
        Args:
            element: WebElement
            
        Returns:
            Element text or empty string
        """
        try:
            return element.text.strip()
        except Exception as e:
            logger.debug(f"Failed to get text: {str(e)}")
            return ""
    
    def get_attribute_safe(self, element, attribute: str) -> str:
        """
        Safely get attribute from element
        
        Args:
            element: WebElement
            attribute: Attribute name
            
        Returns:
            Attribute value or empty string
        """
        try:
            return element.get_attribute(attribute) or ""
        except Exception as e:
            logger.debug(f"Failed to get attribute {attribute}: {str(e)}")
            return ""
    
    def check_for_captcha(self) -> bool:
        """
        Check if CAPTCHA is present on page
        
        Returns:
            True if CAPTCHA detected, False otherwise
        """
        captcha_indicators = [
            "captcha",
            "recaptcha",
            "challenge",
            "verify",
            "robot",
            "security check"
        ]
        
        page_source = self.driver.page_source.lower()
        for indicator in captcha_indicators:
            if indicator in page_source:
                logger.warning(f"CAPTCHA detected: {indicator}")
                return True
        
        return False
    
    def check_for_rate_limit(self) -> bool:
        """
        Check if rate limited or blocked
        
        Returns:
            True if rate limited, False otherwise
        """
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "temporarily blocked",
            "access denied",
            "suspicious activity"
        ]
        
        page_source = self.driver.page_source.lower()
        for indicator in rate_limit_indicators:
            if indicator in page_source:
                logger.warning(f"Rate limit detected: {indicator}")
                return True
        
        return False
    
    def handle_popup(self) -> bool:
        """
        Handle common popups (cookies, notifications, etc.)
        
        Returns:
            True if popup was handled, False otherwise
        """
        popup_selectors = [
            # Cookie consent
            "button[id*='accept']",
            "button[class*='accept']",
            "button[class*='cookie']",
            ".cookie-consent button",
            
            # Notification popups
            "button[aria-label*='dismiss']",
            "button[aria-label*='close']",
            ".modal button[class*='close']",
            
            # LinkedIn specific
            ".msg-overlay__dismiss-btn",
            ".artdeco-modal__dismiss",
            ".notification-banner__dismiss"
        ]
        
        for selector in popup_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        self.safe_click(element)
                        logger.debug(f"Dismissed popup: {selector}")
                        time.sleep(1)
                        return True
            except Exception as e:
                logger.debug(f"Popup handling failed for {selector}: {str(e)}")
                continue
        
        return False
    
    @abstractmethod
    def scrape_jobs(self, **kwargs) -> List[JobListing]:
        """
        Abstract method for scraping jobs
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        """
        Abstract method for login
        Must be implemented by subclasses
        """
        pass
