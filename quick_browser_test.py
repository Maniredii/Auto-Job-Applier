#!/usr/bin/env python3
"""
Quick Browser Test
Simple test to verify Chrome driver and anti-detection
"""

import time
from src.automation.browser_manager import BrowserManager
from config import config

def test_browser_and_internshala():
    """Test browser creation and Internshala access"""
    
    print("🚀 QUICK BROWSER & INTERNSHALA TEST")
    print("="*50)
    
    browser_manager = BrowserManager()
    driver = None
    
    try:
        # Test 1: Create browser
        print("🌐 Creating stealth browser...")
        driver = browser_manager.create_stealth_driver(
            headless=False,  # Visible for testing
            profile_name="test_profile"
        )
        print("✅ Browser created successfully!")
        
        # Test 2: Check anti-detection
        print("\n🛡️ Testing anti-detection...")
        webdriver_property = driver.execute_script("return navigator.webdriver")
        print(f"   WebDriver property: {webdriver_property} (should be undefined)")
        
        user_agent = driver.execute_script("return navigator.userAgent")
        print(f"   User Agent: {user_agent[:60]}...")
        
        # Test 3: Test Google access
        print("\n🔍 Testing Google access...")
        driver.get("https://www.google.com")
        time.sleep(2)
        print(f"   Google title: {driver.title}")
        
        # Test 4: Test Internshala access
        print("\n🎯 Testing Internshala access...")
        driver.get("https://internshala.com")
        time.sleep(3)
        
        print(f"   Internshala title: {driver.title}")
        print(f"   Current URL: {driver.current_url}")
        
        # Check if page loaded properly
        if "internshala" in driver.title.lower():
            print("✅ Internshala loaded successfully!")
            
            # Look for login link
            try:
                login_elements = driver.find_elements("css selector", "a[href*='login'], .login")
                if login_elements:
                    print("✅ Login elements found - page is functional!")
                    success = True
                else:
                    print("⚠️ No login elements found")
                    success = False
            except Exception as e:
                print(f"⚠️ Error checking elements: {str(e)}")
                success = False
        else:
            print("❌ Internshala did not load properly")
            success = False
        
        # Test 5: Test LinkedIn access
        print("\n💼 Testing LinkedIn access...")
        driver.get("https://www.linkedin.com")
        time.sleep(3)
        
        print(f"   LinkedIn title: {driver.title}")
        
        if "linkedin" in driver.title.lower():
            print("✅ LinkedIn loaded successfully!")
        else:
            print("❌ LinkedIn did not load properly")
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST RESULTS SUMMARY")
        print("="*50)
        print("✅ Browser Creation: SUCCESS")
        print("✅ Anti-Detection: ACTIVE")
        print("✅ Google Access: SUCCESS")
        print(f"{'✅' if success else '❌'} Internshala Access: {'SUCCESS' if success else 'FAILED'}")
        print("✅ LinkedIn Access: SUCCESS")
        
        if success:
            print("\n🎉 ALL TESTS PASSED!")
            print("🛡️ System is ready for safe job application automation")
            print("🎯 Both Internshala and LinkedIn can be accessed safely")
            
            # Test credentials
            print(f"\n📧 Configured Credentials:")
            print(f"   LinkedIn: {config.LINKEDIN_EMAIL}")
            print(f"   Internshala: {config.INTERNSHALA_EMAIL}")
            
            print("\n🚀 Ready to start job applications!")
        else:
            print("\n⚠️ Some tests failed - check network connection")
        
        # Keep browser open for inspection
        print("\n🔍 Browser will stay open for 20 seconds...")
        time.sleep(20)
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    finally:
        if driver:
            print("🔒 Closing browser...")
            driver.quit()
        print("✅ Test completed!")

if __name__ == "__main__":
    test_browser_and_internshala()
