# Author: Enhanced by AI Assistant
# Enhanced LinkedIn Job Application Bot
# Integrates all advanced features: stealth mode, AI optimization, analytics, and networking

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config.personals import *
from config.questions import *
from config.search import *
from config.secrets import use_AI, username, password, ai_provider
from config.settings import *

# Import enhanced modules
from modules.open_chrome import *
from modules.helpers import *
from modules.enhanced_job_applier import EnhancedJobApplier
from modules.smart_application_strategy import SmartApplicationStrategy
from modules.resume_optimizer import ResumeOptimizer
from modules.job_matching_intelligence import JobMatchingIntelligence
from modules.analytics_dashboard import ApplicationAnalyticsDashboard
from modules.network_builder import NetworkBuilder
from modules.follow_up_automation import FollowUpAutomation

# Import AI connections
from modules.ai.openaiConnections import ai_create_openai_client, ai_close_openai_client
from modules.ai.deepseekConnections import deepseek_create_client

# Import original functions for compatibility
from runAiBot import is_logged_in_LN, login_LN, get_applied_job_ids

class EnhancedJobBot:
    """
    Enhanced LinkedIn Job Application Bot with advanced features.
    """
    
    def __init__(self):
        self.driver = driver  # From open_chrome.py
        self.wait = wait
        self.actions = actions
        
        # Initialize AI client
        self.ai_client = None
        if use_AI:
            print_lg("🤖 Initializing AI client...")
            try:
                if ai_provider.lower() == "openai":
                    self.ai_client = ai_create_openai_client()
                elif ai_provider.lower() == "deepseek":
                    self.ai_client = deepseek_create_client()
                else:
                    print_lg(f"❌ Unknown AI provider: {ai_provider}")
            except Exception as e:
                print_lg(f"❌ Failed to initialize AI client: {e}")
        
        # Initialize enhanced modules
        self.job_applier = EnhancedJobApplier(self.driver)
        self.application_strategy = SmartApplicationStrategy()
        self.resume_optimizer = ResumeOptimizer()
        self.job_matcher = JobMatchingIntelligence()
        self.analytics_dashboard = ApplicationAnalyticsDashboard()
        self.network_builder = NetworkBuilder(self.driver)
        self.follow_up_automation = FollowUpAutomation(self.driver)
        
        # Session tracking
        self.session_start_time = datetime.now()
        self.jobs_processed = 0
        self.applications_submitted = 0
        self.connections_made = 0
        
        print_lg("🚀 Enhanced Job Bot initialized successfully!")
    
    def run_enhanced_job_search(self, search_terms: List[str]):
        """
        Run the enhanced job search and application process.
        """
        print_lg("=" * 80)
        print_lg("🎯 STARTING ENHANCED JOB APPLICATION SESSION")
        print_lg("=" * 80)
        
        # Update analytics dashboard
        print_lg("📊 Updating analytics dashboard...")
        self.analytics_dashboard.update_analytics()
        
        # Display current statistics
        quick_stats = self.analytics_dashboard.get_quick_stats()
        print_lg(f"📈 Current Stats: {quick_stats['total_applications']} applications, "
                f"{quick_stats['success_rate']} success rate, "
                f"{quick_stats['applications_per_day']} apps/day")
        
        # Get applied job IDs to avoid duplicates
        applied_jobs = get_applied_job_ids()
        print_lg(f"📋 Found {len(applied_jobs)} previously applied jobs")
        
        # Process each search term
        for search_term in search_terms:
            print_lg(f"\n🔍 Processing search term: '{search_term}'")
            
            try:
                # Navigate to job search
                self._navigate_to_job_search(search_term)
                
                # Apply filters
                self._apply_enhanced_filters()
                
                # Get job listings
                job_listings = self._get_job_listings()
                print_lg(f"📋 Found {len(job_listings)} job listings")
                
                # Analyze jobs with matching intelligence
                job_matches = self.job_matcher.get_job_recommendations(job_listings)
                
                # Process jobs based on match scores
                self._process_job_matches(job_matches, applied_jobs)
                
                # Check if we should take a break
                if self.driver.human_behavior and enable_break_simulation:
                    should_break, break_type = self.driver.human_behavior.should_take_break()
                    if should_break:
                        self.driver.human_behavior.take_break(break_type, self.driver)
                
            except Exception as e:
                print_lg(f"❌ Error processing search term '{search_term}': {e}")
                continue
        
        # Execute networking activities
        self._execute_networking_activities()
        
        # Execute follow-up activities
        self._execute_follow_up_activities()
        
        # Generate session report
        self._generate_session_report()
        
        print_lg("✅ Enhanced job application session completed!")
    
    def _navigate_to_job_search(self, search_term: str):
        """Navigate to LinkedIn job search with the given term."""
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_term}"
        self.driver.get(search_url)
        
        # Wait for page to load
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list")))
        
        # Simulate human reading behavior
        if self.driver.human_behavior:
            self.driver.human_behavior.simulate_reading_behavior(self.driver, 3.0)
    
    def _apply_enhanced_filters(self):
        """Apply job search filters with human-like behavior."""
        try:
            # Click filters button
            filters_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="All filters"]')))
            
            if self.driver.stealth_engine:
                self.driver.stealth_engine.human_like_click(self.driver, filters_button)
            else:
                filters_button.click()
            
            # Apply filters (using existing filter logic from runAiBot.py)
            # This would integrate with the existing apply_filters() function
            
            # Show results
            show_results_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Apply current filters")]')))
            
            if self.driver.stealth_engine:
                self.driver.stealth_engine.human_like_click(self.driver, show_results_button)
            else:
                show_results_button.click()
            
        except Exception as e:
            print_lg(f"❌ Error applying filters: {e}")
    
    def _get_job_listings(self) -> List[Dict]:
        """Extract job listings from the current page."""
        job_listings = []
        
        try:
            # Wait for job listings to load
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]")))
            
            job_elements = self.driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")
            
            for job_element in job_elements:
                try:
                    job_data = self._extract_job_data(job_element)
                    if job_data:
                        job_listings.append(job_data)
                except Exception as e:
                    print_lg(f"Error extracting job data: {e}")
                    continue
            
        except Exception as e:
            print_lg(f"❌ Error getting job listings: {e}")
        
        return job_listings
    
    def _extract_job_data(self, job_element: WebElement) -> Optional[Dict]:
        """Extract job data from a job listing element."""
        try:
            job_id = job_element.get_attribute('data-occludable-job-id')
            
            # Get job title and link
            title_element = job_element.find_element(By.TAG_NAME, 'a')
            title = title_element.text.strip()
            job_link = title_element.get_attribute('href')
            
            # Get company and location
            subtitle_element = job_element.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle')
            subtitle_text = subtitle_element.text
            
            # Parse company and location
            parts = subtitle_text.split(' · ')
            company = parts[0] if parts else "Unknown"
            location_info = parts[1] if len(parts) > 1 else "Unknown"
            
            # Extract work style (Remote, Hybrid, On-site)
            work_style = "On-site"  # Default
            if '(' in location_info and ')' in location_info:
                work_style = location_info[location_info.rfind('(')+1:location_info.rfind(')')]
                location = location_info[:location_info.rfind('(')].strip()
            else:
                location = location_info
            
            # Click on job to get description (if needed)
            description = ""
            try:
                title_element.click()
                time.sleep(2)  # Wait for job details to load
                
                description_element = self.driver.find_element(By.CLASS_NAME, "jobs-box__html-content")
                description = description_element.text
            except:
                pass  # Description extraction failed
            
            return {
                'job_id': job_id,
                'title': title,
                'company': company,
                'work_location': location,
                'work_style': work_style,
                'description': description,
                'job_link': job_link
            }
            
        except Exception as e:
            print_lg(f"Error extracting job data: {e}")
            return None
    
    def _process_job_matches(self, job_matches: List, applied_jobs: set):
        """Process job matches based on their scores and recommendations."""
        for job_match in job_matches:
            if self.jobs_processed >= switch_number:
                print_lg(f"📊 Reached job processing limit ({switch_number})")
                break
            
            self.jobs_processed += 1
            
            # Skip if already applied
            if job_match.job_id in applied_jobs:
                print_lg(f"⏭️ Skipping {job_match.title} at {job_match.company} (already applied)")
                continue
            
            print_lg(f"\n🎯 Processing: {job_match.title} at {job_match.company}")
            print_lg(f"📊 Match Score: {job_match.match_score:.2f} | Recommendation: {job_match.recommendation}")
            
            # Check if we should apply based on recommendation
            if "NOT RECOMMENDED" in job_match.recommendation:
                print_lg(f"❌ Skipping due to low match score")
                continue
            
            if job_match.red_flags:
                print_lg(f"⚠️ Red flags detected: {', '.join(job_match.red_flags)}")
                if "CAUTION" in job_match.recommendation:
                    print_lg(f"⏭️ Skipping due to red flags")
                    continue
            
            # Apply to the job
            try:
                job_data = {
                    'job_id': job_match.job_id,
                    'title': job_match.title,
                    'company': job_match.company,
                    'description': getattr(job_match, 'description', ''),
                    'work_location': getattr(job_match, 'work_location', ''),
                    'work_style': getattr(job_match, 'work_style', '')
                }
                
                success, message = self.job_applier.apply_to_job_enhanced(job_data)
                
                if success:
                    self.applications_submitted += 1
                    print_lg(f"✅ Successfully applied to {job_match.title}")
                    
                    # Create follow-up tasks
                    self.follow_up_automation.create_follow_up_tasks_for_application(
                        job_match.job_id, job_match.company, job_match.title
                    )
                    
                    # Add company to networking targets
                    self._add_networking_targets([job_match.company])
                    
                else:
                    print_lg(f"❌ Failed to apply: {message}")
                
            except Exception as e:
                print_lg(f"❌ Error applying to job: {e}")
                continue
    
    def _execute_networking_activities(self):
        """Execute networking activities if enabled."""
        if not self.network_builder.should_send_connections_now():
            print_lg("⏭️ Skipping networking (not optimal time)")
            return
        
        print_lg("\n🤝 Executing networking activities...")
        
        try:
            # Find new connection targets
            target_companies = self._get_target_companies()
            if target_companies:
                new_targets = self.network_builder.find_connection_targets(target_companies)
                if new_targets:
                    self.network_builder.add_connection_targets(new_targets)
            
            # Send connection requests
            connections_sent = self.network_builder.send_connection_requests()
            self.connections_made += connections_sent
            
            # Generate networking report
            networking_report = self.network_builder.get_networking_report()
            print_lg(f"🤝 Networking Report: {networking_report}")
            
        except Exception as e:
            print_lg(f"❌ Error in networking activities: {e}")
    
    def _execute_follow_up_activities(self):
        """Execute follow-up activities."""
        print_lg("\n📤 Executing follow-up activities...")
        
        try:
            follow_ups_sent = self.follow_up_automation.execute_follow_ups()
            
            # Generate follow-up report
            follow_up_report = self.follow_up_automation.get_follow_up_report()
            print_lg(f"📤 Follow-up Report: {follow_up_report}")
            
        except Exception as e:
            print_lg(f"❌ Error in follow-up activities: {e}")
    
    def _add_networking_targets(self, companies: List[str]):
        """Add companies to networking targets."""
        try:
            new_targets = self.network_builder.find_connection_targets(companies, ["recruiter", "hiring manager"])
            if new_targets:
                self.network_builder.add_connection_targets(new_targets)
        except Exception as e:
            print_lg(f"Error adding networking targets: {e}")
    
    def _get_target_companies(self) -> List[str]:
        """Get list of target companies for networking."""
        # This could be enhanced to get companies from recent applications
        return ["Google", "Microsoft", "Amazon", "Apple", "Meta"]  # Example companies
    
    def _generate_session_report(self):
        """Generate and display session report."""
        session_duration = datetime.now() - self.session_start_time
        
        print_lg("\n" + "=" * 80)
        print_lg("📊 ENHANCED JOB BOT SESSION REPORT")
        print_lg("=" * 80)
        print_lg(f"⏱️ Session Duration: {session_duration}")
        print_lg(f"🎯 Jobs Processed: {self.jobs_processed}")
        print_lg(f"📝 Applications Submitted: {self.applications_submitted}")
        print_lg(f"🤝 Connections Made: {self.connections_made}")
        
        # Get enhanced statistics
        if self.driver.human_behavior:
            behavior_stats = self.driver.human_behavior.get_session_stats()
            print_lg(f"🤖 Human Behavior Stats: {behavior_stats}")
        
        # Get application strategy recommendations
        strategy_recommendations = self.application_strategy.get_application_recommendations()
        if strategy_recommendations.get('recommendations'):
            print_lg("💡 Strategy Recommendations:")
            for rec in strategy_recommendations['recommendations']:
                print_lg(f"   • {rec}")
        
        # Save analytics report
        report_path = self.analytics_dashboard.save_dashboard_report()
        if report_path:
            print_lg(f"📄 Detailed report saved: {report_path}")
        
        # Generate charts
        chart_path = self.analytics_dashboard.generate_charts()
        if chart_path:
            print_lg(f"📊 Analytics charts saved: {chart_path}")
        
        print_lg("=" * 80)
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if self.ai_client:
                if ai_provider.lower() == "openai":
                    ai_close_openai_client(self.ai_client)
                print_lg("🤖 AI client closed")
            
            print_lg("🧹 Cleanup completed")
        except Exception as e:
            print_lg(f"❌ Error during cleanup: {e}")

def main():
    """Main function to run the enhanced job bot."""
    enhanced_bot = None
    
    try:
        # Login to LinkedIn
        print_lg("🔐 Logging into LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        
        if not is_logged_in_LN():
            login_LN()
        
        print_lg("✅ Successfully logged into LinkedIn")
        
        # Initialize enhanced bot
        enhanced_bot = EnhancedJobBot()
        
        # Run enhanced job search
        search_terms = ["python developer", "data scientist", "software engineer"]  # Example search terms
        enhanced_bot.run_enhanced_job_search(search_terms)
        
    except KeyboardInterrupt:
        print_lg("\n⏹️ Bot stopped by user")
    except Exception as e:
        print_lg(f"❌ Critical error: {e}")
        critical_error_log("Enhanced Job Bot Error", e)
    finally:
        if enhanced_bot:
            enhanced_bot.cleanup()
        
        try:
            driver.quit()
            print_lg("🚪 Browser closed")
        except:
            pass

if __name__ == "__main__":
    main()
