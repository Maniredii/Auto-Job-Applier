"""
Demo script to test the Resume Parser functionality
"""

import json
from pathlib import Path
from src.parsers.resume_parser import ResumeParser
from src.parsers.text_processor import TextProcessor

def create_sample_resume_text():
    """Create a sample resume text for testing"""
    return """
JOHN DOE
Software Engineer
john.doe@example.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe
San Francisco, CA

PROFESSIONAL SUMMARY
Experienced Full-Stack Software Engineer with 5+ years of experience developing scalable web applications 
using Python, JavaScript, and cloud technologies. Proven track record of leading development teams and 
delivering high-quality software solutions. Strong expertise in machine learning and data analysis.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, C++, SQL
Web Technologies: React, Angular, Node.js, Express, HTML5, CSS3, Bootstrap
Frameworks: Django, Flask, Spring Boot, Next.js
Databases: MySQL, PostgreSQL, MongoDB, Redis
Cloud Platforms: AWS, Azure, Google Cloud Platform
DevOps: Docker, Kubernetes, Jenkins, Git, GitHub Actions
Data Science: Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch
Testing: Jest, Pytest, Selenium, Cypress

PROFESSIONAL EXPERIENCE

Senior Software Engineer | Tech Innovations Inc. | 2021 - Present
• Led a team of 5 developers in building a microservices-based e-commerce platform using Python and React
• Implemented CI/CD pipelines using Jenkins and Docker, reducing deployment time by 60%
• Developed machine learning models for product recommendation system, increasing user engagement by 25%
• Mentored junior developers and conducted code reviews to maintain high code quality standards

Software Engineer | Digital Solutions Corp | 2019 - 2021
• Developed and maintained web applications using Django and React for 10+ clients
• Optimized database queries and improved application performance by 40%
• Collaborated with cross-functional teams to deliver projects on time and within budget
• Implemented automated testing strategies, reducing bug reports by 50%

Junior Developer | StartUp Ventures | 2018 - 2019
• Built responsive web interfaces using HTML, CSS, JavaScript, and React
• Participated in agile development processes and daily stand-up meetings
• Contributed to open-source projects and gained experience with version control systems

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley | 2018
GPA: 3.8/4.0
Relevant Coursework: Data Structures, Algorithms, Database Systems, Machine Learning

CERTIFICATIONS
• AWS Certified Solutions Architect - Associate (2022)
• Google Cloud Professional Developer (2021)
• Microsoft Azure Fundamentals (2020)

PROJECTS
E-Commerce Platform | Personal Project
• Built a full-stack e-commerce application using React, Node.js, and MongoDB
• Implemented user authentication, payment processing, and inventory management
• Deployed on AWS using Docker containers and managed with Kubernetes

Machine Learning Stock Predictor | Academic Project
• Developed a stock price prediction model using Python and TensorFlow
• Achieved 85% accuracy in predicting short-term price movements
• Presented findings at university research symposium

ACHIEVEMENTS
• Employee of the Month - Tech Innovations Inc. (March 2022)
• Hackathon Winner - Bay Area Tech Challenge (2021)
• Dean's List - University of California, Berkeley (2016-2018)
"""

