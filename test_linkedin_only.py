#!/usr/bin/env python3
"""
Simple LinkedIn Test Script
Tests LinkedIn integration with your credentials
"""

import logging
import time
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.automation.browser_manager import BrowserManager
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_browser_creation():
    """Test if we can create a browser instance"""
    print("🌐 Testing Browser Creation...")
    
    try:
        browser_manager = BrowserManager()
        driver = browser_manager.create_stealth_driver(
            headless=False,  # Visible browser for testing
            profile_name="linkedin_test"
        )
        
        print("✅ Browser created successfully!")
        
        # Test basic navigation
        print("🔗 Testing navigation to LinkedIn...")
        driver.get("https://www.linkedin.com")
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Close browser
        driver.quit()
        print("✅ Browser test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Browser creation failed: {str(e)}")
        return False

def test_linkedin_credentials():
    """Test LinkedIn credentials"""
    print("\n🔐 Testing LinkedIn Credentials...")
    
    print(f"📧 Email/Phone: {config.LINKEDIN_EMAIL}")
    print(f"🔒 Password: {'*' * len(config.LINKEDIN_PASSWORD) if config.LINKEDIN_PASSWORD else 'NOT SET'}")
    print(f"📱 Phone: {config.LINKEDIN_PHONE}")
    
    if not config.LINKEDIN_EMAIL or not config.LINKEDIN_PASSWORD:
        print("❌ LinkedIn credentials not properly configured!")
        print("   Please check your .env file")
        return False
    
    print("✅ LinkedIn credentials are configured")
    return True

def test_linkedin_login():
    """Test LinkedIn login process"""
    print("\n🚀 Testing LinkedIn Login...")
    
    if not test_linkedin_credentials():
        return False
    
    try:
        # Initialize LinkedIn scraper
        scraper = LinkedInScraper()
        
        print("🔧 Initializing LinkedIn scraper...")
        scraper.initialize_driver()
        
        print("🔐 Attempting login...")
        login_success = scraper.login(config.LINKEDIN_EMAIL, config.LINKEDIN_PASSWORD)
        
        if login_success:
            print("✅ LinkedIn login successful!")
            
            # Test if we're actually logged in
            print("🔍 Verifying login status...")
            current_url = scraper.driver.current_url
            page_source = scraper.driver.page_source
            
            # Check for login indicators
            if "feed" in current_url or "mynetwork" in current_url:
                print("✅ Successfully logged into LinkedIn!")
                print(f"   Current URL: {current_url}")
            elif "challenge" in current_url or "checkpoint" in current_url:
                print("⚠️ LinkedIn security challenge detected")
                print("   You may need to complete verification manually")
            else:
                print(f"⚠️ Unexpected page after login: {current_url}")
            
            # Keep browser open for manual inspection
            print("\n🔍 Browser will stay open for 30 seconds for manual inspection...")
            print("   Check if login was successful and close browser manually if needed")
            time.sleep(30)
            
        else:
            print("❌ LinkedIn login failed!")
            print("   Please check your credentials")
        
        # Close scraper
        scraper.close()
        return login_success
        
    except Exception as e:
        print(f"❌ LinkedIn login test failed: {str(e)}")
        return False

def test_linkedin_job_search():
    """Test LinkedIn job search functionality"""
    print("\n🔍 Testing LinkedIn Job Search...")
    
    try:
        # Initialize LinkedIn scraper
        scraper = LinkedInScraper()
        scraper.initialize_driver()
        
        # Login first
        print("🔐 Logging in for job search test...")
        login_success = scraper.login(config.LINKEDIN_EMAIL, config.LINKEDIN_PASSWORD)
        
        if not login_success:
            print("❌ Cannot test job search - login failed")
            scraper.close()
            return False
        
        print("✅ Login successful, starting job search...")
        
        # Test job search
        jobs = scraper.scrape_jobs(
            job_title="Python Developer",
            location="Remote",
            max_jobs=5,
            date_posted="week"
        )
        
        print(f"✅ Job search completed! Found {len(jobs)} jobs")
        
        # Display results
        if jobs:
            print("\n📋 Sample Job Results:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"\n{i}. {job.title}")
                print(f"   🏢 Company: {job.company}")
                print(f"   📍 Location: {job.location}")
                print(f"   📅 Posted: {job.posted_date}")
                print(f"   🔗 URL: {job.url[:60]}...")
                if job.salary:
                    print(f"   💰 Salary: {job.salary}")
        else:
            print("⚠️ No jobs found - this might be normal depending on search criteria")
        
        scraper.close()
        return True
        
    except Exception as e:
        print(f"❌ LinkedIn job search test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 LinkedIn Integration Test")
    print("=" * 50)
    
    # Test 1: Browser creation
    browser_test = test_browser_creation()
    
    if not browser_test:
        print("\n❌ Browser test failed - cannot proceed with LinkedIn tests")
        print("   Please ensure Chrome browser is installed and accessible")
        return
    
    # Test 2: Credentials
    creds_test = test_linkedin_credentials()
    
    if not creds_test:
        print("\n❌ Credentials test failed - cannot proceed with login tests")
        return
    
    # Test 3: Login
    print("\n" + "=" * 50)
    user_input = input("🔐 Test LinkedIn login? This will open a browser window (y/n): ").lower().strip()
    
    if user_input == 'y':
        login_test = test_linkedin_login()
        
        if login_test:
            # Test 4: Job search
            print("\n" + "=" * 50)
            user_input = input("🔍 Test LinkedIn job search? (y/n): ").lower().strip()
            
            if user_input == 'y':
                test_linkedin_job_search()
    
    print("\n" + "=" * 50)
    print("✅ LinkedIn integration test completed!")
    
    print("\n📋 Summary:")
    print(f"   Browser Creation: {'✅ PASS' if browser_test else '❌ FAIL'}")
    print(f"   Credentials: {'✅ PASS' if creds_test else '❌ FAIL'}")
    
    print("\n🎯 Next Steps:")
    print("1. If login worked, you can now use the full job application system")
    print("2. Configure job search preferences in your .env file")
    print("3. Add your resume to ./data/resumes/ folder")
    print("4. Run the main application: python main.py")

if __name__ == "__main__":
    main()
