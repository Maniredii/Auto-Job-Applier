"""
Configuration module for Smart Auto Job Applier
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # LinkedIn Credentials
    LINKEDIN_EMAIL: str = os.getenv('LINKEDIN_EMAIL', '')
    LINKEDIN_PASSWORD: str = os.getenv('LINKEDIN_PASSWORD', '')
    LINKEDIN_PHONE: str = os.getenv('LINKEDIN_PHONE', '')
    
    # Email Configuration
    EMAIL_HOST: str = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT: int = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USER: str = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD: str = os.getenv('EMAIL_PASSWORD', '')
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///job_applications.db')
    
    # Application Settings
    MAX_APPLICATIONS_PER_DAY: int = int(os.getenv('MAX_APPLICATIONS_PER_DAY', '50'))
    DELAY_BETWEEN_APPLICATIONS: int = int(os.getenv('DELAY_BETWEEN_APPLICATIONS', '30'))
    ENABLE_NOTIFICATIONS: bool = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # Browser Settings
    HEADLESS_MODE: bool = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
    BROWSER_PROFILE_PATH: str = os.getenv('BROWSER_PROFILE_PATH', './browser_profiles')
    ENABLE_STEALTH_MODE: bool = os.getenv('ENABLE_STEALTH_MODE', 'true').lower() == 'true'
    
    # Job Search Preferences
    DEFAULT_LOCATION: str = os.getenv('DEFAULT_LOCATION', 'Remote')
    DEFAULT_EXPERIENCE_LEVEL: str = os.getenv('DEFAULT_EXPERIENCE_LEVEL', 'Mid-Level')
    DEFAULT_JOB_TYPES: str = os.getenv('DEFAULT_JOB_TYPES', 'Full-time,Contract')
    
    # File Paths
    RESUMES_DIR: str = './data/resumes'
    COVER_LETTERS_DIR: str = './data/cover_letters'
    LOGS_DIR: str = './logs'
    TEMP_DIR: str = './temp'
    
    # AI Model Settings
    GROQ_MODEL: str = 'mixtral-8x7b-32768'  # Default Groq model
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate required configuration"""
        required_fields = ['GROQ_API_KEY']
        missing_fields = []
        
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"Missing required configuration: {', '.join(missing_fields)}")
            return False
        
        return True
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories"""
        directories = [
            cls.RESUMES_DIR,
            cls.COVER_LETTERS_DIR,
            cls.LOGS_DIR,
            cls.TEMP_DIR,
            cls.BROWSER_PROFILE_PATH
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

# Initialize configuration
config = Config()

# Validate and create directories on import
if not config.validate_config():
    print("Warning: Configuration validation failed. Please check your .env file.")

config.create_directories()
