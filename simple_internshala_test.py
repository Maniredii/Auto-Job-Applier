#!/usr/bin/env python3
"""
Simple Internshala Test
Basic test of Internshala credentials and functionality
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from config import config

def test_internshala_basic():
    """Basic test of Internshala login and job search"""
    
    print("🎯 SIMPLE INTERNSHALA TEST")
    print("="*40)
    print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
    print(f"🔒 Password: {'*' * len(config.INTERNSHALA_PASSWORD)}")
    print("="*40)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    driver = None
    
    try:
        print("🌐 Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("🔗 Navigating to Internshala...")
        driver.get("https://internshala.com")
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Look for login link
        print("🔍 Looking for login link...")
        login_selectors = [
            'a[href*="login"]',
            '.login',
            '#login',
            'a[contains(text(), "Login")]'
        ]
        
        login_link = None
        for selector in login_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and 'login' in element.text.lower():
                        login_link = element
                        break
                if login_link:
                    break
            except:
                continue
        
        if login_link:
            print("✅ Login link found!")
            print("🖱️ Clicking login link...")
            login_link.click()
            time.sleep(3)
            
            print(f"🌐 After login click URL: {driver.current_url}")
            
            # Try to find email/phone field
            print("🔍 Looking for email/phone field...")
            email_selectors = [
                '#email',
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="email"]',
                'input[placeholder*="phone"]'
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if email_field.is_displayed():
                        break
                except:
                    continue
            
            if email_field:
                print("✅ Email field found!")
                print("⌨️ Typing email...")
                email_field.clear()
                email_field.send_keys(config.INTERNSHALA_EMAIL)
                time.sleep(1)
                
                # Look for password field
                print("🔍 Looking for password field...")
                password_selectors = [
                    '#password',
                    'input[name="password"]',
                    'input[type="password"]'
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = driver.find_element(By.CSS_SELECTOR, selector)
                        if password_field.is_displayed():
                            break
                    except:
                        continue
                
                if password_field:
                    print("✅ Password field found!")
                    print("⌨️ Typing password...")
                    password_field.clear()
                    password_field.send_keys(config.INTERNSHALA_PASSWORD)
                    time.sleep(1)
                    
                    # Look for submit button
                    print("🔍 Looking for submit button...")
                    submit_selectors = [
                        'button[type="submit"]',
                        '#login_submit',
                        '.login-btn',
                        'input[type="submit"]'
                    ]
                    
                    submit_button = None
                    for selector in submit_selectors:
                        try:
                            submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                            if submit_button.is_displayed() and submit_button.is_enabled():
                                break
                        except:
                            continue
                    
                    if submit_button:
                        print("✅ Submit button found!")
                        print("🖱️ Clicking submit...")
                        submit_button.click()
                        time.sleep(5)
                        
                        print(f"🌐 After login URL: {driver.current_url}")
                        
                        # Check if login was successful
                        if 'dashboard' in driver.current_url or 'student' in driver.current_url:
                            print("🎉 LOGIN SUCCESSFUL!")
                            
                            # Try to navigate to jobs page
                            print("🔍 Looking for jobs section...")
                            driver.get("https://internshala.com/internships")
                            time.sleep(3)
                            
                            print(f"📄 Jobs page title: {driver.title}")
                            
                            # Look for job listings
                            job_selectors = [
                                '.individual_internship',
                                '.internship_meta',
                                '.job-card',
                                '.internship-card'
                            ]
                            
                            jobs_found = 0
                            for selector in job_selectors:
                                try:
                                    job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                    jobs_found = len(job_elements)
                                    if jobs_found > 0:
                                        break
                                except:
                                    continue
                            
                            print(f"📋 Found {jobs_found} job/internship listings")
                            
                            if jobs_found > 0:
                                print("✅ INTERNSHALA INTEGRATION WORKING!")
                                print("🎯 Ready for real-time job applications!")
                            else:
                                print("⚠️ No job listings found, but login successful")
                        
                        elif 'login' in driver.current_url:
                            print("❌ Login failed - still on login page")
                            print("   Please check credentials")
                        else:
                            print(f"⚠️ Unexpected page after login: {driver.current_url}")
                    else:
                        print("❌ Submit button not found")
                else:
                    print("❌ Password field not found")
            else:
                print("❌ Email field not found")
        else:
            print("❌ Login link not found")
        
        # Keep browser open for manual inspection
        print("\n🔍 Browser will stay open for 30 seconds for manual inspection...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if driver:
            print("🔒 Closing browser...")
            driver.quit()
        
        print("\n✅ Test completed!")

if __name__ == "__main__":
    test_internshala_basic()
