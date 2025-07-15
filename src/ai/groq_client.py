"""
Groq API client for AI-powered resume and cover letter generation
"""

import logging
from typing import Dict, List, Optional, Any
from groq import Groq

from config import config

logger = logging.getLogger(__name__)

class GroqClient:
    """Client for interacting with Groq API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (uses config if not provided)
        """
        self.api_key = api_key or config.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.client = Groq(api_key=self.api_key)
        self.model = config.GROQ_MODEL
        self.max_tokens = config.MAX_TOKENS
        self.temperature = config.TEMPERATURE
    
    def generate_completion(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate completion using Groq API
        
        Args:
            prompt: User prompt
            system_message: System message for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text completion
        """
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise
    
    def modify_resume(self, resume_text: str, job_description: str) -> str:
        """
        Modify resume to match job description
        
        Args:
            resume_text: Original resume content
            job_description: Target job description
        
        Returns:
            Modified resume text
        """
        system_message = """You are an expert resume writer and career coach. Your task is to modify resumes to better match job descriptions while maintaining truthfulness and the candidate's core qualifications."""
        
        prompt = f"""
        Please modify the following resume to better align with the job description. Focus on:
        1. Adjusting the professional summary to highlight relevant skills
        2. Reordering and emphasizing relevant experience
        3. Adding relevant keywords naturally
        4. Maintaining all factual information
        5. Keeping the same format and structure
        
        ORIGINAL RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Please provide the modified resume:
        """
        
        return self.generate_completion(prompt, system_message)
    
    def generate_cover_letter(
        self, 
        resume_text: str, 
        job_description: str, 
        company_name: str,
        job_title: str,
        candidate_name: str = "Candidate"
    ) -> str:
        """
        Generate personalized cover letter
        
        Args:
            resume_text: Candidate's resume
            job_description: Job description
            company_name: Target company name
            job_title: Target job title
            candidate_name: Candidate's name
        
        Returns:
            Generated cover letter
        """
        system_message = """You are an expert cover letter writer. Create compelling, personalized cover letters that highlight the candidate's relevant experience and enthusiasm for the role."""
        
        prompt = f"""
        Write a professional cover letter for the following job application:
        
        CANDIDATE NAME: {candidate_name}
        COMPANY: {company_name}
        JOB TITLE: {job_title}
        
        CANDIDATE'S RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Requirements:
        1. Professional tone and format
        2. Highlight relevant experience from the resume
        3. Show enthusiasm for the company and role
        4. Keep it concise (3-4 paragraphs)
        5. Include specific examples when possible
        6. End with a strong call to action
        
        Please write the cover letter:
        """
        
        return self.generate_completion(prompt, system_message)
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """
        Extract key requirements from job description
        
        Args:
            job_description: Job description text
        
        Returns:
            Dictionary with categorized requirements
        """
        system_message = """You are an expert at analyzing job descriptions. Extract and categorize key requirements accurately."""
        
        prompt = f"""
        Analyze the following job description and extract key requirements in JSON format:
        
        JOB DESCRIPTION:
        {job_description}
        
        Please extract and return a JSON object with these categories:
        - "required_skills": List of required technical skills
        - "preferred_skills": List of preferred/nice-to-have skills
        - "experience_level": Required years of experience
        - "education": Education requirements
        - "responsibilities": Key job responsibilities
        - "keywords": Important keywords for ATS systems
        
        Return only valid JSON:
        """
        
        try:
            response = self.generate_completion(prompt, system_message)
            # Parse JSON response
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error extracting job requirements: {str(e)}")
            return {
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "",
                "education": "",
                "responsibilities": [],
                "keywords": []
            }
