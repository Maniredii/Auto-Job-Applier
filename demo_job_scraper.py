"""
Demo script to test the Job Scraper functionality
"""

import json
import time
from pathlib import Path
from src.scrapers.job_scraper import JobScraper, SearchCriteria, JobPlatform, scrape_jobs_simple
from src.scrapers.linkedin_scraper import LinkedInScraper
from config import config

def demo_basic_scraping():
    """Demonstrate basic job scraping functionality"""
    print("=== Job Scraper Demo ===\n")
    
    # Test simple scraping function
    print("🔍 Testing simple job scraping...")
    
    try:
        jobs = scrape_jobs_simple(
            job_title="Python Developer",
            location="Remote",
            max_jobs=5,
            platforms=["linkedin"]
        )
        
        print(f"✅ Found {len(jobs)} jobs")
        
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location}")
            print(f"   Posted: {job.posted_date}")
            print(f"   URL: {job.url[:80]}...")
        
        return jobs
        
    except Exception as e:
        print(f"❌ Error in basic scraping: {str(e)}")
        return []

def demo_advanced_scraping():
    """Demonstrate advanced job scraping with criteria"""
    print("\n=== Advanced Job Scraping Demo ===\n")
    
    # Create search criteria
    criteria = SearchCriteria(
        job_title="Software Engineer",
        location="San Francisco, CA",
        max_jobs=10,
        experience_level="mid",
        job_type="full-time",
        date_posted="week",
        platforms=[JobPlatform.LINKEDIN]
    )
    
    print(f"🎯 Search Criteria:")
    print(f"   Job Title: {criteria.job_title}")
    print(f"   Location: {criteria.location}")
    print(f"   Max Jobs: {criteria.max_jobs}")
    print(f"   Experience: {criteria.experience_level}")
    print(f"   Job Type: {criteria.job_type}")
    print(f"   Date Posted: {criteria.date_posted}")
    print(f"   Platforms: {[p.value for p in criteria.platforms]}")
    
    try:
        with JobScraper() as scraper:
            jobs = scraper.scrape_jobs(criteria)
            
            print(f"\n✅ Advanced scraping completed: {len(jobs)} jobs found")
            
            # Show job statistics
            if jobs:
                companies = set(job.company for job in jobs)
                locations = set(job.location for job in jobs)
                
                print(f"\n📊 Job Statistics:")
                print(f"   Unique Companies: {len(companies)}")
                print(f"   Unique Locations: {len(locations)}")
                
                print(f"\n🏢 Top Companies:")
                company_counts = {}
                for job in jobs:
                    company_counts[job.company] = company_counts.get(job.company, 0) + 1
                
                for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"   • {company}: {count} jobs")
            
            return jobs
            
    except Exception as e:
        print(f"❌ Error in advanced scraping: {str(e)}")
        return []

def demo_linkedin_login():
    """Demonstrate LinkedIn login functionality"""
    print("\n=== LinkedIn Login Demo ===\n")
    
    if not config.LINKEDIN_EMAIL or not config.LINKEDIN_PASSWORD:
        print("⚠️ LinkedIn credentials not configured in .env file")
        print("   Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD to test login")
        return False
    
    try:
        scraper = LinkedInScraper()
        scraper.initialize_driver(headless=False)  # Use visible browser for demo
        
        print("🔐 Attempting LinkedIn login...")
        print("   Email:", config.LINKEDIN_EMAIL)
        print("   (Password hidden for security)")
        
        login_success = scraper.login()
        
        if login_success:
            print("✅ LinkedIn login successful!")
            
            # Test a quick search
            print("\n🔍 Testing authenticated search...")
            jobs = scraper.scrape_jobs(
                job_title="Data Scientist",
                location="Remote",
                max_jobs=3
            )
            
            print(f"   Found {len(jobs)} jobs with authentication")
            
        else:
            print("❌ LinkedIn login failed")
        
        scraper.close()
        return login_success
        
    except Exception as e:
        print(f"❌ Error in LinkedIn login: {str(e)}")
        return False

