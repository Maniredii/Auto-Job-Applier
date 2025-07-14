#!/usr/bin/env python3
"""
Chrome Driver Fix Script
Resolves common Chrome driver issues with the enhanced job bot
"""

import os
import sys
import subprocess
import shutil
import requests
import zipfile
import platform
from pathlib import Path

def close_chrome_processes():
    """Close all Chrome processes"""
    print("🔄 Closing all Chrome processes...")
    
    system = platform.system().lower()
    
    if system == "windows":
        try:
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True, check=False)
            subprocess.run(["taskkill", "/f", "/im", "chromedriver.exe"], 
                         capture_output=True, check=False)
            print("✅ Chrome processes closed on Windows")
        except Exception as e:
            print(f"⚠️ Error closing Chrome processes: {e}")
    
    elif system in ["linux", "darwin"]:  # Linux or macOS
        try:
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True, check=False)
            subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True, check=False)
            print("✅ Chrome processes closed on Unix-like system")
        except Exception as e:
            print(f"⚠️ Error closing Chrome processes: {e}")

def clean_chrome_driver_cache():
    """Clean undetected-chromedriver cache"""
    print("🧹 Cleaning Chrome driver cache...")
    
    # Common cache locations
    cache_locations = [
        os.path.expanduser("~/.cache/undetected_chromedriver"),
        os.path.expanduser("~/AppData/Local/undetected_chromedriver"),
        os.path.expanduser("~/Library/Caches/undetected_chromedriver"),
        "./undetected_chromedriver",
        "./.cache/undetected_chromedriver"
    ]
    
    for cache_path in cache_locations:
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path)
                print(f"✅ Removed cache: {cache_path}")
            except Exception as e:
                print(f"⚠️ Could not remove {cache_path}: {e}")

def reinstall_undetected_chromedriver():
    """Reinstall undetected-chromedriver"""
    print("📦 Reinstalling undetected-chromedriver...")
    
    try:
        # Uninstall current version
        subprocess.run([sys.executable, "-m", "pip", "uninstall", 
                       "undetected-chromedriver", "-y"], check=True)
        print("✅ Uninstalled old undetected-chromedriver")
        
        # Install latest version
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "undetected-chromedriver", "--upgrade"], check=True)
        print("✅ Installed latest undetected-chromedriver")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error reinstalling undetected-chromedriver: {e}")
        return False
    
    return True

def update_chrome_browser():
    """Check and suggest Chrome browser update"""
    print("🌐 Checking Chrome browser...")
    
    system = platform.system().lower()
    
    if system == "windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
    elif system == "darwin":  # macOS
        chrome_paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    else:  # Linux
        chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_found = True
            print(f"✅ Chrome found at: {path}")
            break
    
    if not chrome_found:
        print("❌ Chrome browser not found!")
        print("📥 Please install Google Chrome from: https://www.google.com/chrome/")
        return False
    
    print("💡 If issues persist, please update Chrome to the latest version")
    return True

def create_safe_mode_config():
    """Create a safe mode configuration"""
    print("🛡️ Creating safe mode configuration...")
    
    safe_config = '''# Safe Mode Configuration
# Temporary settings to resolve Chrome driver issues

# Disable stealth mode temporarily
stealth_mode = False

# Use standard Chrome options
run_in_background = False
disable_extensions = False
safe_mode = True

# Reduce application limits for testing
switch_number = 5
daily_application_limit = 10

print("✅ Safe mode configuration created")
print("📝 You can enable stealth mode later after confirming basic functionality")
'''
    
    try:
        with open("config/safe_mode_settings.py", "w") as f:
            f.write(safe_config)
        print("✅ Safe mode configuration saved to config/safe_mode_settings.py")
    except Exception as e:
        print(f"❌ Error creating safe mode config: {e}")

def test_basic_chrome_driver():
    """Test basic Chrome driver functionality"""
    print("🧪 Testing basic Chrome driver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Basic Chrome driver test successful! Page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Basic Chrome driver test failed: {e}")
        return False

def test_undetected_chrome_driver():
    """Test undetected Chrome driver"""
    print("🕵️ Testing undetected Chrome driver...")
    
    try:
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        
        driver = uc.Chrome(options=options, version_main=None)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Undetected Chrome driver test successful! Page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Undetected Chrome driver test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 Chrome Driver Fix Script")
    print("=" * 50)
    
    # Step 1: Close Chrome processes
    close_chrome_processes()
    
    # Step 2: Clean cache
    clean_chrome_driver_cache()
    
    # Step 3: Check Chrome browser
    if not update_chrome_browser():
        return
    
    # Step 4: Test basic Chrome driver
    if not test_basic_chrome_driver():
        print("❌ Basic Chrome driver failed. Please install ChromeDriver manually.")
        print("📥 Download from: https://chromedriver.chromium.org/")
        return
    
    # Step 5: Reinstall undetected-chromedriver
    if not reinstall_undetected_chromedriver():
        return
    
    # Step 6: Test undetected Chrome driver
    if test_undetected_chrome_driver():
        print("\n✅ All tests passed! You can now enable stealth mode.")
        print("📝 Edit config/settings.py and set stealth_mode = True")
    else:
        print("\n⚠️ Undetected Chrome driver still has issues.")
        print("🛡️ Creating safe mode configuration...")
        create_safe_mode_config()
        print("\n📋 Troubleshooting steps:")
        print("1. Run the bot with stealth_mode = False first")
        print("2. If that works, gradually enable stealth features")
        print("3. Check GitHub issues: https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues")
    
    print("\n🚀 You can now try running the enhanced job bot!")

if __name__ == "__main__":
    main()
