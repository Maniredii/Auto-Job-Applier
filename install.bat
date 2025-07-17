@echo off
echo 🚀 AUTO JOB APPLIER - QUICK INSTALLATION
echo ========================================

echo 📦 Installing core dependencies...
pip install selenium==4.15.2
pip install undetected-chromedriver==3.5.4
pip install webdriver-manager==4.0.1
pip install fake-useragent==1.4.0
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install pandas==2.1.3
pip install groq==0.4.1

echo 📁 Creating directories...
if not exist "data\resumes" mkdir "data\resumes"
if not exist "data\cover_letters" mkdir "data\cover_letters"
if not exist "data\applications" mkdir "data\applications"
if not exist "logs" mkdir "logs"
if not exist "temp" mkdir "temp"
if not exist "browser_profiles" mkdir "browser_profiles"

echo ✅ Installation completed!
echo.
echo 📋 NEXT STEPS:
echo 1. Configure your .env file with credentials
echo 2. Add your resume to data\resumes\ folder
echo 3. Run: python quick_browser_test.py
echo 4. Start job applications!
echo.
pause
