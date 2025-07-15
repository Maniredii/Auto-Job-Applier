"""
Browser Manager with Advanced Anti-Detection Features
"""

import os
import random
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

from config import config

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages browser instances with anti-detection features"""
    
    def __init__(self):
        """Initialize browser manager"""
        self.driver = None
        self.profile_path = Path(config.BROWSER_PROFILE_PATH)
        self.profile_path.mkdir(exist_ok=True)
        
        # User agent manager
        self.ua = UserAgent()
        
        # Browser fingerprint randomization
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (1280, 720), (1600, 900), (1024, 768), (1280, 1024)
        ]
        
        # Timezone options
        self.timezones = [
            "America/New_York", "America/Los_Angeles", "America/Chicago",
            "Europe/London", "Europe/Berlin", "Asia/Tokyo"
        ]
    
    def create_stealth_driver(
        self, 
        headless: bool = None,
        profile_name: str = "default",
        proxy: Optional[str] = None
    ) -> uc.Chrome:
        """
        Create undetected Chrome driver with stealth features
        
        Args:
            headless: Run in headless mode
            profile_name: Browser profile name
            proxy: Proxy server (format: host:port)
            
        Returns:
            Undetected Chrome driver instance
        """
        if headless is None:
            headless = config.HEADLESS_MODE
        
        logger.info(f"Creating stealth browser (headless={headless}, profile={profile_name})")
        
        # Chrome options
        options = uc.ChromeOptions()
        
        # Basic stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions-file-access-check")
        options.add_argument("--disable-extensions-http-throttling")
        options.add_argument("--disable-extensions-except")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-preconnect")
        
        # Anti-detection measures
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)
        
        # Disable logging
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        
        # Performance optimizations
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        
        # Memory optimizations
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=4096")
        
        # Set user agent
        if config.ENABLE_STEALTH_MODE:
            user_agent = self.ua.random
            options.add_argument(f"--user-agent={user_agent}")
            logger.debug(f"Using user agent: {user_agent}")
        
        # Set random screen resolution
        if config.ENABLE_STEALTH_MODE:
            width, height = random.choice(self.screen_resolutions)
            options.add_argument(f"--window-size={width},{height}")
            logger.debug(f"Using screen resolution: {width}x{height}")
        
        # Browser profile
        profile_dir = self.profile_path / profile_name
        profile_dir.mkdir(exist_ok=True)
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        # Proxy configuration
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
            logger.info(f"Using proxy: {proxy}")
        
        # Language and locale
        options.add_argument("--lang=en-US")
        options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-US,en;q=0.9',
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
            'profile.managed_default_content_settings.images': 2  # Block images for faster loading
        })
        
        # Headless mode
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        
        try:
            # Create undetected Chrome driver
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                driver_executable_path=None,  # Auto-download driver
                browser_executable_path=None,  # Use system Chrome
            )
            
            # Additional stealth measures
            if config.ENABLE_STEALTH_MODE:
                self._apply_stealth_scripts(driver)
            
            # Set timeouts
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            
            logger.info("Stealth browser created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create stealth browser: {str(e)}")
            raise
    
    def _apply_stealth_scripts(self, driver: uc.Chrome) -> None:
        """
        Apply additional stealth JavaScript modifications
        
        Args:
            driver: Chrome driver instance
        """
        stealth_scripts = [
            # Remove webdriver property
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """,
            
            # Randomize navigator properties
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            """,
            
            # Mock plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Mock chrome runtime
            """
            if (!window.chrome) {
                window.chrome = {};
            }
            if (!window.chrome.runtime) {
                window.chrome.runtime = {};
            }
            """,
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': script
                })
            except Exception as e:
                logger.debug(f"Failed to apply stealth script: {str(e)}")
    
    def setup_browser_fingerprint(self, driver: uc.Chrome) -> None:
        """
        Setup browser fingerprint randomization
        
        Args:
            driver: Chrome driver instance
        """
        if not config.ENABLE_STEALTH_MODE:
            return
        
        try:
            # Randomize timezone
            timezone = random.choice(self.timezones)
            driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                'timezoneId': timezone
            })
            logger.debug(f"Set timezone: {timezone}")
            
            # Randomize geolocation
            latitude = random.uniform(25.0, 49.0)  # US latitude range
            longitude = random.uniform(-125.0, -66.0)  # US longitude range
            
            driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
                'latitude': latitude,
                'longitude': longitude,
                'accuracy': 100
            })
            logger.debug(f"Set geolocation: {latitude}, {longitude}")
            
        except Exception as e:
            logger.debug(f"Failed to setup browser fingerprint: {str(e)}")
    
    def get_driver(
        self, 
        headless: bool = None,
        profile_name: str = "default",
        proxy: Optional[str] = None
    ) -> uc.Chrome:
        """
        Get or create browser driver instance
        
        Args:
            headless: Run in headless mode
            profile_name: Browser profile name
            proxy: Proxy server
            
        Returns:
            Chrome driver instance
        """
        if self.driver is None:
            self.driver = self.create_stealth_driver(headless, profile_name, proxy)
            self.setup_browser_fingerprint(self.driver)
        
        return self.driver
    
    def close_driver(self) -> None:
        """Close browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")
            finally:
                self.driver = None
    
    def restart_driver(
        self, 
        headless: bool = None,
        profile_name: str = "default",
        proxy: Optional[str] = None
    ) -> uc.Chrome:
        """
        Restart browser driver with new settings
        
        Args:
            headless: Run in headless mode
            profile_name: Browser profile name
            proxy: Proxy server
            
        Returns:
            New Chrome driver instance
        """
        self.close_driver()
        return self.get_driver(headless, profile_name, proxy)
    
    def clear_profile(self, profile_name: str = "default") -> None:
        """
        Clear browser profile data
        
        Args:
            profile_name: Profile name to clear
        """
        profile_dir = self.profile_path / profile_name
        if profile_dir.exists():
            import shutil
            try:
                shutil.rmtree(profile_dir)
                logger.info(f"Cleared profile: {profile_name}")
            except Exception as e:
                logger.error(f"Failed to clear profile {profile_name}: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        return self.get_driver()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()
