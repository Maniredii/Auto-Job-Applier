#!/usr/bin/env python3
"""
Bot Detection Test Script
Tests the effectiveness of stealth mode against various detection methods
"""

import sys
import os
import time
import json
from datetime import datetime

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.stealth_engine import StealthEngine
from modules.bot_detection_tester import BotDetectionTester
from modules.helpers import print_lg
from config.settings import stealth_mode

def test_standard_chrome():
    """Test standard Chrome driver for bot detection."""
    print_lg("🔍 Testing STANDARD Chrome driver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        
        # Run bot detection tests
        tester = BotDetectionTester(driver)
        results = tester.run_comprehensive_test()
        
        tester.print_test_summary()
        tester.save_test_results("data/standard_chrome_test.json")
        
        driver.quit()
        return results
        
    except Exception as e:
        print_lg(f"❌ Standard Chrome test failed: {e}")
        return None

def test_undetected_chrome():
    """Test undetected Chrome driver for bot detection."""
    print_lg("🕵️ Testing UNDETECTED Chrome driver...")
    
    try:
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = uc.Chrome(options=options, version_main=None)
        
        # Run bot detection tests
        tester = BotDetectionTester(driver)
        results = tester.run_comprehensive_test()
        
        tester.print_test_summary()
        tester.save_test_results("data/undetected_chrome_test.json")
        
        driver.quit()
        return results
        
    except Exception as e:
        print_lg(f"❌ Undetected Chrome test failed: {e}")
        return None

def test_enhanced_stealth():
    """Test enhanced stealth mode with all features."""
    print_lg("🚀 Testing ENHANCED STEALTH mode...")
    
    try:
        stealth_engine = StealthEngine()
        
        # Get enhanced Chrome options
        options = stealth_engine.get_enhanced_chrome_options()
        
        # Setup stealth driver
        driver = stealth_engine.setup_stealth_driver(options)
        
        # Run bot detection tests
        tester = BotDetectionTester(driver)
        results = tester.run_comprehensive_test()
        
        tester.print_test_summary()
        tester.save_test_results("data/enhanced_stealth_test.json")
        
        driver.quit()
        return results
        
    except Exception as e:
        print_lg(f"❌ Enhanced stealth test failed: {e}")
        return None

def test_linkedin_specific():
    """Test LinkedIn-specific bot detection."""
    print_lg("🔗 Testing LinkedIn-specific detection...")
    
    try:
        stealth_engine = StealthEngine()
        options = stealth_engine.get_enhanced_chrome_options()
        driver = stealth_engine.setup_stealth_driver(options)
        
        # Navigate to LinkedIn
        print_lg("🌐 Navigating to LinkedIn...")
        driver.get("https://www.linkedin.com")
        
        # Wait and check for detection
        time.sleep(5)
        
        # Check page source for detection indicators
        page_source = driver.page_source.lower()
        
        detection_indicators = [
            "unusual activity",
            "automated behavior", 
            "suspicious activity",
            "verify you're human",
            "captcha",
            "security check",
            "challenge",
            "blocked"
        ]
        
        detected = []
        for indicator in detection_indicators:
            if indicator in page_source:
                detected.append(indicator)
        
        if detected:
            print_lg(f"❌ LinkedIn detection triggered: {detected}")
            return False
        else:
            print_lg("✅ LinkedIn detection bypassed successfully!")
            return True
            
    except Exception as e:
        print_lg(f"❌ LinkedIn test failed: {e}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

def compare_results(standard_results, undetected_results, enhanced_results):
    """Compare results from different testing methods."""
    print_lg("\n" + "="*80)
    print_lg("📊 COMPARISON RESULTS")
    print_lg("="*80)
    
    methods = [
        ("Standard Chrome", standard_results),
        ("Undetected Chrome", undetected_results), 
        ("Enhanced Stealth", enhanced_results)
    ]
    
    for method_name, results in methods:
        if results:
            risk_assessment = results.get('risk_assessment', {})
            risk_level = risk_assessment.get('level', 'UNKNOWN')
            risk_score = risk_assessment.get('score', 0)
            
            print_lg(f"\n🔍 {method_name}:")
            print_lg(f"   Risk Level: {risk_level}")
            print_lg(f"   Risk Score: {risk_score}/100")
            
            # Show specific detection results
            webdriver_detected = results.get('webdriver_detection', {}).get('webdriver_property', False)
            linkedin_detected = results.get('linkedin_detection', {}).get('bot_detected', False)
            
            print_lg(f"   Webdriver Detected: {'❌ YES' if webdriver_detected else '✅ NO'}")
            print_lg(f"   LinkedIn Detected: {'❌ YES' if linkedin_detected else '✅ NO'}")
        else:
            print_lg(f"\n❌ {method_name}: Test failed")
    
    print_lg("="*80)

def generate_recommendations(results):
    """Generate recommendations based on test results."""
    print_lg("\n💡 RECOMMENDATIONS:")
    print_lg("-"*50)
    
    if not results:
        print_lg("❌ No test results available for recommendations")
        return
    
    risk_assessment = results.get('risk_assessment', {})
    risk_level = risk_assessment.get('level', 'UNKNOWN')
    
    if risk_level == "CRITICAL":
        print_lg("🚨 CRITICAL: Immediate action required!")
        print_lg("   • Use enhanced stealth mode")
        print_lg("   • Enable all anti-detection features")
        print_lg("   • Consider using proxy servers")
        print_lg("   • Implement human behavior simulation")
        
    elif risk_level == "HIGH":
        print_lg("⚠️ HIGH: Significant improvements needed")
        print_lg("   • Enable stealth mode")
        print_lg("   • Use undetected-chromedriver")
        print_lg("   • Add random delays and human behavior")
        
    elif risk_level == "MEDIUM":
        print_lg("🔶 MEDIUM: Some improvements recommended")
        print_lg("   • Fine-tune stealth settings")
        print_lg("   • Monitor for detection patterns")
        
    elif risk_level == "LOW":
        print_lg("✅ LOW: Current configuration is effective")
        print_lg("   • Continue monitoring")
        print_lg("   • Consider minor optimizations")
    
    # Specific recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print_lg("\n🎯 Specific Actions:")
        for rec in recommendations:
            print_lg(f"   • {rec}")

def main():
    """Main testing function."""
    print_lg("🚀 Bot Detection Bypass Testing Suite")
    print_lg("="*80)
    print_lg(f"⏰ Test started at: {datetime.now()}")
    print_lg(f"🔧 Current stealth mode setting: {stealth_mode}")
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Test different configurations
    print_lg("\n🧪 Running comprehensive bot detection tests...")
    
    # Test 1: Standard Chrome
    standard_results = test_standard_chrome()
    time.sleep(2)
    
    # Test 2: Undetected Chrome
    undetected_results = test_undetected_chrome()
    time.sleep(2)
    
    # Test 3: Enhanced Stealth
    enhanced_results = test_enhanced_stealth()
    time.sleep(2)
    
    # Test 4: LinkedIn-specific
    linkedin_success = test_linkedin_specific()
    
    # Compare results
    compare_results(standard_results, undetected_results, enhanced_results)
    
    # Generate recommendations based on best results
    best_results = enhanced_results or undetected_results or standard_results
    generate_recommendations(best_results)
    
    # Final summary
    print_lg(f"\n🏁 Testing completed at: {datetime.now()}")
    print_lg("📁 Test results saved in data/ directory")
    
    if linkedin_success:
        print_lg("✅ LinkedIn detection bypass: SUCCESSFUL")
    else:
        print_lg("❌ LinkedIn detection bypass: FAILED")
    
    print_lg("\n🎯 Next Steps:")
    print_lg("   1. Review test results in data/ directory")
    print_lg("   2. Implement recommended improvements")
    print_lg("   3. Re-run tests to verify improvements")
    print_lg("   4. Enable stealth mode in config/settings.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_lg("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print_lg(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
