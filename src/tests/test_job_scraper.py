"""
Test cases for Job Scraper Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By

from src.scrapers.job_scraper import JobScraper, SearchCriteria, JobPlatform, scrape_jobs_simple
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.base_scraper import JobListing, BaseScraper
from src.automation.browser_manager import BrowserManager

class TestJobListing:
    """Test cases for JobListing data class"""
    
    def test_job_listing_creation(self):
        """Test JobListing creation with required fields"""
        job = JobListing(
            title="Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            description="Great job opportunity",
            url="https://example.com/job/123",
            posted_date="2 days ago"
        )
        
        assert job.title == "Software Engineer"
        assert job.company == "Tech Corp"
        assert job.location == "San Francisco, CA"
        assert job.skills == []  # Default empty list
        assert job.scraped_at != ""  # Should be auto-populated
    
    def test_job_listing_with_skills(self):
        """Test JobListing with skills"""
        skills = ["Python", "JavaScript", "React"]
        job = JobListing(
            title="Full Stack Developer",
            company="Startup Inc",
            location="Remote",
            description="Full stack role",
            url="https://example.com/job/456",
            posted_date="1 week ago",
            skills=skills
        )
        
        assert job.skills == skills

class TestSearchCriteria:
    """Test cases for SearchCriteria data class"""
    
    def test_search_criteria_defaults(self):
        """Test SearchCriteria with default values"""
        criteria = SearchCriteria(job_title="Data Scientist")
        
        assert criteria.job_title == "Data Scientist"
        assert criteria.location == "Remote"
        assert criteria.max_jobs == 50
        assert criteria.platforms == [JobPlatform.LINKEDIN]
    
    def test_search_criteria_custom(self):
        """Test SearchCriteria with custom values"""
        criteria = SearchCriteria(
            job_title="DevOps Engineer",
            location="New York, NY",
            max_jobs=25,
            experience_level="senior",
            job_type="full-time",
            platforms=[JobPlatform.LINKEDIN, JobPlatform.INDEED]
        )
        
        assert criteria.job_title == "DevOps Engineer"
        assert criteria.location == "New York, NY"
        assert criteria.max_jobs == 25
        assert criteria.experience_level == "senior"
        assert len(criteria.platforms) == 2

class TestBaseScraper:
    """Test cases for BaseScraper base class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.mock_driver = Mock()
        self.scraper = BaseScraper(self.mock_driver)
    
    def test_human_delay(self):
        """Test human delay functionality"""
        import time
        start_time = time.time()
        self.scraper.human_delay(0.1, 0.2)
        end_time = time.time()
        
        # Should take at least 0.1 seconds
        assert end_time - start_time >= 0.1
    
    def test_get_text_safe(self):
        """Test safe text extraction"""
        mock_element = Mock()
        mock_element.text = "  Test Text  "
        
        result = self.scraper.get_text_safe(mock_element)
        assert result == "Test Text"
        
        # Test with exception
        mock_element.text = Mock(side_effect=Exception("Error"))
        result = self.scraper.get_text_safe(mock_element)
        assert result == ""
    
    def test_get_attribute_safe(self):
        """Test safe attribute extraction"""
        mock_element = Mock()
        mock_element.get_attribute.return_value = "test_value"
        
        result = self.scraper.get_attribute_safe(mock_element, "href")
        assert result == "test_value"
        
        # Test with None return
        mock_element.get_attribute.return_value = None
        result = self.scraper.get_attribute_safe(mock_element, "href")
        assert result == ""
    
    def test_check_for_captcha(self):
        """Test CAPTCHA detection"""
        self.mock_driver.page_source = "Please solve this captcha to continue"
        assert self.scraper.check_for_captcha() == True
        
        self.mock_driver.page_source = "Normal page content"
        assert self.scraper.check_for_captcha() == False
    
    def test_check_for_rate_limit(self):
        """Test rate limit detection"""
        self.mock_driver.page_source = "Too many requests. Please try again later."
        assert self.scraper.check_for_rate_limit() == True
        
        self.mock_driver.page_source = "Normal page content"
        assert self.scraper.check_for_rate_limit() == False

class TestBrowserManager:
    """Test cases for BrowserManager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.browser_manager = BrowserManager()
    
    def test_browser_manager_initialization(self):
        """Test BrowserManager initialization"""
        assert self.browser_manager.driver is None
        assert self.browser_manager.profile_path.exists()
        assert len(self.browser_manager.screen_resolutions) > 0
        assert len(self.browser_manager.timezones) > 0
    
    @patch('undetected_chromedriver.Chrome')
    def test_create_stealth_driver(self, mock_chrome):
        """Test stealth driver creation"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        driver = self.browser_manager.create_stealth_driver(headless=True)
        
        assert driver == mock_driver
        mock_chrome.assert_called_once()
        mock_driver.implicitly_wait.assert_called_with(10)
        mock_driver.set_page_load_timeout.assert_called_with(30)

