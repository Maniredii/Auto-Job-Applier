# Author: Enhanced by AI Assistant
# Human Behavior Simulation Module
# Implements realistic human interaction patterns for LinkedIn automation

import random
import time
import math
from typing import Dict, List, Tuple, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from modules.helpers import print_lg, buffer

class HumanBehaviorSimulator:
    """
    Simulates realistic human behavior patterns to avoid bot detection.
    """
    
    def __init__(self):
        self.session_start_time = time.time()
        self.actions_performed = 0
        self.last_action_time = time.time()
        self.fatigue_level = 0.0
        self.attention_span = random.uniform(300, 900)  # 5-15 minutes
        
        # Behavior patterns
        self.reading_speeds = {
            'fast': (150, 250),      # words per minute
            'normal': (200, 300),
            'slow': (100, 200)
        }
        
        self.break_patterns = {
            'micro': (2, 8),         # seconds
            'short': (15, 45),       # seconds  
            'medium': (60, 180),     # seconds
            'long': (300, 600)       # seconds
        }
        
    def should_take_break(self) -> Tuple[bool, str]:
        """
        Determines if a break should be taken based on human behavior patterns.
        """
        session_duration = time.time() - self.session_start_time
        time_since_last_action = time.time() - self.last_action_time
        
        # Micro breaks (very short pauses)
        if self.actions_performed % random.randint(8, 15) == 0:
            return True, 'micro'
        
        # Short breaks (brief pauses)
        if self.actions_performed % random.randint(25, 40) == 0:
            return True, 'short'
        
        # Medium breaks (attention span related)
        if session_duration > self.attention_span:
            self.attention_span = random.uniform(300, 900)  # Reset attention span
            return True, 'medium'
        
        # Long breaks (fatigue related)
        if session_duration > random.uniform(1800, 3600):  # 30-60 minutes
            return True, 'long'
        
        # Random breaks (human unpredictability)
        if random.random() < 0.02:  # 2% chance
            return True, random.choice(['micro', 'short'])
        
        return False, 'none'
    
    def take_break(self, break_type: str, driver: WebDriver):
        """
        Takes a break with realistic human behavior.
        """
        min_duration, max_duration = self.break_patterns[break_type]
        duration = random.uniform(min_duration, max_duration)
        
        print_lg(f"🛌 Taking {break_type} break for {duration:.1f} seconds...")
        
        if break_type in ['short', 'medium', 'long']:
            # Simulate tab switching or scrolling during breaks
            self._simulate_break_activity(driver, duration)
        else:
            # Simple pause for micro breaks
            time.sleep(duration)
        
        self.last_action_time = time.time()
        print_lg(f"✅ Break completed, resuming activity")
    
    def _simulate_break_activity(self, driver: WebDriver, duration: float):
        """
        Simulates realistic activity during breaks.
        """
        end_time = time.time() + duration
        
        while time.time() < end_time:
            activity = random.choice([
                'scroll', 'tab_switch', 'pause', 'mouse_move'
            ])
            
            if activity == 'scroll':
                self._random_scroll(driver)
                time.sleep(random.uniform(1, 3))
                
            elif activity == 'tab_switch':
                # Simulate checking other tabs (if any)
                if len(driver.window_handles) > 1:
                    current_handle = driver.current_window_handle
                    other_handles = [h for h in driver.window_handles if h != current_handle]
                    driver.switch_to.window(random.choice(other_handles))
                    time.sleep(random.uniform(2, 8))
                    driver.switch_to.window(current_handle)
                else:
                    time.sleep(random.uniform(3, 8))
                    
            elif activity == 'mouse_move':
                self._random_mouse_movement(driver)
                time.sleep(random.uniform(0.5, 2))
                
            else:  # pause
                time.sleep(random.uniform(2, 6))
    
    def _random_scroll(self, driver: WebDriver):
        """
        Performs random scrolling to simulate browsing behavior.
        """
        scroll_direction = random.choice(['up', 'down'])
        scroll_amount = random.randint(100, 500)
        
        if scroll_direction == 'down':
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
        else:
            driver.execute_script(f"window.scrollBy(0, -{scroll_amount})")
    
    def _random_mouse_movement(self, driver: WebDriver):
        """
        Performs random mouse movements.
        """
        actions = ActionChains(driver)
        
        for _ in range(random.randint(1, 3)):
            x_offset = random.randint(-200, 200)
            y_offset = random.randint(-200, 200)
            actions.move_by_offset(x_offset, y_offset)
            actions.pause(random.uniform(0.1, 0.5))
        
        actions.perform()
    
    def simulate_job_reading(self, driver: WebDriver, job_description_length: int = 500):
        """
        Simulates realistic job description reading behavior.
        """
        # Estimate reading time based on content length
        words = job_description_length // 5  # Rough word count estimation
        wpm_min, wpm_max = self.reading_speeds['normal']
        reading_speed = random.uniform(wpm_min, wpm_max)
        
        base_reading_time = (words / reading_speed) * 60  # Convert to seconds
        
        # Add human variability
        actual_reading_time = base_reading_time * random.uniform(0.7, 1.5)
        
        print_lg(f"📖 Simulating job reading for {actual_reading_time:.1f} seconds...")
        
        # Simulate reading with scrolling patterns
        self._simulate_reading_with_scrolling(driver, actual_reading_time)
    
    def _simulate_reading_with_scrolling(self, driver: WebDriver, duration: float):
        """
        Simulates reading behavior with realistic scrolling patterns.
        """
        start_time = time.time()
        scroll_position = 0
        
        while time.time() - start_time < duration:
            # Reading pause
            pause_duration = random.uniform(1.5, 4.0)
            time.sleep(pause_duration)
            
            # Scroll down (reading progress)
            if random.random() < 0.8:  # 80% chance to scroll down
                scroll_amount = random.randint(100, 300)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                scroll_position += scroll_amount
            
            # Occasional scroll back up (re-reading)
            elif random.random() < 0.3 and scroll_position > 0:  # 30% chance
                scroll_back = random.randint(50, 150)
                driver.execute_script(f"window.scrollBy(0, -{scroll_back})")
                scroll_position -= scroll_back
            
            # Random mouse movement during reading
            if random.random() < 0.2:  # 20% chance
                self._subtle_mouse_movement(driver)
    
    def _subtle_mouse_movement(self, driver: WebDriver):
        """
        Performs subtle mouse movements that occur during reading.
        """
        actions = ActionChains(driver)
        
        # Small, natural movements
        x_offset = random.randint(-50, 50)
        y_offset = random.randint(-30, 30)
        
        actions.move_by_offset(x_offset, y_offset)
        actions.pause(random.uniform(0.1, 0.3))
        actions.perform()
    
    def simulate_form_filling_hesitation(self, field_name: str) -> float:
        """
        Simulates realistic hesitation when filling forms.
        """
        hesitation_patterns = {
            'name': (0.1, 0.5),
            'email': (0.2, 0.8),
            'phone': (0.3, 1.0),
            'experience': (0.5, 2.0),
            'salary': (1.0, 3.0),
            'cover_letter': (2.0, 8.0),
            'default': (0.2, 1.0)
        }
        
        field_type = 'default'
        for key in hesitation_patterns:
            if key.lower() in field_name.lower():
                field_type = key
                break
        
        min_hesitation, max_hesitation = hesitation_patterns[field_type]
        hesitation_time = random.uniform(min_hesitation, max_hesitation)
        
        print_lg(f"🤔 Hesitating before filling '{field_name}' for {hesitation_time:.1f} seconds...")
        time.sleep(hesitation_time)
        
        return hesitation_time
    
    def simulate_decision_making(self, decision_complexity: str = 'normal') -> float:
        """
        Simulates decision-making time for different types of choices.
        """
        decision_times = {
            'simple': (0.5, 2.0),      # Yes/No questions
            'normal': (1.0, 4.0),      # Multiple choice
            'complex': (3.0, 10.0),    # Complex decisions
            'critical': (5.0, 15.0)    # Important decisions like salary
        }
        
        min_time, max_time = decision_times.get(decision_complexity, decision_times['normal'])
        decision_time = random.uniform(min_time, max_time)
        
        print_lg(f"🧠 Making {decision_complexity} decision for {decision_time:.1f} seconds...")
        time.sleep(decision_time)
        
        return decision_time
    
    def simulate_application_review(self, driver: WebDriver):
        """
        Simulates reviewing the application before submission.
        """
        print_lg("👀 Reviewing application before submission...")
        
        # Scroll through the application
        review_duration = random.uniform(10.0, 30.0)
        start_time = time.time()
        
        while time.time() - start_time < review_duration:
            # Scroll to different sections
            scroll_amount = random.randint(-200, 300)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            
            # Pause to "read"
            time.sleep(random.uniform(1.0, 3.0))
            
            # Occasional mouse movement
            if random.random() < 0.3:
                self._subtle_mouse_movement(driver)
        
        # Final pause before submission
        final_hesitation = random.uniform(2.0, 8.0)
        print_lg(f"⏳ Final consideration before submitting for {final_hesitation:.1f} seconds...")
        time.sleep(final_hesitation)
    
    def update_fatigue_level(self):
        """
        Updates fatigue level based on session duration and activity.
        """
        session_duration = time.time() - self.session_start_time
        self.fatigue_level = min(1.0, session_duration / 3600)  # Max fatigue after 1 hour
        
        # Adjust behavior based on fatigue
        if self.fatigue_level > 0.7:
            print_lg("😴 High fatigue detected - slowing down actions")
        elif self.fatigue_level > 0.4:
            print_lg("😐 Moderate fatigue detected - adding more pauses")
    
    def get_fatigue_multiplier(self) -> float:
        """
        Returns a multiplier for action delays based on fatigue level.
        """
        return 1.0 + (self.fatigue_level * 2.0)  # Up to 3x slower when fully fatigued
    
    def record_action(self):
        """
        Records that an action was performed.
        """
        self.actions_performed += 1
        self.last_action_time = time.time()
        self.update_fatigue_level()
    
    def get_session_stats(self) -> Dict:
        """
        Returns statistics about the current session.
        """
        session_duration = time.time() - self.session_start_time
        
        return {
            'session_duration': session_duration,
            'actions_performed': self.actions_performed,
            'fatigue_level': self.fatigue_level,
            'actions_per_minute': self.actions_performed / (session_duration / 60) if session_duration > 0 else 0
        }
