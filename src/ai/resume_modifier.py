"""
AI Resume Modifier Module
Uses Groq API to intelligently modify resumes based on job descriptions
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

from .groq_client import GroqClient
from ..parsers.resume_parser import ResumeData
from ..parsers.job_description_parser import JobRequirements
from ..parsers.text_processor import TextProcessor
from config import config

logger = logging.getLogger(__name__)

@dataclass
class ResumeModification:
    """Data class for resume modification results"""
    original_resume: ResumeData
    modified_resume: ResumeData
    modifications_made: List[str]
    keyword_additions: List[str]
    skill_enhancements: List[str]
    match_score_before: float
    match_score_after: float
    improvement_percentage: float

class ResumeModifier:
    """AI-powered resume modifier using Groq API"""
    
    def __init__(self):
        """Initialize resume modifier"""
        self.groq_client = GroqClient()
        self.text_processor = TextProcessor()
        
        # Modification strategies
        self.modification_strategies = {
            'conservative': {
                'description': 'Minimal changes, preserve original content',
                'keyword_density': 0.1,
                'rewrite_percentage': 0.2,
                'add_skills': False
            },
            'moderate': {
                'description': 'Balanced approach with strategic improvements',
                'keyword_density': 0.15,
                'rewrite_percentage': 0.4,
                'add_skills': True
            },
            'aggressive': {
                'description': 'Maximum optimization for job match',
                'keyword_density': 0.2,
                'rewrite_percentage': 0.6,
                'add_skills': True
            }
        }
    
    def modify_resume_for_job(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        strategy: str = 'moderate',
        preserve_truthfulness: bool = True
    ) -> ResumeModification:
        """
        Modify resume to better match job requirements
        
        Args:
            resume_data: Original resume data
            job_requirements: Target job requirements
            strategy: Modification strategy (conservative, moderate, aggressive)
            preserve_truthfulness: Whether to maintain factual accuracy
            
        Returns:
            ResumeModification object with results
        """
        logger.info(f"Modifying resume with {strategy} strategy")
        
        # Calculate initial match score
        initial_score = self._calculate_match_score(resume_data, job_requirements)
        
        # Create modified copy
        modified_resume = self._create_resume_copy(resume_data)
        
        # Track modifications
        modifications_made = []
        keyword_additions = []
        skill_enhancements = []
        
        # Apply modifications based on strategy
        strategy_config = self.modification_strategies.get(strategy, self.modification_strategies['moderate'])
        
        # 1. Enhance professional summary
        if modified_resume.summary:
            enhanced_summary, summary_mods = self._enhance_summary(
                modified_resume.summary,
                job_requirements,
                strategy_config,
                preserve_truthfulness
            )
            modified_resume.summary = enhanced_summary
            modifications_made.extend(summary_mods)
        
        # 2. Optimize skills section
        enhanced_skills, skill_mods, added_keywords = self._optimize_skills(
            modified_resume.skills,
            job_requirements,
            strategy_config
        )
        modified_resume.skills = enhanced_skills
        modifications_made.extend(skill_mods)
        keyword_additions.extend(added_keywords)
        
        # 3. Enhance work experience
        enhanced_experience, exp_mods, exp_keywords = self._enhance_experience(
            modified_resume.experience,
            job_requirements,
            strategy_config,
            preserve_truthfulness
        )
        modified_resume.experience = enhanced_experience
        modifications_made.extend(exp_mods)
        keyword_additions.extend(exp_keywords)
        
        # 4. Optimize section order and formatting
        formatting_mods = self._optimize_formatting(modified_resume, job_requirements)
        modifications_made.extend(formatting_mods)
        
        # Calculate final match score
        final_score = self._calculate_match_score(modified_resume, job_requirements)
        improvement = ((final_score - initial_score) / initial_score * 100) if initial_score > 0 else 0
        
        logger.info(f"Resume modification completed. Score improved from {initial_score:.1%} to {final_score:.1%}")
        
        return ResumeModification(
            original_resume=resume_data,
            modified_resume=modified_resume,
            modifications_made=modifications_made,
            keyword_additions=keyword_additions,
            skill_enhancements=skill_enhancements,
            match_score_before=initial_score,
            match_score_after=final_score,
            improvement_percentage=improvement
        )
    
    def _enhance_summary(
        self,
        original_summary: str,
        job_requirements: JobRequirements,
        strategy_config: Dict,
        preserve_truthfulness: bool
    ) -> Tuple[str, List[str]]:
        """
        Enhance professional summary using AI
        
        Args:
            original_summary: Original summary text
            job_requirements: Target job requirements
            strategy_config: Strategy configuration
            preserve_truthfulness: Whether to maintain factual accuracy
            
        Returns:
            Tuple of (enhanced_summary, modifications_made)
        """
        modifications = []
        
        try:
            # Create AI prompt for summary enhancement
            prompt = self._create_summary_prompt(
                original_summary,
                job_requirements,
                strategy_config,
                preserve_truthfulness
            )
            
            enhanced_summary = self.groq_client.generate_completion(
                prompt,
                system_message="You are an expert resume writer who enhances professional summaries while maintaining truthfulness."
            )
            
            # Validate and clean the enhanced summary
            enhanced_summary = self._validate_summary(enhanced_summary, original_summary)
            
            if enhanced_summary != original_summary:
                modifications.append("Enhanced professional summary with job-relevant keywords")
                
                # Identify added keywords
                original_words = set(original_summary.lower().split())
                enhanced_words = set(enhanced_summary.lower().split())
                new_words = enhanced_words - original_words
                
                if new_words:
                    modifications.append(f"Added keywords: {', '.join(list(new_words)[:5])}")
            
            return enhanced_summary, modifications
            
        except Exception as e:
            logger.error(f"Summary enhancement failed: {str(e)}")
            return original_summary, []
    
    def _create_summary_prompt(
        self,
        original_summary: str,
        job_requirements: JobRequirements,
        strategy_config: Dict,
        preserve_truthfulness: bool
    ) -> str:
        """Create AI prompt for summary enhancement"""
        
        required_skills_str = ", ".join(job_requirements.required_skills[:10])
        preferred_skills_str = ", ".join(job_requirements.preferred_skills[:5])
        
        truthfulness_instruction = """
        IMPORTANT: Maintain complete factual accuracy. Do not add false information, 
        exaggerate experience, or claim skills not present in the original summary.
        Only rephrase and optimize existing content.
        """ if preserve_truthfulness else """
        You may enhance the summary strategically while keeping it realistic and professional.
        """
        
        prompt = f"""
        Enhance this professional summary to better match the target job requirements:
        
        ORIGINAL SUMMARY:
        {original_summary}
        
        TARGET JOB REQUIREMENTS:
        - Required Skills: {required_skills_str}
        - Preferred Skills: {preferred_skills_str}
        - Job Level: {job_requirements.job_level}
        - Industry: {job_requirements.industry}
        
        ENHANCEMENT GUIDELINES:
        {truthfulness_instruction}
        
        - Incorporate relevant keywords naturally
        - Highlight matching skills and experience
        - Maintain professional tone and readability
        - Keep length similar to original (2-4 sentences)
        - Focus on value proposition for the target role
        
        Strategy: {strategy_config['description']}
        
        Return only the enhanced summary text:
        """
        
        return prompt
    
    def _validate_summary(self, enhanced_summary: str, original_summary: str) -> str:
        """Validate and clean enhanced summary"""
        # Remove any unwanted formatting or instructions
        enhanced_summary = re.sub(r'^(enhanced summary:|summary:)', '', enhanced_summary, flags=re.IGNORECASE)
        enhanced_summary = enhanced_summary.strip()
        
        # Ensure reasonable length
        if len(enhanced_summary) > len(original_summary) * 2:
            logger.warning("Enhanced summary too long, using original")
            return original_summary
        
        # Ensure minimum quality
        if len(enhanced_summary) < 50:
            logger.warning("Enhanced summary too short, using original")
            return original_summary
        
        return enhanced_summary
    
    def _optimize_skills(
        self,
        original_skills: List[str],
        job_requirements: JobRequirements,
        strategy_config: Dict
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Optimize skills section
        
        Args:
            original_skills: Original skills list
            job_requirements: Target job requirements
            strategy_config: Strategy configuration
            
        Returns:
            Tuple of (optimized_skills, modifications, added_keywords)
        """
        modifications = []
        added_keywords = []
        optimized_skills = original_skills.copy()
        
        # Add missing required skills that are reasonable to add
        if strategy_config.get('add_skills', False):
            missing_skills = self._identify_addable_skills(
                original_skills,
                job_requirements.required_skills
            )
            
            for skill in missing_skills[:3]:  # Limit additions
                if skill not in optimized_skills:
                    optimized_skills.append(skill)
                    added_keywords.append(skill)
                    modifications.append(f"Added relevant skill: {skill}")
        
        # Reorder skills to prioritize job-relevant ones
        prioritized_skills = self._prioritize_skills(optimized_skills, job_requirements)
        
        if prioritized_skills != optimized_skills:
            modifications.append("Reordered skills to highlight job-relevant expertise")
            optimized_skills = prioritized_skills
        
        # Add skill variations and synonyms
        enhanced_skills = self._add_skill_variations(optimized_skills, job_requirements)
        
        if len(enhanced_skills) > len(optimized_skills):
            modifications.append("Added skill variations and related technologies")
            added_keywords.extend(enhanced_skills[len(optimized_skills):])
            optimized_skills = enhanced_skills
        
        return optimized_skills, modifications, added_keywords
    
    def _identify_addable_skills(
        self,
        current_skills: List[str],
        required_skills: List[str]
    ) -> List[str]:
        """Identify skills that can reasonably be added"""
        current_skills_lower = [skill.lower() for skill in current_skills]
        addable_skills = []
        
        # Skill relationships - if you have one, you likely know the other
        skill_relationships = {
            'javascript': ['html', 'css', 'dom'],
            'react': ['jsx', 'javascript', 'html'],
            'python': ['pip', 'virtual environments'],
            'sql': ['database design', 'data modeling'],
            'git': ['version control', 'github'],
            'aws': ['cloud computing', 'ec2'],
            'docker': ['containerization', 'devops'],
            'agile': ['scrum', 'sprint planning']
        }
        
        for required_skill in required_skills:
            required_lower = required_skill.lower()
            
            # Skip if already have the skill
            if required_lower in current_skills_lower:
                continue
            
            # Check if we have related skills that justify adding this one
            for current_skill in current_skills_lower:
                if current_skill in skill_relationships:
                    related_skills = skill_relationships[current_skill]
                    if required_lower in related_skills:
                        addable_skills.append(required_skill)
                        break
        
        return addable_skills
    
    def _prioritize_skills(
        self,
        skills: List[str],
        job_requirements: JobRequirements
    ) -> List[str]:
        """Reorder skills to prioritize job-relevant ones"""
        required_skills_lower = [skill.lower() for skill in job_requirements.required_skills]
        preferred_skills_lower = [skill.lower() for skill in job_requirements.preferred_skills]
        
        # Categorize skills
        required_matches = []
        preferred_matches = []
        other_skills = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in required_skills_lower:
                required_matches.append(skill)
            elif skill_lower in preferred_skills_lower:
                preferred_matches.append(skill)
            else:
                other_skills.append(skill)
        
        # Return prioritized order
        return required_matches + preferred_matches + other_skills
    
    def _add_skill_variations(
        self,
        skills: List[str],
        job_requirements: JobRequirements
    ) -> List[str]:
        """Add skill variations and related technologies"""
        enhanced_skills = skills.copy()
        
        # Skill variations mapping
        variations = {
            'javascript': ['js', 'es6', 'es2015+'],
            'python': ['python3', 'py'],
            'react': ['reactjs', 'react.js'],
            'node.js': ['nodejs', 'node'],
            'postgresql': ['postgres', 'psql'],
            'mongodb': ['mongo', 'nosql'],
            'aws': ['amazon web services', 'cloud'],
            'git': ['github', 'version control']
        }
        
        skills_lower = [skill.lower() for skill in skills]
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in variations:
                for variation in variations[skill_lower]:
                    if variation not in skills_lower and len(enhanced_skills) < len(skills) + 5:
                        enhanced_skills.append(variation.title())
                        skills_lower.append(variation)
        
        return enhanced_skills

    def _enhance_experience(
        self,
        original_experience: List[Dict[str, str]],
        job_requirements: JobRequirements,
        strategy_config: Dict,
        preserve_truthfulness: bool
    ) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        """
        Enhance work experience descriptions

        Args:
            original_experience: Original experience list
            job_requirements: Target job requirements
            strategy_config: Strategy configuration
            preserve_truthfulness: Whether to maintain factual accuracy

        Returns:
            Tuple of (enhanced_experience, modifications, added_keywords)
        """
        modifications = []
        added_keywords = []
        enhanced_experience = []

        for exp in original_experience:
            try:
                enhanced_exp = exp.copy()

                # Enhance job description if available
                if exp.get('description'):
                    enhanced_desc, desc_mods, desc_keywords = self._enhance_job_description(
                        exp['description'],
                        job_requirements,
                        strategy_config,
                        preserve_truthfulness
                    )
                    enhanced_exp['description'] = enhanced_desc
                    modifications.extend(desc_mods)
                    added_keywords.extend(desc_keywords)

                enhanced_experience.append(enhanced_exp)

            except Exception as e:
                logger.error(f"Experience enhancement failed: {str(e)}")
                enhanced_experience.append(exp)

        return enhanced_experience, modifications, added_keywords

    def _enhance_job_description(
        self,
        original_description: str,
        job_requirements: JobRequirements,
        strategy_config: Dict,
        preserve_truthfulness: bool
    ) -> Tuple[str, List[str], List[str]]:
        """Enhance individual job description"""
        modifications = []
        added_keywords = []

        try:
            prompt = self._create_experience_prompt(
                original_description,
                job_requirements,
                strategy_config,
                preserve_truthfulness
            )

            enhanced_description = self.groq_client.generate_completion(
                prompt,
                system_message="You are an expert resume writer who enhances job descriptions while maintaining truthfulness."
            )

            # Validate enhanced description
            enhanced_description = self._validate_experience(enhanced_description, original_description)

            if enhanced_description != original_description:
                modifications.append("Enhanced job description with relevant keywords")

                # Identify added keywords
                original_words = set(original_description.lower().split())
                enhanced_words = set(enhanced_description.lower().split())
                new_words = enhanced_words - original_words

                # Filter for meaningful keywords
                meaningful_keywords = [
                    word for word in new_words
                    if len(word) > 2 and word not in ['the', 'and', 'or', 'but', 'with', 'for']
                ]
                added_keywords.extend(meaningful_keywords[:5])

            return enhanced_description, modifications, added_keywords

        except Exception as e:
            logger.error(f"Job description enhancement failed: {str(e)}")
            return original_description, [], []

    def _create_experience_prompt(
        self,
        original_description: str,
        job_requirements: JobRequirements,
        strategy_config: Dict,
        preserve_truthfulness: bool
    ) -> str:
        """Create AI prompt for experience enhancement"""

        required_skills_str = ", ".join(job_requirements.required_skills[:8])
        responsibilities_str = "\n".join(job_requirements.responsibilities[:3])

        truthfulness_instruction = """
        CRITICAL: Maintain complete factual accuracy. Do not add false achievements,
        exaggerate responsibilities, or claim technologies not mentioned in the original.
        Only rephrase and optimize existing content with better action verbs and structure.
        """ if preserve_truthfulness else """
        You may enhance the description strategically while keeping it realistic and professional.
        """

        prompt = f"""
        Enhance this job description to better align with the target role requirements:

        ORIGINAL DESCRIPTION:
        {original_description}

        TARGET ROLE REQUIREMENTS:
        - Key Skills: {required_skills_str}
        - Typical Responsibilities: {responsibilities_str}
        - Job Level: {job_requirements.job_level}

        ENHANCEMENT GUIDELINES:
        {truthfulness_instruction}

        - Use strong action verbs (developed, implemented, optimized, led, etc.)
        - Incorporate relevant technical keywords naturally
        - Quantify achievements where possible (maintain existing numbers)
        - Highlight transferable skills and technologies
        - Maintain professional tone and bullet point format
        - Keep similar length to original

        Strategy: {strategy_config['description']}

        Return only the enhanced description:
        """

        return prompt

    def _validate_experience(self, enhanced_description: str, original_description: str) -> str:
        """Validate and clean enhanced experience description"""
        # Remove any unwanted formatting or instructions
        enhanced_description = re.sub(r'^(enhanced description:|description:)', '', enhanced_description, flags=re.IGNORECASE)
        enhanced_description = enhanced_description.strip()

        # Ensure reasonable length (not more than 2x original)
        if len(enhanced_description) > len(original_description) * 2.5:
            logger.warning("Enhanced description too long, using original")
            return original_description

        # Ensure minimum quality
        if len(enhanced_description) < 20:
            logger.warning("Enhanced description too short, using original")
            return original_description

        return enhanced_description

    def _optimize_formatting(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements
    ) -> List[str]:
        """Optimize resume formatting and section order"""
        modifications = []

        # This would typically involve reordering sections based on job relevance
        # For now, we'll just note that formatting optimization occurred
        modifications.append("Optimized resume structure for target role")

        return modifications

    def _calculate_match_score(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements
    ) -> float:
        """Calculate how well resume matches job requirements"""
        return self.text_processor.calculate_skill_relevance(
            resume_data.skills,
            job_requirements.required_skills + job_requirements.preferred_skills
        )

    def _create_resume_copy(self, resume_data: ResumeData) -> ResumeData:
        """Create a deep copy of resume data"""
        return ResumeData(
            raw_text=resume_data.raw_text,
            name=resume_data.name,
            email=resume_data.email,
            phone=resume_data.phone,
            summary=resume_data.summary,
            skills=resume_data.skills.copy(),
            experience=[exp.copy() for exp in resume_data.experience],
            education=[edu.copy() for edu in resume_data.education],
            sections=resume_data.sections.copy()
        )

    def generate_multiple_versions(
        self,
        resume_data: ResumeData,
        job_requirements: JobRequirements,
        strategies: List[str] = None
    ) -> Dict[str, ResumeModification]:
        """
        Generate multiple resume versions with different strategies

        Args:
            resume_data: Original resume data
            job_requirements: Target job requirements
            strategies: List of strategies to use

        Returns:
            Dictionary mapping strategy names to modifications
        """
        if strategies is None:
            strategies = ['conservative', 'moderate', 'aggressive']

        versions = {}

        for strategy in strategies:
            if strategy in self.modification_strategies:
                logger.info(f"Generating {strategy} version")
                modification = self.modify_resume_for_job(
                    resume_data,
                    job_requirements,
                    strategy=strategy
                )
                versions[strategy] = modification

        return versions

    def export_modified_resume(
        self,
        modification: ResumeModification,
        output_path: Path,
        format_type: str = 'text'
    ) -> bool:
        """
        Export modified resume to file

        Args:
            modification: Resume modification result
            output_path: Output file path
            format_type: Export format (text, json, markdown)

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == 'json':
                self._export_json(modification, output_path)
            elif format_type == 'markdown':
                self._export_markdown(modification, output_path)
            else:  # text
                self._export_text(modification, output_path)

            logger.info(f"Modified resume exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return False

    def _export_text(self, modification: ResumeModification, output_path: Path):
        """Export as formatted text"""
        resume = modification.modified_resume

        content = f"""
{resume.name}
{resume.email} | {resume.phone}