class TestLinkedInScraper:
    """Test cases for LinkedInScraper"""
    
    def setup_method(self):
        """Setup test environment"""
        self.scraper = LinkedInScraper()
    
    def test_linkedin_scraper_initialization(self):
        """Test LinkedInScraper initialization"""
        assert self.scraper.driver is None
        assert self.scraper.is_logged_in == False
        assert self.scraper.base_url == "https://www.linkedin.com"
        assert 'login' in self.scraper.selectors
        assert 'jobs' in self.scraper.selectors
    
    def test_get_date_filter(self):
        """Test date filter conversion"""
        assert self.scraper._get_date_filter('day') == 'r86400'
        assert self.scraper._get_date_filter('week') == 'r604800'
        assert self.scraper._get_date_filter('month') == 'r2592000'
        assert self.scraper._get_date_filter('invalid') == 'r604800'  # Default to week
    
    def test_get_job_type_filter(self):
        """Test job type filter conversion"""
        assert self.scraper._get_job_type_filter('full-time') == 'F'
        assert self.scraper._get_job_type_filter('part-time') == 'P'
        assert self.scraper._get_job_type_filter('contract') == 'C'
        assert self.scraper._get_job_type_filter('invalid') == None
    
    def test_get_experience_filter(self):
        """Test experience filter conversion"""
        assert self.scraper._get_experience_filter('entry') == '2'
        assert self.scraper._get_experience_filter('mid') == '4'
        assert self.scraper._get_experience_filter('director') == '5'
        assert self.scraper._get_experience_filter('invalid') == None
    
    @patch('src.automation.browser_manager.BrowserManager.get_driver')
    def test_initialize_driver(self, mock_get_driver):
        """Test driver initialization"""
        mock_driver = Mock()
        mock_get_driver.return_value = mock_driver
        
        self.scraper.initialize_driver()
        
        assert self.scraper.driver == mock_driver
        mock_get_driver.assert_called_once()
    
    def test_extract_job_data(self):
        """Test job data extraction from card element"""
        # Create mock job card element
        mock_card = Mock()
        
        # Mock title element
        mock_title = Mock()
        mock_title.text = "Software Engineer"
        mock_card.find_element.side_effect = lambda by, selector: {
            self.scraper.selectors['jobs']['job_title']: mock_title,
            self.scraper.selectors['jobs']['company_name']: Mock(text="Tech Corp"),
            self.scraper.selectors['jobs']['location']: Mock(text="San Francisco, CA"),
            self.scraper.selectors['jobs']['job_link']: Mock(get_attribute=lambda x: "https://example.com/job/123"),
            self.scraper.selectors['jobs']['posted_date']: Mock(text="2 days ago")
        }.get(selector, Mock())
        
        # Mock the scraper methods
        self.scraper.get_text_safe = lambda x: x.text if hasattr(x, 'text') else ""
        self.scraper.get_attribute_safe = lambda x, attr: x.get_attribute(attr) if hasattr(x, 'get_attribute') else ""
        
        job = self.scraper._extract_job_data(mock_card)
        
        assert job is not None
        assert job.title == "Software Engineer"
        assert job.company == "Tech Corp"
        assert job.location == "San Francisco, CA"

class TestJobScraper:
    """Test cases for JobScraper main class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.scraper = JobScraper()
    
    def test_job_scraper_initialization(self):
        """Test JobScraper initialization"""
        assert JobPlatform.LINKEDIN in self.scraper.scrapers
        assert len(self.scraper.active_scrapers) == 0
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        jobs = [
            JobListing("Engineer", "Company A", "Location 1", "Desc", "url1", "date1"),
            JobListing("Engineer", "Company A", "Location 1", "Desc", "url2", "date2"),  # Duplicate
            JobListing("Developer", "Company B", "Location 2", "Desc", "url3", "date3"),
        ]
        
        unique_jobs = self.scraper._remove_duplicates(jobs)
        
        assert len(unique_jobs) == 2
        assert unique_jobs[0].title == "Engineer"
        assert unique_jobs[1].title == "Developer"
    
    def test_get_date_score(self):
        """Test date scoring for sorting"""
        assert self.scraper._get_date_score("2 hours ago") == 100
        assert self.scraper._get_date_score("1 day ago") > self.scraper._get_date_score("5 days ago")
        assert self.scraper._get_date_score("1 week ago") > self.scraper._get_date_score("1 month ago")
    
    def test_sort_jobs(self):
        """Test job sorting"""
        jobs = [
            JobListing("Job C", "Company", "Location", "Desc", "url", "1 month ago"),
            JobListing("Job A", "Company", "Location", "Desc", "url", "1 day ago"),
            JobListing("Job B", "Company", "Location", "Desc", "url", "1 week ago"),
        ]
        
        sorted_jobs = self.scraper._sort_jobs(jobs)
        
        # Should be sorted by date (newest first)
        assert sorted_jobs[0].title == "Job A"  # 1 day ago
        assert sorted_jobs[1].title == "Job B"  # 1 week ago
        assert sorted_jobs[2].title == "Job C"  # 1 month ago

def test_scrape_jobs_simple():
    """Test simple job scraping function"""
    with patch('src.scrapers.job_scraper.JobScraper') as mock_scraper_class:
        mock_scraper = Mock()
        mock_scraper_class.return_value.__enter__.return_value = mock_scraper
        
        mock_jobs = [
            JobListing("Engineer", "Company", "Location", "Desc", "url", "date")
        ]
        mock_scraper.scrape_jobs.return_value = mock_jobs
        
        result = scrape_jobs_simple("Python Developer", "Remote", 10)
        
        assert len(result) == 1
        assert result[0].title == "Engineer"
        mock_scraper.scrape_jobs.assert_called_once()

# Integration tests
class TestJobScraperIntegration:
    """Integration tests for job scraper"""
    
    @pytest.mark.integration
    def test_full_scraping_workflow(self):
        """Test complete scraping workflow (requires internet)"""
        # This test requires actual internet connection and browser
        # Skip in CI/CD environments
        pytest.skip("Integration test - requires browser and internet")
        
        criteria = SearchCriteria(
            job_title="Software Engineer",
            location="Remote",
            max_jobs=2,
            platforms=[JobPlatform.LINKEDIN]
        )
        
        with JobScraper() as scraper:
            jobs = scraper.scrape_jobs(criteria)
            
            # Basic validation
            assert isinstance(jobs, list)
            for job in jobs:
                assert isinstance(job, JobListing)
                assert job.title != ""
                assert job.company != ""

if __name__ == "__main__":
    pytest.main([__file__])
