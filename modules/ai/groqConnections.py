# Author: Enhanced by AI Assistant
# Groq API Integration Module
# High-performance AI inference with Groq's lightning-fast LLM API

import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from modules.helpers import print_lg

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print_lg("⚠️ Groq package not installed. Install with: pip install groq")

@dataclass
class GroqConfig:
    """Configuration for Groq API."""
    api_key: str
    model: str = "mixtral-8x7b-32768"  # Default high-performance model
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False

class GroqAIClient:
    """
    Enhanced Groq AI client for job application optimization.
    Provides lightning-fast AI inference for resume optimization, 
    cover letter generation, and job matching.
    """
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        if not GROQ_AVAILABLE:
            raise ImportError("Groq package not installed. Install with: pip install groq")
        
        self.api_key = api_key
        self.model = model
        self.client = None
        self.config = GroqConfig(api_key=api_key, model=model)
        
        # Available Groq models with their capabilities
        self.available_models = {
            "mixtral-8x7b-32768": {
                "name": "Mixtral 8x7B",
                "context_length": 32768,
                "best_for": ["reasoning", "code", "analysis"],
                "speed": "ultra-fast"
            },
            "llama2-70b-4096": {
                "name": "Llama 2 70B",
                "context_length": 4096,
                "best_for": ["general", "conversation"],
                "speed": "fast"
            },
            "gemma-7b-it": {
                "name": "Gemma 7B",
                "context_length": 8192,
                "best_for": ["instruction", "tasks"],
                "speed": "very-fast"
            }
        }
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Groq client."""
        try:
            self.client = Groq(api_key=self.api_key)
            print_lg(f"🚀 Groq AI client initialized with model: {self.model}")
            
            # Test the connection
            self._test_connection()
            
        except Exception as e:
            print_lg(f"❌ Failed to initialize Groq client: {e}")
            raise
    
    def _test_connection(self):
        """Test the Groq API connection."""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.model,
                max_tokens=10
            )
            print_lg("✅ Groq API connection successful")
            
        except Exception as e:
            print_lg(f"❌ Groq API connection test failed: {e}")
            raise
    
    def generate_cover_letter(self, job_description: str, user_profile: Dict, 
                            company_info: Dict = None) -> str:
        """
        Generate a personalized cover letter using Groq AI.
        Ultra-fast generation with high quality.
        """
        print_lg("📝 Generating cover letter with Groq AI...")
        
        # Enhanced prompt for better cover letter generation
        prompt = f"""
        Create a compelling, personalized cover letter for the following job application.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE PROFILE:
        - Name: {user_profile.get('name', 'Candidate')}
        - Experience: {user_profile.get('experience_years', 'N/A')} years
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Education: {user_profile.get('education', 'N/A')}
        - Career Goals: {', '.join(user_profile.get('career_goals', []))}
        
        COMPANY INFO:
        {json.dumps(company_info, indent=2) if company_info else 'Not provided'}
        
        REQUIREMENTS:
        1. Write a professional, engaging cover letter
        2. Highlight relevant skills and experience
        3. Show enthusiasm for the role and company
        4. Keep it concise (3-4 paragraphs)
        5. Use a confident, professional tone
        6. Include specific examples when possible
        7. End with a strong call to action
        
        Generate only the cover letter content, no additional text.
        """
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert career coach and professional writer specializing in creating compelling cover letters that get results."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p
            )
            
            generation_time = time.time() - start_time
            cover_letter = response.choices[0].message.content.strip()
            
            print_lg(f"✅ Cover letter generated in {generation_time:.2f} seconds")
            return cover_letter
            
        except Exception as e:
            print_lg(f"❌ Error generating cover letter: {e}")
            return self._fallback_cover_letter(job_description, user_profile)
    
    def optimize_resume_content(self, resume_sections: Dict, job_description: str) -> Dict:
        """
        Optimize resume content for specific job using Groq AI.
        """
        print_lg("🎯 Optimizing resume content with Groq AI...")
        
        prompt = f"""
        Optimize the following resume sections for this specific job posting.
        
        JOB DESCRIPTION:
        {job_description}
        
        CURRENT RESUME SECTIONS:
        {json.dumps(resume_sections, indent=2)}
        
        OPTIMIZATION REQUIREMENTS:
        1. Enhance the professional summary to match job requirements
        2. Reorder and emphasize relevant skills
        3. Optimize work experience descriptions with relevant keywords
        4. Suggest improvements for better ATS compatibility
        5. Maintain truthfulness - only enhance, don't fabricate
        6. Use action verbs and quantifiable achievements
        7. Ensure keyword optimization for the specific role
        
        Return the optimized resume sections in the same JSON format.
        Focus on making the resume highly relevant to the job posting.
        """
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert resume writer and ATS optimization specialist with deep knowledge of hiring practices across industries."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=self.config.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent optimization
                top_p=self.config.top_p
            )
            
            generation_time = time.time() - start_time
            
            # Parse the optimized resume sections
            optimized_content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, fallback to original if parsing fails
            try:
                optimized_sections = json.loads(optimized_content)
                print_lg(f"✅ Resume optimized in {generation_time:.2f} seconds")
                return optimized_sections
            except json.JSONDecodeError:
                print_lg("⚠️ Could not parse optimized resume, using original")
                return resume_sections
                
        except Exception as e:
            print_lg(f"❌ Error optimizing resume: {e}")
            return resume_sections
    
    def analyze_job_match(self, job_description: str, user_profile: Dict) -> Dict:
        """
        Analyze job match compatibility using Groq AI.
        """
        print_lg("🔍 Analyzing job match with Groq AI...")
        
        prompt = f"""
        Analyze the compatibility between this job posting and candidate profile.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE PROFILE:
        {json.dumps(user_profile, indent=2)}
        
        ANALYSIS REQUIREMENTS:
        1. Calculate match percentage (0-100%)
        2. Identify matching skills and experience
        3. Highlight missing requirements
        4. Suggest improvements for better match
        5. Assess salary expectations compatibility
        6. Evaluate cultural fit indicators
        7. Provide application recommendation
        
        Return analysis in JSON format:
        {{
            "match_percentage": 85,
            "matching_skills": ["skill1", "skill2"],
            "missing_requirements": ["req1", "req2"],
            "experience_match": "good/fair/poor",
            "salary_compatibility": "high/medium/low",
            "cultural_fit": "excellent/good/fair/poor",
            "recommendation": "highly_recommended/recommended/consider/not_recommended",
            "improvement_suggestions": ["suggestion1", "suggestion2"],
            "key_selling_points": ["point1", "point2"]
        }}
        """
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert career counselor and job matching specialist with deep understanding of hiring requirements across industries."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=2048,
                temperature=0.2,  # Low temperature for consistent analysis
                top_p=0.8
            )
            
            generation_time = time.time() - start_time
            
            # Parse the analysis
            analysis_content = response.choices[0].message.content.strip()
            
            try:
                analysis = json.loads(analysis_content)
                print_lg(f"✅ Job match analyzed in {generation_time:.2f} seconds")
                return analysis
            except json.JSONDecodeError:
                print_lg("⚠️ Could not parse job analysis, using fallback")
                return self._fallback_job_analysis()
                
        except Exception as e:
            print_lg(f"❌ Error analyzing job match: {e}")
            return self._fallback_job_analysis()
    
    def generate_connection_message(self, target_profile: Dict, context: str = "job_search") -> str:
        """
        Generate personalized LinkedIn connection messages using Groq AI.
        """
        print_lg("🤝 Generating connection message with Groq AI...")
        
        prompt = f"""
        Create a personalized LinkedIn connection request message.
        
        TARGET PROFILE:
        - Name: {target_profile.get('name', 'Professional')}
        - Title: {target_profile.get('title', 'Unknown')}
        - Company: {target_profile.get('company', 'Unknown')}
        - Industry: {target_profile.get('industry', 'Unknown')}
        
        CONTEXT: {context}
        
        REQUIREMENTS:
        1. Keep it under 300 characters (LinkedIn limit)
        2. Be professional and genuine
        3. Mention specific reason for connecting
        4. Show value proposition
        5. Include a clear call to action
        6. Avoid being overly salesy
        7. Personalize based on their role/company
        
        Generate only the message content, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert networker and LinkedIn specialist who creates compelling connection messages that get accepted."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=200,
                temperature=0.7,
                top_p=0.9
            )
            
            message = response.choices[0].message.content.strip()
            
            # Ensure message is within LinkedIn's character limit
            if len(message) > 300:
                message = message[:297] + "..."
            
            print_lg("✅ Connection message generated")
            return message
            
        except Exception as e:
            print_lg(f"❌ Error generating connection message: {e}")
            return self._fallback_connection_message(target_profile)
    
    def _fallback_cover_letter(self, job_description: str, user_profile: Dict) -> str:
        """Fallback cover letter if AI generation fails."""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the position at your company. With {user_profile.get('experience_years', 'several')} years of experience and expertise in {', '.join(user_profile.get('skills', ['relevant technologies'])[:3])}, I am confident I would be a valuable addition to your team.

