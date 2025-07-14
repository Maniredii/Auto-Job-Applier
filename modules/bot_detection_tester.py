# Author: Enhanced by AI Assistant
# Bot Detection Tester and Advanced Stealth Module
# Tests for bot detection and implements military-grade stealth techniques

import time
import random
import json
import base64
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.helpers import print_lg

class BotDetectionTester:
    """
    Advanced bot detection tester that checks for various detection methods.
    """
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.detection_results = {}
    
    def test_webdriver_detection(self) -> Dict[str, bool]:
        """Test for webdriver property detection."""
        print_lg("🔍 Testing webdriver property detection...")
        
        results = {}
        
        # Test 1: Check if webdriver property exists
        webdriver_exists = self.driver.execute_script("return navigator.webdriver")
        results['webdriver_property'] = webdriver_exists is not None
        
        # Test 2: Check for automation flags
        automation_flags = self.driver.execute_script("""
            return {
                webdriver: navigator.webdriver,
                chrome_runtime: window.chrome && window.chrome.runtime,
                permissions_query: navigator.permissions && navigator.permissions.query,
                plugins_length: navigator.plugins.length,
                languages: navigator.languages
            }
        """)
        
        results['automation_flags'] = automation_flags
        
        # Test 3: Check for common automation indicators
        automation_indicators = self.driver.execute_script("""
            return {
                webdriver_in_window: 'webdriver' in window,
                webdriver_in_navigator: 'webdriver' in navigator,
                selenium_ide: window._selenium,
                phantom_js: window.callPhantom || window._phantom,
                nightmare_js: window.__nightmare
            }
        """)
        
        results['automation_indicators'] = automation_indicators
        
        return results
    
    def test_chrome_detection(self) -> Dict[str, bool]:
        """Test for Chrome-specific detection methods."""
        print_lg("🔍 Testing Chrome-specific detection...")
        
        results = {}
        
        # Test Chrome object properties
        chrome_properties = self.driver.execute_script("""
            if (window.chrome) {
                return {
                    runtime_exists: !!window.chrome.runtime,
                    runtime_onconnect: !!window.chrome.runtime && !!window.chrome.runtime.onConnect,
                    app_exists: !!window.chrome.app,
                    csi_exists: !!window.chrome.csi,
                    loadtimes_exists: !!window.chrome.loadTimes
                }
            }
            return null;
        """)
        
        results['chrome_properties'] = chrome_properties
        
        # Test for missing Chrome properties (indicates automation)
        missing_properties = self.driver.execute_script("""
            const expectedProperties = ['app', 'runtime', 'csi'];
            const missing = [];
            
            if (window.chrome) {
                expectedProperties.forEach(prop => {
                    if (!window.chrome[prop]) {
                        missing.push(prop);
                    }
                });
            }
            
            return missing;
        """)
        
        results['missing_chrome_properties'] = missing_properties
        
        return results
    
    def test_behavioral_detection(self) -> Dict[str, bool]:
        """Test for behavioral detection patterns."""
        print_lg("🔍 Testing behavioral detection...")
        
        results = {}
        
        # Test mouse movement tracking
        self.driver.execute_script("""
            window.mouseMovements = [];
            document.addEventListener('mousemove', function(e) {
                window.mouseMovements.push({x: e.clientX, y: e.clientY, time: Date.now()});
            });
        """)
        
        # Simulate some mouse movements
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(self.driver)
        for _ in range(5):
            actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
            actions.pause(random.uniform(0.1, 0.3))
        actions.perform()
        
        time.sleep(1)
        
        # Check mouse movements
        mouse_data = self.driver.execute_script("return window.mouseMovements || []")
        results['mouse_movements_detected'] = len(mouse_data) > 0
        results['mouse_movement_count'] = len(mouse_data)
        
        # Test timing patterns
        timing_test = self.driver.execute_script("""
            const start = performance.now();
            // Simulate some work
            for (let i = 0; i < 1000; i++) {
                Math.random();
            }
            const end = performance.now();
            return end - start;
        """)
        
        results['timing_precision'] = timing_test
        
        return results
    
    def test_fingerprint_detection(self) -> Dict[str, any]:
        """Test browser fingerprinting detection."""
        print_lg("🔍 Testing fingerprint detection...")
        
        fingerprint = self.driver.execute_script("""
            return {
                userAgent: navigator.userAgent,
                language: navigator.language,
                languages: navigator.languages,
                platform: navigator.platform,
                cookieEnabled: navigator.cookieEnabled,
                doNotTrack: navigator.doNotTrack,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                screen: {
                    width: screen.width,
                    height: screen.height,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth
                },
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                plugins: Array.from(navigator.plugins).map(p => p.name),
                mimeTypes: Array.from(navigator.mimeTypes).map(m => m.type),
                canvas: (function() {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    ctx.textBaseline = 'top';
                    ctx.font = '14px Arial';
                    ctx.fillText('Bot detection test', 2, 2);
                    return canvas.toDataURL();
                })(),
                webgl: (function() {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl');
                    if (!gl) return null;
                    return {
                        vendor: gl.getParameter(gl.VENDOR),
                        renderer: gl.getParameter(gl.RENDERER)
                    };
                })()
            }
        """)
        
        return fingerprint
    
    def test_linkedin_specific_detection(self) -> Dict[str, bool]:
        """Test LinkedIn-specific bot detection."""
        print_lg("🔍 Testing LinkedIn-specific detection...")
        
        results = {}
        
        try:
            # Navigate to LinkedIn
            self.driver.get("https://www.linkedin.com")
            time.sleep(3)
            
            # Check for bot detection indicators
            page_source = self.driver.page_source.lower()
            
            # Common bot detection phrases
            detection_phrases = [
                "unusual activity",
                "automated behavior",
                "suspicious activity",
                "verify you're human",
                "captcha",
                "security check",
                "blocked",
                "restricted"
            ]
            
            detected_phrases = []
            for phrase in detection_phrases:
                if phrase in page_source:
                    detected_phrases.append(phrase)
            
            results['detection_phrases'] = detected_phrases
            results['bot_detected'] = len(detected_phrases) > 0
            
            # Check for specific LinkedIn detection elements
            detection_elements = [
                "challenge-page",
                "security-challenge",
                "captcha-container",
                "bot-detection"
            ]
            
            detected_elements = []
            for element_class in detection_elements:
                elements = self.driver.find_elements(By.CLASS_NAME, element_class)
                if elements:
                    detected_elements.append(element_class)
            
            results['detection_elements'] = detected_elements
            results['elements_detected'] = len(detected_elements) > 0
            
        except Exception as e:
            print_lg(f"Error testing LinkedIn detection: {e}")
            results['error'] = str(e)
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, any]:
        """Run all bot detection tests."""
        print_lg("🚀 Running comprehensive bot detection test...")
        
        test_results = {
            'timestamp': time.time(),
            'webdriver_detection': self.test_webdriver_detection(),
            'chrome_detection': self.test_chrome_detection(),
            'behavioral_detection': self.test_behavioral_detection(),
            'fingerprint_detection': self.test_fingerprint_detection(),
            'linkedin_detection': self.test_linkedin_specific_detection()
        }
        
        # Analyze overall detection risk
        risk_score = self._calculate_risk_score(test_results)
        test_results['risk_assessment'] = risk_score
        
        # Generate recommendations
        recommendations = self._generate_recommendations(test_results)
        test_results['recommendations'] = recommendations
        
        self.detection_results = test_results
        return test_results
    
    def _calculate_risk_score(self, results: Dict) -> Dict[str, any]:
        """Calculate overall bot detection risk score."""
        risk_factors = []
        
        # Webdriver detection risks
        if results['webdriver_detection'].get('webdriver_property'):
            risk_factors.append("Webdriver property detected")
        
        # Chrome detection risks
        chrome_results = results['chrome_detection']
        if chrome_results.get('missing_chrome_properties'):
            risk_factors.append("Missing Chrome properties")
        
        # LinkedIn detection risks
        linkedin_results = results['linkedin_detection']
        if linkedin_results.get('bot_detected'):
            risk_factors.append("LinkedIn bot detection triggered")
        
        # Behavioral risks
        behavioral_results = results['behavioral_detection']
        if behavioral_results.get('mouse_movement_count', 0) == 0:
            risk_factors.append("No natural mouse movements")
        
        # Calculate risk score (0-100)
        risk_score = min(100, len(risk_factors) * 25)
        
        risk_level = "LOW"
        if risk_score >= 75:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 25:
            risk_level = "MEDIUM"
        
        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors,
            'total_factors': len(risk_factors)
        }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        risk_assessment = results.get('risk_assessment', {})
        risk_factors = risk_assessment.get('factors', [])
        
        if "Webdriver property detected" in risk_factors:
            recommendations.append("Enable advanced webdriver property masking")
        
        if "Missing Chrome properties" in risk_factors:
            recommendations.append("Implement Chrome object property injection")
        
        if "LinkedIn bot detection triggered" in risk_factors:
            recommendations.append("Use more aggressive stealth techniques")
        
        if "No natural mouse movements" in risk_factors:
            recommendations.append("Enable human behavior simulation")
        
        if not recommendations:
            recommendations.append("Current stealth configuration appears effective")
        
        return recommendations
    
    def save_test_results(self, filepath: str = "data/bot_detection_test.json"):
        """Save test results to file."""
        try:
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(self.detection_results, f, indent=2)
            
            print_lg(f"✅ Test results saved to {filepath}")
        except Exception as e:
            print_lg(f"❌ Error saving test results: {e}")
    
    def print_test_summary(self):
        """Print a summary of test results."""
        if not self.detection_results:
            print_lg("❌ No test results available")
            return
        
        risk_assessment = self.detection_results.get('risk_assessment', {})
        
        print_lg("\n" + "="*60)
        print_lg("🔍 BOT DETECTION TEST SUMMARY")
        print_lg("="*60)
        print_lg(f"🎯 Risk Level: {risk_assessment.get('level', 'UNKNOWN')}")
        print_lg(f"📊 Risk Score: {risk_assessment.get('score', 0)}/100")
        print_lg(f"⚠️ Risk Factors: {risk_assessment.get('total_factors', 0)}")
        
        factors = risk_assessment.get('factors', [])
        if factors:
            print_lg("\n🚨 Detected Issues:")
            for factor in factors:
                print_lg(f"   • {factor}")
        
        recommendations = self.detection_results.get('recommendations', [])
        if recommendations:
            print_lg("\n💡 Recommendations:")
            for rec in recommendations:
                print_lg(f"   • {rec}")
        
        print_lg("="*60)
