# Author: Enhanced by AI Assistant
# Network Building Features Module
# Intelligent connection requests to recruiters and employees at target companies

import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.helpers import print_lg, buffer
from modules.human_behavior import HumanBehaviorSimulator

@dataclass
class ConnectionTarget:
    """Data class for connection targets."""
    name: str
    title: str
    company: str
    profile_url: str
    connection_reason: str
    priority: int = 1
    attempted: bool = False
    connected: bool = False
    response_received: bool = False
    last_attempt: Optional[str] = None

@dataclass
class NetworkingStats:
    """Data class for networking statistics."""
    total_connections_sent: int = 0
    connections_accepted: int = 0
    responses_received: int = 0
    acceptance_rate: float = 0.0
    response_rate: float = 0.0
    daily_limit_reached: bool = False
    weekly_connections: int = 0

class NetworkBuilder:
    """
    Intelligent network building system for LinkedIn connections.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.human_behavior = getattr(driver, 'human_behavior', None)
        
        # Configuration
        self.config_path = "config/networking_config.json"
        self.targets_path = "data/connection_targets.json"
        self.stats_path = "data/networking_stats.json"
        
        # Load configuration and data
        self.config = self._load_config()
        self.connection_targets = self._load_connection_targets()
        self.networking_stats = self._load_networking_stats()
        
        # Daily limits
        self.daily_connection_limit = self.config.get("daily_connection_limit", 20)
        self.weekly_connection_limit = self.config.get("weekly_connection_limit", 100)
        self.connections_sent_today = self._count_connections_today()
        
        # Message templates
        self.message_templates = self._load_message_templates()
        
    def _load_config(self) -> Dict:
        """Load networking configuration."""
        default_config = {
            "daily_connection_limit": 20,
            "weekly_connection_limit": 100,
            "target_roles": ["recruiter", "hiring manager", "hr", "talent acquisition"],
            "target_companies": [],
            "connection_message_enabled": True,
            "auto_follow_up": True,
            "follow_up_delay_days": 7,
            "networking_hours": [9, 10, 11, 14, 15, 16, 17],
            "avoid_weekends": True,
            "personalization_level": "medium"  # low, medium, high
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
            print_lg(f"Error loading networking config: {e}")
            return default_config
    
    def _load_connection_targets(self) -> List[ConnectionTarget]:
        """Load connection targets from file."""
        try:
            if os.path.exists(self.targets_path):
                with open(self.targets_path, 'r') as f:
                    targets_data = json.load(f)
                return [ConnectionTarget(**target) for target in targets_data]
            else:
                return []
        except Exception as e:
            print_lg(f"Error loading connection targets: {e}")
            return []
    
    def _save_connection_targets(self):
        """Save connection targets to file."""
        try:
            os.makedirs(os.path.dirname(self.targets_path), exist_ok=True)
            targets_data = [asdict(target) for target in self.connection_targets]
            with open(self.targets_path, 'w') as f:
                json.dump(targets_data, f, indent=2)
        except Exception as e:
            print_lg(f"Error saving connection targets: {e}")
    
    def _load_networking_stats(self) -> NetworkingStats:
        """Load networking statistics."""
        try:
            if os.path.exists(self.stats_path):
                with open(self.stats_path, 'r') as f:
                    stats_data = json.load(f)
                return NetworkingStats(**stats_data)
            else:
                return NetworkingStats()
        except Exception as e:
            print_lg(f"Error loading networking stats: {e}")
            return NetworkingStats()
    
    def _save_networking_stats(self):
        """Save networking statistics."""
        try:
            os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)
            with open(self.stats_path, 'w') as f:
                json.dump(asdict(self.networking_stats), f, indent=2)
        except Exception as e:
            print_lg(f"Error saving networking stats: {e}")
    
    def _load_message_templates(self) -> Dict:
        """Load connection message templates."""
        return {
            "recruiter": [
                "Hi {name}, I noticed you're a {title} at {company}. I'm actively seeking new opportunities in {industry} and would love to connect to learn more about potential roles at {company}.",
                "Hello {name}, I'm impressed by {company}'s work in {industry}. As someone looking to advance my career in this field, I'd appreciate the opportunity to connect and learn from your experience.",
                "Hi {name}, I see you work in talent acquisition at {company}. I'm currently exploring new opportunities and would value connecting with you to learn about {company}'s culture and potential openings."
            ],
            "employee": [
                "Hi {name}, I'm very interested in {company} and the work you do as a {title}. I'd love to connect and learn more about your experience at the company.",
                "Hello {name}, I noticed we share similar interests in {industry}. I'm exploring opportunities at {company} and would appreciate connecting to learn about your experience there.",
                "Hi {name}, I'm impressed by your background in {industry} at {company}. I'd love to connect and potentially learn from your experience in the field."
            ],
            "hiring_manager": [
                "Hi {name}, I see you're a {title} at {company}. I'm very interested in opportunities in your team and would love to connect to learn more about your work.",
                "Hello {name}, I'm actively seeking opportunities in {industry} and noticed your role at {company}. I'd appreciate the chance to connect and learn about potential openings.",
                "Hi {name}, I'm impressed by {company}'s work and your role as {title}. I'd love to connect to learn more about opportunities in your team."
            ]
        }
    
    def _count_connections_today(self) -> int:
        """Count connections sent today."""
        today = datetime.now().date()
        count = 0
        
        for target in self.connection_targets:
            if target.last_attempt:
                attempt_date = datetime.fromisoformat(target.last_attempt).date()
                if attempt_date == today:
                    count += 1
        
        return count
    
    def find_connection_targets(self, companies: List[str], job_titles: List[str] = None) -> List[ConnectionTarget]:
        """
        Find potential connection targets at specified companies.
        """
        print_lg(f"🔍 Finding connection targets at {len(companies)} companies...")
        
        targets = []
        
        for company in companies:
            try:
                # Search for people at the company
                company_targets = self._search_company_employees(company, job_titles)
                targets.extend(company_targets)
                
                # Add delay between company searches
                if self.human_behavior:
                    self.human_behavior.human_like_delay(2.0, 5.0)
                else:
                    time.sleep(random.uniform(2.0, 5.0))
                    
            except Exception as e:
                print_lg(f"Error searching for targets at {company}: {e}")
        
        # Remove duplicates and existing targets
        existing_urls = {target.profile_url for target in self.connection_targets}
        new_targets = [target for target in targets if target.profile_url not in existing_urls]
        
        print_lg(f"✅ Found {len(new_targets)} new connection targets")
        return new_targets
    
    def _search_company_employees(self, company: str, job_titles: List[str] = None) -> List[ConnectionTarget]:
        """Search for employees at a specific company."""
        targets = []
        
        # Build search query
        if job_titles:
            title_query = " OR ".join([f'"{title}"' for title in job_titles])
            search_query = f'company:"{company}" AND ({title_query})'
        else:
            # Default to recruiting and hiring roles
            default_titles = self.config.get("target_roles", ["recruiter", "hiring manager"])
            title_query = " OR ".join([f'"{title}"' for title in default_titles])
            search_query = f'company:"{company}" AND ({title_query})'
        
        try:
            # Navigate to LinkedIn people search
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            self.driver.get(search_url)
            
            # Wait for results to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-results-container")))
            
            # Extract profile information
            profile_cards = self.driver.find_elements(By.CLASS_NAME, "search-result__wrapper")
            
            for card in profile_cards[:10]:  # Limit to first 10 results
                try:
                    target = self._extract_profile_info(card, company)
                    if target:
                        targets.append(target)
                except Exception as e:
                    print_lg(f"Error extracting profile info: {e}")
                    continue
            
        except Exception as e:
            print_lg(f"Error searching company employees: {e}")
        
        return targets
    
    def _extract_profile_info(self, profile_card: WebElement, company: str) -> Optional[ConnectionTarget]:
        """Extract profile information from search result card."""
        try:
            # Get name
            name_element = profile_card.find_element(By.CLASS_NAME, "search-result__result-link")
            name = name_element.text.strip()
            profile_url = name_element.get_attribute("href")
            
            # Get title
            title_element = profile_card.find_element(By.CLASS_NAME, "subline-level-1")
            title = title_element.text.strip()
            
            # Determine connection reason based on title
            title_lower = title.lower()
            if any(role in title_lower for role in ["recruiter", "talent", "hr"]):
                reason = "recruiter"
            elif any(role in title_lower for role in ["manager", "director", "lead"]):
                reason = "hiring_manager"
            else:
                reason = "employee"
            
            # Determine priority
            priority = 1
            if "recruiter" in title_lower or "talent" in title_lower:
                priority = 3  # High priority
            elif "manager" in title_lower or "director" in title_lower:
                priority = 2  # Medium priority
            
            return ConnectionTarget(
                name=name,
                title=title,
                company=company,
                profile_url=profile_url,
                connection_reason=reason,
                priority=priority
            )
            
        except Exception as e:
            print_lg(f"Error extracting profile info: {e}")
            return None
    
    def send_connection_requests(self, max_connections: int = None) -> int:
        """
        Send connection requests to targets.
        """
        if max_connections is None:
            max_connections = min(
                self.daily_connection_limit - self.connections_sent_today,
                len([t for t in self.connection_targets if not t.attempted])
            )
        
        if max_connections <= 0:
            print_lg("❌ Daily connection limit reached or no targets available")
            return 0
        
        print_lg(f"📤 Sending up to {max_connections} connection requests...")
        
        # Sort targets by priority
        available_targets = [t for t in self.connection_targets if not t.attempted]
        available_targets.sort(key=lambda x: x.priority, reverse=True)
        
        connections_sent = 0
        
        for target in available_targets[:max_connections]:
            try:
                success = self._send_connection_request(target)
                if success:
                    connections_sent += 1
                    self.connections_sent_today += 1
                    self.networking_stats.total_connections_sent += 1
                
                # Mark as attempted
                target.attempted = True
                target.last_attempt = datetime.now().isoformat()
                
                # Human-like delay between connections
                if self.human_behavior:
                    self.human_behavior.human_like_delay(3.0, 8.0)
                else:
                    time.sleep(random.uniform(3.0, 8.0))
                
            except Exception as e:
                print_lg(f"Error sending connection to {target.name}: {e}")
                continue
        
        # Update statistics
        self._update_networking_stats()
        self._save_connection_targets()
        self._save_networking_stats()
        
        print_lg(f"✅ Sent {connections_sent} connection requests")
        return connections_sent
    
    def _send_connection_request(self, target: ConnectionTarget) -> bool:
        """Send a connection request to a specific target."""
        try:
            print_lg(f"📤 Connecting to {target.name} ({target.title} at {target.company})")
            
            # Navigate to profile
            self.driver.get(target.profile_url)
            
            # Wait for profile to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pv-top-card")))
            
            # Find and click connect button
            connect_button = self._find_connect_button()
            if not connect_button:
                print_lg(f"❌ Connect button not found for {target.name}")
                return False
            
            # Click connect button
            if self.human_behavior:
                self.human_behavior.simulate_decision_making('simple')
            
            connect_button.click()
            
            # Handle connection modal
            success = self._handle_connection_modal(target)
            
            if success:
                target.connected = True
                print_lg(f"✅ Connection request sent to {target.name}")
            
            return success
            
        except Exception as e:
            print_lg(f"❌ Error sending connection request to {target.name}: {e}")
            return False
    
    def _find_connect_button(self) -> Optional[WebElement]:
        """Find the connect button on a LinkedIn profile."""
        connect_selectors = [
            "//button[contains(@aria-label, 'Connect')]",
            "//button[contains(text(), 'Connect')]",
            "//button[contains(@class, 'connect')]"
        ]
        
        for selector in connect_selectors:
            try:
                button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                return button
            except TimeoutException:
                continue
        
        return None
    
    def _handle_connection_modal(self, target: ConnectionTarget) -> bool:
        """Handle the connection request modal."""
        try:
            # Wait for modal to appear
            modal = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "send-invite")))
            
            # Check if we should add a note
            if self.config.get("connection_message_enabled", True):
                add_note_button = modal.find_element(By.XPATH, "//button[contains(text(), 'Add a note')]")
                add_note_button.click()
                
                # Generate and enter personalized message
                message = self._generate_connection_message(target)
                message_box = modal.find_element(By.TAG_NAME, "textarea")
                
                if self.human_behavior:
                    self.human_behavior.simulate_form_filling_hesitation("connection message")
                
                message_box.clear()
                message_box.send_keys(message)
            
            # Send the connection request
            send_button = modal.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
            send_button.click()
            
            # Wait for confirmation
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print_lg(f"Error handling connection modal: {e}")
            return False
    
    def _generate_connection_message(self, target: ConnectionTarget) -> str:
        """Generate a personalized connection message."""
        templates = self.message_templates.get(target.connection_reason, self.message_templates["employee"])
        template = random.choice(templates)
        
        # Replace placeholders
        message = template.format(
            name=target.name.split()[0],  # First name only
            title=target.title,
            company=target.company,
            industry="technology"  # This could be made dynamic
        )
        
        # Ensure message is within LinkedIn's character limit (300 characters)
        if len(message) > 300:
            message = message[:297] + "..."
        
        return message
    
    def _update_networking_stats(self):
        """Update networking statistics."""
        # Calculate acceptance rate
        accepted_connections = sum(1 for target in self.connection_targets if target.connected)
        total_sent = self.networking_stats.total_connections_sent
        
        if total_sent > 0:
            self.networking_stats.acceptance_rate = accepted_connections / total_sent
        
        # Calculate response rate
        responses = sum(1 for target in self.connection_targets if target.response_received)
        if total_sent > 0:
            self.networking_stats.response_rate = responses / total_sent
        
        # Update weekly count
        week_ago = datetime.now() - timedelta(days=7)
        weekly_connections = sum(
            1 for target in self.connection_targets
            if target.last_attempt and datetime.fromisoformat(target.last_attempt) > week_ago
        )
        self.networking_stats.weekly_connections = weekly_connections
        
        # Check daily limit
        self.networking_stats.daily_limit_reached = (
            self.connections_sent_today >= self.daily_connection_limit
        )
    
    def add_connection_targets(self, targets: List[ConnectionTarget]):
        """Add new connection targets to the list."""
        self.connection_targets.extend(targets)
        self._save_connection_targets()
        print_lg(f"➕ Added {len(targets)} new connection targets")
    
    def get_networking_report(self) -> Dict:
        """Generate a networking activity report."""
        total_targets = len(self.connection_targets)
        attempted = sum(1 for target in self.connection_targets if target.attempted)
        connected = sum(1 for target in self.connection_targets if target.connected)
        
        return {
            "total_targets": total_targets,
            "attempted_connections": attempted,
            "successful_connections": connected,
            "connections_today": self.connections_sent_today,
            "daily_limit": self.daily_connection_limit,
            "acceptance_rate": f"{self.networking_stats.acceptance_rate:.1%}",
            "response_rate": f"{self.networking_stats.response_rate:.1%}",
            "weekly_connections": self.networking_stats.weekly_connections,
            "daily_limit_reached": self.networking_stats.daily_limit_reached
        }
    
    def should_send_connections_now(self) -> bool:
        """Check if it's a good time to send connection requests."""
        now = datetime.now()
        
        # Check if within networking hours
        if now.hour not in self.config.get("networking_hours", [9, 10, 11, 14, 15, 16, 17]):
            return False
        
        # Check if weekend and we want to avoid weekends
        if self.config.get("avoid_weekends", True) and now.weekday() >= 5:
            return False
        
        # Check daily limit
        if self.connections_sent_today >= self.daily_connection_limit:
            return False
        
        # Check weekly limit
        if self.networking_stats.weekly_connections >= self.weekly_connection_limit:
            return False
        
        return True
