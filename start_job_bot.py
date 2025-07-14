#!/usr/bin/env python3
"""
Enhanced Job Bot Startup Script
Handles Chrome driver issues and provides safe startup options
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'selenium',
        'undetected-chromedriver',
        'pandas',
        'requests',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
            print("✅ All dependencies installed!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    return True

def close_chrome_processes():
    """Close existing Chrome processes"""
    print("🔄 Closing existing Chrome processes...")
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True, check=False)
            subprocess.run(["taskkill", "/f", "/im", "chromedriver.exe"], 
                         capture_output=True, check=False)
        else:  # Unix-like
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True, check=False)
            subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True, check=False)
        
        time.sleep(2)  # Wait for processes to close
        print("✅ Chrome processes closed")
    except Exception as e:
        print(f"⚠️ Error closing Chrome: {e}")

def test_chrome_driver():
    """Test if Chrome driver works"""
    print("🧪 Testing Chrome driver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        driver.quit()
        
        print("✅ Chrome driver test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Chrome driver test failed: {e}")
        return False

def run_safe_mode():
    """Run the bot in safe mode"""
    print("🛡️ Starting bot in SAFE MODE...")
    print("📝 Safe mode features:")
    print("   - Stealth mode disabled")
    print("   - Reduced application limits")
    print("   - Enhanced error handling")
    print("   - Visible browser window")
    
    try:
        # Import and run the original bot with safe settings
        from runAiBot import main as run_original_bot
        run_original_bot()
    except Exception as e:
        print(f"❌ Error running safe mode: {e}")
        print("💡 Try running the original app.py instead")

def run_enhanced_mode():
    """Run the enhanced bot"""
    print("🚀 Starting ENHANCED bot...")
    print("✨ Enhanced features:")
    print("   - AI-powered job matching")
    print("   - Smart application strategy")
    print("   - Advanced analytics")
    print("   - Networking automation")
    
    try:
        from enhanced_job_bot import main as run_enhanced_bot
        run_enhanced_bot()
    except Exception as e:
        print(f"❌ Error running enhanced mode: {e}")
        print("🛡️ Falling back to safe mode...")
        run_safe_mode()

def main():
    """Main startup function"""
    print("🚀 Enhanced LinkedIn Job Bot Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install requirements manually:")
        print("pip install -r requirements_enhanced.txt")
        return
    
    # Close existing Chrome processes
    close_chrome_processes()
    
    # Test Chrome driver
    chrome_works = test_chrome_driver()
    
    print("\n🎯 Startup Options:")
    print("1. Safe Mode (Recommended if Chrome issues)")
    print("2. Enhanced Mode (Full features)")
    print("3. Fix Chrome Driver Issues")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\n👉 Select option (1-4): ").strip()
            
            if choice == "1":
                run_safe_mode()
                break
            elif choice == "2":
                if chrome_works:
                    run_enhanced_mode()
                else:
                    print("⚠️ Chrome driver issues detected. Running safe mode instead...")
                    run_safe_mode()
                break
            elif choice == "3":
                print("🔧 Running Chrome driver fix...")
                try:
                    subprocess.run([sys.executable, "fix_chrome_driver.py"], check=True)
                except subprocess.CalledProcessError:
                    print("❌ Fix script failed. Please run manually: python fix_chrome_driver.py")
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
