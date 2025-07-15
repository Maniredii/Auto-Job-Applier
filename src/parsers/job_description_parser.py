"""
Job Description Parser Module
Extracts requirements, skills, and keywords from job descriptions using NLP
"""

import re
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import spacy
from spacy.matcher import Matcher
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag

from .text_processor import TextProcessor
from src.ai.groq_client import GroqClient

logger = logging.getLogger(__name__)

@dataclass
class JobRequirements:
    """Data class for parsed job requirements"""
    required_skills: List[str]
    preferred_skills: List[str]
    experience_years: Dict[str, int]
    education_requirements: List[str]
    certifications: List[str]
    responsibilities: List[str]
    keywords: List[str]
    soft_skills: List[str]
    technologies: Dict[str, List[str]]
    salary_range: Optional[Tuple[int, int]]
    job_level: str
    remote_work: bool
    benefits: List[str]
    company_size: str
    industry: str

class JobDescriptionParser:
    """Parser for extracting structured information from job descriptions"""
    
    def __init__(self, use_ai: bool = True):
        """
        Initialize job description parser
        
        Args:
            use_ai: Whether to use AI for enhanced parsing
        """
        self.use_ai = use_ai
        self.text_processor = TextProcessor()
        
        # Initialize AI client if enabled
        if use_ai:
            try:
                self.ai_client = GroqClient()
            except Exception as e:
                logger.warning(f"Failed to initialize AI client: {str(e)}")
                self.ai_client = None
        else:
            self.ai_client = None
        
        # Initialize spaCy
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.matcher = Matcher(self.nlp.vocab)
            self._setup_patterns()
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            self.matcher = None
        
        # Initialize NLTK
        self._download_nltk_resources()
        
        # Pattern definitions
        self._setup_regex_patterns()
        
        # Skill categories
        self.skill_categories = self.text_processor.skill_database
    
    def _download_nltk_resources(self):
        """Download required NLTK resources"""
        resources = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                try:
                    nltk.download(resource, quiet=True)
                except Exception as e:
                    logger.debug(f"Failed to download NLTK resource {resource}: {str(e)}")
    
    def _setup_patterns(self):
        """Setup spaCy patterns for entity extraction"""
        if not self.matcher:
            return
        
        # Experience patterns
        experience_patterns = [
            [{"LOWER": {"IN": ["minimum", "min", "at", "least"]}}, 
             {"IS_DIGIT": True}, 
             {"LOWER": {"IN": ["years", "yrs", "year"]}}],
            [{"IS_DIGIT": True}, 
             {"LOWER": "+"}, 
             {"LOWER": {"IN": ["years", "yrs", "year"]}}],
            [{"IS_DIGIT": True}, 
             {"LOWER": {"IN": ["years", "yrs", "year"]}}, 
             {"LOWER": "of"}, 
             {"LOWER": "experience"}]
        ]
        
        self.matcher.add("EXPERIENCE", experience_patterns)
        
        # Education patterns
        education_patterns = [
            [{"LOWER": {"IN": ["bachelor", "bachelor's", "bs", "ba"]}}, 
             {"LOWER": {"IN": ["degree", "in"]}, "OP": "?"}],
            [{"LOWER": {"IN": ["master", "master's", "ms", "ma", "mba"]}}, 
             {"LOWER": {"IN": ["degree", "in"]}, "OP": "?"}],
            [{"LOWER": {"IN": ["phd", "ph.d", "doctorate", "doctoral"]}}]
        ]
        
        self.matcher.add("EDUCATION", education_patterns)
    
    def _setup_regex_patterns(self):
        """Setup regex patterns for various extractions"""
        self.patterns = {
            'salary': [
                r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'\$(\d{1,3}(?:,\d{3})*(?:k|K))\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:k|K))',
                r'(\d{1,3}(?:,\d{3})*(?:k|K))\s*-\s*(\d{1,3}(?:,\d{3})*(?:k|K))',
            ],
            'experience_years': [
                r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
                r'minimum\s+of\s+(\d+)\s+(?:years?|yrs?)',
                r'at\s+least\s+(\d+)\s+(?:years?|yrs?)',
                r'(\d+)\+\s*(?:years?|yrs?)',
            ],
            'remote_work': [
                r'\b(?:remote|work\s+from\s+home|wfh|telecommute|distributed)\b',
                r'\b(?:hybrid|flexible\s+work)\b',
                r'\b(?:on-site|onsite|office\s+based)\b',
            ],
            'job_level': [
                r'\b(?:senior|sr\.?|lead|principal|staff)\b',
                r'\b(?:junior|jr\.?|entry\s+level|associate)\b',
                r'\b(?:mid\s+level|intermediate)\b',
                r'\b(?:director|manager|head\s+of)\b',
            ],
            'company_size': [
                r'(?:startup|small\s+company|<\s*50\s+employees)',
                r'(?:medium\s+company|50-500\s+employees)',
                r'(?:large\s+company|enterprise|500\+\s+employees)',
                r'(?:fortune\s+500|multinational)',
            ]
        }
    
    def parse_job_description(self, job_description: str, job_title: str = "") -> JobRequirements:
        """
        Parse job description and extract structured requirements
        
        Args:
            job_description: Job description text
            job_title: Job title for context
            
        Returns:
            JobRequirements object with extracted information
        """
        logger.info("Parsing job description...")
        
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(job_description)
        
        # Extract basic information using regex and NLP
        basic_requirements = self._extract_basic_requirements(cleaned_text)
        
        # Extract skills and technologies
        skills_data = self._extract_skills_and_technologies(cleaned_text)
        
        # Extract experience and education
        experience_data = self._extract_experience_education(cleaned_text)
        
        # Extract job metadata
        metadata = self._extract_job_metadata(cleaned_text, job_title)
        
        # Use AI for enhanced extraction if available
        if self.ai_client:
            ai_requirements = self._extract_with_ai(job_description, job_title)
            # Merge AI results with rule-based results
            merged_requirements = self._merge_requirements(
                basic_requirements, skills_data, experience_data, metadata, ai_requirements
            )
        else:
            merged_requirements = self._merge_requirements(
                basic_requirements, skills_data, experience_data, metadata
            )
        
        logger.info("Job description parsing completed")
        return merged_requirements
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess job description text
        
        Args:
            text: Raw job description
            
        Returns:
            Cleaned text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,;:()\-+/]', ' ', text)
        
        return text.strip()
    
    def _extract_basic_requirements(self, text: str) -> Dict:
        """Extract basic requirements using regex patterns"""
        requirements = {
            'responsibilities': self._extract_responsibilities(text),
            'benefits': self._extract_benefits(text),
            'keywords': self._extract_keywords(text)
        }
        
        return requirements
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibility_indicators = [
            'responsibilities', 'duties', 'role', 'you will', 'the candidate will',
            'key responsibilities', 'main duties', 'primary responsibilities'
        ]
        
        responsibilities = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains responsibility indicators
            if any(indicator in sentence_lower for indicator in responsibility_indicators):
                # Extract bullet points or numbered lists
                if re.search(r'[•·▪▫◦‣⁃]|\d+\.|\-\s', sentence):
                    responsibilities.append(sentence.strip())
                continue
            
            # Look for action verbs that indicate responsibilities
            action_verbs = [
                'develop', 'design', 'implement', 'maintain', 'create', 'build',
                'manage', 'lead', 'coordinate', 'collaborate', 'work with',
                'analyze', 'optimize', 'improve', 'ensure', 'support'
            ]
            
            if any(verb in sentence_lower for verb in action_verbs) and len(sentence) > 20:
                responsibilities.append(sentence.strip())
        
        return responsibilities[:10]  # Limit to top 10
    
    def _extract_benefits(self, text: str) -> List[str]:
        """Extract job benefits"""
        benefit_keywords = [
            'health insurance', 'dental', 'vision', '401k', 'retirement',
            'vacation', 'pto', 'paid time off', 'flexible hours', 'remote work',
            'stock options', 'equity', 'bonus', 'gym membership', 'learning budget',
            'conference', 'training', 'professional development'
        ]
        
        benefits = []
        text_lower = text.lower()
        
        for benefit in benefit_keywords:
            if benefit in text_lower:
                benefits.append(benefit.title())
        
        return list(set(benefits))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords using TF-IDF-like approach"""
        # Get stop words
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            stop_words = set()
        
        # Add job-specific stop words
        stop_words.update([
            'experience', 'knowledge', 'skills', 'ability', 'strong', 'excellent',
            'good', 'required', 'preferred', 'must', 'should', 'candidate',
            'position', 'role', 'job', 'work', 'team', 'company', 'years'
        ])
        
        # Tokenize and filter
        words = word_tokenize(text.lower())
        filtered_words = [
            word for word in words 
            if word.isalpha() and len(word) > 2 and word not in stop_words
        ]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        # Return top keywords
        return [word for word, count in word_freq.most_common(20)]
    
    def _extract_skills_and_technologies(self, text: str) -> Dict:
        """Extract skills and technologies"""
        # Use text processor for categorized skill extraction
        categorized_skills = self.text_processor.extract_skills_advanced(text)
        
        # Extract soft skills
        soft_skills = self.text_processor.extract_soft_skills(text)
        
        # Separate required vs preferred skills
        required_skills, preferred_skills = self._categorize_skills(text, categorized_skills)
        
        return {
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'soft_skills': soft_skills,
            'technologies': categorized_skills
        }
    
    def _categorize_skills(self, text: str, skills_dict: Dict) -> Tuple[List[str], List[str]]:
        """Categorize skills as required vs preferred"""
        all_skills = []
        for skill_list in skills_dict.values():
            all_skills.extend(skill_list)
        
        required_skills = []
        preferred_skills = []
        
        text_lower = text.lower()
        
        # Look for context around each skill
        for skill in all_skills:
            skill_lower = skill.lower()
            
            # Find skill mentions in text
            skill_pattern = r'\b' + re.escape(skill_lower) + r'\b'
            matches = list(re.finditer(skill_pattern, text_lower))
            
            is_required = False
            for match in matches:
                # Get context around the skill (50 characters before and after)
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                context = text_lower[start:end]
                
                # Check for required indicators
                required_indicators = [
                    'required', 'must have', 'essential', 'mandatory', 'necessary',
                    'minimum', 'at least', 'strong', 'proficient', 'expert'
                ]
                
                if any(indicator in context for indicator in required_indicators):
                    is_required = True
                    break
            
            if is_required:
                required_skills.append(skill)
            else:
                # Check for preferred indicators
                preferred_indicators = [
                    'preferred', 'nice to have', 'bonus', 'plus', 'advantage',
                    'desirable', 'beneficial', 'helpful'
                ]
                
                is_preferred = False
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(text_lower), match.end() + 50)
                    context = text_lower[start:end]
                    
                    if any(indicator in context for indicator in preferred_indicators):
                        is_preferred = True
                        break
                
                if is_preferred:
                    preferred_skills.append(skill)
                else:
                    # Default to required if no clear indication
                    required_skills.append(skill)
        
        return list(set(required_skills)), list(set(preferred_skills))
    
    def _extract_experience_education(self, text: str) -> Dict:
        """Extract experience and education requirements"""
        # Extract years of experience
        experience_years = {}
        for pattern in self.patterns['experience_years']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                years = int(match.group(1))
                # Try to find what the experience is for
                context_start = max(0, match.start() - 100)
                context_end = min(len(text), match.end() + 100)
                context = text[context_start:context_end].lower()
                
                # Look for technology/skill names in context
                for category, skills in self.skill_categories.items():
                    for skill in skills:
                        if skill.lower() in context:
                            experience_years[skill.title()] = years
                            break
                
                # General experience if no specific skill found
                if not experience_years:
                    experience_years['General'] = years
        
        # Extract education requirements
        education_requirements = []
        education_patterns = [
            r"bachelor'?s?\s+(?:degree\s+)?(?:in\s+)?([a-zA-Z\s]+)",
            r"master'?s?\s+(?:degree\s+)?(?:in\s+)?([a-zA-Z\s]+)",
            r"phd\s+(?:in\s+)?([a-zA-Z\s]+)",
            r"(?:bs|ba|ms|ma|mba)\s+(?:in\s+)?([a-zA-Z\s]+)"
        ]
        
        for pattern in education_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education_requirements.append(match.group().strip())
        
        # Extract certifications
        certifications = self.text_processor.extract_certifications(text)
        
        return {
            'experience_years': experience_years,
            'education_requirements': education_requirements,
            'certifications': certifications
        }
    
    def _extract_job_metadata(self, text: str, job_title: str) -> Dict:
        """Extract job metadata like level, remote work, salary"""
        metadata = {}
        
        # Extract salary range
        salary_range = None
        for pattern in self.patterns['salary']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    min_sal = self._parse_salary(match.group(1))
                    max_sal = self._parse_salary(match.group(2))
                    salary_range = (min_sal, max_sal)
                    break
                except (ValueError, IndexError):
                    continue
        
        # Extract job level
        job_level = "Mid-Level"  # Default
        for pattern in self.patterns['job_level']:
            if re.search(pattern, text + " " + job_title, re.IGNORECASE):
                if 'senior' in pattern or 'lead' in pattern:
                    job_level = "Senior"
                elif 'junior' in pattern or 'entry' in pattern:
                    job_level = "Entry"
                elif 'director' in pattern or 'manager' in pattern:
                    job_level = "Management"
                break
        
        # Extract remote work info
        remote_work = False
        for pattern in self.patterns['remote_work']:
            if re.search(pattern, text, re.IGNORECASE):
                if 'remote' in pattern or 'wfh' in pattern:
                    remote_work = True
                break
        
        # Extract company size
        company_size = "Unknown"
        for pattern in self.patterns['company_size']:
            if re.search(pattern, text, re.IGNORECASE):
                if 'startup' in pattern or 'small' in pattern:
                    company_size = "Small"
                elif 'medium' in pattern:
                    company_size = "Medium"
                elif 'large' in pattern or 'enterprise' in pattern:
                    company_size = "Large"
                break
        
        metadata.update({
            'salary_range': salary_range,
            'job_level': job_level,
            'remote_work': remote_work,
            'company_size': company_size,
            'industry': self._extract_industry(text)
        })
        
        return metadata
    
    def _parse_salary(self, salary_str: str) -> int:
        """Parse salary string to integer"""
        # Remove $ and commas
        salary_str = salary_str.replace('$', '').replace(',', '')
        
        # Handle K notation
        if salary_str.lower().endswith('k'):
            return int(float(salary_str[:-1]) * 1000)
        
        return int(float(salary_str))
    
    def _extract_industry(self, text: str) -> str:
        """Extract industry from job description"""
        industries = {
            'Technology': ['software', 'tech', 'saas', 'ai', 'machine learning', 'data science'],
            'Finance': ['finance', 'banking', 'fintech', 'investment', 'trading'],
            'Healthcare': ['healthcare', 'medical', 'pharma', 'biotech', 'hospital'],
            'E-commerce': ['e-commerce', 'retail', 'marketplace', 'shopping'],
            'Gaming': ['gaming', 'game', 'entertainment', 'mobile games'],
            'Education': ['education', 'edtech', 'learning', 'university', 'school']
        }
        
        text_lower = text.lower()
        for industry, keywords in industries.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        return "Other"

    def _extract_with_ai(self, job_description: str, job_title: str) -> Dict:
        """
        Use AI to extract job requirements with enhanced accuracy

        Args:
            job_description: Job description text
            job_title: Job title for context

        Returns:
            Dictionary with AI-extracted requirements
        """
        if not self.ai_client:
            return {}

        try:
            # Use Groq AI to extract structured requirements
            ai_requirements = self.ai_client.extract_job_requirements(job_description)

            # Enhance with additional AI analysis
            enhanced_requirements = self._enhance_ai_extraction(
                job_description, job_title, ai_requirements
            )

            return enhanced_requirements

        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            return {}

    def _enhance_ai_extraction(
        self,
        job_description: str,
        job_title: str,
        base_requirements: Dict
    ) -> Dict:
        """
        Enhance AI extraction with additional analysis

        Args:
            job_description: Job description text
            job_title: Job title
            base_requirements: Base requirements from AI

        Returns:
            Enhanced requirements dictionary
        """
        enhanced = base_requirements.copy()

        # Additional AI prompts for specific extractions
        try:
            # Extract job level and seniority
            level_prompt = f"""
            Analyze this job posting and determine the seniority level:

            Job Title: {job_title}
            Job Description: {job_description[:1000]}...

            Return only one of: Entry, Mid-Level, Senior, Lead, Principal, Director, VP, C-Level
            """

            job_level = self.ai_client.generate_completion(
                level_prompt,
                system_message="You are an expert at analyzing job postings for seniority levels."
            )

            enhanced['job_level'] = job_level.strip()

            # Extract company culture and values
            culture_prompt = f"""
            Extract company culture, values, and work environment details from this job posting:

            {job_description}

            Return a JSON object with:
            - "culture": list of culture keywords
            - "values": list of company values
            - "work_environment": description of work environment
            """

            culture_response = self.ai_client.generate_completion(
                culture_prompt,
                system_message="Extract company culture information from job postings."
            )

            try:
                import json
                culture_data = json.loads(culture_response)
                enhanced.update(culture_data)
            except json.JSONDecodeError:
                logger.debug("Failed to parse culture data from AI")

        except Exception as e:
            logger.debug(f"Enhanced AI extraction failed: {str(e)}")

        return enhanced

    def _merge_requirements(self, *requirement_dicts) -> JobRequirements:
        """
        Merge multiple requirement dictionaries into JobRequirements object

        Args:
            *requirement_dicts: Variable number of requirement dictionaries

        Returns:
            Merged JobRequirements object
        """
        merged = {
            'required_skills': [],
            'preferred_skills': [],
            'experience_years': {},
            'education_requirements': [],
            'certifications': [],
            'responsibilities': [],
            'keywords': [],
            'soft_skills': [],
            'technologies': {},
            'salary_range': None,
            'job_level': 'Mid-Level',
            'remote_work': False,
            'benefits': [],
            'company_size': 'Unknown',
            'industry': 'Other'
        }

        # Merge all dictionaries
        for req_dict in requirement_dicts:
            if not req_dict:
                continue

            for key, value in req_dict.items():
                if key in merged:
                    if isinstance(merged[key], list) and isinstance(value, list):
                        merged[key].extend(value)
                    elif isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key].update(value)
                    elif value is not None:
                        merged[key] = value

        # Remove duplicates from lists
        for key, value in merged.items():
            if isinstance(value, list):
                merged[key] = list(set(value))

        # Create JobRequirements object
        return JobRequirements(**merged)

    def analyze_job_match(
        self,
        job_requirements: JobRequirements,
        candidate_skills: List[str]
    ) -> Dict[str, float]:
        """
        Analyze how well a candidate matches job requirements

        Args:
            job_requirements: Parsed job requirements
            candidate_skills: List of candidate skills

        Returns:
            Dictionary with match scores and analysis
        """
        # Calculate skill match scores
        required_match = self.text_processor.calculate_skill_relevance(
            candidate_skills, job_requirements.required_skills
        )

        preferred_match = self.text_processor.calculate_skill_relevance(
            candidate_skills, job_requirements.preferred_skills
        )

        # Calculate technology category matches
        tech_matches = {}
        for category, skills in job_requirements.technologies.items():
            if skills:
                tech_matches[category] = self.text_processor.calculate_skill_relevance(
                    candidate_skills, skills
                )

        # Overall match score (weighted)
        overall_score = (required_match * 0.7) + (preferred_match * 0.3)

        # Find missing skills
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        missing_required = [
            skill for skill in job_requirements.required_skills
            if skill.lower() not in candidate_skills_lower
        ]

        missing_preferred = [
            skill for skill in job_requirements.preferred_skills
            if skill.lower() not in candidate_skills_lower
        ]

        return {
            'overall_score': overall_score,
            'required_skills_match': required_match,
            'preferred_skills_match': preferred_match,
            'technology_matches': tech_matches,
            'missing_required_skills': missing_required,
            'missing_preferred_skills': missing_preferred,
            'recommendation': self._generate_match_recommendation(overall_score)
        }

    def _generate_match_recommendation(self, score: float) -> str:
        """Generate recommendation based on match score"""
        if score >= 0.8:
            return "Excellent match - Highly recommended to apply"
        elif score >= 0.6:
            return "Good match - Recommended to apply"
        elif score >= 0.4:
            return "Moderate match - Consider applying with skill development"
        else:
            return "Low match - Focus on skill development before applying"

    def extract_application_instructions(self, job_description: str) -> Dict[str, str]:
        """
        Extract application instructions and requirements

        Args:
            job_description: Job description text

        Returns:
            Dictionary with application instructions
        """
        instructions = {
            'application_method': 'Unknown',
            'required_documents': [],
            'application_deadline': '',
            'contact_info': '',
            'special_instructions': ''
        }

        text_lower = job_description.lower()

        # Extract application method
        if 'apply online' in text_lower or 'click apply' in text_lower:
            instructions['application_method'] = 'Online Application'
        elif 'email' in text_lower and '@' in job_description:
            instructions['application_method'] = 'Email'
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, job_description)
            if emails:
                instructions['contact_info'] = emails[0]

        # Extract required documents
        doc_keywords = [
            'resume', 'cv', 'cover letter', 'portfolio', 'references',
            'transcript', 'writing sample', 'code sample'
        ]

        for keyword in doc_keywords:
            if keyword in text_lower:
                instructions['required_documents'].append(keyword.title())

        # Extract deadline
        deadline_patterns = [
            r'deadline[:\s]+([^.]+)',
            r'apply by[:\s]+([^.]+)',
            r'closing date[:\s]+([^.]+)'
        ]

        for pattern in deadline_patterns:
            match = re.search(pattern, text_lower)
            if match:
                instructions['application_deadline'] = match.group(1).strip()
                break

        return instructions
