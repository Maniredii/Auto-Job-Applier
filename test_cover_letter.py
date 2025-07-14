# Author: Manideep Reddy Eevuri
# LinkedIn: https://www.linkedin.com/in/manideep-reddy-eevuri-661659268/
# GitHub: https://github.com/Maniredii

from modules.ai.openaiConnections import ai_create_openai_client, ai_generate_coverletter
from config.questions import user_information_all

def test_cover_letter_generator():
    """
    Test function for the cover letter generator
    """
    print("Testing Cover Letter Generator...")
    
    # Sample job description for testing
    job_description = """
    Software Engineer - Python/Java Developer
    
    We are looking for a passionate Software Engineer to join our team. The ideal candidate will have:
    
    Required Skills:
    - Strong programming skills in Python and Java
    - Experience with machine learning frameworks (TensorFlow, Keras)
    - Knowledge of web technologies (HTML, CSS)
    - Experience with version control systems (Git)
    - Strong problem-solving and analytical skills
    
    Preferred Skills:
    - Experience with OpenCV and computer vision
    - Knowledge of database systems
    - Experience with cloud platforms
    - Understanding of AI/ML concepts
    
    Responsibilities:
    - Develop and maintain software applications
    - Collaborate with cross-functional teams
    - Participate in code reviews and technical discussions
    - Contribute to the development of AI/ML solutions
    
    Education: Bachelor's degree in Computer Science or related field
    Experience: 0-2 years of relevant experience
    """
    
    about_company = """
    TechCorp is a leading technology company specializing in AI and machine learning solutions. 
    We work with Fortune 500 companies to develop innovative software solutions that drive business growth. 
    Our team is passionate about technology and committed to delivering high-quality products.
    """
    
    try:
        # Create OpenAI client
        print("Creating OpenAI client...")
        client = ai_create_openai_client()
        
        if client:
            print("Generating cover letter...")
            # Generate cover letter
            cover_letter_path = ai_generate_coverletter(
                client=client,
                job_description=job_description,
                about_company=about_company,
                required_skills={},  # Empty dict for testing
                user_information=user_information_all,
                stream=False  # Set to False for testing
            )
            
            print(f"Cover letter generated successfully!")
            print(f"Saved to: {cover_letter_path}")
            
            # Close the client
            client.close()
        else:
            print("Failed to create OpenAI client. Please check your API configuration.")
            
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_cover_letter_generator() 