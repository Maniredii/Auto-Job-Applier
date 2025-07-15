"""
Test cases for Auto Application System Module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import tempfile
import json
from datetime import datetime, timedelta

from src.automation.auto_application_system import (
    AutoApplicationSystem, ApplicationManager, ApplicationConfig, 
    JobApplication, ApplicationStatus
)
from src.parsers.resume_parser import ResumeData
from src.parsers.job_description_parser import JobRequirements

class TestApplicationConfig:
    """Test cases for ApplicationConfig data class"""
    
    def test_config_creation_with_defaults(self):
        """Test ApplicationConfig creation with default values"""
        config = ApplicationConfig(
            job_titles=["Software Engineer"]
        )
        
        assert config.job_titles == ["Software Engineer"]
        assert config.locations == ["Remote"]
        assert config.max_applications_per_day == 20
        assert config.platforms == ["linkedin"]
        assert config.min_match_score == 0.6
        assert config.resume_strategy == "moderate"
        assert config.cover_letter_template == "professional"
    
    def test_config_creation_with_custom_values(self):
        """Test ApplicationConfig creation with custom values"""
        config = ApplicationConfig(
            job_titles=["Data Scientist", "ML Engineer"],
            locations=["San Francisco", "Remote"],
            max_applications_per_day=15,
            platforms=["linkedin", "indeed"],
            min_match_score=0.7,
            resume_strategy="aggressive",
            exclude_companies=["Company A"],
            exclude_keywords=["unpaid"]
        )
        
        assert len(config.job_titles) == 2
        assert len(config.locations) == 2
        assert config.max_applications_per_day == 15
        assert config.min_match_score == 0.7
        assert config.resume_strategy == "aggressive"
        assert "Company A" in config.exclude_companies
        assert "unpaid" in config.exclude_keywords

class TestJobApplication:
    """Test cases for JobApplication data class"""
    
    def test_application_creation(self):
        """Test JobApplication creation"""
        app = JobApplication(
            job_id="test_job_001",
            job_title="Software Engineer",
            company_name="Tech Corp",
            job_url="https://example.com/job/123",
            platform="linkedin"
        )
        
        assert app.job_id == "test_job_001"
        assert app.job_title == "Software Engineer"
        assert app.company_name == "Tech Corp"
        assert app.status == ApplicationStatus.PENDING
        assert app.created_at != ""
        assert app.applied_at is None
    
    def test_application_status_enum(self):
        """Test ApplicationStatus enum values"""
        assert ApplicationStatus.PENDING.value == "pending"
        assert ApplicationStatus.IN_PROGRESS.value == "in_progress"
        assert ApplicationStatus.APPLIED.value == "applied"
        assert ApplicationStatus.FAILED.value == "failed"
        assert ApplicationStatus.SKIPPED.value == "skipped"
        assert ApplicationStatus.DUPLICATE.value == "duplicate"

class TestAutoApplicationSystem:
    """Test cases for AutoApplicationSystem class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = ApplicationConfig(
            job_titles=["Software Engineer"],
            locations=["Remote"],
            max_applications_per_day=5,
            resume_path="test_resume.pdf",
            output_directory="test_output"
        )
        
        # Mock all the components
        with patch.multiple(
            'src.automation.auto_application_system',
            JobScraper=Mock(),
            ResumeParser=Mock(),
            JobDescriptionParser=Mock(),
            ResumeModifier=Mock(),
            CoverLetterGenerator=Mock(),
            BrowserManager=Mock()
        ):
            self.system = AutoApplicationSystem(self.config)
    
    def test_system_initialization(self):
        """Test AutoApplicationSystem initialization"""
        assert self.system.config == self.config
        assert self.system.applications == []
        assert self.system.daily_application_count == 0
        assert self.system.total_application_count == 0
        assert self.system.job_scraper is not None
        assert self.system.resume_parser is not None
    
    def test_check_daily_limits(self):
        """Test daily limit checking"""
        # Test within limits
        assert self.system._check_daily_limits() == True
        
        # Test daily limit exceeded
        self.system.daily_application_count = 10
        assert self.system._check_daily_limits() == False
        
        # Test total limit exceeded
        self.system.daily_application_count = 0
        self.system.total_application_count = 150
        assert self.system._check_daily_limits() == False
    
    def test_increment_application_count(self):
        """Test application count increment"""
        initial_daily = self.system.daily_application_count
        initial_total = self.system.total_application_count
        
        self.system._increment_application_count()
        
        assert self.system.daily_application_count == initial_daily + 1
        assert self.system.total_application_count == initial_total + 1
    
    def test_get_application_delay(self):
        """Test application delay calculation"""
        delay = self.system._get_application_delay()
        min_delay, max_delay = self.config.delay_between_applications
        
        assert min_delay <= delay <= max_delay
    
    def test_filter_jobs(self):
        """Test job filtering"""
        # Create mock jobs
        mock_jobs = [
            Mock(company="Good Company", title="Engineer", description="Great job"),
            Mock(company="Excluded Company", title="Engineer", description="Another job"),
            Mock(company="Another Company", title="Unpaid Intern", description="Unpaid position")
        ]
        
        # Set up config with exclusions
        self.config.exclude_companies = ["Excluded Company"]
        self.config.exclude_keywords = ["unpaid"]
        
        # Mock the already_applied method
        self.system._already_applied = Mock(return_value=False)
        
        filtered_jobs = self.system._filter_jobs(mock_jobs)
        
        # Should only have the first job
        assert len(filtered_jobs) == 1
        assert filtered_jobs[0].company == "Good Company"
    
    def test_remove_duplicate_jobs(self):
        """Test duplicate job removal"""
        mock_jobs = [
            Mock(url="https://example.com/job1", title="Engineer", company="Company A"),
            Mock(url="https://example.com/job1", title="Engineer", company="Company A"),  # Duplicate URL
            Mock(url="https://example.com/job2", title="Engineer", company="Company A"),  # Duplicate title+company
            Mock(url="https://example.com/job3", title="Developer", company="Company B")   # Unique
        ]
        
        unique_jobs = self.system._remove_duplicate_jobs(mock_jobs)
        
        # Should have 2 unique jobs
        assert len(unique_jobs) == 2
        assert unique_jobs[0].url == "https://example.com/job1"
        assert unique_jobs[1].url == "https://example.com/job3"
    
    def test_calculate_job_match(self):
        """Test job match calculation"""
        # Mock base resume
        self.system.base_resume = Mock(spec=ResumeData)
        self.system.base_resume.skills = ["Python", "JavaScript", "React"]
        self.system.base_resume.education = [{"degree": "BS Computer Science"}]
        
        # Mock job requirements
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["Python", "React"]
        job_requirements.preferred_skills = ["AWS"]
        job_requirements.job_level = "Mid-Level"
        job_requirements.education_requirements = ["Bachelor's degree"]
        
        # Mock text processor
        self.system.resume_modifier.text_processor.calculate_skill_relevance = Mock(return_value=0.8)
        
        match_score = self.system._calculate_job_match(job_requirements)
        
        assert 0.0 <= match_score <= 1.0
        assert match_score > 0.5  # Should be reasonably high
    
    def test_get_application_status(self):
        """Test application status retrieval"""
        # Add test application
        app = JobApplication(
            job_id="test_001",
            job_title="Engineer",
            company_name="Company",
            job_url="https://example.com",
            platform="linkedin"
        )
        self.system.applications.append(app)
        
        # Test existing application
        result = self.system.get_application_status("test_001")
        assert result == app
        
        # Test non-existing application
        result = self.system.get_application_status("nonexistent")
        assert result is None
    
    def test_get_applications_by_status(self):
        """Test filtering applications by status"""
        # Add test applications with different statuses
        app1 = JobApplication("id1", "Job1", "Company1", "url1", "platform1")
        app1.status = ApplicationStatus.PENDING
        
        app2 = JobApplication("id2", "Job2", "Company2", "url2", "platform2")
        app2.status = ApplicationStatus.APPLIED
        
        app3 = JobApplication("id3", "Job3", "Company3", "url3", "platform3")
        app3.status = ApplicationStatus.PENDING
        
        self.system.applications.extend([app1, app2, app3])
        
        # Test filtering
        pending_apps = self.system.get_applications_by_status(ApplicationStatus.PENDING)
        applied_apps = self.system.get_applications_by_status(ApplicationStatus.APPLIED)
        
        assert len(pending_apps) == 2
        assert len(applied_apps) == 1
        assert app2 in applied_apps
    
    @pytest.mark.asyncio
    async def test_reject_application(self):
        """Test application rejection"""
        # Add test application
        app = JobApplication("test_001", "Engineer", "Company", "url", "platform")
        self.system.applications.append(app)
        
        # Reject application
        success = await self.system.reject_application("test_001", "Not interested")
        
        assert success == True
        assert app.status == ApplicationStatus.SKIPPED
        assert "Rejected: Not interested" in app.notes
    
    def test_export_applications_report(self):
        """Test applications report export"""
        # Add test application with mock data
        app = JobApplication("test_001", "Engineer", "Company", "url", "platform")
        app.match_score = 0.8
        app.status = ApplicationStatus.APPLIED
        
        # Mock resume modification
        app.modified_resume = Mock()
        app.modified_resume.match_score_before = 0.6
        app.modified_resume.match_score_after = 0.8
        app.modified_resume.improvement_percentage = 33.3
        app.modified_resume.modifications_made = ["Enhanced summary"]
        app.modified_resume.keyword_additions = ["React", "AWS"]
        
        # Mock cover letter
        app.cover_letter = Mock()
        app.cover_letter.personalization_score = 0.85
        app.cover_letter.word_count = 250
        app.cover_letter.template_used = "professional"
        app.cover_letter.key_points = ["Strong Python skills"]
        
        self.system.applications.append(app)
        
        # Export report
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            success = self.system.export_applications_report(tmp_path)
            
            assert success == True
            assert tmp_path.exists()
            
            # Verify report content
            with open(tmp_path, 'r') as f:
                report_data = json.load(f)
            
            assert 'generated_at' in report_data
            assert 'session_statistics' in report_data
            assert 'applications' in report_data
            assert len(report_data['applications']) == 1
            
            app_data = report_data['applications'][0]
            assert app_data['job_id'] == "test_001"
            assert app_data['match_score'] == 0.8
            assert 'resume_analysis' in app_data
            assert 'cover_letter_analysis' in app_data
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

