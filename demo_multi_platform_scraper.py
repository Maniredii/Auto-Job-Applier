#!/usr/bin/env python3
"""
Multi-Platform Job Scraper Demo
Demonstrates the enhanced Auto Job Applier with support for 10+ job platforms
"""

import asyncio
import logging
from typing import List, Dict, Any

from src.scrapers.job_scraper import JobScraper, SearchCriteria, JobPlatform
from src.automation.auto_application_system import AutoApplicationSystem, ApplicationConfig
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_platform_support():
    """Demonstrate all supported platforms"""
    print("🌐 Smart Auto Job Applier - Multi-Platform Support")
    print("=" * 60)
    
    # List all supported platforms
    platforms = [
        ("LinkedIn", "Professional networking and job search"),
        ("Indeed", "Global job search engine"),
        ("Glassdoor", "Jobs with company reviews and salary insights"),
        ("Naukri.com", "Leading Indian job portal"),
        ("Internshala", "Internships and entry-level opportunities"),
        ("Unstop", "Competitions, hackathons, and jobs"),
        ("AngelList", "Startup and tech company jobs"),
        ("Dice", "Technology and IT jobs"),
        ("Monster", "General job search platform"),
        ("ZipRecruiter", "Quick apply job platform")
    ]
    
    print("\n📋 Supported Platforms:")
    for i, (platform, description) in enumerate(platforms, 1):
        print(f"{i:2d}. {platform:<15} - {description}")
    
    print(f"\n✅ Total Platforms Supported: {len(platforms)}")

def demo_search_criteria():
    """Demonstrate different search criteria configurations"""
    print("\n🔍 Search Criteria Examples:")
    print("-" * 40)
    
    # Example 1: Software Engineer across multiple platforms
    criteria1 = SearchCriteria(
        job_title="Software Engineer",
        location="Remote",
        max_jobs=20,
        platforms=[
            JobPlatform.LINKEDIN,
            JobPlatform.INDEED,
            JobPlatform.GLASSDOOR,
            JobPlatform.ANGELLIST
        ]
    )
    
    print("1. Software Engineer (Remote) - Tech Platforms:")
    print(f"   Platforms: {[p.value for p in criteria1.platforms]}")
    print(f"   Max Jobs: {criteria1.max_jobs}")
    
    # Example 2: Data Scientist in specific location
    criteria2 = SearchCriteria(
        job_title="Data Scientist",
        location="San Francisco, CA",
        max_jobs=15,
        experience_level="mid-level",
        platforms=[
            JobPlatform.LINKEDIN,
            JobPlatform.INDEED,
            JobPlatform.DICE
        ]
    )
    
    print("\n2. Data Scientist (San Francisco) - Professional Platforms:")
    print(f"   Platforms: {[p.value for p in criteria2.platforms]}")
    print(f"   Experience: {criteria2.experience_level}")
    
    # Example 3: Internships for students
    criteria3 = SearchCriteria(
        job_title="Software Development Intern",
        location="India",
        max_jobs=25,
        platforms=[
            JobPlatform.INTERNSHALA,
            JobPlatform.UNSTOP,
            JobPlatform.NAUKRI
        ]
    )
    
    print("\n3. Internships (India) - Student-focused Platforms:")
    print(f"   Platforms: {[p.value for p in criteria3.platforms]}")
    print(f"   Target: Entry-level/Internship opportunities")

