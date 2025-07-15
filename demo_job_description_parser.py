"""
Demo script to test the Job Description Parser functionality
"""

import json
from pathlib import Path
from src.parsers.job_description_parser import JobDescriptionParser, JobRequirements

def create_sample_job_descriptions():
    """Create sample job descriptions for testing"""
    return {
        "software_engineer": """
        Software Engineer - Full Stack Development
        
        Company: TechCorp Inc.
        Location: San Francisco, CA (Remote options available)
        Salary: $120,000 - $180,000
        
        About the Role:
        We are seeking a talented Software Engineer to join our growing team. You will be responsible for developing and maintaining our web applications using modern technologies.
        
        Key Responsibilities:
        • Design and develop scalable web applications using React and Node.js
        • Collaborate with cross-functional teams to define and implement new features
        • Write clean, maintainable, and well-tested code
        • Participate in code reviews and maintain high coding standards
        • Optimize application performance and ensure security best practices
        • Mentor junior developers and contribute to team knowledge sharing
        
        Required Qualifications:
        • Bachelor's degree in Computer Science or related field
        • 3+ years of experience in full-stack web development
        • Strong proficiency in JavaScript, React, and Node.js
        • Experience with SQL databases (PostgreSQL preferred)
        • Knowledge of RESTful APIs and microservices architecture
        • Proficient with Git version control
        • Strong problem-solving and analytical skills
        • Excellent communication and teamwork abilities
        
        Preferred Qualifications:
        • Experience with TypeScript and modern JavaScript frameworks
        • Knowledge of cloud platforms (AWS, Azure, or GCP)
        • Experience with Docker and Kubernetes
        • Familiarity with CI/CD pipelines
        • Understanding of Agile development methodologies
        • Experience with testing frameworks (Jest, Cypress)
        
        Benefits:
        • Competitive salary and equity package
        • Comprehensive health, dental, and vision insurance
        • 401(k) with company matching
        • Flexible work arrangements and unlimited PTO
        • Professional development budget
        • Modern office with free meals and snacks
        
        How to Apply:
        Please submit your resume and cover letter through our online portal. Include links to your GitHub profile and any relevant portfolio projects.
        """,
        
        "data_scientist": """
        Senior Data Scientist - Machine Learning
        
        Company: DataTech Solutions
        Location: Remote (US timezone)
        Salary: $140,000 - $200,000 + bonus
        
        Position Overview:
        Join our data science team to build cutting-edge machine learning models that drive business decisions. You'll work with large datasets and deploy models at scale.
        
        What You'll Do:
        • Develop and deploy machine learning models for predictive analytics
        • Analyze large datasets to extract actionable business insights
        • Collaborate with engineering teams to productionize ML models
        • Design and conduct A/B tests to measure model performance
        • Present findings to stakeholders and executive leadership
        • Stay current with latest ML research and industry best practices
        
        Must-Have Requirements:
        • Master's degree in Data Science, Statistics, or related quantitative field
        • 5+ years of experience in data science and machine learning
        • Expert-level Python programming skills
        • Strong experience with pandas, scikit-learn, and TensorFlow/PyTorch
        • Proficiency in SQL and experience with big data tools (Spark, Hadoop)
        • Experience with cloud ML platforms (AWS SageMaker, Google AI Platform)
        • Strong statistical analysis and experimental design skills
        • Excellent data visualization skills (matplotlib, seaborn, Tableau)
        
        Nice-to-Have:
        • PhD in a quantitative field
        • Experience with deep learning and neural networks
        • Knowledge of MLOps and model deployment pipelines
        • Experience with real-time data processing (Kafka, Kinesis)
        • Familiarity with containerization (Docker, Kubernetes)
        • Previous experience in fintech or e-commerce
        
        Certifications Preferred:
        • AWS Certified Machine Learning - Specialty
        • Google Cloud Professional ML Engineer
        • Microsoft Azure AI Engineer Associate
        
        Company Culture:
        We're a fast-growing startup with a collaborative, data-driven culture. We value innovation, continuous learning, and work-life balance.
        
        Application Process:
        Send your resume, cover letter, and portfolio to careers@datatech.com. Include examples of your ML projects and any published research.
        Deadline: Applications due by March 15, 2024.
        """,
        
        "devops_engineer": """
        DevOps Engineer - Infrastructure & Automation
        
        Company: CloudScale Systems
        Location: Austin, TX (Hybrid - 3 days in office)
        Compensation: $110,000 - $160,000 + benefits
        
        Role Summary:
        We're looking for a DevOps Engineer to help scale our infrastructure and improve our deployment processes. You'll work with cutting-edge cloud technologies.
        
        Core Responsibilities:
        • Design and maintain CI/CD pipelines using Jenkins and GitLab CI
        • Manage AWS infrastructure using Terraform and CloudFormation
        • Implement monitoring and alerting solutions with Prometheus and Grafana
        • Automate deployment processes and infrastructure provisioning
        • Ensure security best practices across all environments
        • Troubleshoot production issues and optimize system performance
        • Collaborate with development teams to improve deployment workflows
        
        Required Skills:
        • Bachelor's degree in Computer Science, Engineering, or equivalent experience
        • Minimum 3 years of DevOps or Site Reliability Engineering experience
        • Strong experience with AWS services (EC2, S3, RDS, Lambda, EKS)
        • Proficiency in Infrastructure as Code (Terraform, CloudFormation)
        • Experience with containerization (Docker) and orchestration (Kubernetes)
        • Solid scripting skills in Python, Bash, or PowerShell
        • Knowledge of CI/CD tools (Jenkins, GitLab CI, GitHub Actions)
        • Understanding of networking, security, and monitoring concepts
        
        Bonus Points:
        • Experience with multiple cloud providers (Azure, GCP)
        • Knowledge of service mesh technologies (Istio, Linkerd)
        • Experience with configuration management (Ansible, Chef, Puppet)
        • Familiarity with observability tools (ELK stack, Jaeger)
        • Previous experience in a high-growth startup environment
        
        What We Offer:
        • Competitive salary with performance bonuses
        • Stock options in a growing company
        • Health, dental, vision, and life insurance
        • Flexible PTO and parental leave
        • $2,000 annual learning and development budget
        • Top-tier equipment and home office stipend
        
        Company Size: 200-500 employees
        Industry: Cloud Infrastructure
        
        To Apply:
        Apply online at cloudscale.com/careers or email your resume to hiring@cloudscale.com
        """
    }

