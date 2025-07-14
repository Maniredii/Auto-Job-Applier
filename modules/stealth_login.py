# Author: Enhanced by AI Assistant
# Stealth LinkedIn Login Module
# Military-grade stealth login to avoid bot detection

import time
import random
import re
from typing import Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from modules.helpers import print_lg

class StealthLinkedInLogin:
    """
    Advanced stealth login system for LinkedIn with human-like behavior.
    Designed to completely bypass bot detection systems.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.actions = ActionChains(driver)
        
        # Human behavior patterns
        self.typing_delays = {
            'fast': (0.05, 0.12),
            'normal': (0.08, 0.18),
            'slow': (0.15, 0.25),
            'hesitant': (0.2, 0.4)
        }
        
        # Login attempt tracking
        self.login_attempts = 0
        self.max_attempts = 3
    
    def perform_stealth_login(self, username: str, password: str) -> bool:
        """
        Perform stealth login with maximum human-like behavior.
        """
        print_lg("🔐 Starting stealth LinkedIn login...")
        
        try:
            # Step 1: Navigate to LinkedIn with human-like behavior
            if not self._navigate_to_linkedin():
                return False
            
            # Step 2: Handle any initial popups or overlays
            self._handle_initial_popups()
            
            # Step 3: Locate and interact with login form
            if not self._locate_login_form():
                return False
            
            # Step 4: Perform human-like login
            if not self._perform_human_login(username, password):
                return False
            
            # Step 5: Handle post-login verification
            return self._handle_post_login_verification()
            
        except Exception as e:
            print_lg(f"❌ Stealth login failed: {e}")
            return False
    
    def _navigate_to_linkedin(self) -> bool:
        """Navigate to LinkedIn with stealth behavior."""
        print_lg("🌐 Navigating to LinkedIn...")
        
        try:
            # Simulate human navigation pattern
            self.driver.get("https://www.linkedin.com")
            
            # Random delay to simulate reading
            self._human_delay(2, 4)
            
            # Simulate mouse movement
            self._simulate_mouse_movement()
            
            # Check if we're already logged in
            if self._check_if_logged_in():
                print_lg("✅ Already logged in to LinkedIn")
                return True
            
            # Look for login button or form
            login_elements = [
                "//a[contains(@href, '/login')]",
                "//button[contains(text(), 'Sign in')]",
                "//a[contains(text(), 'Sign in')]",
                "//*[@id='session_key']",  # Direct login form
            ]
            
            for xpath in login_elements:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element.is_displayed():
                        if 'session_key' not in xpath:  # If it's a login link/button
                            self._human_click(element)
                            self._human_delay(2, 3)
                        break
                except NoSuchElementException:
                    continue
            
            return True
            
        except Exception as e:
            print_lg(f"❌ Navigation failed: {e}")
            return False
    
    def _handle_initial_popups(self):
        """Handle any initial popups or overlays."""
        print_lg("🔍 Checking for popups...")
        
        # Common popup selectors
        popup_selectors = [
            "//button[contains(@aria-label, 'Dismiss')]",
            "//button[contains(text(), 'Not now')]",
            "//button[contains(text(), 'Skip')]",
            "//button[contains(@class, 'modal-wormhole-close')]",
            "//*[@data-test-modal-close-btn]",
            "//button[@aria-label='Close']"
        ]
        
        for selector in popup_selectors:
            try:
                popup = self.driver.find_element(By.XPATH, selector)
                if popup.is_displayed():
                    self._human_click(popup)
                    self._human_delay(1, 2)
                    print_lg("✅ Dismissed popup")
            except NoSuchElementException:
                continue
    
    def _locate_login_form(self) -> bool:
        """Locate the login form with multiple strategies."""
        print_lg("🔍 Locating login form...")
        
        # Multiple strategies to find login form
        strategies = [
            # Strategy 1: Direct form elements
            lambda: self.driver.find_element(By.ID, "session_key"),
            lambda: self.driver.find_element(By.ID, "session_password"),
            
            # Strategy 2: Name attributes
            lambda: self.driver.find_element(By.NAME, "session_key"),
            lambda: self.driver.find_element(By.NAME, "session_password"),
            
            # Strategy 3: XPath with text
            lambda: self.driver.find_element(By.XPATH, "//input[@placeholder='Email or phone']"),
            lambda: self.driver.find_element(By.XPATH, "//input[@type='password']"),
            
            # Strategy 4: Class-based
            lambda: self.driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username']"),
            lambda: self.driver.find_element(By.CSS_SELECTOR, "input[autocomplete='current-password']"),
        ]
        
        for strategy in strategies:
            try:
                element = strategy()
                if element.is_displayed():
                    print_lg("✅ Login form located")
                    return True
            except NoSuchElementException:
                continue
        
        # If direct form not found, try to navigate to login page
        try:
            self.driver.get("https://www.linkedin.com/login")
            self._human_delay(2, 3)
            
            # Check again after navigation
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            if username_field:
                print_lg("✅ Login form located after navigation")
                return True
                
        except TimeoutException:
            print_lg("❌ Could not locate login form")
            return False
        
        return False
    
    def _perform_human_login(self, username: str, password: str) -> bool:
        """Perform human-like login with realistic typing patterns."""
        print_lg("⌨️ Performing human-like login...")
        
        try:
            # Find username field with multiple selectors
            username_selectors = [
                (By.ID, "session_key"),
                (By.ID, "username"),
                (By.NAME, "session_key"),
                (By.CSS_SELECTOR, "input[autocomplete='username']"),
                (By.XPATH, "//input[@placeholder='Email or phone']")
            ]
            
            username_field = None
            for selector_type, selector_value in username_selectors:
                try:
                    username_field = self.driver.find_element(selector_type, selector_value)
                    if username_field.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                print_lg("❌ Could not find username field")
                return False
            
            # Human-like interaction with username field
            self._human_click(username_field)
            self._human_delay(0.5, 1.0)
            
            # Clear field with human-like behavior
            username_field.clear()
            self._human_delay(0.3, 0.6)
            
            # Type username with human-like delays
            self._human_type(username_field, username)
            
            # Find password field
            password_selectors = [
                (By.ID, "session_password"),
                (By.ID, "password"),
                (By.NAME, "session_password"),
                (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            password_field = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = self.driver.find_element(selector_type, selector_value)
                    if password_field.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                print_lg("❌ Could not find password field")
                return False
            
            # Human-like interaction with password field
            self._human_click(password_field)
            self._human_delay(0.5, 1.0)
            
            # Clear and type password
            password_field.clear()
            self._human_delay(0.3, 0.6)
            self._human_type(password_field, password)
            
            # Random delay before submitting
            self._human_delay(1, 2)
            
            # Find and click submit button
            submit_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.CSS_SELECTOR, "button[data-litms-control-urn]"),
                (By.CLASS_NAME, "sign-in-form__submit-button")
            ]
            
            submit_button = None
            for selector_type, selector_value in submit_selectors:
                try:
                    submit_button = self.driver.find_element(selector_type, selector_value)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                self._human_click(submit_button)
            else:
                # Fallback: Press Enter on password field
                password_field.send_keys(Keys.RETURN)
            
            print_lg("✅ Login form submitted")
            return True
            
        except Exception as e:
            print_lg(f"❌ Login interaction failed: {e}")
            return False
    
    def _handle_post_login_verification(self) -> bool:
        """Handle post-login verification and challenges."""
        print_lg("🔍 Handling post-login verification...")
        
        # Wait for page to load
        self._human_delay(3, 5)
        
        # Check for various post-login scenarios
        current_url = self.driver.current_url
        
        # Success indicators
        success_indicators = [
            "/feed/",
            "/in/",
            "linkedin.com/feed",
            "linkedin.com/in/"
        ]
        
        if any(indicator in current_url for indicator in success_indicators):
            print_lg("✅ Login successful - redirected to feed")
            return True
        
        # Check for challenge/verification pages
        challenge_indicators = [
            "challenge",
            "checkpoint",
            "verify",
            "security"
        ]
        
        if any(indicator in current_url for indicator in challenge_indicators):
            print_lg("⚠️ Security challenge detected")
            return self._handle_security_challenge()
        
        # Check for error messages
        error_selectors = [
            "//div[contains(@class, 'alert--error')]",
            "//div[contains(text(), 'incorrect')]",
            "//div[contains(text(), 'error')]"
        ]
        
        for selector in error_selectors:
            try:
                error_element = self.driver.find_element(By.XPATH, selector)
                if error_element.is_displayed():
                    error_text = error_element.text
                    print_lg(f"❌ Login error: {error_text}")
                    return False
            except NoSuchElementException:
                continue
        
        # Check if we're still on login page
        if "login" in current_url:
            print_lg("⚠️ Still on login page, checking for issues...")
            self._human_delay(2, 3)
            
            # Try to detect if login was successful but page didn't redirect
            if self._check_if_logged_in():
                print_lg("✅ Login successful (detected via elements)")
                return True
            else:
                print_lg("❌ Login appears to have failed")
                return False
        
        # Default success if no errors detected
        print_lg("✅ Login appears successful")
        return True
    
    def _handle_security_challenge(self) -> bool:
        """Handle LinkedIn security challenges."""
        print_lg("🛡️ Handling security challenge...")
        
        # Look for phone verification
        phone_selectors = [
            "//input[@type='tel']",
            "//input[contains(@placeholder, 'phone')]",
            "//input[contains(@name, 'phone')]"
        ]
        
        for selector in phone_selectors:
            try:
                phone_field = self.driver.find_element(By.XPATH, selector)
                if phone_field.is_displayed():
                    print_lg("📱 Phone verification required")
                    # Note: In a real scenario, you'd need to handle SMS verification
                    print_lg("⚠️ Manual intervention required for phone verification")
                    return False
            except NoSuchElementException:
                continue
        
        # Look for email verification
        email_selectors = [
            "//input[@type='email']",
            "//input[contains(@placeholder, 'email')]"
        ]
        
        for selector in email_selectors:
            try:
                email_field = self.driver.find_element(By.XPATH, selector)
                if email_field.is_displayed():
                    print_lg("📧 Email verification required")
                    print_lg("⚠️ Manual intervention required for email verification")
                    return False
            except NoSuchElementException:
                continue
        
        # Look for CAPTCHA
        captcha_selectors = [
            "//iframe[contains(@src, 'recaptcha')]",
            "//*[contains(@class, 'captcha')]",
            "//*[contains(text(), 'verify you are human')]"
        ]
        
        for selector in captcha_selectors:
            try:
                captcha_element = self.driver.find_element(By.XPATH, selector)
                if captcha_element.is_displayed():
                    print_lg("🤖 CAPTCHA detected")
                    print_lg("⚠️ Manual intervention required for CAPTCHA")
                    return False
            except NoSuchElementException:
                continue
        
        return True
    
    def _check_if_logged_in(self) -> bool:
        """Check if already logged in to LinkedIn."""
        logged_in_indicators = [
            "//button[contains(@aria-label, 'View profile')]",
            "//a[contains(@href, '/in/')]",
            "//*[@data-control-name='nav.settings_and_privacy']",
            "//span[contains(text(), 'Me')]",
            "//*[contains(@class, 'global-nav__me')]"
        ]
        
        for selector in logged_in_indicators:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    
    def _human_click(self, element):
        """Perform human-like clicking."""
        # Move to element first
        self.actions.move_to_element(element).perform()
        self._human_delay(0.1, 0.3)
        
        # Random click offset
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        
        self.actions.move_to_element_with_offset(element, offset_x, offset_y).click().perform()
    
    def _human_type(self, element, text: str, typing_style: str = 'normal'):
        """Type text with human-like delays and patterns."""
        delays = self.typing_delays[typing_style]
        
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Variable typing speed
            delay = random.uniform(delays[0], delays[1])
            
            # Occasional longer pauses (thinking)
            if random.random() < 0.1:
                delay += random.uniform(0.3, 0.8)
            
            # Slight pause after numbers or special characters
            if char.isdigit() or char in "!@#$%^&*()":
                delay += random.uniform(0.1, 0.2)
            
            time.sleep(delay)
    
    def _human_delay(self, min_seconds: float, max_seconds: float):
        """Human-like delay with natural variation."""
        delay = random.normalvariate((min_seconds + max_seconds) / 2, (max_seconds - min_seconds) / 6)
        delay = max(min_seconds, min(max_seconds, delay))
        time.sleep(delay)
    
    def _simulate_mouse_movement(self):
        """Simulate natural mouse movements."""
        try:
            # Get viewport size
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Random mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, viewport_width - 100)
                y = random.randint(100, viewport_height - 100)
                
                self.actions.move_by_offset(x - viewport_width//2, y - viewport_height//2).perform()
                self._human_delay(0.2, 0.5)
                
        except Exception:
            # Fallback simple movement
            self.actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50)).perform()

def perform_stealth_linkedin_login(driver: WebDriver, username: str, password: str) -> bool:
    """
    Main function to perform stealth LinkedIn login.
    """
    stealth_login = StealthLinkedInLogin(driver)
    return stealth_login.perform_stealth_login(username, password)
