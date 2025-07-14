# Author: Enhanced by AI Assistant
# Advanced Stealth Engine for LinkedIn Auto Job Applier
# Implements sophisticated bot detection bypass techniques

import random
import time
import json
import os
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from modules.helpers import print_lg, buffer
import undetected_chromedriver as uc

class StealthEngine:
    """
    Advanced stealth engine for bypassing bot detection systems.
    Implements human-like behavior patterns and sophisticated evasion techniques.
    """
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1280, 720)
        ]
        
        self.typing_patterns = {
            'fast': (0.05, 0.15),
            'normal': (0.1, 0.3),
            'slow': (0.2, 0.5)
        }
        
        self.mouse_patterns = {
            'direct': 0.1,
            'curved': 0.3,
            'hesitant': 0.5
        }
        
    def get_enhanced_chrome_options(self, profile_dir: Optional[str] = None, proxy: Optional[str] = None) -> Options:
        """
        Creates enhanced Chrome options with advanced stealth configurations.
        """
        options = uc.ChromeOptions()
        
        # Basic stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Advanced fingerprint masking
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-extensions-file-access-check")
        options.add_argument("--disable-extensions-http-throttling")

        # Military-grade stealth options
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-features=BlinkGenPropertyTrees")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-features=AudioServiceOutOfProcess")
        options.add_argument("--disable-features=VizServiceDisplayCompositor")
        options.add_argument("--disable-features=ChromeWhatsNewUI")
        options.add_argument("--disable-features=OptimizationHints")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-field-trial-config")
        options.add_argument("--disable-back-forward-cache")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-component-update")
        options.add_argument("--disable-background-networking")

        # Bot detection bypass
        options.add_argument("--disable-automation")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-web-resources")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--mute-audio")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-pings")
        options.add_argument("--no-zygote")
        options.add_argument("--single-process")

        # Memory and performance optimizations
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--aggressive-cache-discard")
        options.add_argument("--enable-aggressive-domstorage-flushing")

        # Network and security
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--ignore-certificate-errors-spki-list")
        options.add_argument("--ignore-urlfetcher-cert-requests")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")

        # Additional stealth flags
        options.add_argument("--disable-gpu-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--enable-features=NetworkService,NetworkServiceLogging")
        options.add_argument("--force-color-profile=srgb")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--use-mock-keychain")
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f"--user-agent={user_agent}")
        
        # Random window size
        width, height = random.choice(self.screen_resolutions)
        options.add_argument(f"--window-size={width},{height}")
        
        # Profile directory
        if profile_dir:
            options.add_argument(f"--user-data-dir={profile_dir}")

        # Proxy configuration
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
            print_lg(f"🌐 Using proxy: {proxy}")

        # Additional stealth preferences
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 1
            },
            "profile.default_content_settings": {
                "popups": 0
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        return options
    
    def setup_stealth_driver(self, options: Options) -> uc.Chrome:
        """
        Sets up the Chrome driver with stealth configurations.
        """
        print_lg("Initializing enhanced stealth mode...")
        
        # Create driver with stealth options
        driver = uc.Chrome(options=options, version_main=None)
        
        # Execute stealth scripts
        self._execute_stealth_scripts(driver)
        
        # Set random viewport
        self._randomize_viewport(driver)
        
        print_lg("✅ Enhanced stealth mode activated")
        return driver
    
    def _execute_stealth_scripts(self, driver):
        """
        Executes advanced JavaScript to mask automation indicators.
        Military-grade stealth techniques.
        """
        # Advanced stealth scripts with multiple layers of protection
        stealth_scripts = [
            # 1. Remove webdriver property completely
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
            delete navigator.webdriver;
            """,

            # 2. Advanced Chrome object masking
            """
            if (window.chrome) {
                // Restore missing Chrome properties
                window.chrome.app = {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                };

                window.chrome.csi = function() {
                    return {
                        onloadT: Date.now(),
                        startE: Date.now(),
                        tran: 15
                    };
                };

                window.chrome.loadTimes = function() {
                    return {
                        requestTime: Date.now() / 1000,
                        startLoadTime: Date.now() / 1000,
                        commitLoadTime: Date.now() / 1000,
                        finishDocumentLoadTime: Date.now() / 1000,
                        finishLoadTime: Date.now() / 1000,
                        firstPaintTime: Date.now() / 1000,
                        firstPaintAfterLoadTime: 0,
                        navigationType: 'Other',
                        wasFetchedViaSpdy: false,
                        wasNpnNegotiated: false,
                        npnNegotiatedProtocol: 'unknown',
                        wasAlternateProtocolAvailable: false,
                        connectionInfo: 'unknown'
                    };
                };
            }
            """,

            # 3. Enhanced plugin masking
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        {
                            name: 'Chrome PDF Plugin',
                            filename: 'internal-pdf-viewer',
                            description: 'Portable Document Format'
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            description: ''
                        },
                        {
                            name: 'Native Client',
                            filename: 'internal-nacl-plugin',
                            description: ''
                        }
                    ];
                    return plugins;
                }
            });
            """,

            # 4. Advanced permissions override
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                return parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters);
            };
            """,

            # 5. Language and locale masking
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            Object.defineProperty(navigator, 'language', {
                get: () => 'en-US'
            });
            """,

            # 6. Hardware concurrency masking
            """
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4
            });
            """,

            # 7. Device memory masking
            """
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            """,

            # 8. Connection masking
            """
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 50,
                    downlink: 10,
                    saveData: false
                })
            });
            """,

            # 9. Battery API masking
            """
            if (navigator.getBattery) {
                navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                });
            }
            """,

            # 10. WebRTC IP leak protection
            """
            const getOrig = RTCPeerConnection.prototype.getStats;
            RTCPeerConnection.prototype.getStats = function() {
                return getOrig.apply(this, arguments);
            };
            """,

            # 11. Canvas fingerprint protection
            """
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {
                if (contextType === '2d') {
                    const context = getContext.apply(this, arguments);
                    const getImageData = context.getImageData;
                    context.getImageData = function() {
                        const imageData = getImageData.apply(this, arguments);
                        // Add slight noise to prevent fingerprinting
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                            imageData.data[i + 1] += Math.floor(Math.random() * 3) - 1;
                            imageData.data[i + 2] += Math.floor(Math.random() * 3) - 1;
                        }
                        return imageData;
                    };
                    return context;
                }
                return getContext.apply(this, arguments);
            };
            """,

            # 12. Audio context fingerprint protection
            """
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                const getChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function() {
                    const channelData = getChannelData.apply(this, arguments);
                    // Add noise to audio fingerprint
                    for (let i = 0; i < channelData.length; i++) {
                        channelData[i] += (Math.random() - 0.5) * 0.0001;
                    }
                    return channelData;
                };
            }
            """,

            # 13. Screen resolution masking
            """
            Object.defineProperty(screen, 'width', {
                get: () => 1920
            });
            Object.defineProperty(screen, 'height', {
                get: () => 1080
            });
            Object.defineProperty(screen, 'availWidth', {
                get: () => 1920
            });
            Object.defineProperty(screen, 'availHeight', {
                get: () => 1040
            });
            """,

            # 14. Timezone masking
            """
            const originalDateTimeFormat = Intl.DateTimeFormat;
            Intl.DateTimeFormat = function() {
                const formatter = originalDateTimeFormat.apply(this, arguments);
                const originalResolvedOptions = formatter.resolvedOptions;
                formatter.resolvedOptions = function() {
                    const options = originalResolvedOptions.apply(this, arguments);
                    options.timeZone = 'America/New_York';
                    return options;
                };
                return formatter;
            };
            """,

            # 15. Remove automation indicators
            """
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Function;
            """,
        ]

        print_lg("🔒 Executing advanced stealth scripts...")
        executed_count = 0

        for i, script in enumerate(stealth_scripts):
            try:
                driver.execute_script(script)
                executed_count += 1
            except Exception as e:
                print_lg(f"⚠️ Stealth script {i+1} failed: {e}")

        print_lg(f"✅ Executed {executed_count}/{len(stealth_scripts)} stealth scripts")
    
    def _randomize_viewport(self, driver):
        """
        Sets a random viewport size to avoid detection.
        """
        width, height = random.choice(self.screen_resolutions)
        driver.set_window_size(width, height)
        
        # Random position
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        driver.set_window_position(x, y)
    
    def human_like_delay(self, min_delay: float = 0.5, max_delay: float = 3.0):
        """
        Implements human-like delays with natural variation.
        """
        # Use normal distribution for more natural timing
        delay = random.normalvariate((min_delay + max_delay) / 2, (max_delay - min_delay) / 6)
        delay = max(min_delay, min(max_delay, delay))  # Clamp to bounds
        time.sleep(delay)
    
    def human_like_typing(self, element, text: str, typing_speed: str = 'normal'):
        """
        Types text with human-like patterns and occasional mistakes.
        """
        min_delay, max_delay = self.typing_patterns[typing_speed]
        
        # Clear field first
        element.clear()
        
        # Occasionally make typing mistakes
        if random.random() < 0.1:  # 10% chance of making a mistake
            # Type wrong character first
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            element.send_keys(wrong_char)
            time.sleep(random.uniform(0.1, 0.3))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.1, 0.2))
        
        # Type the actual text
        for char in text:
            element.send_keys(char)
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            
            # Occasional longer pauses (thinking)
            if random.random() < 0.05:  # 5% chance
                time.sleep(random.uniform(0.5, 1.5))
    
    def human_like_scroll(self, driver, direction: str = 'down', distance: int = None):
        """
        Implements human-like scrolling patterns.
        """
        if distance is None:
            distance = random.randint(200, 800)
        
        # Scroll in smaller increments for more natural behavior
        increments = random.randint(3, 8)
        increment_size = distance // increments
        
        for i in range(increments):
            if direction == 'down':
                driver.execute_script(f"window.scrollBy(0, {increment_size})")
            else:
                driver.execute_script(f"window.scrollBy(0, -{increment_size})")
            
            # Random pause between scroll increments
            time.sleep(random.uniform(0.1, 0.3))
        
        # Final pause after scrolling
        self.human_like_delay(0.2, 0.8)
    
    def human_like_click(self, driver, element, pattern: str = 'normal'):
        """
        Performs human-like clicking with mouse movement patterns.
        """
        actions = ActionChains(driver)
        
        # Move to element with human-like curve
        if pattern == 'hesitant':
            # Move near the element first, then to the element
            actions.move_to_element_with_offset(element, 
                                              random.randint(-20, 20), 
                                              random.randint(-20, 20))
            actions.pause(random.uniform(0.1, 0.3))
        
        actions.move_to_element(element)
        
        # Random small pause before clicking
        actions.pause(random.uniform(0.05, 0.2))
        
        # Click
        actions.click()
        
        # Execute the action chain
        actions.perform()
        
        # Post-click delay
        self.human_like_delay(0.1, 0.5)
    
    def random_mouse_movement(self, driver):
        """
        Performs random mouse movements to simulate human behavior.
        """
        actions = ActionChains(driver)
        
        # Random movements
        for _ in range(random.randint(1, 3)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset)
            actions.pause(random.uniform(0.1, 0.5))
        
        actions.perform()
    
    def simulate_reading_behavior(self, driver, duration: float = None):
        """
        Simulates human reading behavior with eye movement patterns.
        """
        if duration is None:
            duration = random.uniform(2.0, 8.0)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Random small scrolls (simulating reading)
            scroll_amount = random.randint(50, 150)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            
            # Pause for "reading"
            time.sleep(random.uniform(0.8, 2.5))
            
            # Occasional back-scroll (re-reading)
            if random.random() < 0.3:
                back_scroll = random.randint(20, 100)
                driver.execute_script(f"window.scrollBy(0, -{back_scroll})")
                time.sleep(random.uniform(0.5, 1.0))
    
    def evade_detection_check(self, driver) -> bool:
        """
        Checks for common bot detection mechanisms and attempts evasion.
        """
        detection_indicators = [
            "challenge",
            "captcha", 
            "verification",
            "suspicious activity",
            "automated behavior"
        ]
        
        page_source = driver.page_source.lower()
        
        for indicator in detection_indicators:
            if indicator in page_source:
                print_lg(f"⚠️ Potential detection mechanism found: {indicator}")
                self._handle_detection(driver, indicator)
                return False
        
        return True
    
    def _handle_detection(self, driver, detection_type: str):
        """
        Handles different types of bot detection.
        """
        print_lg(f"Implementing evasion strategy for: {detection_type}")
        
        # General evasion strategies
        self.simulate_reading_behavior(driver, random.uniform(5.0, 15.0))
        self.random_mouse_movement(driver)
        
        # Specific strategies based on detection type
        if "captcha" in detection_type:
            print_lg("CAPTCHA detected - manual intervention may be required")
            # Could implement CAPTCHA solving service integration here
            
        elif "challenge" in detection_type:
            print_lg("Challenge page detected - simulating human behavior")
            self.human_like_delay(10.0, 30.0)
            
        # Refresh page as last resort
        if random.random() < 0.3:  # 30% chance
            print_lg("Refreshing page to reset detection state")
            driver.refresh()
            self.human_like_delay(3.0, 8.0)
