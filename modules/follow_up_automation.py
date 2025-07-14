# Author: Enhanced by AI Assistant
# Follow-up Automation Module
# Automated follow-up messaging system for applications and connection requests

import json
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.helpers import print_lg

@dataclass
class FollowUpTask:
    """Data class for follow-up tasks."""
    task_id: str
    task_type: str  # 'application', 'connection', 'interview'
    target_name: str
    target_company: str
    target_profile_url: str
    original_date: str
    follow_up_date: str
    message_template: str
    priority: int = 1
    completed: bool = False
    attempts: int = 0
    last_attempt: Optional[str] = None
    response_received: bool = False

@dataclass
class FollowUpStats:
    """Data class for follow-up statistics."""
    total_follow_ups_sent: int = 0
    responses_received: int = 0
    response_rate: float = 0.0
    average_response_time_days: float = 0.0
    follow_ups_pending: int = 0

class FollowUpAutomation:
    """
    Automated follow-up system for job applications and networking.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.human_behavior = getattr(driver, 'human_behavior', None)
        
        # Configuration
        self.config_path = "config/follow_up_config.json"
        self.tasks_path = "data/follow_up_tasks.json"
        self.stats_path = "data/follow_up_stats.json"
        
        # Load configuration and data
        self.config = self._load_config()
        self.follow_up_tasks = self._load_follow_up_tasks()
        self.follow_up_stats = self._load_follow_up_stats()
        
        # Message templates
        self.message_templates = self._load_message_templates()
        
    def _load_config(self) -> Dict:
        """Load follow-up configuration."""
        default_config = {
            "application_follow_up_days": [7, 14],
            "connection_follow_up_days": [7],
            "interview_follow_up_days": [1, 7],
            "max_follow_ups_per_target": 2,
            "daily_follow_up_limit": 10,
            "follow_up_hours": [9, 10, 11, 14, 15, 16],
            "avoid_weekends": True,
            "personalization_enabled": True,
            "auto_follow_up_enabled": True
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
            print_lg(f"Error loading follow-up config: {e}")
            return default_config
    
    def _load_follow_up_tasks(self) -> List[FollowUpTask]:
        """Load follow-up tasks from file."""
        try:
            if os.path.exists(self.tasks_path):
                with open(self.tasks_path, 'r') as f:
                    tasks_data = json.load(f)
                return [FollowUpTask(**task) for task in tasks_data]
            else:
                return []
        except Exception as e:
            print_lg(f"Error loading follow-up tasks: {e}")
            return []
    
    def _save_follow_up_tasks(self):
        """Save follow-up tasks to file."""
        try:
            os.makedirs(os.path.dirname(self.tasks_path), exist_ok=True)
            tasks_data = [asdict(task) for task in self.follow_up_tasks]
            with open(self.tasks_path, 'w') as f:
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            print_lg(f"Error saving follow-up tasks: {e}")
    
    def _load_follow_up_stats(self) -> FollowUpStats:
        """Load follow-up statistics."""
        try:
            if os.path.exists(self.stats_path):
                with open(self.stats_path, 'r') as f:
                    stats_data = json.load(f)
                return FollowUpStats(**stats_data)
            else:
                return FollowUpStats()
        except Exception as e:
            print_lg(f"Error loading follow-up stats: {e}")
            return FollowUpStats()
    
    def _save_follow_up_stats(self):
        """Save follow-up statistics."""
        try:
            os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)
            with open(self.stats_path, 'w') as f:
                json.dump(asdict(self.follow_up_stats), f, indent=2)
        except Exception as e:
            print_lg(f"Error saving follow-up stats: {e}")
    
    def _load_message_templates(self) -> Dict:
        """Load follow-up message templates."""
        return {
            "application_first": [
                "Hi {name}, I wanted to follow up on my application for the {position} role at {company}. I'm very excited about this opportunity and would love to discuss how my skills align with your team's needs.",
                "Hello {name}, I hope this message finds you well. I applied for the {position} position at {company} last week and wanted to reiterate my strong interest in the role.",
                "Hi {name}, I'm following up on my recent application for the {position} role. I'm particularly excited about {company}'s mission and would welcome the opportunity to contribute to your team."
            ],
            "application_second": [
                "Hi {name}, I wanted to reach out once more regarding the {position} role at {company}. I remain very interested and would appreciate any updates on the hiring process.",
                "Hello {name}, I hope you're doing well. I'm still very interested in the {position} opportunity and wanted to check if there are any updates on the application process.",
                "Hi {name}, I'm following up on my application for the {position} role. I'd be happy to provide any additional information that might be helpful for your decision."
            ],
            "connection_follow_up": [
                "Hi {name}, thank you for connecting! I'm very interested in learning more about opportunities at {company} and would love to hear about your experience there.",
                "Hello {name}, I appreciate you accepting my connection request. I'm exploring opportunities in {industry} and would value any insights you might share about {company}.",
                "Hi {name}, thanks for connecting! I'm particularly interested in {company}'s work and would love to learn more about potential opportunities in your team."
            ],
            "interview_thank_you": [
                "Hi {name}, thank you for taking the time to interview me for the {position} role. I enjoyed our conversation and am even more excited about the opportunity to join {company}.",
                "Hello {name}, I wanted to thank you for the great interview yesterday. I'm very enthusiastic about the {position} role and the chance to contribute to {company}'s success.",
                "Hi {name}, thank you for the insightful interview. I'm excited about the possibility of bringing my skills to the {position} role at {company}."
            ]
        }
    
    def create_follow_up_tasks_for_application(self, job_id: str, company: str, 
                                             position: str, recruiter_info: Dict = None):
        """Create follow-up tasks for a job application."""
        if not self.config.get("auto_follow_up_enabled", True):
            return
        
        follow_up_days = self.config.get("application_follow_up_days", [7, 14])
        original_date = datetime.now()
        
        for i, days in enumerate(follow_up_days):
            follow_up_date = original_date + timedelta(days=days)
            
            # Determine message template
            if i == 0:
                template_key = "application_first"
            else:
                template_key = "application_second"
            
            task = FollowUpTask(
                task_id=f"app_{job_id}_{i+1}",
                task_type="application",
                target_name=recruiter_info.get("name", "Hiring Manager") if recruiter_info else "Hiring Manager",
                target_company=company,
                target_profile_url=recruiter_info.get("profile_url", "") if recruiter_info else "",
                original_date=original_date.isoformat(),
                follow_up_date=follow_up_date.isoformat(),
                message_template=template_key,
                priority=2 if i == 0 else 1  # First follow-up has higher priority
            )
            
            self.follow_up_tasks.append(task)
        
        self._save_follow_up_tasks()
        print_lg(f"📅 Created {len(follow_up_days)} follow-up tasks for {position} at {company}")
    
    def create_follow_up_task_for_connection(self, name: str, company: str, 
                                           profile_url: str, connection_date: datetime = None):
        """Create follow-up task for a new connection."""
        if not self.config.get("auto_follow_up_enabled", True):
            return
        
        if connection_date is None:
            connection_date = datetime.now()
        
        follow_up_days = self.config.get("connection_follow_up_days", [7])
        follow_up_date = connection_date + timedelta(days=follow_up_days[0])
        
        task = FollowUpTask(
            task_id=f"conn_{name.replace(' ', '_')}_{int(connection_date.timestamp())}",
            task_type="connection",
            target_name=name,
            target_company=company,
            target_profile_url=profile_url,
            original_date=connection_date.isoformat(),
            follow_up_date=follow_up_date.isoformat(),
            message_template="connection_follow_up",
            priority=1
        )
        
        self.follow_up_tasks.append(task)
        self._save_follow_up_tasks()
        print_lg(f"📅 Created follow-up task for connection with {name} at {company}")
    
    def create_follow_up_task_for_interview(self, interviewer_name: str, company: str,
                                          position: str, interview_date: datetime = None):
        """Create follow-up task for an interview."""
        if interview_date is None:
            interview_date = datetime.now()
        
        # Create thank you follow-up (next day)
        thank_you_date = interview_date + timedelta(days=1)
        
        task = FollowUpTask(
            task_id=f"interview_{interviewer_name.replace(' ', '_')}_{int(interview_date.timestamp())}",
            task_type="interview",
            target_name=interviewer_name,
            target_company=company,
            target_profile_url="",
            original_date=interview_date.isoformat(),
            follow_up_date=thank_you_date.isoformat(),
            message_template="interview_thank_you",
            priority=3  # High priority for interview follow-ups
        )
        
        self.follow_up_tasks.append(task)
        self._save_follow_up_tasks()
        print_lg(f"📅 Created interview follow-up task for {interviewer_name} at {company}")
    
    def get_pending_follow_ups(self) -> List[FollowUpTask]:
        """Get follow-up tasks that are due."""
        now = datetime.now()
        pending_tasks = []
        
        for task in self.follow_up_tasks:
            if (not task.completed and 
                datetime.fromisoformat(task.follow_up_date) <= now and
                task.attempts < self.config.get("max_follow_ups_per_target", 2)):
                pending_tasks.append(task)
        
        # Sort by priority and date
        pending_tasks.sort(key=lambda x: (x.priority, x.follow_up_date), reverse=True)
        
        return pending_tasks
    
    def execute_follow_ups(self, max_follow_ups: int = None) -> int:
        """Execute pending follow-up tasks."""
        if not self.should_send_follow_ups_now():
            print_lg("❌ Not an optimal time for sending follow-ups")
            return 0
        
        pending_tasks = self.get_pending_follow_ups()
        
        if not pending_tasks:
            print_lg("✅ No pending follow-up tasks")
            return 0
        
        if max_follow_ups is None:
            max_follow_ups = min(
                self.config.get("daily_follow_up_limit", 10),
                len(pending_tasks)
            )
        
        print_lg(f"📤 Executing {min(max_follow_ups, len(pending_tasks))} follow-up tasks...")
        
        follow_ups_sent = 0
        
        for task in pending_tasks[:max_follow_ups]:
            try:
                success = self._execute_follow_up_task(task)
                if success:
                    follow_ups_sent += 1
                    self.follow_up_stats.total_follow_ups_sent += 1
                
                # Update task
                task.attempts += 1
                task.last_attempt = datetime.now().isoformat()
                
                # Mark as completed if max attempts reached
                if task.attempts >= self.config.get("max_follow_ups_per_target", 2):
                    task.completed = True
                
                # Human-like delay between follow-ups
                if self.human_behavior:
                    self.human_behavior.human_like_delay(2.0, 5.0)
                else:
                    time.sleep(random.uniform(2.0, 5.0))
                
            except Exception as e:
                print_lg(f"Error executing follow-up task {task.task_id}: {e}")
                continue
        
        # Update statistics and save
        self._update_follow_up_stats()
        self._save_follow_up_tasks()
        self._save_follow_up_stats()
        
        print_lg(f"✅ Sent {follow_ups_sent} follow-up messages")
        return follow_ups_sent
    
    def _execute_follow_up_task(self, task: FollowUpTask) -> bool:
        """Execute a specific follow-up task."""
        try:
            print_lg(f"📤 Sending follow-up to {task.target_name} at {task.target_company}")
            
            if task.task_type == "application":
                return self._send_application_follow_up(task)
            elif task.task_type == "connection":
                return self._send_connection_follow_up(task)
            elif task.task_type == "interview":
                return self._send_interview_follow_up(task)
            else:
                print_lg(f"Unknown task type: {task.task_type}")
                return False
                
        except Exception as e:
            print_lg(f"Error executing follow-up task: {e}")
            return False
    
    def _send_application_follow_up(self, task: FollowUpTask) -> bool:
        """Send follow-up message for job application."""
        # This would typically involve finding the recruiter's profile
        # and sending a LinkedIn message or email
        
        if task.target_profile_url:
            return self._send_linkedin_message(task)
        else:
            # Could implement email follow-up here
            print_lg(f"No profile URL for {task.target_name}, skipping LinkedIn follow-up")
            return False
    
    def _send_connection_follow_up(self, task: FollowUpTask) -> bool:
        """Send follow-up message to a connection."""
        return self._send_linkedin_message(task)
    
    def _send_interview_follow_up(self, task: FollowUpTask) -> bool:
        """Send thank you message after interview."""
        return self._send_linkedin_message(task)
    
    def _send_linkedin_message(self, task: FollowUpTask) -> bool:
        """Send a LinkedIn message."""
        try:
            if not task.target_profile_url:
                print_lg(f"No profile URL for {task.target_name}")
                return False
            
            # Navigate to profile
            self.driver.get(task.target_profile_url)
            
            # Wait for profile to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pv-top-card")))
            
            # Find and click message button
            message_button = self._find_message_button()
            if not message_button:
                print_lg(f"Message button not found for {task.target_name}")
                return False
            
            message_button.click()
            
            # Wait for message modal
            message_modal = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "msg-form")))
            
            # Generate and send message
            message_text = self._generate_follow_up_message(task)
            message_box = message_modal.find_element(By.TAG_NAME, "textarea")
            
            if self.human_behavior:
                self.human_behavior.simulate_form_filling_hesitation("follow-up message")
                self.human_behavior.human_like_typing(message_box, message_text, 'normal')
            else:
                message_box.clear()
                message_box.send_keys(message_text)
            
            # Send message
            send_button = message_modal.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
            send_button.click()
            
            print_lg(f"✅ Follow-up message sent to {task.target_name}")
            return True
            
        except Exception as e:
            print_lg(f"Error sending LinkedIn message: {e}")
            return False
    
    def _find_message_button(self) -> Optional[WebElement]:
        """Find the message button on a LinkedIn profile."""
        message_selectors = [
            "//button[contains(@aria-label, 'Message')]",
            "//button[contains(text(), 'Message')]",
            "//a[contains(@class, 'message')]"
        ]
        
        for selector in message_selectors:
            try:
                button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                return button
            except TimeoutException:
                continue
        
        return None
    
    def _generate_follow_up_message(self, task: FollowUpTask) -> str:
        """Generate a personalized follow-up message."""
        templates = self.message_templates.get(task.message_template, ["Hello {name}, I wanted to follow up with you."])
        template = random.choice(templates)
        
        # Extract position from task (if available)
        position = "the position"  # This could be enhanced to store actual position
        
        # Replace placeholders
        message = template.format(
            name=task.target_name.split()[0],  # First name only
            company=task.target_company,
            position=position,
            industry="technology"  # This could be made dynamic
        )
        
        return message
    
    def _update_follow_up_stats(self):
        """Update follow-up statistics."""
        # Count pending follow-ups
        pending = len([task for task in self.follow_up_tasks if not task.completed])
        self.follow_up_stats.follow_ups_pending = pending
        
        # Calculate response rate
        total_sent = self.follow_up_stats.total_follow_ups_sent
        responses = self.follow_up_stats.responses_received
        
        if total_sent > 0:
            self.follow_up_stats.response_rate = responses / total_sent
    
    def should_send_follow_ups_now(self) -> bool:
        """Check if it's a good time to send follow-ups."""
        now = datetime.now()
        
        # Check if within follow-up hours
        if now.hour not in self.config.get("follow_up_hours", [9, 10, 11, 14, 15, 16]):
            return False
        
        # Check if weekend and we want to avoid weekends
        if self.config.get("avoid_weekends", True) and now.weekday() >= 5:
            return False
        
        return True
    
    def mark_response_received(self, task_id: str):
        """Mark that a response was received for a follow-up."""
        for task in self.follow_up_tasks:
            if task.task_id == task_id:
                task.response_received = True
                self.follow_up_stats.responses_received += 1
                break
        
        self._save_follow_up_tasks()
        self._save_follow_up_stats()
    
    def get_follow_up_report(self) -> Dict:
        """Generate a follow-up activity report."""
        pending_tasks = self.get_pending_follow_ups()
        
        return {
            "total_follow_ups_sent": self.follow_up_stats.total_follow_ups_sent,
            "responses_received": self.follow_up_stats.responses_received,
            "response_rate": f"{self.follow_up_stats.response_rate:.1%}",
            "pending_follow_ups": len(pending_tasks),
            "follow_ups_due_today": len([
                task for task in pending_tasks 
                if datetime.fromisoformat(task.follow_up_date).date() == datetime.now().date()
            ]),
            "next_follow_up": min([
                datetime.fromisoformat(task.follow_up_date) 
                for task in pending_tasks
            ]).isoformat() if pending_tasks else None
        }
