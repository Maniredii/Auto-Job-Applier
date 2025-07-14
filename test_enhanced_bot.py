# Author: Manideep Reddy Eevuri
# LinkedIn: https://www.linkedin.com/in/manideep-reddy-eevuri-661659268/
# GitHub: https://github.com/Maniredii

"""
Enhanced Bot Test Script
Tests the LinkedIn Auto Job Applier with resume customization and cover letter generation
"""

from modules.ai.openaiConnections import ai_create_openai_client, ai_generate_resume, ai_generate_coverletter, ai_close_openai_client
from modules.ai.deepseekConnections import deepseek_create_client, deepseek_generate_resume, deepseek_generate_coverletter
from modules.ai.huggingfaceConnections import huggingface_create_client, huggingface_generate_resume, huggingface_generate_coverletter
from config.questions import user_information_all
from config.secrets import use_AI, ai_provider

def test_enhanced_features():
    """
    Test the enhanced features: resume customization and cover letter generation
    """
    print("Testing Enhanced LinkedIn Auto Job Applier Features...")
    print("=" * 60)
    
    # Sample job data for testing
    job_description = """
    Senior Software Engineer - Python/Java Developer
    
    We are looking for a passionate Senior Software Engineer to join our innovative team. 
    The ideal candidate will have strong programming skills and experience with modern technologies.
    
    Required Skills:
    - Strong programming skills in Python and Java
    - Experience with machine learning frameworks (TensorFlow, Keras)
    - Knowledge of web technologies (HTML, CSS, JavaScript)
    - Experience with databases (SQL, MongoDB)
    - Version control with Git
    - Experience with cloud platforms (AWS, Azure)
    
    Responsibilities:
    - Develop and maintain scalable software applications
    - Collaborate with cross-functional teams
    - Implement machine learning models
    - Optimize application performance
    - Write clean, maintainable code
    
    Requirements:
    - 5+ years of software development experience
    - Bachelor's degree in Computer Science or related field
    - Experience with agile development methodologies
    """
    
    about_company = """
    TechCorp is a leading technology company specializing in AI and machine learning solutions.
    We help businesses transform their operations through innovative software solutions.
    Our team is passionate about technology and committed to delivering high-quality products.
    """
    
    required_skills = {
        "programming": ["Python", "Java"],
        "machine_learning": ["TensorFlow", "Keras"],
        "web_technologies": ["HTML", "CSS", "JavaScript"],
        "databases": ["SQL", "MongoDB"],
        "tools": ["Git"],
        "cloud": ["AWS", "Azure"]
    }
    
    print("1. Testing Resume Customization...")
    print("-" * 40)
    
    if use_AI:
        try:
            # Create AI client based on provider
            if ai_provider == "openai":
                ai_client = ai_create_openai_client()
                generate_resume_func = ai_generate_resume
                generate_coverletter_func = ai_generate_coverletter
                close_client_func = ai_close_openai_client
            elif ai_provider == "deepseek":
                ai_client = deepseek_create_client()
                generate_resume_func = deepseek_generate_resume
                generate_coverletter_func = deepseek_generate_coverletter
                close_client_func = lambda client: None  # DeepSeek doesn't need explicit closing
            elif ai_provider == "huggingface":
                ai_client = huggingface_create_client()
                generate_resume_func = huggingface_generate_resume
                generate_coverletter_func = huggingface_generate_coverletter
                close_client_func = lambda client: None  # No explicit close needed
            else:
                raise ValueError(f"Unsupported AI provider: {ai_provider}")
            
            # Test resume generation
            resume_path = generate_resume_func(
                ai_client,
                job_description,
                about_company,
                required_skills,
                user_information_all
            )
            
            if isinstance(resume_path, ValueError):
                print(f"❌ Resume generation failed: {resume_path}")
            else:
                print(f"✅ Customized resume generated: {resume_path}")
            
            print("\n2. Testing Cover Letter Generation...")
            print("-" * 40)
            
            # Test cover letter generation
            cover_letter_path = generate_coverletter_func(
                ai_client,
                job_description,
                about_company,
                required_skills,
                user_information_all
            )
            
            if isinstance(cover_letter_path, ValueError):
                print(f"❌ Cover letter generation failed: {cover_letter_path}")
            else:
                print(f"✅ Cover letter generated: {cover_letter_path}")
            
            # Close AI client
            close_client_func(ai_client)
            
        except Exception as e:
            print(f"❌ Error during AI testing: {e}")
    else:
        print("⚠️  AI is disabled in config/secrets.py. Enable it to test these features.")
    
    print("\n3. Configuration Summary...")
    print("-" * 40)
    print(f"AI Provider: {ai_provider}")
    print(f"AI Enabled: {use_AI}")
    print(f"User Information Available: {'Yes' if user_information_all else 'No'}")
    
    print("\n" + "=" * 60)
    print("Enhanced Bot Test Complete!")
    print("The bot will now:")
    print("✅ Search for jobs automatically")
    print("✅ Generate customized resumes for each job")
    print("✅ Create personalized cover letters")
    print("✅ Apply to jobs with tailored materials")
    print("✅ Run continuously without manual intervention")

if __name__ == "__main__":
    test_enhanced_features() 