class TestApplicationManager:
    """Test cases for ApplicationManager class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.manager = ApplicationManager(
            resume_path="test_resume.pdf",
            output_directory="test_output"
        )
    
    def test_manager_initialization(self):
        """Test ApplicationManager initialization"""
        assert self.manager.resume_path == "test_resume.pdf"
        assert self.manager.output_directory == "test_output"
        assert self.manager.system is None
    
    def test_create_config(self):
        """Test configuration creation"""
        config = self.manager.create_config(
            job_titles=["Data Scientist"],
            locations=["San Francisco"],
            max_applications_per_day=10,
            platforms=["linkedin"],
            min_match_score=0.7
        )
        
        assert isinstance(config, ApplicationConfig)
        assert config.job_titles == ["Data Scientist"]
        assert config.locations == ["San Francisco"]
        assert config.max_applications_per_day == 10
        assert config.min_match_score == 0.7
        assert config.resume_path == "test_resume.pdf"
        assert config.output_directory == "test_output"
    
    def test_create_config_with_defaults(self):
        """Test configuration creation with default values"""
        config = self.manager.create_config(
            job_titles=["Engineer"]
        )
        
        assert config.locations == ["Remote"]
        assert config.platforms == ["linkedin"]
        assert config.max_applications_per_day == 20
    
    @pytest.mark.asyncio
    async def test_approve_and_submit_without_system(self):
        """Test approval without active system"""
        with pytest.raises(ValueError, match="No active application system"):
            await self.manager.approve_and_submit(["job_001"])
    
    def test_get_application_summary_without_system(self):
        """Test getting summary without active system"""
        summary = self.manager.get_application_summary()
        assert summary == {}
    
    def test_export_report_without_system(self):
        """Test export without active system"""
        success = self.manager.export_report("test_report.json")
        assert success == False

# Integration tests
class TestAutoApplicationSystemIntegration:
    """Integration tests for auto application system"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_application_workflow(self):
        """Test complete application workflow (requires actual components)"""
        # This test requires actual components and would be slow
        pytest.skip("Integration test - requires full system setup")
        
        config = ApplicationConfig(
            job_titles=["Software Engineer"],
            locations=["Remote"],
            max_applications_per_day=1,
            resume_path="test_resume.pdf"
        )
        
        system = AutoApplicationSystem(config)
        
        # This would test the full workflow:
        # 1. Job search
        # 2. Job analysis
        # 3. Application creation
        # 4. Material generation
        # 5. Export and tracking
        
        results = await system.run_application_cycle()
        
        assert isinstance(results, dict)
        assert 'session_stats' in results

# Mock helpers for testing
def create_mock_job():
    """Create a mock job for testing"""
    job = Mock()
    job.title = "Software Engineer"
    job.company = "Tech Corp"
    job.description = "Great software engineering position"
    job.url = "https://example.com/job/123"
    job.platform = "linkedin"
    return job

def create_mock_resume():
    """Create a mock resume for testing"""
    return ResumeData(
        raw_text="test",
        name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        summary="Software developer",
        skills=["Python", "JavaScript", "React"],
        experience=[{"title": "Developer", "description": "Built apps"}],
        education=[{"degree": "BS Computer Science"}],
        sections={}
    )

def create_mock_job_requirements():
    """Create mock job requirements for testing"""
    return JobRequirements(
        required_skills=["Python", "JavaScript"],
        preferred_skills=["React"],
        experience_years={},
        education_requirements=["Bachelor's degree"],
        certifications=[],
        responsibilities=[],
        keywords=[],
        soft_skills=[],
        technologies={},
        salary_range=None,
        job_level="Mid-Level",
        remote_work=True,
        benefits=[],
        company_size="Medium",
        industry="Technology"
    )

if __name__ == "__main__":
    pytest.main([__file__])