My background in {user_profile.get('education', 'my field')} and hands-on experience with {', '.join(user_profile.get('skills', ['key technologies'])[:2])} align well with the requirements outlined in your job posting. I am particularly excited about the opportunity to contribute to your organization's success.

I would welcome the opportunity to discuss how my skills and enthusiasm can benefit your team. Thank you for considering my application.

Best regards,
{user_profile.get('name', 'Candidate')}"""
    
    def _fallback_job_analysis(self) -> Dict:
        """Fallback job analysis if AI analysis fails."""
        return {
            "match_percentage": 70,
            "matching_skills": ["general skills"],
            "missing_requirements": ["to be determined"],
            "experience_match": "fair",
            "salary_compatibility": "medium",
            "cultural_fit": "good",
            "recommendation": "consider",
            "improvement_suggestions": ["Review job requirements carefully"],
            "key_selling_points": ["Relevant experience", "Strong skills"]
        }
    
    def _fallback_connection_message(self, target_profile: Dict) -> str:
        """Fallback connection message if AI generation fails."""
        name = target_profile.get('name', 'there').split()[0]
        company = target_profile.get('company', 'your company')
        
        return f"Hi {name}, I'm interested in learning more about opportunities at {company}. Would love to connect and hear about your experience there!"
    
    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        return self.available_models.get(self.model, {
            "name": self.model,
            "context_length": "unknown",
            "best_for": ["general"],
            "speed": "fast"
        })
    
    def switch_model(self, new_model: str):
        """Switch to a different Groq model."""
        if new_model in self.available_models:
            self.model = new_model
            self.config.model = new_model
            print_lg(f"🔄 Switched to model: {new_model}")
        else:
            print_lg(f"❌ Model {new_model} not available")
            print_lg(f"Available models: {list(self.available_models.keys())}")

def groq_create_client(api_key: str = None, model: str = "mixtral-8x7b-32768") -> Optional[GroqAIClient]:
    """
    Create and initialize a Groq AI client.
    """
    if not GROQ_AVAILABLE:
        print_lg("❌ Groq package not installed")
        return None
    
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        print_lg("❌ Groq API key not provided")
        return None
    
    try:
        client = GroqAIClient(api_key=api_key, model=model)
        return client
    except Exception as e:
        print_lg(f"❌ Failed to create Groq client: {e}")
        return None

def groq_close_client(client: GroqAIClient):
    """
    Close the Groq AI client.
    """
    if client:
        print_lg("🔒 Groq AI client closed")
        # Groq client doesn't need explicit closing
        pass
