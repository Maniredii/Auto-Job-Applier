# Author: Enhanced by AI Assistant
# Enhanced Job Application Module
# Integrates stealth mode, human behavior simulation, and smart application strategy

import time
import random
from typing import Dict, List, Tuple, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.helpers import print_lg, buffer
from modules.clickers_and_finders import *
from config.settings import enable_human_behavior, randomize_timing, enable_break_simulation

class EnhancedJobApplier:
    """
    Enhanced job application system with stealth mode and intelligent behavior.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # Get enhanced modules from driver
        self.stealth_engine = getattr(driver, 'stealth_engine', None)
        self.human_behavior = getattr(driver, 'human_behavior', None)
        self.application_strategy = getattr(driver, 'application_strategy', None)
        
        self.applications_this_session = 0
        self.session_start_time = time.time()
        
    def apply_to_job_enhanced(self, job_data: Dict) -> Tuple[bool, str]:
        """
        Enhanced job application with intelligent decision making and human behavior.
        """
        job_id = job_data.get('job_id', 'unknown')
        title = job_data.get('title', 'Unknown')
        company = job_data.get('company', 'Unknown')
        
        print_lg(f"🎯 Evaluating job: {title} at {company}")
        
        # Check if we should apply using smart strategy
        if self.application_strategy:
            should_apply, reason, job_score = self.application_strategy.should_apply_to_job(job_data)
            
            if not should_apply:
                print_lg(f"❌ Skipping job: {reason}")
                return False, reason
            
            print_lg(f"✅ Job approved for application: {reason}")
        
        # Check for breaks if human behavior is enabled
        if self.human_behavior and enable_break_simulation:
            should_break, break_type = self.human_behavior.should_take_break()
            if should_break:
                self.human_behavior.take_break(break_type, self.driver)
        
        # Perform stealth checks
        if self.stealth_engine:
            if not self.stealth_engine.evade_detection_check(self.driver):
                print_lg("⚠️ Potential bot detection - implementing evasion")
                self.stealth_engine.human_like_delay(5.0, 15.0)
        
        # Simulate reading the job description
        if self.human_behavior:
            job_description_length = len(job_data.get('description', ''))
            self.human_behavior.simulate_job_reading(self.driver, job_description_length)
        
        # Apply to the job with enhanced behavior
        success, message = self._perform_enhanced_application(job_data)
        
        # Record the result
        if self.application_strategy:
            result = "success" if success else "failed"
            self.application_strategy.record_application_result(job_id, result)
        
        # Update session tracking
        self.applications_this_session += 1
        
        if self.human_behavior:
            self.human_behavior.record_action()
        
        return success, message
    
    def _perform_enhanced_application(self, job_data: Dict) -> Tuple[bool, str]:
        """
        Performs the actual job application with enhanced behavior patterns.
        """
        try:
            # Click apply button with human-like behavior
            apply_button = self._find_apply_button()
            if not apply_button:
                return False, "Apply button not found"
            
            if self.stealth_engine:
                self.stealth_engine.human_like_click(self.driver, apply_button)
            else:
                apply_button.click()
            
            # Wait for application form to load
            self._wait_for_application_form()
            
            # Fill out the application form
            success = self._fill_application_form_enhanced(job_data)
            if not success:
                return False, "Failed to fill application form"
            
            # Review application before submission
            if self.human_behavior:
                self.human_behavior.simulate_application_review(self.driver)
            
            # Submit application
            success = self._submit_application_enhanced()
            if success:
                print_lg("✅ Application submitted successfully!")
                return True, "Application submitted"
            else:
                return False, "Failed to submit application"
                
        except Exception as e:
            print_lg(f"❌ Error during application: {e}")
            return False, f"Application error: {str(e)}"
    
    def _find_apply_button(self) -> Optional[WebElement]:
        """
        Finds the apply button with enhanced detection.
        """
        apply_selectors = [
            "//button[contains(@class, 'jobs-apply-button')]",
            "//button[contains(text(), 'Easy Apply')]",
            "//button[contains(text(), 'Apply')]",
            "//a[contains(@class, 'jobs-apply-button')]"
        ]
        
        for selector in apply_selectors:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                return element
            except TimeoutException:
                continue
        
        return None
    
    def _wait_for_application_form(self):
        """
        Waits for the application form to load with enhanced detection.
        """
        form_indicators = [
            (By.CLASS_NAME, "jobs-easy-apply-content"),
            (By.CLASS_NAME, "jobs-easy-apply-modal"),
            (By.XPATH, "//div[contains(@class, 'jobs-easy-apply')]"),
            (By.XPATH, "//form[contains(@class, 'jobs-easy-apply')]")
        ]
        
        for by, selector in form_indicators:
            try:
                self.wait.until(EC.presence_of_element_located((by, selector)))
                print_lg("📝 Application form loaded")
                return
            except TimeoutException:
                continue
        
        # Add human-like delay even if form detection fails
        if randomize_timing:
            time.sleep(random.uniform(1.0, 3.0))
    
    def _fill_application_form_enhanced(self, job_data: Dict) -> bool:
        """
        Fills the application form with enhanced human-like behavior.
        """
        try:
            # Find all form fields
            form_fields = self._detect_form_fields()
            
            for field_info in form_fields:
                field_element = field_info['element']
                field_type = field_info['type']
                field_name = field_info['name']
                
                # Simulate hesitation before filling
                if self.human_behavior:
                    self.human_behavior.simulate_form_filling_hesitation(field_name)
                
                # Fill the field based on type
                if field_type == 'text':
                    self._fill_text_field_enhanced(field_element, field_name)
                elif field_type == 'select':
                    self._fill_select_field_enhanced(field_element, field_name)
                elif field_type == 'radio':
                    self._fill_radio_field_enhanced(field_element, field_name)
                elif field_type == 'checkbox':
                    self._fill_checkbox_field_enhanced(field_element, field_name)
                elif field_type == 'textarea':
                    self._fill_textarea_field_enhanced(field_element, field_name)
                
                # Random delay between fields
                if randomize_timing:
                    time.sleep(random.uniform(0.5, 2.0))
            
            return True
            
        except Exception as e:
            print_lg(f"Error filling form: {e}")
            return False
    
    def _detect_form_fields(self) -> List[Dict]:
        """
        Detects all form fields in the application form.
        """
        fields = []
        
        # Text inputs
        text_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
        for input_elem in text_inputs:
            fields.append({
                'element': input_elem,
                'type': 'text',
                'name': self._get_field_name(input_elem)
            })
        
        # Select dropdowns
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for select_elem in selects:
            fields.append({
                'element': select_elem,
                'type': 'select',
                'name': self._get_field_name(select_elem)
            })
        
        # Radio buttons
        radios = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
        for radio_elem in radios:
            fields.append({
                'element': radio_elem,
                'type': 'radio',
                'name': self._get_field_name(radio_elem)
            })
        
        # Checkboxes
        checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        for checkbox_elem in checkboxes:
            fields.append({
                'element': checkbox_elem,
                'type': 'checkbox',
                'name': self._get_field_name(checkbox_elem)
            })
        
        # Textareas
        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
        for textarea_elem in textareas:
            fields.append({
                'element': textarea_elem,
                'type': 'textarea',
                'name': self._get_field_name(textarea_elem)
            })
        
        return fields
    
    def _get_field_name(self, element: WebElement) -> str:
        """
        Extracts a meaningful name for a form field.
        """
        # Try various attributes to get field name
        for attr in ['name', 'id', 'aria-label', 'placeholder']:
            value = element.get_attribute(attr)
            if value:
                return value
        
        # Try to find associated label
        try:
            field_id = element.get_attribute('id')
            if field_id:
                label = self.driver.find_element(By.XPATH, f"//label[@for='{field_id}']")
                return label.text
        except:
            pass
        
        return "unknown_field"
    
    def _fill_text_field_enhanced(self, element: WebElement, field_name: str):
        """
        Fills a text field with human-like typing.
        """
        # Determine what to fill based on field name
        value = self._get_field_value(field_name, 'text')
        
        if self.stealth_engine:
            self.stealth_engine.human_like_typing(element, value)
        else:
            element.clear()
            element.send_keys(value)
    
    def _fill_select_field_enhanced(self, element: WebElement, field_name: str):
        """
        Fills a select field with decision-making simulation.
        """
        if self.human_behavior:
            self.human_behavior.simulate_decision_making('normal')
        
        # Get appropriate value for the field
        value = self._get_field_value(field_name, 'select')
        
        # Select the option
        from selenium.webdriver.support.ui import Select
        select = Select(element)
        
        try:
            select.select_by_visible_text(value)
        except:
            # Fallback to first non-default option
            options = select.options
            if len(options) > 1:
                select.select_by_index(1)
    
    def _fill_radio_field_enhanced(self, element: WebElement, field_name: str):
        """
        Fills a radio field with decision simulation.
        """
        if self.human_behavior:
            self.human_behavior.simulate_decision_making('simple')
        
        if self.stealth_engine:
            self.stealth_engine.human_like_click(self.driver, element)
        else:
            element.click()
    
    def _fill_checkbox_field_enhanced(self, element: WebElement, field_name: str):
        """
        Fills a checkbox field.
        """
        # Usually check checkboxes (like terms and conditions)
        if not element.is_selected():
            if self.stealth_engine:
                self.stealth_engine.human_like_click(self.driver, element)
            else:
                element.click()
    
    def _fill_textarea_field_enhanced(self, element: WebElement, field_name: str):
        """
        Fills a textarea field (like cover letter).
        """
        value = self._get_field_value(field_name, 'textarea')
        
        if self.stealth_engine:
            self.stealth_engine.human_like_typing(element, value, 'slow')
        else:
            element.clear()
            element.send_keys(value)
    
    def _get_field_value(self, field_name: str, field_type: str) -> str:
        """
        Gets the appropriate value for a field based on its name and type.
        """
        # This would integrate with the existing question answering logic
        # For now, return placeholder values
        
        field_name_lower = field_name.lower()
        
        if 'name' in field_name_lower:
            return "John Doe"
        elif 'email' in field_name_lower:
            return "john.doe@email.com"
        elif 'phone' in field_name_lower:
            return "+1234567890"
        elif 'experience' in field_name_lower:
            return "3"
        elif field_type == 'textarea':
            return "I am very interested in this position and believe my skills would be a great fit."
        else:
            return "Yes"
    
    def _submit_application_enhanced(self) -> bool:
        """
        Submits the application with enhanced behavior.
        """
        try:
            # Find submit button
            submit_selectors = [
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Send')]",
                "//button[contains(@class, 'submit')]",
                "//input[@type='submit']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not submit_button:
                print_lg("❌ Submit button not found")
                return False
            
            # Final hesitation before submission
            if self.human_behavior:
                self.human_behavior.simulate_decision_making('critical')
            
            # Click submit
            if self.stealth_engine:
                self.stealth_engine.human_like_click(self.driver, submit_button)
            else:
                submit_button.click()
            
            # Wait for confirmation
            time.sleep(random.uniform(2.0, 5.0))
            
            return True
            
        except Exception as e:
            print_lg(f"Error submitting application: {e}")
            return False
    
    def get_session_stats(self) -> Dict:
        """
        Returns statistics about the current application session.
        """
        session_duration = time.time() - self.session_start_time
        
        stats = {
            'applications_this_session': self.applications_this_session,
            'session_duration': session_duration,
            'applications_per_hour': (self.applications_this_session / (session_duration / 3600)) if session_duration > 0 else 0
        }
        
        # Add human behavior stats if available
        if self.human_behavior:
            stats.update(self.human_behavior.get_session_stats())
        
        # Add application strategy stats if available
        if self.application_strategy:
            stats.update(self.application_strategy.get_application_recommendations())
        
        return stats
