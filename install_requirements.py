#!/usr/bin/env python3
"""
Installation Script for Auto Job Applier
Installs all required dependencies and sets up the system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is too old. Need Python 3.8+")
        return False

def check_chrome_installed():
    """Check if Chrome browser is installed"""
    print("🌐 Checking Chrome browser...")
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            return True
    
    print("❌ Chrome browser not found!")
    print("   Please install Google Chrome from: https://www.google.com/chrome/")
    return False

def install_core_dependencies():
    """Install core dependencies"""
    core_packages = [
        "selenium==4.15.2",
        "undetected-chromedriver==3.5.4",
        "webdriver-manager==4.0.1",
        "fake-useragent==1.4.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "pandas==2.1.3",
        "groq==0.4.1"
    ]
    
    print("📦 Installing core dependencies...")
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            return False
    return True

def install_optional_dependencies():
    """Install optional dependencies"""
    optional_packages = [
        "flask==2.3.3",
        "fastapi==0.104.1",
        "streamlit==1.28.1",
        "openai==1.3.7",
        "PyMuPDF==1.23.8",
        "python-docx==1.1.0"
    ]
    
    print("📦 Installing optional dependencies...")
    for package in optional_packages:
        run_command(f"pip install {package}", f"Installing {package.split('==')[0]}")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "data/resumes",
        "data/cover_letters", 
        "data/applications",
        "logs",
        "temp",
        "browser_profiles"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def setup_env_file():
    """Setup environment file"""
    print("⚙️ Setting up environment file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your credentials")
        return False
    else:
        print("✅ .env file exists")
        return True

def test_installation():
    """Test if installation was successful"""
    print("🧪 Testing installation...")
    
    test_imports = [
        ("selenium", "Selenium WebDriver"),
        ("undetected_chromedriver", "Undetected ChromeDriver"),
        ("fake_useragent", "Fake User Agent"),
        ("requests", "Requests"),
        ("dotenv", "Python Dotenv"),
        ("groq", "Groq API")
    ]
    
    all_passed = True
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Main installation function"""
    print("🚀 AUTO JOB APPLIER INSTALLATION")
    print("="*50)
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Installation cannot continue with incompatible Python version")
        return False
    
    # Step 2: Check Chrome browser
    if not check_chrome_installed():
        print("\n❌ Installation cannot continue without Chrome browser")
        return False
    
    # Step 3: Install core dependencies
    if not install_core_dependencies():
        print("\n❌ Core dependency installation failed")
        return False
    
    # Step 4: Install optional dependencies
    install_optional_dependencies()
    
    # Step 5: Create directories
    create_directories()
    
    # Step 6: Setup environment
    setup_env_file()
    
    # Step 7: Test installation
    if test_installation():
        print("\n" + "="*50)
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("✅ All dependencies installed")
        print("✅ Directories created")
        print("✅ System ready for job applications")
        
        print("\n📋 NEXT STEPS:")
        print("1. Configure your .env file with platform credentials")
        print("2. Add your resume to data/resumes/ folder")
        print("3. Run: python quick_browser_test.py")
        print("4. Start job applications: python internshala_live_test.py")
        
        return True
    else:
        print("\n❌ Installation completed but some tests failed")
        print("   You may still be able to use the system")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready to start automated job applications!")
    else:
        print("\n⚠️ Installation had issues. Check the errors above.")