def demo_basic_parsing():
    """Demonstrate basic job description parsing"""
    print("=== Job Description Parser Demo ===\n")
    
    # Initialize parser
    parser = JobDescriptionParser(use_ai=True)
    
    # Get sample job descriptions
    job_descriptions = create_sample_job_descriptions()
    
    print("🔍 Parsing sample job descriptions...\n")
    
    parsed_jobs = {}
    
    for job_type, description in job_descriptions.items():
        print(f"📋 Parsing {job_type.replace('_', ' ').title()} position...")
        
        # Extract job title from description
        lines = description.strip().split('\n')
        job_title = lines[0].strip() if lines else job_type
        
        # Parse the job description
        requirements = parser.parse_job_description(description, job_title)
        parsed_jobs[job_type] = requirements
        
        # Display key results
        print(f"   ✅ Extracted {len(requirements.required_skills)} required skills")
        print(f"   ✅ Extracted {len(requirements.preferred_skills)} preferred skills")
        print(f"   ✅ Found {len(requirements.responsibilities)} responsibilities")
        print(f"   ✅ Job Level: {requirements.job_level}")
        print(f"   ✅ Remote Work: {requirements.remote_work}")
        print(f"   ✅ Industry: {requirements.industry}")
        
        if requirements.salary_range:
            print(f"   ✅ Salary Range: ${requirements.salary_range[0]:,} - ${requirements.salary_range[1]:,}")
        
        print()
    
    return parsed_jobs

