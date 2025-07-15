"""
Test cases for AI Cover Letter Generator Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from src.ai.cover_letter_generator import CoverLetterGenerator, CoverLetterData, CoverLetterTemplate
from src.parsers.resume_parser import ResumeData
from src.parsers.job_description_parser import JobRequirements

class TestCoverLetterData:
    """Test cases for CoverLetterData data class"""
    
    def test_cover_letter_data_creation(self):
        """Test CoverLetterData creation with required fields"""
        cover_letter = CoverLetterData(
            content="Dear Hiring Manager, I am writing to apply...",
            job_title="Software Engineer",
            company_name="Tech Corp",
            candidate_name="John Doe",
            generated_at="2024-01-15 10:30:00",
            word_count=250,
            key_points=["Strong Python skills", "5 years experience"],
            personalization_score=0.85,
            template_used="professional"
        )
        
        assert cover_letter.job_title == "Software Engineer"
        assert cover_letter.company_name == "Tech Corp"
        assert cover_letter.word_count == 250
        assert cover_letter.personalization_score == 0.85
        assert len(cover_letter.key_points) == 2
    
    def test_cover_letter_data_auto_fields(self):
        """Test auto-populated fields"""
        cover_letter = CoverLetterData(
            content="Test content with multiple words here",
            job_title="Developer",
            company_name="Company",
            candidate_name="Jane",
            generated_at="",  # Should be auto-filled
            word_count=0,  # Should be auto-calculated
            key_points=[],
            personalization_score=0.5,
            template_used="test"
        )
        
        assert cover_letter.generated_at != ""
        assert cover_letter.word_count == 6  # "Test content with multiple words here"

class TestCoverLetterTemplate:
    """Test cases for CoverLetterTemplate data class"""
    
    def test_template_creation(self):
        """Test CoverLetterTemplate creation"""
        template = CoverLetterTemplate(
            name="Professional",
            description="Standard professional template",
            structure=["opening", "body", "closing"],
            tone="professional",
            length="medium",
            use_cases=["corporate", "formal"]
        )
        
        assert template.name == "Professional"
        assert template.tone == "professional"
        assert len(template.structure) == 3
        assert "corporate" in template.use_cases

class TestCoverLetterGenerator:
    """Test cases for CoverLetterGenerator class"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch('src.ai.cover_letter_generator.GroqClient') as mock_groq:
            mock_groq.return_value = Mock()
            self.generator = CoverLetterGenerator()
    
    def test_generator_initialization(self):
        """Test CoverLetterGenerator initialization"""
        assert self.generator.groq_client is not None
        assert self.generator.text_processor is not None
        assert len(self.generator.templates) == 5
        assert 'professional' in self.generator.templates
        assert 'enthusiastic' in self.generator.templates
        assert 'technical' in self.generator.templates
        assert 'concise' in self.generator.templates
        assert 'story_driven' in self.generator.templates
    
    def test_template_configurations(self):
        """Test template configurations"""
        templates = self.generator.templates
        
        # Test professional template
        professional = templates['professional']
        assert professional.tone == "professional"
        assert "corporate" in professional.use_cases
        
        # Test technical template
        technical = templates['technical']
        assert technical.tone == "technical"
        assert "engineering" in technical.use_cases
        
        # Test concise template
        concise = templates['concise']
        assert concise.length == "short"
        assert "brief_closing" in concise.structure
    
    def test_find_relevant_experience(self):
        """Test relevant experience finding"""
        experience = [
            {
                "title": "Python Developer",
                "company": "Tech Corp",
                "description": "Developed web applications using Python and Django"
            },
            {
                "title": "Data Analyst",
                "company": "Data Inc",
                "description": "Analyzed data using SQL and Excel"
            },
            {
                "title": "Frontend Developer",
                "company": "Web Co",
                "description": "Built user interfaces with React and JavaScript"
            }
        ]
        
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["Python", "Django", "React"]
        job_requirements.preferred_skills = ["JavaScript"]
        job_requirements.keywords = ["web", "development"]
        
        relevant_exp = self.generator._find_relevant_experience(experience, job_requirements)
        
        # Should return experiences sorted by relevance
        assert len(relevant_exp) <= 3
        assert all('relevance_score' in exp for exp in relevant_exp)
        
        # Python Developer should be most relevant
        if relevant_exp:
            assert relevant_exp[0]['title'] == "Python Developer"
    
    def test_check_education_match(self):
        """Test education matching"""
        education = [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University",
                "year": "2020"
            }
        ]
        
        # Test positive match
        requirements = ["Bachelor's degree in Computer Science"]
        assert self.generator._check_education_match(education, requirements) == True
        
        # Test no requirements
        assert self.generator._check_education_match(education, []) == True
        
        # Test with general degree requirement
        general_req = ["Bachelor's degree"]
        assert self.generator._check_education_match(education, general_req) == True
    
    def test_prepare_context(self):
        """Test context preparation"""
        resume_data = Mock(spec=ResumeData)
        resume_data.name = "John Doe"
        resume_data.email = "john@example.com"
        resume_data.summary = "Software developer"
        resume_data.skills = ["Python", "JavaScript", "React"]
        resume_data.experience = [{"title": "Developer", "description": "Built apps"}]
        resume_data.education = [{"degree": "BS Computer Science"}]
        
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["Python", "React"]
        job_requirements.preferred_skills = ["AWS"]
        job_requirements.responsibilities = ["Develop software"]
        job_requirements.job_level = "Mid-Level"
        job_requirements.industry = "Technology"
        job_requirements.remote_work = True
        job_requirements.salary_range = (100000, 150000)
        job_requirements.experience_years = {"Python": 3}
        job_requirements.education_requirements = ["Bachelor's degree"]
        job_requirements.keywords = ["development"]
        
        # Mock text processor
        self.generator.text_processor.calculate_skill_relevance = Mock(return_value=0.8)
        
        context = self.generator._prepare_context(
            resume_data, job_requirements, "Tech Corp", "Software Engineer", None
        )
        
        assert 'candidate' in context
        assert 'job' in context
        assert 'analysis' in context
        assert context['candidate']['name'] == "John Doe"
        assert context['job']['title'] == "Software Engineer"
        assert context['job']['company'] == "Tech Corp"
        assert context['analysis']['skill_match_score'] == 0.8
    
    def test_calculate_personalization_score(self):
        """Test personalization score calculation"""
        content = """
        Dear Hiring Manager,
        
        I am excited to apply for the Software Engineer position at Tech Corp.
        My experience with Python and React aligns well with your requirements.
        I have worked extensively in the Technology industry and am passionate
        about developing innovative solutions.
        
        At my previous company DataCorp, I led several successful projects.
        
        Sincerely,
        John Doe
        """
        
        context = {
            'job': {
                'company': 'Tech Corp',
                'title': 'Software Engineer',
                'industry': 'Technology'
            },
            'analysis': {
                'matching_skills': ['Python', 'React'],
                'relevant_experience': [{'company': 'DataCorp'}]
            }
        }
        
        score = self.generator._calculate_personalization_score(
            content, context, 'high'
        )
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be reasonably high given the content
    
    def test_validate_content_quality(self):
        """Test content quality validation"""
        context = {
            'job': {'title': 'Engineer', 'company': 'Corp'},
            'candidate': {'name': 'John'}
        }
        
        # Test valid content
        good_content = "I am writing to apply for the Engineer position at Corp. My name is John and I have relevant experience."
        result = self.generator._validate_content_quality(good_content, context)
        assert result == good_content
        
        # Test content missing required elements
        bad_content = "I am a great candidate for this position."
        result = self.generator._validate_content_quality(bad_content, context)
        # Should still return content but log warnings
        assert result == bad_content
    
    def test_extract_key_points(self):
        """Test key point extraction"""
        content = """
        I have 5 years of experience developing Python applications.
        My expertise in React has helped me build scalable user interfaces.
        I led a team of developers to implement microservices architecture.
        I enjoy working with databases and optimizing queries.
        """
        
        context = {
            'analysis': {
                'matching_skills': ['Python', 'React', 'microservices']
            }
        }
        
        key_points = self.generator._extract_key_points(content, context)
        
        assert len(key_points) <= 5
        assert any('Python' in point for point in key_points)
        assert any('React' in point for point in key_points)
    
    def test_calculate_length_score(self):
        """Test length score calculation"""
        # Optimal length
        assert self.generator._calculate_length_score(250) == 1.0
        assert self.generator._calculate_length_score(300) == 1.0
        
        # Good length
        assert self.generator._calculate_length_score(180) == 0.8
        assert self.generator._calculate_length_score(380) == 0.8
        
        # Poor length
        assert self.generator._calculate_length_score(50) == 0.3
        assert self.generator._calculate_length_score(600) == 0.3
    
    def test_calculate_readability_score(self):
        """Test readability score calculation"""
        # Good readability (15-20 words per sentence)
        good_content = "This is a sentence with exactly fifteen words in it for testing purposes. Another sentence with similar length for consistency."
        score = self.generator._calculate_readability_score(good_content)
        assert score >= 0.8
        
        # Poor readability (very long sentences)
        poor_content = "This is an extremely long sentence that goes on and on with many words and clauses that make it difficult to read and understand."
        score = self.generator._calculate_readability_score(poor_content)
        assert score <= 0.8
    
    def test_calculate_structure_score(self):
        """Test structure score calculation"""
        # Good structure (3-5 paragraphs)
        good_structure = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3.\n\nParagraph 4."
        score = self.generator._calculate_structure_score(good_structure)
        assert score == 1.0
        
        # Poor structure (too few paragraphs)
        poor_structure = "Only one paragraph here."
        score = self.generator._calculate_structure_score(poor_structure)
        assert score < 1.0
    
    def test_calculate_enthusiasm_score(self):
        """Test enthusiasm score calculation"""
        # High enthusiasm
        enthusiastic_content = "I am excited and passionate about this opportunity to contribute and make an impact."
        score = self.generator._calculate_enthusiasm_score(enthusiastic_content)
        assert score >= 0.8
        
        # Low enthusiasm
        bland_content = "I am applying for this position because I need a job."
        score = self.generator._calculate_enthusiasm_score(bland_content)
        assert score <= 0.6
    
    @patch('src.ai.cover_letter_generator.CoverLetterGenerator._generate_content')
    def test_generate_cover_letter(self, mock_generate_content):
        """Test complete cover letter generation"""
        # Mock content generation
        mock_generate_content.return_value = "Dear Hiring Manager,\n\nI am excited to apply for the Software Engineer position at Tech Corp.\n\nSincerely,\nJohn Doe"
        
        # Create test data
        resume_data = Mock(spec=ResumeData)
        resume_data.name = "John Doe"
        resume_data.email = "john@example.com"
        resume_data.summary = "Software developer"
        resume_data.skills = ["Python", "JavaScript"]
        resume_data.experience = []
        resume_data.education = []
        
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["Python"]
        job_requirements.preferred_skills = []
        job_requirements.responsibilities = []
        job_requirements.keywords = []
        job_requirements.experience_years = {}
        job_requirements.education_requirements = []
        
        # Mock text processor
        self.generator.text_processor.calculate_skill_relevance = Mock(return_value=0.8)
        
        # Generate cover letter
        result = self.generator.generate_cover_letter(
            resume_data=resume_data,
            job_requirements=job_requirements,
            company_name="Tech Corp",
            job_title="Software Engineer",
            template="professional",
            personalization_level="high"
        )
        
        assert isinstance(result, CoverLetterData)
        assert result.job_title == "Software Engineer"
        assert result.company_name == "Tech Corp"
        assert result.candidate_name == "John Doe"
        assert result.template_used == "professional"
        assert len(result.content) > 0
    
    def test_export_text_format(self):
        """Test text format export"""
        cover_letter = CoverLetterData(
            content="Test cover letter content",
            job_title="Engineer",
            company_name="Corp",
            candidate_name="John",
            generated_at="2024-01-01",
            word_count=4,
            key_points=[],
            personalization_score=0.8,
            template_used="professional"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            success = self.generator.export_cover_letter(
                cover_letter, tmp_path, 'text'
            )
            
            assert success == True
            assert tmp_path.exists()
            
            content = tmp_path.read_text(encoding='utf-8')
            assert "Test cover letter content" in content
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_export_json_format(self):
        """Test JSON format export"""
        cover_letter = CoverLetterData(
            content="Test content",
            job_title="Engineer",
            company_name="Corp",
            candidate_name="John",
            generated_at="2024-01-01",
            word_count=2,
            key_points=["Key point 1"],
            personalization_score=0.8,
            template_used="professional"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            success = self.generator.export_cover_letter(
                cover_letter, tmp_path, 'json'
            )
            
            assert success == True
            assert tmp_path.exists()
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert 'content' in data
            assert 'metadata' in data
            assert data['metadata']['job_title'] == "Engineer"
            assert data['metadata']['personalization_score'] == 0.8
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

class TestCoverLetterGeneratorWithAI:
    """Test cases for AI-enhanced functionality"""
    
    @patch('src.ai.cover_letter_generator.GroqClient')
    def test_ai_content_generation(self, mock_groq_client):
        """Test AI-powered content generation"""
        # Mock AI client
        mock_ai = Mock()
        mock_ai.generate_completion.return_value = "Dear Hiring Manager,\n\nI am writing to express my interest in the Software Engineer position at Tech Corp.\n\nSincerely,\nJohn Doe"
        mock_groq_client.return_value = mock_ai
        
        generator = CoverLetterGenerator()
        
        # Create test context
        context = {
            'candidate': {
                'name': 'John Doe',
                'summary': 'Software developer',
                'skills': ['Python', 'JavaScript']
            },
            'job': {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'required_skills': ['Python'],
                'industry': 'Technology'
            },
            'analysis': {
                'matching_skills': ['Python'],
                'relevant_experience': []
            }
        }
        
        content = generator._generate_content(context, generator.templates['professional'], 'high')
        
        # Verify AI was called
        mock_ai.generate_completion.assert_called_once()
        
        # Verify content
        assert "Dear Hiring Manager" in content
        assert "Tech Corp" in content
        assert "John Doe" in content

# Integration tests
class TestCoverLetterGeneratorIntegration:
    """Integration tests for cover letter generator"""
    
    @pytest.mark.integration
    def test_full_generation_workflow(self):
        """Test complete generation workflow (requires Groq API)"""
        # This test requires actual Groq API access
        pytest.skip("Integration test - requires Groq API key")
        
        generator = CoverLetterGenerator()
        
        # Create test data
        resume_data = ResumeData(
            raw_text="test", name="John Doe", email="john@test.com", phone="123",
            summary="Software developer", skills=["Python", "JavaScript"],
            experience=[{"title": "Developer", "description": "Built apps"}],
            education=[], sections={}
        )
        
        job_requirements = JobRequirements(
            required_skills=["Python", "JavaScript"], preferred_skills=[],
            experience_years={}, education_requirements=[], certifications=[],
            responsibilities=[], keywords=[], soft_skills=[], technologies={},
            salary_range=None, job_level="Mid-Level", remote_work=False,
            benefits=[], company_size="Unknown", industry="Technology"
        )
        
        # Test generation
        result = generator.generate_cover_letter(
            resume_data, job_requirements, "Test Corp", "Software Engineer"
        )
        
        assert isinstance(result, CoverLetterData)
        assert len(result.content) > 100
        assert result.personalization_score > 0

if __name__ == "__main__":
    pytest.main([__file__])