async def demo_job_scraping():
    """Demonstrate job scraping from multiple platforms"""
    print("\n🤖 Job Scraping Demo:")
    print("-" * 30)
    
    # Initialize job scraper
    job_scraper = JobScraper()
    
    # Create search criteria for Python Developer
    criteria = SearchCriteria(
        job_title="Python Developer",
        location="Remote",
        max_jobs=10,
        platforms=[
            JobPlatform.LINKEDIN,
            JobPlatform.INDEED,
            JobPlatform.GLASSDOOR
        ]
    )
    
    print(f"Searching for: {criteria.job_title}")
    print(f"Location: {criteria.location}")
    print(f"Platforms: {[p.value for p in criteria.platforms]}")
    print("\n🔄 Scraping jobs...")
    
    try:
        # Scrape jobs (this would normally take time and require proper setup)
        jobs = job_scraper.scrape_jobs(criteria)
        
        print(f"\n✅ Found {len(jobs)} jobs across platforms:")
        
        # Group jobs by platform
        platform_counts = {}
        for job in jobs:
            platform = job.platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        for platform, count in platform_counts.items():
            print(f"   {platform.title()}: {count} jobs")
        
        # Show sample jobs
        if jobs:
            print("\n📄 Sample Job Listings:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"\n{i}. {job.title}")
                print(f"   Company: {job.company}")
                print(f"   Location: {job.location}")
                print(f"   Platform: {job.platform.title()}")
                print(f"   URL: {job.url[:50]}...")
    
    except Exception as e:
        print(f"❌ Demo scraping error: {str(e)}")
        print("   (This is expected in demo mode without proper credentials)")

def demo_application_config():
    """Demonstrate application configuration for multiple platforms"""
    print("\n⚙️ Application Configuration Demo:")
    print("-" * 40)
    
    # Create application configuration
    app_config = ApplicationConfig(
        job_titles=["Software Engineer", "Python Developer", "Full Stack Developer"],
        locations=["Remote", "San Francisco, CA", "New York, NY"],
        platforms=["linkedin", "indeed", "glassdoor", "angellist"],
        max_applications_per_day=20,
        max_applications_total=100,
        experience_levels=["mid-level", "senior-level"],
        job_types=["full-time", "contract"],
        resume_path="./data/resumes/my_resume.pdf"
    )
    
    print("📋 Configuration Summary:")
    print(f"   Job Titles: {app_config.job_titles}")
    print(f"   Locations: {app_config.locations}")
    print(f"   Platforms: {app_config.platforms}")
    print(f"   Daily Limit: {app_config.max_applications_per_day}")
    print(f"   Experience: {app_config.experience_levels}")
    print(f"   Job Types: {app_config.job_types}")

def demo_platform_features():
    """Demonstrate platform-specific features"""
    print("\n🎯 Platform-Specific Features:")
    print("-" * 35)
    
    features = {
        "LinkedIn": [
            "Professional networking integration",
            "Easy Apply detection",
            "Company insights",
            "Connection-based recommendations"
        ],
        "Indeed": [
            "Comprehensive job search",
            "Salary insights",
            "Company reviews",
            "Resume upload automation"
        ],
        "Glassdoor": [
            "Company ratings and reviews",
            "Salary transparency",
            "Interview insights",
            "Employee feedback"
        ],
        "Internshala": [
            "Internship focus",
            "Student-friendly interface",
            "Skill-based matching",
            "Certificate programs"
        ],
        "AngelList": [
            "Startup ecosystem",
            "Equity information",
            "Company stage details",
            "Founder connections"
        ]
    }
    
    for platform, feature_list in features.items():
        print(f"\n{platform}:")
        for feature in feature_list:
            print(f"   • {feature}")

def main():
    """Main demo function"""
    print("🚀 Starting Multi-Platform Job Scraper Demo\n")
    
    # Run all demos
    demo_platform_support()
    demo_search_criteria()
    demo_application_config()
    demo_platform_features()
    
    # Run async demo
    print("\n" + "=" * 60)
    asyncio.run(demo_job_scraping())
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("\n📚 Next Steps:")
    print("1. Configure your .env file with platform credentials")
    print("2. Add your resume to ./data/resumes/")
    print("3. Run the main application: python main.py")
    print("4. Monitor applications in the dashboard")
    
    print("\n🔗 For more information:")
    print("   • Check README.md for detailed setup instructions")
    print("   • Review .env.example for configuration options")
    print("   • Explore src/scrapers/ for platform implementations")

if __name__ == "__main__":
    main()
