#!/usr/bin/env python3
"""
Basic Chrome Test
Very simple test to see if Chrome works at all
"""

import time
import sys

def test_basic_chrome():
    """Test basic Chrome functionality"""
    
    print("🧪 BASIC CHROME TEST")
    print("="*30)
    
    try:
        print("📦 Importing selenium...")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium imported successfully")
        
        print("🔧 Creating Chrome options...")
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        print("✅ Chrome options created")
        
        print("🌐 Creating Chrome driver...")
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome driver created successfully!")
        
        print("🔗 Navigating to Google...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        if "google" in driver.title.lower():
            print("✅ Google loaded successfully!")
            
            print("🎯 Testing Internshala access...")
            driver.get("https://internshala.com")
            time.sleep(3)
            
            print(f"📄 Internshala title: {driver.title}")
            
            if "internshala" in driver.title.lower():
                print("✅ Internshala loaded successfully!")
                print("🎉 CHROME IS WORKING!")
                success = True
            else:
                print("❌ Internshala failed to load")
                success = False
        else:
            print("❌ Google failed to load")
            success = False
        
        print("🔒 Closing browser...")
        driver.quit()
        
        return success
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Try: pip install selenium")
        return False
        
    except Exception as e:
        print(f"❌ Chrome test failed: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Install Google Chrome browser")
        print("2. Update Chrome to latest version")
        print("3. Run: pip install selenium webdriver-manager")
        print("4. Check if Chrome is in PATH")
        return False

def test_with_webdriver_manager():
    """Test with webdriver-manager"""
    
    print("\n🔧 TESTING WITH WEBDRIVER-MANAGER")
    print("="*40)
    
    try:
        print("📦 Importing webdriver-manager...")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options
        print("✅ Webdriver-manager imported")
        
        print("⬇️ Installing Chrome driver...")
        service = Service(ChromeDriverManager().install())
        print("✅ Chrome driver installed")
        
        print("🔧 Creating options...")
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        print("🌐 Creating driver with service...")
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Driver created with webdriver-manager!")
        
        print("🔗 Testing navigation...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        print(f"📄 Title: {driver.title}")
        
        driver.quit()
        print("✅ Webdriver-manager test successful!")
        return True
        
    except ImportError:
        print("❌ webdriver-manager not installed")
        print("   Run: pip install webdriver-manager")
        return False
        
    except Exception as e:
        print(f"❌ Webdriver-manager test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 CHROME DRIVER DIAGNOSTIC TEST")
    print("="*50)
    
    # Test 1: Basic Chrome
    basic_success = test_basic_chrome()
    
    # Test 2: Webdriver-manager (if basic failed)
    if not basic_success:
        webdriver_success = test_with_webdriver_manager()
    else:
        webdriver_success = True
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    print(f"🌐 Basic Chrome: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"🔧 Webdriver-manager: {'✅ PASS' if webdriver_success else '❌ FAIL'}")
    
    if basic_success or webdriver_success:
        print("\n🎉 CHROME IS WORKING!")
        print("✅ Ready to proceed with Internshala job applications")
        
        print("\n🚀 Next steps:")
        print("1. Run: python internshala_simple_applier.py")
        print("2. Or run: python quick_browser_test.py")
        
    else:
        print("\n❌ CHROME SETUP ISSUES")
        print("🔧 Try these solutions:")
        print("1. Install Google Chrome: https://www.google.com/chrome/")
        print("2. Run: pip install selenium webdriver-manager")
        print("3. Restart your computer")
        print("4. Try running as administrator")

if __name__ == "__main__":
    main()