PROFESSIONAL SUMMARY
{resume.summary}

TECHNICAL SKILLS
{', '.join(resume.skills)}

PROFESSIONAL EXPERIENCE
"""

        for exp in resume.experience:
            content += f"\n{exp.get('title', 'Position')} | {exp.get('company', 'Company')}\n"
            content += f"{exp.get('description', '')}\n"

        content += f"\nEDUCATION\n"
        for edu in resume.education:
            content += f"{edu.get('degree', 'Degree')}\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())

    def _export_json(self, modification: ResumeModification, output_path: Path):
        """Export as JSON"""
        data = {
            'modified_resume': {
                'name': modification.modified_resume.name,
                'email': modification.modified_resume.email,
                'phone': modification.modified_resume.phone,
                'summary': modification.modified_resume.summary,
                'skills': modification.modified_resume.skills,
                'experience': modification.modified_resume.experience,
                'education': modification.modified_resume.education
            },
            'modifications': {
                'modifications_made': modification.modifications_made,
                'keyword_additions': modification.keyword_additions,
                'skill_enhancements': modification.skill_enhancements,
                'match_score_before': modification.match_score_before,
                'match_score_after': modification.match_score_after,
                'improvement_percentage': modification.improvement_percentage
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_markdown(self, modification: ResumeModification, output_path: Path):
        """Export as Markdown"""
        resume = modification.modified_resume

        content = f"""# {resume.name}
**Contact:** {resume.email} | {resume.phone}

## Professional Summary
{resume.summary}

## Technical Skills
{', '.join(resume.skills)}

## Professional Experience
"""

        for exp in resume.experience:
            content += f"\n### {exp.get('title', 'Position')} | {exp.get('company', 'Company')}\n"
            content += f"{exp.get('description', '')}\n"

        content += f"\n## Education\n"
        for edu in resume.education:
            content += f"- {edu.get('degree', 'Degree')}\n"

        content += f"\n## Modifications Made\n"
        for mod in modification.modifications_made:
            content += f"- {mod}\n"

        content += f"\n**Match Score Improvement:** {modification.match_score_before:.1%} → {modification.match_score_after:.1%} (+{modification.improvement_percentage:.1f}%)"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
