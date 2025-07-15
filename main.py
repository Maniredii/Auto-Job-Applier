"""
Smart Auto Job Applier - Main Application Entry Point
"""

import argparse
import sys
import logging
from pathlib import Path

from config import config
from src.utils.logger import setup_logger
from src.core.job_applier import JobApplier

def setup_logging():
    """Setup application logging"""
    log_file = Path(config.LOGS_DIR) / "job_applier.log"
    return setup_logger("job_applier", log_file, config.DEBUG_MODE)

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Smart Auto Job Applier")
    parser.add_argument("--mode", choices=["scrape", "apply", "dashboard", "test"], 
                       default="dashboard", help="Application mode")
    parser.add_argument("--resume", type=str, help="Path to resume file")
    parser.add_argument("--job-title", type=str, help="Job title to search for")
    parser.add_argument("--location", type=str, default=config.DEFAULT_LOCATION, 
                       help="Job location")
    parser.add_argument("--max-applications", type=int, 
                       default=config.MAX_APPLICATIONS_PER_DAY,
                       help="Maximum applications per run")
    parser.add_argument("--headless", action="store_true", 
                       help="Run browser in headless mode")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Smart Auto Job Applier")
    
    try:
        if args.mode == "dashboard":
            from src.ui.dashboard import run_dashboard
            run_dashboard()
        
        elif args.mode == "scrape":
            from src.scrapers.job_scraper import JobScraper
            scraper = JobScraper()
            jobs = scraper.scrape_jobs(
                job_title=args.job_title,
                location=args.location,
                max_jobs=args.max_applications
            )
            logger.info(f"Scraped {len(jobs)} jobs")
        
        elif args.mode == "apply":
            if not args.resume:
                logger.error("Resume file is required for apply mode")
                sys.exit(1)
            
            applier = JobApplier(resume_path=args.resume)
            applier.run_application_process(
                job_title=args.job_title,
                location=args.location,
                max_applications=args.max_applications
            )
        
        elif args.mode == "test":
            from src.tests.test_runner import run_tests
            run_tests()
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        if config.DEBUG_MODE:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
