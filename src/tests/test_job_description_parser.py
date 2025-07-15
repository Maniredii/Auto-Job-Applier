"""
Test cases for Job Description Parser Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.parsers.job_description_parser import JobDescriptionParser, JobRequirements
from src.parsers.text_processor import TextProcessor

class TestJobRequirements:
    """Test cases for JobRequirements data class"""
    
    def test_job_requirements_creation(self):
        """Test JobRequirements creation with all fields"""
        requirements = JobRequirements(
            required_skills=["Python", "JavaScript"],
            preferred_skills=["React", "AWS"],
            experience_years={"Python": 3},
            education_requirements=["Bachelor's degree"],
            certifications=["AWS Certified"],
            responsibilities=["Develop software"],
            keywords=["software", "development"],
            soft_skills=["Communication"],
            technologies={"programming_languages": ["Python"]},
            salary_range=(100000, 150000),
            job_level="Senior",
            remote_work=True,
            benefits=["Health insurance"],
            company_size="Large",
            industry="Technology"
        )
        
        assert requirements.required_skills == ["Python", "JavaScript"]
        assert requirements.salary_range == (100000, 150000)
        assert requirements.remote_work == True
        assert requirements.job_level == "Senior"

class TestJobDescriptionParser:
    """Test cases for JobDescriptionParser class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.parser = JobDescriptionParser(use_ai=False)  # Disable AI for unit tests
    
    def test_parser_initialization(self):
        """Test JobDescriptionParser initialization"""
        assert self.parser.use_ai == False
        assert isinstance(self.parser.text_processor, TextProcessor)
        assert self.parser.ai_client is None
    
    def test_parser_initialization_with_ai(self):
        """Test JobDescriptionParser initialization with AI"""
        with patch('src.parsers.job_description_parser.GroqClient') as mock_groq:
            mock_groq.return_value = Mock()
            parser = JobDescriptionParser(use_ai=True)
            
            assert parser.use_ai == True
            assert parser.ai_client is not None
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        dirty_text = """
        <p>This is a <strong>job description</strong> with HTML tags.</p>
        <ul><li>Multiple   spaces</li></ul>
        Special characters: @#$%^&*()
        """
        
        cleaned = self.parser._preprocess_text(dirty_text)
        
        assert "<p>" not in cleaned
        assert "<strong>" not in cleaned
        assert "Multiple   spaces" not in cleaned  # Should be single space
        assert "@#$%^&*()" not in cleaned
    
    def test_extract_responsibilities(self):
        """Test responsibility extraction"""
        text = """
        Key Responsibilities:
        • Develop and maintain web applications
        • Collaborate with cross-functional teams
        • Write clean, maintainable code
        
        You will be responsible for:
        - Leading development projects
        - Mentoring junior developers
        """
        
        responsibilities = self.parser._extract_responsibilities(text)
        
        assert len(responsibilities) > 0
        assert any("develop" in resp.lower() for resp in responsibilities)
        assert any("collaborate" in resp.lower() for resp in responsibilities)
    
    def test_extract_benefits(self):
        """Test benefit extraction"""
        text = """
        We offer competitive benefits including:
        - Health insurance and dental coverage
        - 401k retirement plan with matching
        - Flexible work hours and remote work options
        - Professional development budget
        - Gym membership reimbursement
        """
        
        benefits = self.parser._extract_benefits(text)
        
        assert "Health Insurance" in benefits
        assert "401K" in benefits
        assert "Flexible Hours" in benefits
        assert "Professional Development" in benefits
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = """
        We are looking for a software engineer with experience in Python development.
        The candidate should have strong programming skills and knowledge of databases.
        Experience with cloud platforms and agile methodologies is preferred.
        """
        
        keywords = self.parser._extract_keywords(text)
        
        assert len(keywords) > 0
        assert "python" in keywords
        assert "programming" in keywords
        assert "databases" in keywords
        # Stop words should be filtered out
        assert "the" not in keywords
        assert "and" not in keywords
    
    def test_categorize_skills(self):
        """Test skill categorization as required vs preferred"""
        text = """
        Required Skills:
        - Python programming is required
        - Strong JavaScript knowledge is essential
        - SQL database experience is mandatory
        
        Preferred Skills:
        - React experience is a plus
        - AWS knowledge would be beneficial
        - Docker familiarity is nice to have
        """
        
        skills_dict = {
            "programming_languages": ["Python", "JavaScript"],
            "databases": ["SQL"],
            "web_technologies": ["React"],
            "cloud_platforms": ["AWS"],
            "devops_tools": ["Docker"]
        }
        
        required, preferred = self.parser._categorize_skills(text, skills_dict)
        
        assert "Python" in required
        assert "JavaScript" in required
        assert "SQL" in required
        assert "React" in preferred
        assert "AWS" in preferred
        assert "Docker" in preferred
    
    def test_parse_salary(self):
        """Test salary parsing"""
        assert self.parser._parse_salary("120000") == 120000
        assert self.parser._parse_salary("120k") == 120000
        assert self.parser._parse_salary("120K") == 120000
        assert self.parser._parse_salary("$120,000") == 120000
    
    def test_extract_industry(self):
        """Test industry extraction"""
        tech_text = "We are a software company building SaaS applications with AI"
        assert self.parser._extract_industry(tech_text) == "Technology"
        
        finance_text = "Join our fintech startup revolutionizing banking"
        assert self.parser._extract_industry(finance_text) == "Finance"
        
        healthcare_text = "Healthcare technology company improving patient outcomes"
        assert self.parser._extract_industry(healthcare_text) == "Healthcare"
        
        unknown_text = "We make widgets and sell them to customers"
        assert self.parser._extract_industry(unknown_text) == "Other"
    
    def test_extract_job_metadata(self):
        """Test job metadata extraction"""
        text = """
        Senior Software Engineer position
        Salary: $120,000 - $180,000
        Remote work available
        Large enterprise company with 1000+ employees
        """
        
        metadata = self.parser._extract_job_metadata(text, "Senior Software Engineer")
        
        assert metadata['job_level'] == "Senior"
        assert metadata['salary_range'] == (120000, 180000)
        assert metadata['remote_work'] == True
        assert metadata['company_size'] == "Large"
    
    def test_extract_experience_education(self):
        """Test experience and education extraction"""
        text = """
        Requirements:
        - Bachelor's degree in Computer Science
        - 5+ years of Python development experience
        - 3 years of experience with React
        - Master's degree preferred
        - AWS Certified Solutions Architect certification
        """
        
        exp_edu = self.parser._extract_experience_education(text)
        
        assert len(exp_edu['education_requirements']) > 0
        assert any("bachelor" in edu.lower() for edu in exp_edu['education_requirements'])
        assert "AWS Certified Solutions Architect" in exp_edu['certifications']
        assert len(exp_edu['experience_years']) > 0
    
    def test_merge_requirements(self):
        """Test requirement merging"""
        req1 = {
            'required_skills': ['Python', 'JavaScript'],
            'job_level': 'Senior',
            'remote_work': True
        }
        
        req2 = {
            'required_skills': ['SQL', 'Git'],
            'preferred_skills': ['React'],
            'salary_range': (100000, 150000)
        }
        
        merged = self.parser._merge_requirements(req1, req2)
        
        assert isinstance(merged, JobRequirements)
        assert len(merged.required_skills) == 4  # Python, JavaScript, SQL, Git
        assert 'React' in merged.preferred_skills
        assert merged.job_level == 'Senior'
        assert merged.remote_work == True
        assert merged.salary_range == (100000, 150000)
    
    def test_analyze_job_match(self):
        """Test job matching analysis"""
        requirements = JobRequirements(
            required_skills=["Python", "JavaScript", "SQL"],
            preferred_skills=["React", "AWS"],
            experience_years={},
            education_requirements=[],
            certifications=[],
            responsibilities=[],
            keywords=[],
            soft_skills=[],
            technologies={},
            salary_range=None,
            job_level="Mid-Level",
            remote_work=False,
            benefits=[],
            company_size="Unknown",
            industry="Other"
        )
        
        candidate_skills = ["Python", "JavaScript", "React", "Git"]
        
        match_analysis = self.parser.analyze_job_match(requirements, candidate_skills)
        
        assert 'overall_score' in match_analysis
        assert 'required_skills_match' in match_analysis
        assert 'preferred_skills_match' in match_analysis
        assert 'missing_required_skills' in match_analysis
        assert 'recommendation' in match_analysis
        
        # Should have good match for required skills (2/3 = 0.67)
        assert match_analysis['required_skills_match'] > 0.5
        # Should have perfect match for preferred skills (1/1 = 1.0)
        assert match_analysis['preferred_skills_match'] == 1.0
        # Should be missing SQL
        assert "SQL" in match_analysis['missing_required_skills']
    
    def test_generate_match_recommendation(self):
        """Test match recommendation generation"""
        assert "Excellent" in self.parser._generate_match_recommendation(0.9)
        assert "Good" in self.parser._generate_match_recommendation(0.7)
        assert "Moderate" in self.parser._generate_match_recommendation(0.5)
        assert "Low" in self.parser._generate_match_recommendation(0.2)
    
    def test_extract_application_instructions(self):
        """Test application instruction extraction"""
        text = """
        How to Apply:
        Please submit your resume and cover letter to careers@company.com
        Include a portfolio of your work and references.
        Application deadline: March 15, 2024
        """
        
        instructions = self.parser.extract_application_instructions(text)
        
        assert instructions['application_method'] == 'Email'
        assert instructions['contact_info'] == 'careers@company.com'
        assert 'Resume' in instructions['required_documents']
        assert 'Cover Letter' in instructions['required_documents']
        assert 'Portfolio' in instructions['required_documents']
        assert 'march 15, 2024' in instructions['application_deadline'].lower()
    
    def test_parse_job_description_integration(self):
        """Integration test for complete job description parsing"""
        job_description = """
        Senior Software Engineer - Full Stack
        
        Company: TechCorp
        Location: San Francisco, CA (Remote OK)
        Salary: $140,000 - $180,000
        
        We are seeking a Senior Software Engineer to join our team.
        
        Responsibilities:
        • Develop web applications using React and Node.js
        • Collaborate with product teams
        • Mentor junior developers
        
        Required:
        • Bachelor's degree in Computer Science
        • 5+ years of JavaScript experience
        • Strong React and Node.js skills
        • Experience with PostgreSQL
        
        Preferred:
        • AWS experience is a plus
        • Docker knowledge beneficial
        
        Benefits:
        • Health insurance
        • 401k matching
        • Flexible work hours
        
        Apply online at techcorp.com/careers
        """
        
        requirements = self.parser.parse_job_description(job_description, "Senior Software Engineer")
        
        # Verify basic parsing worked
        assert isinstance(requirements, JobRequirements)
        assert len(requirements.required_skills) > 0
        assert len(requirements.responsibilities) > 0
        assert requirements.job_level == "Senior"
        assert requirements.remote_work == True
        assert requirements.salary_range == (140000, 180000)
        assert "Health Insurance" in requirements.benefits

