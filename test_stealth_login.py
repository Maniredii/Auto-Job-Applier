#!/usr/bin/env python3
"""
Stealth LinkedIn Login Test Script
Tests the stealth login functionality with your credentials
"""

import os
import sys
import time
from datetime import datetime

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.helpers import print_lg

def test_stealth_login():
    """Test stealth LinkedIn login with your credentials."""
    print_lg("🔐 Testing stealth LinkedIn login...")
    
    try:
        # Import credentials
        from config.secrets import username, password
        
        if not username or not password:
            print_lg("❌ LinkedIn credentials not configured")
            return False
        
        print_lg(f"📱 Using phone number: {username}")
        print_lg("🔒 Password configured")
        
        # Import stealth modules
        from modules.stealth_engine import StealthEngine
        from modules.stealth_login import perform_stealth_linkedin_login
        
        # Create stealth driver
        stealth_engine = StealthEngine()
        options = stealth_engine.get_enhanced_chrome_options()
        driver = stealth_engine.setup_stealth_driver(options)
        
        print_lg("✅ Stealth driver initialized")
        
        # Perform stealth login
        print_lg("🚀 Starting stealth login process...")
        start_time = time.time()
        
        login_success = perform_stealth_linkedin_login(driver, username, password)
        
        login_time = time.time() - start_time
        
        if login_success:
            print_lg(f"✅ Stealth login successful in {login_time:.2f} seconds!")
            
            # Verify we're logged in
            current_url = driver.current_url
            print_lg(f"📍 Current URL: {current_url}")
            
            # Check for login indicators
            login_indicators = [
                "/feed/",
                "/in/",
                "linkedin.com/feed"
            ]
            
            if any(indicator in current_url for indicator in login_indicators):
                print_lg("🎯 Login verification: SUCCESS")
                
                # Take a screenshot for verification
                try:
                    os.makedirs("test_outputs", exist_ok=True)
                    screenshot_path = f"test_outputs/login_success_{int(time.time())}.png"
                    driver.save_screenshot(screenshot_path)
                    print_lg(f"📸 Screenshot saved: {screenshot_path}")
                except Exception as e:
                    print_lg(f"⚠️ Could not save screenshot: {e}")
                
                # Test basic navigation
                test_basic_navigation(driver)
                
            else:
                print_lg("⚠️ Login verification: UNCERTAIN")
                print_lg("Manual verification may be required")
        
        else:
            print_lg("❌ Stealth login failed")
            
            # Take screenshot for debugging
            try:
                os.makedirs("test_outputs", exist_ok=True)
                screenshot_path = f"test_outputs/login_failed_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                print_lg(f"📸 Debug screenshot saved: {screenshot_path}")
            except Exception as e:
                print_lg(f"⚠️ Could not save debug screenshot: {e}")
        
        # Keep browser open for manual inspection
        print_lg("\n🔍 Browser will remain open for 30 seconds for manual inspection...")
        time.sleep(30)
        
        driver.quit()
        return login_success
        
    except Exception as e:
        print_lg(f"❌ Stealth login test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_navigation(driver):
    """Test basic LinkedIn navigation after login."""
    print_lg("🧭 Testing basic navigation...")
    
    try:
        # Test navigation to profile
        print_lg("📱 Navigating to profile...")
        
        # Look for profile link
        profile_selectors = [
            "//a[contains(@href, '/in/')]",
            "//button[contains(@aria-label, 'View profile')]",
            "//*[contains(@class, 'global-nav__me')]"
        ]
        
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(driver, 10)
        
        for selector in profile_selectors:
            try:
                profile_element = driver.find_element(By.XPATH, selector)
                if profile_element.is_displayed():
                    print_lg("✅ Profile link found")
                    break
            except:
                continue
        
        # Test navigation to jobs
        print_lg("💼 Testing jobs navigation...")
        try:
            driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            current_url = driver.current_url
            if "jobs" in current_url:
                print_lg("✅ Jobs page accessible")
            else:
                print_lg("⚠️ Jobs page navigation uncertain")
                
        except Exception as e:
            print_lg(f"⚠️ Jobs navigation failed: {e}")
        
        print_lg("✅ Basic navigation test completed")
        
    except Exception as e:
        print_lg(f"⚠️ Navigation test failed: {e}")

def test_bot_detection_after_login():
    """Test if bot is detected after login."""
    print_lg("🕵️ Testing bot detection after login...")
    
    try:
        from modules.bot_detection_tester import BotDetectionTester
        from modules.stealth_engine import StealthEngine
        from modules.stealth_login import perform_stealth_linkedin_login
        from config.secrets import username, password
        
        # Create stealth driver
        stealth_engine = StealthEngine()
        options = stealth_engine.get_enhanced_chrome_options()
        driver = stealth_engine.setup_stealth_driver(options)
        
        # Perform login
        login_success = perform_stealth_linkedin_login(driver, username, password)
        
        if not login_success:
            print_lg("❌ Cannot test detection - login failed")
            driver.quit()
            return False
        
        # Run bot detection tests
        tester = BotDetectionTester(driver)
        results = tester.run_comprehensive_test()
        
        # Print summary
        tester.print_test_summary()
        
        # Save results
        tester.save_test_results("test_outputs/post_login_detection_test.json")
        
        driver.quit()
        
        # Analyze results
        risk_assessment = results.get('risk_assessment', {})
        risk_level = risk_assessment.get('level', 'UNKNOWN')
        
        if risk_level in ['LOW', 'MINIMAL']:
            print_lg("🎉 SUCCESS: Bot detection bypassed after login!")
            return True
        else:
            print_lg(f"⚠️ WARNING: Risk level {risk_level} after login")
            return False
            
    except Exception as e:
        print_lg(f"❌ Bot detection test failed: {e}")
        return False

def main():
    """Main test function."""
    print_lg("🚀 STEALTH LINKEDIN LOGIN TEST SUITE")
    print_lg("="*60)
    print_lg("🔐 Testing with your configured credentials")
    print_lg(f"⏰ Started at: {datetime.now()}")
    
    # Create output directory
    os.makedirs("test_outputs", exist_ok=True)
    
    print_lg("\n🧪 Test 1: Basic Stealth Login")
    login_success = test_stealth_login()
    
    if login_success:
        print_lg("\n🧪 Test 2: Bot Detection After Login")
        detection_success = test_bot_detection_after_login()
        
        if detection_success:
            print_lg("\n🏆 ALL TESTS PASSED!")
            print_lg("✅ Stealth login working perfectly")
            print_lg("✅ Bot detection successfully bypassed")
            print_lg("✅ Ready for automated job applications")
        else:
            print_lg("\n⚠️ PARTIAL SUCCESS")
            print_lg("✅ Login successful")
            print_lg("⚠️ Some bot detection risks remain")
    else:
        print_lg("\n❌ LOGIN TEST FAILED")
        print_lg("Please check your credentials and try again")
    
    print_lg(f"\n🏁 Testing completed at: {datetime.now()}")
    print_lg("📁 Test outputs saved in test_outputs/ directory")
    
    print_lg("\n🎯 NEXT STEPS:")
    if login_success:
        print_lg("1. Your stealth login is working!")
        print_lg("2. Run the full bot: python run_stealth_bot.py")
        print_lg("3. Start automated job applications")
    else:
        print_lg("1. Check your LinkedIn credentials in config/secrets.py")
        print_lg("2. Ensure your account is not locked")
        print_lg("3. Try manual login first to verify credentials")
        print_lg("4. Run this test again after verification")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_lg("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print_lg(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
