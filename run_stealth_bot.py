#!/usr/bin/env python3
"""
Enhanced Stealth LinkedIn Bot Runner
Military-grade bot detection bypass with comprehensive testing
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.helpers import print_lg

def close_all_chrome():
    """Close all Chrome processes to ensure clean start."""
    print_lg("🔄 Closing all Chrome processes...")
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True, check=False)
            subprocess.run(["taskkill", "/f", "/im", "chromedriver.exe"], 
                         capture_output=True, check=False)
        else:  # Unix-like
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True, check=False)
            subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True, check=False)
        
        time.sleep(3)  # Wait for processes to fully close
        print_lg("✅ Chrome processes closed")
        
    except Exception as e:
        print_lg(f"⚠️ Error closing Chrome: {e}")

def test_stealth_effectiveness():
    """Test the effectiveness of stealth mode."""
    print_lg("🧪 Testing stealth effectiveness...")
    
    try:
        # Run bot detection test
        result = subprocess.run([sys.executable, "test_bot_detection.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_lg("✅ Stealth test completed successfully")
            return True
        else:
            print_lg(f"⚠️ Stealth test had issues: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_lg("⏰ Stealth test timed out")
        return False
    except Exception as e:
        print_lg(f"❌ Stealth test failed: {e}")
        return False

def check_stealth_dependencies():
    """Check if all stealth dependencies are installed."""
    print_lg("📦 Checking stealth dependencies...")
    
    required_packages = [
        'undetected-chromedriver',
        'selenium',
        'fake-useragent'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_lg(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print_lg(f"❌ {package}")
    
    if missing:
        print_lg(f"📥 Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)
            print_lg("✅ All dependencies installed!")
            return True
        except subprocess.CalledProcessError as e:
            print_lg(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def run_enhanced_bot():
    """Run the enhanced bot with full stealth features."""
    print_lg("🚀 Starting Enhanced LinkedIn Bot with MILITARY-GRADE STEALTH...")
    
    try:
        # Import and run enhanced bot
        from enhanced_job_bot import main as run_enhanced
        run_enhanced()
        
    except ImportError:
        print_lg("⚠️ Enhanced bot not available, running standard bot with stealth...")
        try:
            from runAiBot import main as run_standard
            run_standard()
        except Exception as e:
            print_lg(f"❌ Failed to run standard bot: {e}")
    
    except Exception as e:
        print_lg(f"❌ Enhanced bot failed: {e}")
        print_lg("🛡️ Trying fallback options...")
        
        # Fallback to standard bot
        try:
            from runAiBot import main as run_standard
            run_standard()
        except Exception as e2:
            print_lg(f"❌ Fallback also failed: {e2}")

def display_stealth_status():
    """Display current stealth configuration status."""
    print_lg("\n🔒 STEALTH CONFIGURATION STATUS")
    print_lg("="*50)
    
    try:
        from config.settings import (stealth_mode, enable_human_behavior, 
                                   randomize_timing, enable_break_simulation,
                                   use_proxy, proxy_server)
        
        print_lg(f"🕵️ Stealth Mode: {'✅ ENABLED' if stealth_mode else '❌ DISABLED'}")
        print_lg(f"🤖 Human Behavior: {'✅ ENABLED' if enable_human_behavior else '❌ DISABLED'}")
        print_lg(f"⏰ Random Timing: {'✅ ENABLED' if randomize_timing else '❌ DISABLED'}")
        print_lg(f"☕ Break Simulation: {'✅ ENABLED' if enable_break_simulation else '❌ DISABLED'}")
        print_lg(f"🌐 Proxy Support: {'✅ ENABLED' if use_proxy else '❌ DISABLED'}")
        
        if use_proxy and proxy_server:
            print_lg(f"🔗 Proxy Server: {proxy_server}")
        
        # Calculate stealth score
        stealth_features = [stealth_mode, enable_human_behavior, randomize_timing, enable_break_simulation]
        stealth_score = sum(stealth_features) / len(stealth_features) * 100
        
        print_lg(f"\n🎯 Stealth Score: {stealth_score:.0f}%")
        
        if stealth_score >= 75:
            print_lg("🛡️ STEALTH LEVEL: MILITARY-GRADE")
        elif stealth_score >= 50:
            print_lg("🔒 STEALTH LEVEL: ADVANCED")
        elif stealth_score >= 25:
            print_lg("⚠️ STEALTH LEVEL: BASIC")
        else:
            print_lg("❌ STEALTH LEVEL: MINIMAL")
        
    except ImportError as e:
        print_lg(f"❌ Could not load stealth settings: {e}")

def main():
    """Main stealth bot runner."""
    print_lg("🚀 ENHANCED STEALTH LINKEDIN BOT")
    print_lg("="*60)
    print_lg("🔒 Military-Grade Bot Detection Bypass")
    print_lg("🤖 Advanced Human Behavior Simulation")
    print_lg("📊 AI-Powered Job Matching")
    print_lg("🤝 Intelligent Networking")
    print_lg("="*60)
    print_lg(f"⏰ Started at: {datetime.now()}")
    
    # Step 1: Display stealth status
    display_stealth_status()
    
    # Step 2: Check dependencies
    if not check_stealth_dependencies():
        print_lg("❌ Dependency check failed. Please install requirements manually.")
        return
    
    # Step 3: Close existing Chrome
    close_all_chrome()
    
    # Step 4: Test stealth effectiveness (optional)
    print_lg("\n🎯 STARTUP OPTIONS:")
    print_lg("1. Run Bot with Stealth Testing (Recommended)")
    print_lg("2. Run Bot Immediately (Skip Testing)")
    print_lg("3. Test Stealth Only (No Bot Run)")
    print_lg("4. Exit")
    
    while True:
        try:
            choice = input("\n👉 Select option (1-4): ").strip()
            
            if choice == "1":
                print_lg("\n🧪 Running stealth effectiveness test first...")
                if test_stealth_effectiveness():
                    print_lg("✅ Stealth test passed! Starting bot...")
                    run_enhanced_bot()
                else:
                    print_lg("⚠️ Stealth test had issues. Continue anyway? (y/n)")
                    if input().lower().startswith('y'):
                        run_enhanced_bot()
                break
                
            elif choice == "2":
                print_lg("\n🚀 Starting bot immediately...")
                run_enhanced_bot()
                break
                
            elif choice == "3":
                print_lg("\n🧪 Running stealth test only...")
                test_stealth_effectiveness()
                break
                
            elif choice == "4":
                print_lg("👋 Goodbye!")
                break
                
            else:
                print_lg("❌ Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print_lg("\n👋 Goodbye!")
            break
        except Exception as e:
            print_lg(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_lg("\n⏹️ Bot stopped by user")
    except Exception as e:
        print_lg(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_lg("\n🧹 Cleaning up...")
        close_all_chrome()