def demo_basic_parsing():
    """Demonstrate basic resume parsing functionality"""
    print("=== Resume Parser Demo ===\n")
    
    # Initialize parser
    parser = ResumeParser()
    
    # Create sample resume text
    sample_text = create_sample_resume_text()
    
    # Parse the text directly
    print("Parsing sample resume...")
    resume_data = parser._parse_text(sample_text)
    
    # Display results
    print(f"\n📋 BASIC INFORMATION:")
    print(f"Name: {resume_data.name}")
    print(f"Email: {resume_data.email}")
    print(f"Phone: {resume_data.phone}")
    
    print(f"\n📝 SUMMARY:")
    print(resume_data.summary[:200] + "..." if len(resume_data.summary) > 200 else resume_data.summary)
    
    print(f"\n🛠️ SKILLS ({len(resume_data.skills)} found):")
    for skill in sorted(resume_data.skills)[:10]:  # Show first 10 skills
        print(f"  • {skill}")
    if len(resume_data.skills) > 10:
        print(f"  ... and {len(resume_data.skills) - 10} more")
    
    print(f"\n💼 EXPERIENCE ({len(resume_data.experience)} positions):")
    for i, exp in enumerate(resume_data.experience[:3], 1):  # Show first 3 positions
        print(f"  {i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
    
    print(f"\n🎓 EDUCATION ({len(resume_data.education)} entries):")
    for edu in resume_data.education:
        print(f"  • {edu.get('degree', 'N/A')}")
    
    return resume_data

def demo_advanced_processing():
    """Demonstrate advanced text processing features"""
    print("\n=== Advanced Text Processing Demo ===\n")
    
    # Initialize text processor
    processor = TextProcessor()
    
    # Create sample resume text
    sample_text = create_sample_resume_text()
    
    # Advanced skill extraction
    print("🔍 ADVANCED SKILL EXTRACTION:")
    categorized_skills = processor.extract_skills_advanced(sample_text)
    
    for category, skills in categorized_skills.items():
        if skills:  # Only show categories with skills
            print(f"\n  {category.replace('_', ' ').title()}:")
            for skill in skills[:5]:  # Show first 5 skills per category
                print(f"    • {skill}")
            if len(skills) > 5:
                print(f"    ... and {len(skills) - 5} more")
    
    # Extract years of experience
    print(f"\n⏱️ YEARS OF EXPERIENCE:")
    experience_years = processor.extract_years_of_experience(sample_text)
    if experience_years:
        for skill, years in experience_years.items():
            print(f"  • {skill}: {years} years")
    else:
        print("  No specific experience years found in this format")
    
    # Extract certifications
    print(f"\n🏆 CERTIFICATIONS:")
    certifications = processor.extract_certifications(sample_text)
    for cert in certifications:
        print(f"  • {cert}")
    
    # Extract contact information
    print(f"\n📞 CONTACT INFORMATION:")
    contact_info = processor.extract_contact_info_advanced(sample_text)
    for key, value in contact_info.items():
        print(f"  {key.title()}: {value}")
    
    # Extract soft skills
    print(f"\n🤝 SOFT SKILLS:")
    soft_skills = processor.extract_soft_skills(sample_text)
    for skill in soft_skills:
        print(f"  • {skill}")

def demo_skill_matching():
    """Demonstrate skill matching functionality"""
    print("\n=== Skill Matching Demo ===\n")
    
    processor = TextProcessor()
    sample_text = create_sample_resume_text()
    
    # Extract resume skills
    categorized_skills = processor.extract_skills_advanced(sample_text)
    resume_skills = []
    for skills_list in categorized_skills.values():
        resume_skills.extend(skills_list)
    
    # Sample job requirements
    job_requirements = [
        "Python", "React", "AWS", "Docker", "Machine Learning", 
        "PostgreSQL", "Git", "Agile", "REST APIs", "Microservices"
    ]
    
    print("🎯 JOB REQUIREMENTS:")
    for req in job_requirements:
        print(f"  • {req}")
    
    print(f"\n📊 SKILL MATCHING ANALYSIS:")
    relevance_score = processor.calculate_skill_relevance(resume_skills, job_requirements)
    print(f"  Overall Relevance Score: {relevance_score:.2%}")
    
    # Find matching skills
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    job_skills_lower = [skill.lower() for skill in job_requirements]
    matching_skills = set(resume_skills_lower) & set(job_skills_lower)
    missing_skills = set(job_skills_lower) - set(resume_skills_lower)
    
    print(f"\n✅ MATCHING SKILLS ({len(matching_skills)}):")
    for skill in sorted(matching_skills):
        print(f"  • {skill.title()}")
    
    print(f"\n❌ MISSING SKILLS ({len(missing_skills)}):")
    for skill in sorted(missing_skills):
        print(f"  • {skill.title()}")

def save_parsed_data(resume_data):
    """Save parsed resume data to JSON file"""
    output_data = {
        "name": resume_data.name,
        "email": resume_data.email,
        "phone": resume_data.phone,
        "summary": resume_data.summary,
        "skills": resume_data.skills,
        "experience": resume_data.experience,
        "education": resume_data.education,
        "sections": resume_data.sections
    }
    
    output_file = Path("temp/parsed_resume_demo.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Parsed data saved to: {output_file}")

def main():
    """Main demo function"""
    try:
        # Run basic parsing demo
        resume_data = demo_basic_parsing()
        
        # Run advanced processing demo
        demo_advanced_processing()
        
        # Run skill matching demo
        demo_skill_matching()
        
        # Save parsed data
        save_parsed_data(resume_data)
        
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("3. Test with your own resume files")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Make sure all dependencies are installed.")

if __name__ == "__main__":
    main()