def demo_detailed_analysis():
    """Demonstrate detailed job requirement analysis"""
    print("=== Detailed Job Analysis Demo ===\n")
    
    parser = JobDescriptionParser(use_ai=True)
    job_descriptions = create_sample_job_descriptions()
    
    # Analyze the software engineer position in detail
    job_desc = job_descriptions["software_engineer"]
    requirements = parser.parse_job_description(job_desc, "Software Engineer")
    
    print("🔬 Detailed Analysis: Software Engineer Position\n")
    
    print("📋 REQUIRED SKILLS:")
    for skill in requirements.required_skills[:10]:
        print(f"   • {skill}")
    
    print(f"\n🎯 PREFERRED SKILLS:")
    for skill in requirements.preferred_skills[:10]:
        print(f"   • {skill}")
    
    print(f"\n🛠️ TECHNOLOGIES BY CATEGORY:")
    for category, skills in requirements.technologies.items():
        if skills:
            print(f"   {category.replace('_', ' ').title()}:")
            for skill in skills[:5]:
                print(f"     - {skill}")
    
    print(f"\n💼 RESPONSIBILITIES:")
    for i, resp in enumerate(requirements.responsibilities[:5], 1):
        print(f"   {i}. {resp[:100]}...")
    
    print(f"\n🎓 EDUCATION REQUIREMENTS:")
    for edu in requirements.education_requirements:
        print(f"   • {edu}")
    
    print(f"\n🏆 CERTIFICATIONS:")
    for cert in requirements.certifications:
        print(f"   • {cert}")
    
    print(f"\n💰 COMPENSATION & BENEFITS:")
    if requirements.salary_range:
        print(f"   Salary: ${requirements.salary_range[0]:,} - ${requirements.salary_range[1]:,}")
    for benefit in requirements.benefits[:8]:
        print(f"   • {benefit}")
    
    print(f"\n📊 JOB METADATA:")
    print(f"   Level: {requirements.job_level}")
    print(f"   Remote Work: {requirements.remote_work}")
    print(f"   Company Size: {requirements.company_size}")
    print(f"   Industry: {requirements.industry}")

def demo_job_matching():
    """Demonstrate job matching analysis"""
    print("\n=== Job Matching Analysis Demo ===\n")
    
    parser = JobDescriptionParser(use_ai=True)
    job_descriptions = create_sample_job_descriptions()
    
    # Sample candidate skills
    candidate_skills = [
        "Python", "JavaScript", "React", "Node.js", "SQL", "Git",
        "AWS", "Docker", "PostgreSQL", "REST APIs", "Agile",
        "Problem Solving", "Communication", "Teamwork"
    ]
    
    print("👤 CANDIDATE SKILLS:")
    for skill in candidate_skills:
        print(f"   • {skill}")
    
    print(f"\n🎯 JOB MATCHING ANALYSIS:\n")
    
    for job_type, description in job_descriptions.items():
        job_title = job_type.replace('_', ' ').title()
        requirements = parser.parse_job_description(description, job_title)
        
        # Analyze match
        match_analysis = parser.analyze_job_match(requirements, candidate_skills)
        
        print(f"📊 {job_title}:")
        print(f"   Overall Match: {match_analysis['overall_score']:.1%}")
        print(f"   Required Skills Match: {match_analysis['required_skills_match']:.1%}")
        print(f"   Preferred Skills Match: {match_analysis['preferred_skills_match']:.1%}")
        print(f"   Recommendation: {match_analysis['recommendation']}")
        
        if match_analysis['missing_required_skills']:
            print(f"   Missing Required Skills: {', '.join(match_analysis['missing_required_skills'][:5])}")
        
        print()

