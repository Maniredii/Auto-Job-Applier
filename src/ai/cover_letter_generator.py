"""
AI Cover Letter Generator Module
Uses Groq API to generate personalized cover letters for job applications
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime

from .groq_client import GroqClient
from ..parsers.resume_parser import ResumeData
from ..parsers.job_description_parser import JobRequirements
from ..parsers.text_processor import TextProcessor
from config import config

logger = logging.getLogger(__name__)

@dataclass
class CoverLetterData:
    """Data class for generated cover letter"""
    content: str
    job_title: str
    company_name: str
    candidate_name: str
    generated_at: str
    word_count: int
    key_points: List[str]
    personalization_score: float
    template_used: str
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.word_count:
            self.word_count = len(self.content.split())

@dataclass
class CoverLetterTemplate:
    """Template for cover letter generation"""
    name: str
    description: str
    structure: List[str]
    tone: str
    length: str
    use_cases: List[str]

class CoverLetterGenerator:
    """AI-powered cover letter generator using Groq API"""
    
    def __init__(self):
        """Initialize cover letter generator"""
        self.groq_client = GroqClient()
        self.text_processor = TextProcessor()
        
        # Cover letter templates
        self.templates = {
            'professional': CoverLetterTemplate(
                name="Professional",
                description="Standard professional cover letter",
                structure=["opening", "experience_match", "value_proposition", "closing"],
                tone="professional",
                length="medium",
                use_cases=["corporate", "traditional", "formal"]
            ),
            'enthusiastic': CoverLetterTemplate(
                name="Enthusiastic",
                description="Energetic and passionate tone",
                structure=["engaging_opening", "passion_statement", "relevant_experience", "excited_closing"],
                tone="enthusiastic",
                length="medium",
                use_cases=["startup", "creative", "tech"]
            ),
            'technical': CoverLetterTemplate(
                name="Technical",
                description="Focus on technical skills and achievements",
                structure=["technical_opening", "skills_showcase", "project_highlights", "technical_closing"],
                tone="technical",
                length="detailed",
                use_cases=["engineering", "development", "technical"]
            ),
            'concise': CoverLetterTemplate(
                name="Concise",
                description="Brief and to-the-point",
                structure=["direct_opening", "key_qualifications", "brief_closing"],
                tone="direct",
                length="short",
                use_cases=["busy_hiring_managers", "quick_applications"]
            ),
            'story_driven': CoverLetterTemplate(
                name="Story-Driven",
                description="Narrative approach with personal story",
                structure=["story_opening", "challenge_solution", "growth_narrative", "future_vision"],
                tone="narrative",
                length="detailed",
                use_cases=["career_change", "unique_background", "creative_roles"]
            )
        }
        
        # Personalization strategies
        self.personalization_strategies = {
            'company_research': {
                'weight': 0.3,
                'description': 'Incorporate company-specific information'
            },
            'role_alignment': {
                'weight': 0.25,
                'description': 'Align experience with job requirements'
            },
            'skill_matching': {
                'weight': 0.2,
                'description': 'Highlight relevant skills and technologies'
            },
            'value_proposition': {
                'weight': 0.15,
                'description': 'Articulate unique value to the company'
            },
            'cultural_fit': {
                'weight': 0.1,
                'description': 'Demonstrate cultural alignment'
            }
        }
    
    def generate_cover_letter(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        company_name: str,
        job_title: str,
        template: str = 'professional',
        personalization_level: str = 'high',
        additional_context: Optional[Dict] = None
    ) -> CoverLetterData:
        """
        Generate personalized cover letter
        
        Args:
            resume_data: Candidate's resume data
            job_requirements: Target job requirements
            company_name: Target company name
            job_title: Target job title
            template: Cover letter template to use
            personalization_level: Level of personalization (low, medium, high)
            additional_context: Additional context for personalization
            
        Returns:
            CoverLetterData object with generated cover letter
        """
        logger.info(f"Generating cover letter for {job_title} at {company_name}")
        
        # Validate inputs
        if template not in self.templates:
            logger.warning(f"Unknown template '{template}', using 'professional'")
            template = 'professional'
        
        # Prepare context
        context = self._prepare_context(
            resume_data, job_requirements, company_name, job_title, additional_context
        )
        
        # Generate cover letter content
        content = self._generate_content(
            context, template, personalization_level
        )
        
        # Post-process and validate
        processed_content = self._post_process_content(content, context)
        
        # Extract key points
        key_points = self._extract_key_points(processed_content, context)
        
        # Calculate personalization score
        personalization_score = self._calculate_personalization_score(
            processed_content, context, personalization_level
        )
        
        logger.info(f"Cover letter generated successfully (personalization: {personalization_score:.1%})")
        
        return CoverLetterData(
            content=processed_content,
            job_title=job_title,
            company_name=company_name,
            candidate_name=resume_data.name,
            generated_at="",  # Will be auto-filled
            word_count=0,  # Will be auto-calculated
            key_points=key_points,
            personalization_score=personalization_score,
            template_used=template
        )
    
    def _prepare_context(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        company_name: str,
        job_title: str,
        additional_context: Optional[Dict]
    ) -> Dict:
        """Prepare context for cover letter generation"""
        
        # Analyze skill matches
        skill_matches = self.text_processor.calculate_skill_relevance(
            resume_data.skills,
            job_requirements.required_skills + job_requirements.preferred_skills
        )
        
        # Find top matching skills
        matching_skills = []
        resume_skills_lower = [skill.lower() for skill in resume_data.skills]
        for skill in job_requirements.required_skills + job_requirements.preferred_skills:
            if skill.lower() in resume_skills_lower:
                matching_skills.append(skill)
        
        # Extract relevant experience
        relevant_experience = self._find_relevant_experience(
            resume_data.experience, job_requirements
        )
        
        # Prepare context dictionary
        context = {
            'candidate': {
                'name': resume_data.name,
                'email': resume_data.email,
                'summary': resume_data.summary,
                'skills': resume_data.skills,
                'experience': resume_data.experience,
                'education': resume_data.education
            },
            'job': {
                'title': job_title,
                'company': company_name,
                'required_skills': job_requirements.required_skills,
                'preferred_skills': job_requirements.preferred_skills,
                'responsibilities': job_requirements.responsibilities,
                'job_level': job_requirements.job_level,
                'industry': job_requirements.industry,
                'remote_work': job_requirements.remote_work,
                'salary_range': job_requirements.salary_range
            },
            'analysis': {
                'skill_match_score': skill_matches,
                'matching_skills': matching_skills[:8],  # Top 8 matches
                'relevant_experience': relevant_experience,
                'experience_years': job_requirements.experience_years,
                'education_match': self._check_education_match(
                    resume_data.education, job_requirements.education_requirements
                )
            },
            'additional': additional_context or {}
        }
        
        return context
    
    def _find_relevant_experience(
        self,
        experience: List[Dict[str, str]],
        job_requirements: JobRequirements
    ) -> List[Dict[str, str]]:
        """Find most relevant experience entries"""
        relevant_exp = []
        
        # Keywords to look for in experience
        job_keywords = (
            job_requirements.required_skills + 
            job_requirements.preferred_skills + 
            job_requirements.keywords
        )
        job_keywords_lower = [kw.lower() for kw in job_keywords]
        
        for exp in experience:
            relevance_score = 0
            description = exp.get('description', '').lower()
            title = exp.get('title', '').lower()
            
            # Score based on keyword matches
            for keyword in job_keywords_lower:
                if keyword in description or keyword in title:
                    relevance_score += 1
            
            if relevance_score > 0:
                exp_copy = exp.copy()
                exp_copy['relevance_score'] = relevance_score
                relevant_exp.append(exp_copy)
        
        # Sort by relevance and return top 3
        relevant_exp.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return relevant_exp[:3]
    
    def _check_education_match(
        self,
        education: List[Dict[str, str]],
        education_requirements: List[str]
    ) -> bool:
        """Check if education matches requirements"""
        if not education_requirements:
            return True
        
        education_text = ' '.join([
            edu.get('degree', '') + ' ' + edu.get('field', '')
            for edu in education
        ]).lower()
        
        for req in education_requirements:
            req_lower = req.lower()
            if any(keyword in education_text for keyword in ['bachelor', 'master', 'phd', 'degree']):
                return True
        
        return False
    
    def _generate_content(
        self,
        context: Dict,
        template: str,
        personalization_level: str
    ) -> str:
        """Generate cover letter content using AI"""
        
        template_config = self.templates[template]
        
        # Create comprehensive prompt
        prompt = self._create_cover_letter_prompt(context, template_config, personalization_level)
        
        try:
            # Generate content using Groq
            content = self.groq_client.generate_completion(
                prompt,
                system_message=f"You are an expert cover letter writer who creates compelling, personalized cover letters that highlight the candidate's relevant experience and enthusiasm for the role. Use a {template_config.tone} tone and {template_config.length} length."
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {str(e)}")
            # Fallback to template-based generation
            return self._generate_fallback_content(context, template_config)
    
    def _create_cover_letter_prompt(
        self,
        context: Dict,
        template_config: CoverLetterTemplate,
        personalization_level: str
    ) -> str:
        """Create detailed prompt for cover letter generation"""
        
        candidate = context['candidate']
        job = context['job']
        analysis = context['analysis']
        
        # Personalization instructions based on level
        personalization_instructions = {
            'low': "Create a general cover letter with basic customization.",
            'medium': "Include specific job requirements and highlight relevant experience.",
            'high': "Create a highly personalized letter with company research, specific examples, and strong value proposition."
        }
        
        prompt = f"""
        Write a compelling cover letter for the following job application:
        
        CANDIDATE INFORMATION:
        Name: {candidate['name']}
        Professional Summary: {candidate['summary']}
        Key Skills: {', '.join(candidate['skills'][:10])}
        Relevant Experience: {len(analysis['relevant_experience'])} positions
        
        JOB DETAILS:
        Position: {job['title']}
        Company: {job['company']}
        Industry: {job['industry']}
        Job Level: {job['job_level']}
        Remote Work: {job['remote_work']}
        
        REQUIREMENTS ANALYSIS:
        Required Skills: {', '.join(job['required_skills'][:8])}
        Matching Skills: {', '.join(analysis['matching_skills'])}
        Skill Match Score: {analysis['skill_match_score']:.1%}
        
        MOST RELEVANT EXPERIENCE:
        """
        
        # Add relevant experience details
        for i, exp in enumerate(analysis['relevant_experience'][:2], 1):
            prompt += f"\n{i}. {exp.get('title', 'Position')} at {exp.get('company', 'Company')}"
            if exp.get('description'):
                prompt += f"\n   {exp['description'][:200]}..."
        
        prompt += f"""
        
        COVER LETTER REQUIREMENTS:
        Template: {template_config.name} ({template_config.description})
        Tone: {template_config.tone}
        Length: {template_config.length}
        Structure: {' → '.join(template_config.structure)}
        Personalization Level: {personalization_level}
        
        INSTRUCTIONS:
        {personalization_instructions[personalization_level]}
        
        - Start with a compelling opening that mentions the specific role and company
        - Highlight 2-3 most relevant experiences with specific examples
        - Demonstrate knowledge of the company and role requirements
        - Show enthusiasm and cultural fit
        - Include a strong call-to-action closing
        - Use professional business letter format
        - Keep paragraphs concise and impactful
        - Incorporate relevant keywords naturally
        - Maintain authenticity and avoid generic phrases
        
        FORMATTING:
        - Include proper business letter header with date
        - Address to hiring manager or relevant title
        - Use clear paragraph breaks
        - Professional closing signature
        
        Generate the complete cover letter:
        """
        
        return prompt
    
    def _generate_fallback_content(
        self,
        context: Dict,
        template_config: CoverLetterTemplate
    ) -> str:
        """Generate fallback content if AI generation fails"""
        
        candidate = context['candidate']
        job = context['job']
        analysis = context['analysis']
        
        # Basic template-based cover letter
        content = f"""
{datetime.now().strftime('%B %d, %Y')}

