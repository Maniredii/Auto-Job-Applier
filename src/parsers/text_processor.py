"""
Text Processing Utilities for Resume Parsing
Advanced text processing and information extraction
"""

import re
import logging
from typing import List, Dict, Set, Optional
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag

logger = logging.getLogger(__name__)

class TextProcessor:
    """Advanced text processing for resume parsing"""
    
    def __init__(self):
        """Initialize text processor with NLTK resources"""
        self._download_nltk_resources()
        
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            self.stop_words = set()
            logger.warning("NLTK stopwords not available")
        
        # Extended skill database
        self.skill_database = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 
                'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
                'powershell', 'vba', 'assembly', 'cobol', 'fortran', 'haskell', 'erlang'
            ],
            'web_technologies': [
                'html', 'css', 'sass', 'less', 'react', 'angular', 'vue', 'svelte', 'jquery',
                'bootstrap', 'tailwind', 'node.js', 'express', 'next.js', 'nuxt.js', 'gatsby',
                'webpack', 'vite', 'parcel', 'babel'
            ],
            'frameworks': [
                'django', 'flask', 'fastapi', 'spring', 'spring boot', 'laravel', 'symfony',
                'rails', 'asp.net', 'blazor', 'xamarin', 'flutter', 'react native', 'ionic',
                'cordova', 'electron'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite',
                'mariadb', 'cassandra', 'dynamodb', 'neo4j', 'influxdb', 'couchdb', 'firebase'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'linode',
                'vultr', 'cloudflare', 'vercel', 'netlify', 'railway'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions', 'circleci',
                'travis ci', 'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'helm'
            ],
            'data_science': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv',
                'matplotlib', 'seaborn', 'plotly', 'jupyter', 'anaconda', 'spark', 'hadoop',
                'tableau', 'power bi', 'qlik'
            ],
            'testing': [
                'pytest', 'unittest', 'jest', 'mocha', 'chai', 'selenium', 'cypress', 'playwright',
                'postman', 'insomnia', 'jmeter', 'loadrunner'
            ],
            'version_control': [
                'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial'
            ],
            'operating_systems': [
                'linux', 'unix', 'windows', 'macos', 'ubuntu', 'centos', 'debian', 'redhat',
                'fedora', 'arch', 'alpine'
            ]
        }
        
        # Flatten skill database for easy searching
        self.all_skills = set()
        for category, skills in self.skill_database.items():
            self.all_skills.update(skills)
    
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
                    logger.warning(f"Failed to download NLTK resource {resource}: {str(e)}")
    
    def extract_skills_advanced(self, text: str) -> Dict[str, List[str]]:
        """
        Advanced skill extraction with categorization
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with categorized skills
        """
        text_lower = text.lower()
        found_skills = {category: [] for category in self.skill_database.keys()}
        
        # Extract skills by category
        for category, skills in self.skill_database.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill.title())
        
        # Remove empty categories
        return {k: v for k, v in found_skills.items() if v}
    
    def extract_years_of_experience(self, text: str) -> Dict[str, int]:
        """
        Extract years of experience for different technologies
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary mapping skills to years of experience
        """
        experience_map = {}
        
        # Patterns for experience extraction
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience\s+)?(?:with\s+|in\s+|using\s+)?([a-zA-Z\s.+#-]+)',
            r'([a-zA-Z\s.+#-]+)[\s:,-]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+([a-zA-Z\s.+#-]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if pattern.startswith(r'(\d+)'):
                        years = int(match.group(1))
                        skill = match.group(2).strip().lower()
                    else:
                        skill = match.group(1).strip().lower()
                        years = int(match.group(2))
                    
                    # Check if skill is in our database
                    if skill in self.all_skills:
                        experience_map[skill.title()] = years
                
                except (ValueError, IndexError):
                    continue
        
        return experience_map
    
    def extract_certifications(self, text: str) -> List[str]:
        """
        Extract certifications from resume text
        
        Args:
            text: Resume text
            
        Returns:
            List of certifications
        """
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'AWS\s+Certified\s+[\w\s]+',
            r'Microsoft\s+Certified\s+[\w\s]+',
            r'Google\s+Cloud\s+[\w\s]+',
            r'Cisco\s+Certified\s+[\w\s]+',
            r'CompTIA\s+[\w\s]+',
            r'Oracle\s+Certified\s+[\w\s]+',
            r'Salesforce\s+Certified\s+[\w\s]+',
            r'PMP\b',
            r'CISSP\b',
            r'CISA\b',
            r'CISM\b',
            r'CEH\b',
            r'OSCP\b',
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                cert = match.group().strip()
                if cert not in certifications:
                    certifications.append(cert)
        
        return certifications
    
    def extract_education_details(self, education_text: str) -> List[Dict[str, str]]:
        """
        Extract detailed education information
        
        Args:
            education_text: Education section text
            
        Returns:
            List of education details
        """
        education_list = []
        
        # Degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|Doctorate|Associate|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|MBA|Ph\.?D\.?)\s+(?:of\s+|in\s+)?([^,\n]+)',
            r'(B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?)\s+(?:in\s+)?([^,\n]+)',
        ]
        
        lines = education_text.split('\n')
        current_education = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_education:
                    education_list.append(current_education)
                    current_education = {}
                continue
            
            # Extract degree
            for pattern in degree_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    current_education['degree'] = match.group(1)
                    current_education['field'] = match.group(2).strip()
                    break
            
            # Extract year
            year_match = re.search(r'(19|20)\d{2}', line)
            if year_match:
                current_education['year'] = year_match.group()
            
            # Extract GPA
            gpa_match = re.search(r'GPA:?\s*(\d+\.?\d*)', line, re.IGNORECASE)
            if gpa_match:
                current_education['gpa'] = gpa_match.group(1)
            
            # If no specific pattern matched, treat as institution
            if 'institution' not in current_education and len(line) > 5:
                current_education['institution'] = line
        
        if current_education:
            education_list.append(current_education)
        
        return education_list
    
    def extract_contact_info_advanced(self, text: str) -> Dict[str, str]:
        """
        Advanced contact information extraction
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with contact information
        """
        contact_info = {}
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                if isinstance(phones[0], tuple):
                    contact_info['phone'] = ''.join(phones[0])
                else:
                    contact_info['phone'] = phones[0]
                break
        
        # LinkedIn profile
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contact_info['linkedin'] = linkedin_matches[0]
        
        # GitHub profile
        github_pattern = r'github\.com/[\w-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            contact_info['github'] = github_matches[0]
        
        # Location
        location_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+\s+[A-Z][a-z]+,\s*[A-Z]{2})',  # City Name, State
        ]
        
        for pattern in location_patterns:
            locations = re.findall(pattern, text)
            if locations:
                contact_info['location'] = locations[0]
                break
        
        return contact_info
    
    def calculate_skill_relevance(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """
        Calculate skill relevance score between resume and job requirements
        
        Args:
            resume_skills: Skills found in resume
            job_skills: Skills required for job
            
        Returns:
            Relevance score (0-1)
        """
        if not job_skills:
            return 0.0
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matching_skills = set(resume_skills_lower) & set(job_skills_lower)
        
        return len(matching_skills) / len(job_skills_lower)
    
    def extract_soft_skills(self, text: str) -> List[str]:
        """
        Extract soft skills from resume text
        
        Args:
            text: Resume text
            
        Returns:
            List of soft skills
        """
        soft_skills_keywords = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'creative', 'innovative', 'adaptable', 'flexible', 'organized', 'detail-oriented',
            'time management', 'project management', 'collaboration', 'interpersonal',
            'presentation', 'negotiation', 'customer service', 'mentoring', 'coaching'
        ]
        
        found_soft_skills = []
        text_lower = text.lower()
        
        for skill in soft_skills_keywords:
            if skill in text_lower:
                found_soft_skills.append(skill.title())
        
        return found_soft_skills