def demo_job_details():
    """Demonstrate detailed job information extraction"""
    print("\n=== Job Details Demo ===\n")
    
    try:
        # Get a few jobs first
        jobs = scrape_jobs_simple(
            job_title="Machine Learning Engineer",
            location="Remote",
            max_jobs=2,
            platforms=["linkedin"]
        )
        
        if not jobs:
            print("❌ No jobs found for details demo")
            return
        
        print(f"📋 Getting detailed information for {len(jobs)} jobs...")
        
        with JobScraper() as scraper:
            for i, job in enumerate(jobs, 1):
                print(f"\n{i}. Getting details for: {job.title} at {job.company}")
                
                detailed_job = scraper.get_job_details(job)
                
                print(f"   Description length: {len(detailed_job.description)} characters")
                print(f"   Skills found: {len(detailed_job.skills)}")
                
                if detailed_job.skills:
                    print(f"   Top skills: {', '.join(detailed_job.skills[:5])}")
                
                if detailed_job.description:
                    # Show first 200 characters of description
                    desc_preview = detailed_job.description[:200].replace('\n', ' ')
                    print(f"   Description preview: {desc_preview}...")
        
    except Exception as e:
        print(f"❌ Error in job details demo: {str(e)}")

def demo_anti_detection():
    """Demonstrate anti-detection features"""
    print("\n=== Anti-Detection Features Demo ===\n")
    
    print("🛡️ Anti-Detection Features:")
    print("   • Undetected Chrome Driver")
    print("   • Random user agents")
    print("   • Human-like delays")
    print("   • Random mouse movements")
    print("   • Browser fingerprint randomization")
    print("   • Stealth JavaScript modifications")
    
    try:
        scraper = LinkedInScraper()
        scraper.initialize_driver(headless=False)
        
        print("\n🤖 Testing human-like behavior...")
        
        # Navigate to LinkedIn
        scraper.driver.get("https://www.linkedin.com")
        
        # Demonstrate human-like delays
        print("   • Human delay (2-4 seconds)...")
        scraper.human_delay(2, 4)
        
        # Demonstrate random mouse movement
        print("   • Random mouse movement...")
        scraper.random_mouse_movement()
        
        # Demonstrate human scrolling
        print("   • Human-like scrolling...")
        scraper.human_scroll()
        
        # Check for detection
        print("   • Checking for bot detection...")
        captcha_detected = scraper.check_for_captcha()
        rate_limited = scraper.check_for_rate_limit()
        
        print(f"   • CAPTCHA detected: {captcha_detected}")
        print(f"   • Rate limited: {rate_limited}")
        
        if not captcha_detected and not rate_limited:
            print("✅ Anti-detection measures working!")
        else:
            print("⚠️ Detection measures may need adjustment")
        
        scraper.close()
        
    except Exception as e:
        print(f"❌ Error in anti-detection demo: {str(e)}")

def save_demo_results(jobs):
    """Save demo results to file"""
    if not jobs:
        return
    
    output_data = []
    for job in jobs:
        job_data = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "posted_date": job.posted_date,
            "url": job.url,
            "description": job.description[:500] if job.description else "",
            "skills": job.skills[:10] if job.skills else [],
            "scraped_at": job.scraped_at
        }
        output_data.append(job_data)
    
    output_file = Path("temp/scraped_jobs_demo.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Demo results saved to: {output_file}")

def main():
    """Main demo function"""
    print("🚀 Starting Job Scraper Demo")
    print("=" * 50)
    
    all_jobs = []
    
    try:
        # Demo 1: Basic scraping
        basic_jobs = demo_basic_scraping()
        all_jobs.extend(basic_jobs)
        
        # Demo 2: Advanced scraping
        advanced_jobs = demo_advanced_scraping()
        all_jobs.extend(advanced_jobs)
        
        # Demo 3: LinkedIn login (optional)
        print("\n" + "=" * 50)
        user_input = input("Test LinkedIn login? (y/n): ").lower().strip()
        if user_input == 'y':
            demo_linkedin_login()
        
        # Demo 4: Job details (optional)
        if all_jobs:
            print("\n" + "=" * 50)
            user_input = input("Test job details extraction? (y/n): ").lower().strip()
            if user_input == 'y':
                demo_job_details()
        
        # Demo 5: Anti-detection features
        print("\n" + "=" * 50)
        user_input = input("Test anti-detection features? (y/n): ").lower().strip()
        if user_input == 'y':
            demo_anti_detection()
        
        # Save results
        save_demo_results(all_jobs)
        
        print("\n" + "=" * 50)
        print("✅ Job Scraper Demo completed successfully!")
        print(f"📊 Total jobs scraped: {len(all_jobs)}")
        
        print("\nNext steps:")
        print("1. Configure LinkedIn credentials in .env file")
        print("2. Install Chrome browser if not already installed")
        print("3. Test with your specific job search criteria")
        print("4. Integrate with resume parser and AI modules")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Make sure all dependencies are installed and Chrome is available.")

if __name__ == "__main__":
    main()
