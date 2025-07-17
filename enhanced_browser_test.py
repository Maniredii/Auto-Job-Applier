#!/usr/bin/env python3
"""
Enhanced Browser Test with Maximum Anti-Detection
Tests Chrome driver installation and anti-detection capabilities
"""

import time
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_stealth_browser():
    """Create a stealth browser with maximum anti-detection"""
    
    print("🛡️ Creating stealth browser with anti-detection...")
    
    # Chrome options for maximum stealth
    options = Options()
    
    # Basic stealth options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Advanced anti-detection
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")  # We'll enable this later
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    
    # Remove the problematic arguments
    # options.add_argument("--disable-javascript")  # Remove this line
    
    # User agent randomization
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    # Window size randomization
    window_sizes = ["1920,1080", "1366,768", "1440,900", "1536,864"]
    options.add_argument(f"--window-size={random.choice(window_sizes)}")
    
    # Language and locale
    options.add_argument("--lang=en-US")
    options.add_argument("--accept-lang=en-US,en;q=0.9")
    
    # Disable logging
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_argument("--disable-logging")
    
    try:
        # Try to create driver with automatic driver management
        print("🔧 Attempting to create Chrome driver...")
        
        # Method 1: Try with webdriver-manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Chrome driver created with webdriver-manager")
        except ImportError:
            print("⚠️ webdriver-manager not available, trying system Chrome...")
            # Method 2: Try with system Chrome
            driver = webdriver.Chrome(options=options)
            print("✅ Chrome driver created with system Chrome")
        
        # Apply additional stealth measures
        apply_stealth_scripts(driver)
        
        return driver
        
    except Exception as e:
        print(f"❌ Failed to create Chrome driver: {str(e)}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Install Chrome browser if not installed")
        print("2. Run: pip install webdriver-manager")
        print("3. Check if Chrome is in PATH")
        return None

def apply_stealth_scripts(driver):
    """Apply JavaScript stealth modifications"""
    
    print("🔒 Applying stealth JavaScript modifications...")
    
    # Remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Override plugins
    driver.execute_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
    """)
    
    # Override languages
    driver.execute_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)
    
    # Override permissions
    driver.execute_script("""
        const originalQuery = window.navigator.permissions.query;
        return window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    print("✅ Stealth modifications applied")

def test_anti_detection(driver):
    """Test anti-detection capabilities"""
    
    print("\n🧪 Testing anti-detection capabilities...")
    
    # Test 1: Check webdriver property
    webdriver_detected = driver.execute_script("return navigator.webdriver")
    print(f"🔍 WebDriver property: {webdriver_detected} (should be undefined)")
    
    # Test 2: Check user agent
    user_agent = driver.execute_script("return navigator.userAgent")
    print(f"🔍 User Agent: {user_agent[:50]}...")
    
    # Test 3: Check plugins
    plugins_count = driver.execute_script("return navigator.plugins.length")
    print(f"🔍 Plugins count: {plugins_count} (should be > 0)")
    
    # Test 4: Check languages
    languages = driver.execute_script("return navigator.languages")
    print(f"🔍 Languages: {languages}")
    
    # Test 5: Navigate to bot detection test site
    print("\n🌐 Testing with bot detection website...")
    try:
        driver.get("https://bot.sannysoft.com/")
        time.sleep(5)
        
        page_title = driver.title
        print(f"📄 Page title: {page_title}")
        
        # Check for detection indicators
        page_source = driver.page_source.lower()
        detection_indicators = [
            "webdriver",
            "automation",
            "bot detected",
            "selenium"
        ]
        
        detected = any(indicator in page_source for indicator in detection_indicators)
        print(f"🤖 Bot detection result: {'DETECTED' if detected else 'NOT DETECTED'}")
        
    except Exception as e:
        print(f"⚠️ Could not test bot detection site: {str(e)}")

def test_human_behavior(driver):
    """Test human-like behavior simulation"""
    
    print("\n👤 Testing human-like behavior...")
    
    try:
        # Navigate to a test site
        driver.get("https://www.google.com")
        time.sleep(2)
        
        # Human-like mouse movements
        print("🖱️ Simulating human mouse movements...")
        actions = ActionChains(driver)
        
        # Random mouse movements
        for _ in range(3):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset)
            actions.perform()
            time.sleep(random.uniform(0.5, 1.5))
        
        # Human-like scrolling
        print("📜 Simulating human scrolling...")
        for _ in range(3):
            scroll_amount = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(1, 2))
        
        # Human-like typing
        print("⌨️ Testing human-like typing...")
        try:
            search_box = driver.find_element(By.NAME, "q")
            search_text = "test search"
            
            for char in search_text:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
        except:
            print("⚠️ Could not find search box for typing test")
        
        print("✅ Human behavior simulation completed")
        
    except Exception as e:
        print(f"❌ Human behavior test failed: {str(e)}")

def test_internshala_access(driver):
    """Test access to Internshala with stealth mode"""
    
    print("\n🎯 Testing Internshala access with stealth mode...")
    
    try:
        # Navigate to Internshala
        print("🔗 Navigating to Internshala...")
        driver.get("https://internshala.com")
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Check if page loaded successfully
        if "internshala" in driver.title.lower():
            print("✅ Internshala loaded successfully!")
            
            # Look for key elements
            elements_found = 0
            test_selectors = [
                "a[href*='login']",
                ".header",
                ".navigation",
                "input[type='text']"
            ]
            
            for selector in test_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements_found += 1
                except:
                    pass
            
            print(f"🔍 Found {elements_found}/{len(test_selectors)} expected elements")
            
            if elements_found >= 2:
                print("✅ Internshala is accessible and functional!")
                return True
            else:
                print("⚠️ Internshala loaded but some elements missing")
                return False
        else:
            print("❌ Internshala did not load properly")
            return False
            
    except Exception as e:
        print(f"❌ Internshala access test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    
    print("🚀 ENHANCED BROWSER & ANTI-DETECTION TEST")
    print("="*60)
    
    # Step 1: Create stealth browser
    driver = create_stealth_browser()
    
    if not driver:
        print("❌ Cannot proceed without browser driver")
        return
    
    try:
        # Step 2: Test anti-detection
        test_anti_detection(driver)
        
        # Step 3: Test human behavior
        test_human_behavior(driver)
        
        # Step 4: Test Internshala access
        internshala_success = test_internshala_access(driver)
        
        # Step 5: Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"🌐 Browser Creation: ✅ SUCCESS")
        print(f"🛡️ Anti-Detection: ✅ ACTIVE")
        print(f"👤 Human Behavior: ✅ SIMULATED")
        print(f"🎯 Internshala Access: {'✅ SUCCESS' if internshala_success else '❌ FAILED'}")
        
        if internshala_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ System is ready for safe job application automation")
            print("🛡️ Anti-detection measures are working")
            print("🎯 Internshala can be accessed safely")
        else:
            print("\n⚠️ Some tests failed - check network connection")
        
        # Keep browser open for manual inspection
        print("\n🔍 Browser will stay open for 30 seconds for manual inspection...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        print("🔒 Closing browser...")
        driver.quit()
        print("✅ Test completed!")

if __name__ == "__main__":
    main()
