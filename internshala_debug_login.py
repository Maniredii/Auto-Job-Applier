#!/usr/bin/env python3
"""
Internshala Debug Login
Debug version to see exactly what happens during login
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import config

def debug_internshala_login():
    """Debug Internshala login process"""
    
    print("🔍 INTERNSHALA LOGIN DEBUG")
    print("="*40)
    print(f"📧 Email: {config.INTERNSHALA_EMAIL}")
    print(f"🔒 Password: {config.INTERNSHALA_PASSWORD}")
    print("="*40)
    
    # Create browser
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Step 1: Navigate to login page
        print("\n🔗 Step 1: Navigating to Internshala login...")
        driver.get("https://internshala.com/login")
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # Step 2: Take screenshot of login page
        print("\n📸 Taking screenshot of login page...")
        driver.save_screenshot("internshala_login_page.png")
        print("✅ Screenshot saved as 'internshala_login_page.png'")
        
        # Step 3: Find and analyze form elements
        print("\n🔍 Step 3: Analyzing form elements...")
        
        # Find all input fields
        input_fields = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Found {len(input_fields)} input fields:")
        
        for i, field in enumerate(input_fields):
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name")
            field_id = field.get_attribute("id")
            field_placeholder = field.get_attribute("placeholder")
            is_visible = field.is_displayed()
            
            print(f"   {i+1}. Type: {field_type}, Name: {field_name}, ID: {field_id}")
            print(f"      Placeholder: {field_placeholder}, Visible: {is_visible}")
        
        # Step 4: Try to find email field
        print("\n📧 Step 4: Looking for email field...")
        email_selectors = [
            '#email',
            'input[name="email"]',
            'input[type="email"]',
            'input[placeholder*="email"]',
            'input[placeholder*="Email"]'
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                field = driver.find_element(By.CSS_SELECTOR, selector)
                if field.is_displayed():
                    print(f"✅ Found email field with selector: {selector}")
                    email_field = field
                    break
            except:
                print(f"❌ No field found with selector: {selector}")
        
        if not email_field:
            print("❌ No email field found!")
            return False
        
        # Step 5: Try to find password field
        print("\n🔒 Step 5: Looking for password field...")
        password_selectors = [
            '#password',
            'input[name="password"]',
            'input[type="password"]'
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                field = driver.find_element(By.CSS_SELECTOR, selector)
                if field.is_displayed():
                    print(f"✅ Found password field with selector: {selector}")
                    password_field = field
                    break
            except:
                print(f"❌ No field found with selector: {selector}")
        
        if not password_field:
            print("❌ No password field found!")
            return False
        
        # Step 6: Fill the form
        print("\n⌨️ Step 6: Filling the form...")
        
        print("   Clearing email field...")
        email_field.clear()
        print("   Typing email...")
        email_field.send_keys(config.INTERNSHALA_EMAIL)
        time.sleep(1)
        
        print("   Clearing password field...")
        password_field.clear()
        print("   Typing password...")
        password_field.send_keys(config.INTERNSHALA_PASSWORD)
        time.sleep(1)
        
        # Step 7: Take screenshot after filling
        print("\n📸 Taking screenshot after filling form...")
        driver.save_screenshot("internshala_form_filled.png")
        print("✅ Screenshot saved as 'internshala_form_filled.png'")
        
        # Step 8: Find submit button
        print("\n🔍 Step 8: Looking for submit button...")
        submit_selectors = [
            'button[type="submit"]',
            '#login_submit',
            '.login-btn',
            'input[type="submit"]',
            'button[contains(text(), "Login")]',
            '.btn-primary'
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                button = driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed() and button.is_enabled():
                    print(f"✅ Found submit button with selector: {selector}")
                    print(f"   Button text: '{button.text}'")
                    submit_button = button
                    break
            except:
                print(f"❌ No button found with selector: {selector}")
        
        if not submit_button:
            print("❌ No submit button found!")
            return False
        
        # Step 9: Submit the form
        print("\n🚀 Step 9: Submitting the form...")
        submit_button.click()
        
        print("⏳ Waiting for page to load...")
        time.sleep(5)
        
        # Step 10: Check result
        print("\n📊 Step 10: Checking login result...")
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"🌐 Current URL: {current_url}")
        print(f"📄 Page title: {page_title}")
        
        # Take screenshot of result
        driver.save_screenshot("internshala_after_login.png")
        print("📸 Screenshot saved as 'internshala_after_login.png'")
        
        # Check for error messages
        error_selectors = [
            '.error',
            '.alert-danger',
            '.invalid-feedback',
            '[class*="error"]'
        ]
        
        print("\n🔍 Checking for error messages...")
        for selector in error_selectors:
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for error in error_elements:
                    if error.is_displayed() and error.text.strip():
                        print(f"❌ Error found: {error.text}")
            except:
                continue
        
        # Check login success
        if 'login' not in current_url:
            print("🎉 LOGIN APPEARS SUCCESSFUL!")
            print("✅ Redirected away from login page")
            success = True
        else:
            print("❌ LOGIN FAILED - Still on login page")
            success = False
        
        # Keep browser open for manual inspection
        print(f"\n🔍 Browser will stay open for 30 seconds for manual inspection...")
        print("   Check the browser window to see what happened")
        time.sleep(30)
        
        return success
        
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        return False
    
    finally:
        print("🔒 Closing browser...")
        driver.quit()

def main():
    """Main debug function"""
    
    success = debug_internshala_login()
    
    print("\n" + "="*50)
    print("📊 DEBUG SUMMARY")
    print("="*50)
    
    if success:
        print("✅ Login debugging completed successfully")
        print("🎯 Ready to proceed with job applications")
    else:
        print("❌ Login debugging revealed issues")
        print("🔧 Check the screenshots and error messages above")
        print("📧 Verify your credentials are correct")
    
    print("\n📸 Screenshots saved:")
    print("   - internshala_login_page.png")
    print("   - internshala_form_filled.png") 
    print("   - internshala_after_login.png")

if __name__ == "__main__":
    main()