class TestJobDescriptionParserWithAI:
    """Test cases for AI-enhanced parsing"""
    
    @patch('src.parsers.job_description_parser.GroqClient')
    def test_ai_enhanced_parsing(self, mock_groq_client):
        """Test AI-enhanced job description parsing"""
        # Mock AI client
        mock_ai = Mock()
        mock_ai.extract_job_requirements.return_value = {
            'required_skills': ['Python', 'Machine Learning'],
            'preferred_skills': ['TensorFlow'],
            'experience_level': 'Senior',
            'education': 'Master\'s degree',
            'responsibilities': ['Build ML models'],
            'keywords': ['AI', 'Data Science']
        }
        mock_groq_client.return_value = mock_ai
        
        parser = JobDescriptionParser(use_ai=True)
        
        job_desc = "We need a Senior ML Engineer with Python and TensorFlow experience"
        requirements = parser.parse_job_description(job_desc, "ML Engineer")
        
        # Verify AI was called
        mock_ai.extract_job_requirements.assert_called_once_with(job_desc)
        
        # Verify results include AI-extracted data
        assert isinstance(requirements, JobRequirements)

# Integration tests
class TestJobDescriptionParserIntegration:
    """Integration tests for job description parser"""
    
    @pytest.mark.integration
    def test_real_job_description_parsing(self):
        """Test parsing with real job description (requires AI API)"""
        # This test requires actual Groq API access
        pytest.skip("Integration test - requires Groq API key")
        
        parser = JobDescriptionParser(use_ai=True)
        
        real_job_desc = """
        Software Engineer - Backend
        We're looking for a backend engineer to build scalable APIs.
        Requirements: Python, Django, PostgreSQL, 3+ years experience
        Nice to have: AWS, Docker, Kubernetes
        """
        
        requirements = parser.parse_job_description(real_job_desc, "Software Engineer")
        
        assert isinstance(requirements, JobRequirements)
        assert "Python" in requirements.required_skills
        assert "Django" in requirements.required_skills

if __name__ == "__main__":
    pytest.main([__file__])
