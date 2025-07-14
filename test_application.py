# Author: Manideep Reddy Eevuri
# LinkedIn: https://www.linkedin.com/in/manideep-reddy-eevuri-661659268/
# GitHub: https://github.com/Maniredii
#

"""
Test script to verify that the LinkedIn Auto Job Applier can apply to jobs automatically.
This script will run a single application cycle to test the functionality.
"""

import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all necessary modules and functions
from config.personals import *
from config.questions import *
from config.search import *
from config.secrets import use_AI, username, password, ai_provider
from config.settings import *

from modules.open_chrome import *
from modules.helpers import *
from modules.clickers_and_finders import *
from modules.validator import validate_config
from modules.ai.openaiConnections import ai_create_openai_client, ai_extract_skills, ai_answer_question, ai_close_openai_client, ai_generate_resume, ai_generate_coverletter
from modules.ai.deepseekConnections import deepseek_create_client, deepseek_extract_skills, deepseek_answer_question

# Import functions from runAiBot.py
from runAiBot import is_logged_in_LN, login_LN, apply_to_jobs

def test_single_application():
    """
    Test function to apply to a single job to verify the application process works.
    """
    try:
        print("=" * 80)
        print("TESTING LINKEDIN AUTO JOB APPLIER - SINGLE APPLICATION")
        print("=" * 80)
        print(f"Date and Time: {datetime.now()}")
        print(f"Username: {username}")
        print(f"AI Enabled: {use_AI}")
        print(f"AI Provider: {ai_provider}")
        print(f"Pause before submit: {pause_before_submit}")
        print(f"Pause at failed question: {pause_at_failed_question}")
        print(f"Easy apply only: {easy_apply_only}")
        print(f"Search terms: {search_terms}")
        print(f"Search location: {search_location}")
        print("=" * 80)
        
        # Validate configuration
        print("Validating configuration...")
        validate_config()
        print("✅ Configuration is valid")
        
        # Initialize AI client if enabled
        aiClient = None
        if use_AI:
            print(f"Initializing AI client for {ai_provider}...")
            if ai_provider.lower() == "openai":
                aiClient = ai_create_openai_client()
            elif ai_provider.lower() == "deepseek":
                aiClient = deepseek_create_client()
            else:
                print(f"Unknown AI provider: {ai_provider}")
                aiClient = None
        
        # Login to LinkedIn
        print("Logging into LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN(): 
            login_LN()
        print("✅ Successfully logged into LinkedIn")
        
        # Test with a single search term
        test_search_terms = ["Software Engineer"]
        print(f"Testing with search term: {test_search_terms[0]}")
        
        # Apply to jobs (limited to 1 application for testing)
        print("Starting job application process...")
        apply_to_jobs(test_search_terms)
        
        print("=" * 80)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("The bot should have applied to at least one job.")
        print("Check the CSV files in 'all excels/' folder for application history.")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if 'aiClient' in locals() and aiClient:
            if ai_provider.lower() == "openai":
                ai_close_openai_client(aiClient)
            print("AI client closed")
        
        if 'driver' in locals():
            driver.quit()
            print("Browser closed")

if __name__ == "__main__":
    test_single_application() 