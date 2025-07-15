"""
Test cases for AI Resume Modifier Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from src.ai.resume_modifier import ResumeModifier, ResumeModification
from src.parsers.resume_parser import ResumeData
from src.parsers.job_description_parser import JobRequirements

class TestResumeModification:
    """Test cases for ResumeModification data class"""
    
    def test_resume_modification_creation(self):
        """Test ResumeModification creation"""
        original_resume = Mock(spec=ResumeData)
        modified_resume = Mock(spec=ResumeData)
        
        modification = ResumeModification(
            original_resume=original_resume,
            modified_resume=modified_resume,
            modifications_made=["Enhanced summary"],
            keyword_additions=["React", "AWS"],
            skill_enhancements=["JavaScript"],
            match_score_before=0.6,
            match_score_after=0.8,
            improvement_percentage=33.3
        )
        
        assert modification.original_resume == original_resume
        assert modification.modified_resume == modified_resume
        assert "Enhanced summary" in modification.modifications_made
        assert "React" in modification.keyword_additions
        assert modification.match_score_after > modification.match_score_before
        assert modification.improvement_percentage == 33.3

class TestResumeModifier:
    """Test cases for ResumeModifier class"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch('src.ai.resume_modifier.GroqClient') as mock_groq:
            mock_groq.return_value = Mock()
            self.modifier = ResumeModifier()
    
    def test_modifier_initialization(self):
        """Test ResumeModifier initialization"""
        assert self.modifier.groq_client is not None
        assert self.modifier.text_processor is not None
        assert 'conservative' in self.modifier.modification_strategies
        assert 'moderate' in self.modifier.modification_strategies
        assert 'aggressive' in self.modifier.modification_strategies
    
    def test_modification_strategies(self):
        """Test modification strategy configurations"""
        strategies = self.modifier.modification_strategies
        
        # Test conservative strategy
        conservative = strategies['conservative']
        assert conservative['keyword_density'] < strategies['moderate']['keyword_density']
        assert conservative['rewrite_percentage'] < strategies['moderate']['rewrite_percentage']
        assert conservative['add_skills'] == False
        
        # Test aggressive strategy
        aggressive = strategies['aggressive']
        assert aggressive['keyword_density'] > strategies['moderate']['keyword_density']
        assert aggressive['rewrite_percentage'] > strategies['moderate']['rewrite_percentage']
        assert aggressive['add_skills'] == True
    
    def test_create_resume_copy(self):
        """Test resume copying functionality"""
        original_resume = ResumeData(
            raw_text="test",
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            summary="Software developer",
            skills=["Python", "JavaScript"],
            experience=[{"title": "Developer", "company": "Tech Corp"}],
            education=[{"degree": "BS Computer Science"}],
            sections={"summary": "Software developer"}
        )
        
        copied_resume = self.modifier._create_resume_copy(original_resume)
        
        assert copied_resume.name == original_resume.name
        assert copied_resume.skills == original_resume.skills
        assert copied_resume.skills is not original_resume.skills  # Different objects
        assert copied_resume.experience == original_resume.experience
        assert copied_resume.experience is not original_resume.experience  # Different objects
    
    def test_calculate_match_score(self):
        """Test match score calculation"""
        resume_data = Mock(spec=ResumeData)
        resume_data.skills = ["Python", "JavaScript", "React"]
        
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["Python", "React", "AWS"]
        job_requirements.preferred_skills = ["Docker"]
        
        # Mock text processor
        self.modifier.text_processor.calculate_skill_relevance = Mock(return_value=0.75)
        
        score = self.modifier._calculate_match_score(resume_data, job_requirements)
        
        assert score == 0.75
        self.modifier.text_processor.calculate_skill_relevance.assert_called_once()
    
    def test_identify_addable_skills(self):
        """Test skill addition logic"""
        current_skills = ["JavaScript", "React", "Git"]
        required_skills = ["JavaScript", "HTML", "CSS", "AWS", "Docker"]
        
        addable_skills = self.modifier._identify_addable_skills(current_skills, required_skills)
        
        # Should suggest HTML and CSS since candidate has JavaScript and React
        assert "HTML" in addable_skills or "CSS" in addable_skills
        # Should not suggest JavaScript (already have it)
        assert "JavaScript" not in addable_skills
    
    def test_prioritize_skills(self):
        """Test skill prioritization"""
        skills = ["Git", "Python", "Docker", "JavaScript", "AWS"]
        
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["Python", "JavaScript"]
        job_requirements.preferred_skills = ["Docker"]
        
        prioritized = self.modifier._prioritize_skills(skills, job_requirements)
        
        # Required skills should come first
        assert prioritized.index("Python") < prioritized.index("Git")
        assert prioritized.index("JavaScript") < prioritized.index("Git")
        # Preferred skills should come before other skills
        assert prioritized.index("Docker") < prioritized.index("Git")
    
    def test_add_skill_variations(self):
        """Test skill variation addition"""
        skills = ["JavaScript", "Python", "React"]
        job_requirements = Mock(spec=JobRequirements)
        
        enhanced_skills = self.modifier._add_skill_variations(skills, job_requirements)
        
        # Should have original skills
        assert "JavaScript" in enhanced_skills
        assert "Python" in enhanced_skills
        assert "React" in enhanced_skills
        
        # Should have some variations
        assert len(enhanced_skills) >= len(skills)
    
    def test_validate_summary(self):
        """Test summary validation"""
        original = "Software developer with 3 years of experience."
        
        # Test valid enhancement
        enhanced = "Experienced software developer with 3 years of full-stack development experience."
        result = self.modifier._validate_summary(enhanced, original)
        assert result == enhanced
        
        # Test too long enhancement
        too_long = "A" * (len(original) * 3)
        result = self.modifier._validate_summary(too_long, original)
        assert result == original
        
        # Test too short enhancement
        too_short = "Dev"
        result = self.modifier._validate_summary(too_short, original)
        assert result == original
    
    def test_validate_experience(self):
        """Test experience validation"""
        original = "Developed web applications using JavaScript and Python."
        
        # Test valid enhancement
        enhanced = "Developed and maintained scalable web applications using JavaScript and Python frameworks."
        result = self.modifier._validate_experience(enhanced, original)
        assert result == enhanced
        
        # Test too long enhancement
        too_long = "A" * (len(original) * 3)
        result = self.modifier._validate_experience(too_long, original)
        assert result == original
        
        # Test too short enhancement
        too_short = "Dev apps"
        result = self.modifier._validate_experience(too_short, original)
        assert result == original
    
    @patch('src.ai.resume_modifier.ResumeModifier._enhance_summary')
    @patch('src.ai.resume_modifier.ResumeModifier._optimize_skills')
    @patch('src.ai.resume_modifier.ResumeModifier._enhance_experience')
    def test_modify_resume_for_job(self, mock_enhance_exp, mock_optimize_skills, mock_enhance_summary):
        """Test complete resume modification workflow"""
        # Setup mocks
        mock_enhance_summary.return_value = ("Enhanced summary", ["Summary enhanced"])
        mock_optimize_skills.return_value = (["Python", "React"], ["Skills optimized"], ["React"])
        mock_enhance_exp.return_value = ([{"title": "Dev", "description": "Enhanced desc"}], ["Experience enhanced"], ["keywords"])
        
        # Mock match score calculation
        self.modifier._calculate_match_score = Mock(side_effect=[0.6, 0.8])
        
        # Create test data
        resume_data = ResumeData(
            raw_text="test", name="John", email="john@test.com", phone="123",
            summary="Original summary", skills=["Python"], experience=[{"title": "Dev"}],
            education=[], sections={}
        )
        
        job_requirements = Mock(spec=JobRequirements)
        
        # Test modification
        result = self.modifier.modify_resume_for_job(resume_data, job_requirements)
        
        assert isinstance(result, ResumeModification)
        assert result.match_score_before == 0.6
        assert result.match_score_after == 0.8
        assert result.improvement_percentage > 0
        assert len(result.modifications_made) > 0
    
    def test_generate_multiple_versions(self):
        """Test multiple version generation"""
        resume_data = Mock(spec=ResumeData)
        job_requirements = Mock(spec=JobRequirements)
        
        # Mock the modify_resume_for_job method
        mock_modification = Mock(spec=ResumeModification)
        self.modifier.modify_resume_for_job = Mock(return_value=mock_modification)
        
        strategies = ['conservative', 'moderate']
        versions = self.modifier.generate_multiple_versions(
            resume_data, job_requirements, strategies
        )
        
        assert len(versions) == 2
        assert 'conservative' in versions
        assert 'moderate' in versions
        assert self.modifier.modify_resume_for_job.call_count == 2
    
    def test_export_text_format(self):
        """Test text format export"""
        modification = self._create_mock_modification()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            success = self.modifier.export_modified_resume(
                modification, tmp_path, 'text'
            )
            
            assert success == True
            assert tmp_path.exists()
            
            # Check content
            content = tmp_path.read_text(encoding='utf-8')
            assert "John Doe" in content
            assert "john@example.com" in content
            assert "Software developer" in content
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_export_json_format(self):
        """Test JSON format export"""
        modification = self._create_mock_modification()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            success = self.modifier.export_modified_resume(
                modification, tmp_path, 'json'
            )
            
            assert success == True
            assert tmp_path.exists()
            
            # Check content
            with open(tmp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert 'modified_resume' in data
            assert 'modifications' in data
            assert data['modified_resume']['name'] == "John Doe"
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_export_markdown_format(self):
        """Test Markdown format export"""
        modification = self._create_mock_modification()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            success = self.modifier.export_modified_resume(
                modification, tmp_path, 'markdown'
            )
            
            assert success == True
            assert tmp_path.exists()
            
            # Check content
            content = tmp_path.read_text(encoding='utf-8')
            assert "# John Doe" in content
            assert "## Professional Summary" in content
            assert "## Technical Skills" in content
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def _create_mock_modification(self):
        """Create a mock ResumeModification for testing"""
        modified_resume = ResumeData(
            raw_text="test",
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            summary="Software developer with experience",
            skills=["Python", "JavaScript", "React"],
            experience=[{
                "title": "Software Developer",
                "company": "Tech Corp",
                "description": "Developed applications"
            }],
            education=[{
                "degree": "BS Computer Science",
                "institution": "University",
                "year": "2020"
            }],
            sections={}
        )
        
        return ResumeModification(
            original_resume=Mock(),
            modified_resume=modified_resume,
            modifications_made=["Enhanced summary", "Optimized skills"],
            keyword_additions=["React", "AWS"],
            skill_enhancements=["JavaScript"],
            match_score_before=0.6,
            match_score_after=0.8,
            improvement_percentage=33.3
        )

class TestResumeModifierWithAI:
    """Test cases for AI-enhanced functionality"""
    
    @patch('src.ai.resume_modifier.GroqClient')
    def test_ai_summary_enhancement(self, mock_groq_client):
        """Test AI-powered summary enhancement"""
        # Mock AI client
        mock_ai = Mock()
        mock_ai.generate_completion.return_value = "Enhanced software developer with React and Node.js experience"
        mock_groq_client.return_value = mock_ai
        
        modifier = ResumeModifier()
        
        original_summary = "Software developer with experience"
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["React", "Node.js"]
        job_requirements.preferred_skills = ["AWS"]
        job_requirements.job_level = "Senior"
        job_requirements.industry = "Technology"
        
        strategy_config = modifier.modification_strategies['moderate']
        
        enhanced_summary, modifications = modifier._enhance_summary(
            original_summary, job_requirements, strategy_config, True
        )
        
        # Verify AI was called
        mock_ai.generate_completion.assert_called_once()
        
        # Verify enhancement
        assert enhanced_summary != original_summary
        assert len(modifications) > 0
    
    @patch('src.ai.resume_modifier.GroqClient')
    def test_ai_experience_enhancement(self, mock_groq_client):
        """Test AI-powered experience enhancement"""
        # Mock AI client
        mock_ai = Mock()
        mock_ai.generate_completion.return_value = "Developed and maintained scalable web applications using React and Node.js"
        mock_groq_client.return_value = mock_ai
        
        modifier = ResumeModifier()
        
        original_description = "Developed web applications"
        job_requirements = Mock(spec=JobRequirements)
        job_requirements.required_skills = ["React", "Node.js"]
        job_requirements.responsibilities = ["Build scalable applications"]
        job_requirements.job_level = "Senior"
        
        strategy_config = modifier.modification_strategies['moderate']
        
        enhanced_desc, modifications, keywords = modifier._enhance_job_description(
            original_description, job_requirements, strategy_config, True
        )
        
        # Verify AI was called
        mock_ai.generate_completion.assert_called_once()
        
        # Verify enhancement
        assert enhanced_desc != original_description
        assert len(modifications) > 0

# Integration tests
class TestResumeModifierIntegration:
    """Integration tests for resume modifier"""
    
    @pytest.mark.integration
    def test_full_modification_workflow(self):
        """Test complete modification workflow (requires Groq API)"""
        # This test requires actual Groq API access
        pytest.skip("Integration test - requires Groq API key")
        
        modifier = ResumeModifier()
        
        # Create test data
        resume_data = ResumeData(
            raw_text="test", name="John Doe", email="john@test.com", phone="123",
            summary="Software developer with experience", skills=["Python", "JavaScript"],
            experience=[{"title": "Developer", "description": "Built applications"}],
            education=[], sections={}
        )
        
        job_requirements = JobRequirements(
            required_skills=["React", "Node.js", "JavaScript"],
            preferred_skills=["AWS"], experience_years={}, education_requirements=[],
            certifications=[], responsibilities=[], keywords=[], soft_skills=[],
            technologies={}, salary_range=None, job_level="Mid-Level",
            remote_work=False, benefits=[], company_size="Unknown", industry="Technology"
        )
        
        # Test modification
        result = modifier.modify_resume_for_job(resume_data, job_requirements)
        
        assert isinstance(result, ResumeModification)
        assert result.match_score_after >= result.match_score_before

if __name__ == "__main__":
    pytest.main([__file__])