Dear Hiring Manager,

I am writing to express my strong interest in the {job['title']} position at {job['company']}. With my background in {', '.join(analysis['matching_skills'][:3])}, I am excited about the opportunity to contribute to your team.

In my previous role as {analysis['relevant_experience'][0].get('title', 'Professional') if analysis['relevant_experience'] else 'a professional'}, I have developed expertise in {', '.join(candidate['skills'][:5])}. My experience aligns well with your requirements for {', '.join(job['required_skills'][:3])}.

Key qualifications I bring include:
• {analysis['matching_skills'][0] if analysis['matching_skills'] else 'Relevant technical skills'}
• {analysis['matching_skills'][1] if len(analysis['matching_skills']) > 1 else 'Strong problem-solving abilities'}
• {analysis['matching_skills'][2] if len(analysis['matching_skills']) > 2 else 'Excellent communication skills'}

I am particularly drawn to {job['company']} because of your work in {job['industry']} and would welcome the opportunity to discuss how my skills and enthusiasm can contribute to your continued success.

Thank you for your consideration. I look forward to hearing from you.

Sincerely,
{candidate['name']}
        """.strip()
        
        return content

    def _post_process_content(self, content: str, context: Dict) -> str:
        """Post-process and clean generated content"""

        # Remove any unwanted AI instructions or formatting
        content = re.sub(r'^(cover letter:|letter:)', '', content, flags=re.IGNORECASE)
        content = content.strip()

        # Ensure proper formatting
        content = self._ensure_proper_formatting(content, context)

        # Validate content quality
        content = self._validate_content_quality(content, context)

        return content

    def _ensure_proper_formatting(self, content: str, context: Dict) -> str:
        """Ensure proper business letter formatting"""

        lines = content.split('\n')
        formatted_lines = []

        # Check if date is present at the top
        has_date = False
        for line in lines[:3]:
            if re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december|\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})', line.lower()):
                has_date = True
                break

        # Add date if missing
        if not has_date:
            formatted_lines.append(datetime.now().strftime('%B %d, %Y'))
            formatted_lines.append('')

        # Process existing lines
        for line in lines:
            formatted_lines.append(line)

        # Ensure proper spacing between paragraphs
        final_lines = []
        prev_line_empty = False

        for line in formatted_lines:
            if line.strip() == '':
                if not prev_line_empty:
                    final_lines.append(line)
                prev_line_empty = True
            else:
                final_lines.append(line)
                prev_line_empty = False

        return '\n'.join(final_lines)

    def _validate_content_quality(self, content: str, context: Dict) -> str:
        """Validate and ensure content quality"""

        # Check minimum length
        word_count = len(content.split())
        if word_count < 150:
            logger.warning("Cover letter too short, may need enhancement")
        elif word_count > 500:
            logger.warning("Cover letter too long, may need trimming")

        # Check for required elements
        required_elements = [
            context['job']['title'],
            context['job']['company'],
            context['candidate']['name']
        ]

        content_lower = content.lower()
        for element in required_elements:
            if element.lower() not in content_lower:
                logger.warning(f"Missing required element: {element}")

        return content

    def _extract_key_points(self, content: str, context: Dict) -> List[str]:
        """Extract key points from the cover letter"""

        key_points = []

        # Extract sentences that mention skills
        sentences = re.split(r'[.!?]+', content)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            # Check if sentence mentions relevant skills
            sentence_lower = sentence.lower()
            for skill in context['analysis']['matching_skills']:
                if skill.lower() in sentence_lower:
                    key_points.append(sentence)
                    break

        # Extract experience highlights
        experience_keywords = ['experience', 'developed', 'led', 'managed', 'implemented', 'created']
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in experience_keywords):
                if sentence not in key_points:
                    key_points.append(sentence)

        return key_points[:5]  # Return top 5 key points

    def _calculate_personalization_score(
        self,
        content: str,
        context: Dict,
        personalization_level: str
    ) -> float:
        """Calculate personalization score for the cover letter"""

        score = 0.0
        content_lower = content.lower()

        # Company name mentions
        company_mentions = content_lower.count(context['job']['company'].lower())
        score += min(company_mentions * 0.1, 0.2)

        # Job title mentions
        job_title_mentions = content_lower.count(context['job']['title'].lower())
        score += min(job_title_mentions * 0.1, 0.15)

        # Skill matches
        skill_mentions = 0
        for skill in context['analysis']['matching_skills']:
            if skill.lower() in content_lower:
                skill_mentions += 1
        score += min(skill_mentions * 0.05, 0.25)

        # Industry/domain mentions
        if context['job']['industry'].lower() in content_lower:
            score += 0.1

        # Specific experience mentions
        experience_specificity = 0
        for exp in context['analysis']['relevant_experience']:
            if exp.get('company', '').lower() in content_lower:
                experience_specificity += 1
        score += min(experience_specificity * 0.1, 0.2)

        # Length and detail bonus
        word_count = len(content.split())
        if 200 <= word_count <= 400:
            score += 0.1

        # Personalization level adjustment
        level_multipliers = {'low': 0.7, 'medium': 0.85, 'high': 1.0}
        score *= level_multipliers.get(personalization_level, 1.0)

        return min(score, 1.0)

    def generate_multiple_versions(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        company_name: str,
        job_title: str,
        templates: List[str] = None,
        personalization_level: str = 'high'
    ) -> Dict[str, CoverLetterData]:
        """
        Generate multiple cover letter versions with different templates

        Args:
            resume_data: Candidate's resume data
            job_requirements: Target job requirements
            company_name: Target company name
            job_title: Target job title
            templates: List of templates to use
            personalization_level: Level of personalization

        Returns:
            Dictionary mapping template names to cover letters
        """
        if templates is None:
            templates = ['professional', 'enthusiastic', 'technical']

        versions = {}

        for template in templates:
            if template in self.templates:
                logger.info(f"Generating {template} version")
                try:
                    cover_letter = self.generate_cover_letter(
                        resume_data,
                        job_requirements,
                        company_name,
                        job_title,
                        template=template,
                        personalization_level=personalization_level
                    )
                    versions[template] = cover_letter
                except Exception as e:
                    logger.error(f"Failed to generate {template} version: {str(e)}")

        return versions

    def export_cover_letter(
        self,
        cover_letter: CoverLetterData,
        output_path: Path,
        format_type: str = 'text'
    ) -> bool:
        """
        Export cover letter to file

        Args:
            cover_letter: Cover letter data
            output_path: Output file path
            format_type: Export format (text, pdf, docx, json)

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == 'json':
                self._export_json(cover_letter, output_path)
            elif format_type == 'markdown':
                self._export_markdown(cover_letter, output_path)
            else:  # text
                self._export_text(cover_letter, output_path)

            logger.info(f"Cover letter exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return False

    def _export_text(self, cover_letter: CoverLetterData, output_path: Path):
        """Export as plain text"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter.content)

    def _export_json(self, cover_letter: CoverLetterData, output_path: Path):
        """Export as JSON with metadata"""
        data = {
            'content': cover_letter.content,
            'metadata': {
                'job_title': cover_letter.job_title,
                'company_name': cover_letter.company_name,
                'candidate_name': cover_letter.candidate_name,
                'generated_at': cover_letter.generated_at,
                'word_count': cover_letter.word_count,
                'personalization_score': cover_letter.personalization_score,
                'template_used': cover_letter.template_used,
                'key_points': cover_letter.key_points
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_markdown(self, cover_letter: CoverLetterData, output_path: Path):
        """Export as Markdown with metadata"""
        content = f"""# Cover Letter - {cover_letter.job_title} at {cover_letter.company_name}

**Candidate:** {cover_letter.candidate_name}
**Generated:** {cover_letter.generated_at}
**Template:** {cover_letter.template_used}
**Personalization Score:** {cover_letter.personalization_score:.1%}
**Word Count:** {cover_letter.word_count}

---

{cover_letter.content}

---

## Key Points Highlighted
"""

        for i, point in enumerate(cover_letter.key_points, 1):
            content += f"{i}. {point}\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def analyze_cover_letter_quality(self, cover_letter: CoverLetterData) -> Dict[str, float]:
        """
        Analyze cover letter quality metrics

        Args:
            cover_letter: Cover letter to analyze

        Returns:
            Dictionary with quality metrics
        """
        content = cover_letter.content

        # Calculate various quality metrics
        metrics = {
            'personalization_score': cover_letter.personalization_score,
            'length_score': self._calculate_length_score(cover_letter.word_count),
            'readability_score': self._calculate_readability_score(content),
            'structure_score': self._calculate_structure_score(content),
            'enthusiasm_score': self._calculate_enthusiasm_score(content)
        }

        # Overall quality score (weighted average)
        weights = {
            'personalization_score': 0.3,
            'length_score': 0.2,
            'readability_score': 0.25,
            'structure_score': 0.15,
            'enthusiasm_score': 0.1
        }

        overall_score = sum(metrics[key] * weights[key] for key in weights)
        metrics['overall_score'] = overall_score

        return metrics

    def _calculate_length_score(self, word_count: int) -> float:
        """Calculate score based on optimal length"""
        if 200 <= word_count <= 350:
            return 1.0
        elif 150 <= word_count < 200 or 350 < word_count <= 400:
            return 0.8
        elif 100 <= word_count < 150 or 400 < word_count <= 500:
            return 0.6
        else:
            return 0.3

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score (simplified)"""
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())

        if sentences == 0:
            return 0.0

        avg_sentence_length = words / sentences

        # Optimal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif 10 <= avg_sentence_length < 15 or 20 < avg_sentence_length <= 25:
            return 0.8
        else:
            return 0.6

    def _calculate_structure_score(self, content: str) -> float:
        """Calculate structure score based on paragraph organization"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        # Optimal structure has 3-5 paragraphs
        if 3 <= len(paragraphs) <= 5:
            return 1.0
        elif len(paragraphs) == 2 or len(paragraphs) == 6:
            return 0.7
        else:
            return 0.5

    def _calculate_enthusiasm_score(self, content: str) -> float:
        """Calculate enthusiasm score based on positive language"""
        enthusiasm_words = [
            'excited', 'passionate', 'enthusiastic', 'thrilled', 'eager',
            'motivated', 'inspired', 'committed', 'dedicated', 'love',
            'enjoy', 'opportunity', 'contribute', 'impact', 'growth'
        ]

        content_lower = content.lower()
        enthusiasm_count = sum(1 for word in enthusiasm_words if word in content_lower)

        # Normalize by content length
        words = len(content.split())
        enthusiasm_ratio = enthusiasm_count / words if words > 0 else 0

        # Optimal ratio is 1-3%
        if 0.01 <= enthusiasm_ratio <= 0.03:
            return 1.0
        elif 0.005 <= enthusiasm_ratio < 0.01 or 0.03 < enthusiasm_ratio <= 0.05:
            return 0.8
        else:
            return 0.6