def demo_application_instructions():
    """Demonstrate application instruction extraction"""
    print("=== Application Instructions Demo ===\n")
    
    parser = JobDescriptionParser(use_ai=True)
    job_descriptions = create_sample_job_descriptions()
    
    for job_type, description in job_descriptions.items():
        job_title = job_type.replace('_', ' ').title()
        instructions = parser.extract_application_instructions(description)
        
        print(f"📝 {job_title} - Application Instructions:")
        print(f"   Method: {instructions['application_method']}")
        print(f"   Required Documents: {', '.join(instructions['required_documents'])}")
        if instructions['contact_info']:
            print(f"   Contact: {instructions['contact_info']}")
        if instructions['application_deadline']:
            print(f"   Deadline: {instructions['application_deadline']}")
        print()

def demo_ai_vs_rule_based():
    """Compare AI-based vs rule-based parsing"""
    print("=== AI vs Rule-Based Parsing Comparison ===\n")
    
    job_desc = create_sample_job_descriptions()["data_scientist"]
    
    # Parse with AI
    print("🤖 Parsing with AI enhancement...")
    ai_parser = JobDescriptionParser(use_ai=True)
    ai_results = ai_parser.parse_job_description(job_desc, "Data Scientist")
    
    # Parse without AI
    print("📏 Parsing with rule-based only...")
    rule_parser = JobDescriptionParser(use_ai=False)
    rule_results = rule_parser.parse_job_description(job_desc, "Data Scientist")
    
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"   AI Required Skills: {len(ai_results.required_skills)}")
    print(f"   Rule-based Required Skills: {len(rule_results.required_skills)}")
    print(f"   AI Preferred Skills: {len(ai_results.preferred_skills)}")
    print(f"   Rule-based Preferred Skills: {len(rule_results.preferred_skills)}")
    print(f"   AI Responsibilities: {len(ai_results.responsibilities)}")
    print(f"   Rule-based Responsibilities: {len(rule_results.responsibilities)}")

def save_demo_results(parsed_jobs):
    """Save demo results to file"""
    output_data = {}
    
    for job_type, requirements in parsed_jobs.items():
        output_data[job_type] = {
            "required_skills": requirements.required_skills,
            "preferred_skills": requirements.preferred_skills,
            "experience_years": requirements.experience_years,
            "education_requirements": requirements.education_requirements,
            "certifications": requirements.certifications,
            "responsibilities": requirements.responsibilities[:5],  # Limit for readability
            "keywords": requirements.keywords[:10],
            "soft_skills": requirements.soft_skills,
            "technologies": requirements.technologies,
            "salary_range": requirements.salary_range,
            "job_level": requirements.job_level,
            "remote_work": requirements.remote_work,
            "benefits": requirements.benefits,
            "company_size": requirements.company_size,
            "industry": requirements.industry
        }
    
    output_file = Path("temp/parsed_job_requirements_demo.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Demo results saved to: {output_file}")

def main():
    """Main demo function"""
    print("🚀 Starting Job Description Parser Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Basic parsing
        parsed_jobs = demo_basic_parsing()
        
        # Demo 2: Detailed analysis
        demo_detailed_analysis()
        
        # Demo 3: Job matching
        demo_job_matching()
        
        # Demo 4: Application instructions
        demo_application_instructions()
        
        # Demo 5: AI vs Rule-based comparison
        print("=" * 60)
        user_input = input("Compare AI vs Rule-based parsing? (y/n): ").lower().strip()
        if user_input == 'y':
            demo_ai_vs_rule_based()
        
        # Save results
        save_demo_results(parsed_jobs)
        
        print("\n" + "=" * 60)
        print("✅ Job Description Parser Demo completed successfully!")
        
        print("\nKey Features Demonstrated:")
        print("• Skill extraction and categorization")
        print("• Experience and education requirement parsing")
        print("• Salary and benefit extraction")
        print("• Job matching and candidate analysis")
        print("• Application instruction extraction")
        print("• AI-enhanced parsing with Groq")
        
        print("\nNext steps:")
        print("1. Test with real job descriptions")
        print("2. Integrate with job scraper module")
        print("3. Use for resume optimization")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Make sure all dependencies are installed and Groq API key is configured.")

if __name__ == "__main__":
    main()
