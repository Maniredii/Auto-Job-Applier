"""
Demo script to test the AI Resume Modifier functionality
"""

import json
from pathlib import Path
from src.ai.resume_modifier import ResumeModifier
from src.parsers.resume_parser import ResumeData
from src.parsers.job_description_parser import JobDescriptionParser, JobRequirements

def create_sample_resume() -> ResumeData:
    """Create a sample resume for testing"""
    return ResumeData(
        raw_text="Sample resume text",
        name="John Doe",
        email="john.doe@email.com",
        phone="(555) 123-4567",
        summary="Software developer with 3 years of experience in web development. Skilled in JavaScript and Python programming.",
        skills=["JavaScript", "Python", "HTML", "CSS", "Git", "SQL"],
        experience=[
            {
                "title": "Software Developer",
                "company": "Tech Solutions Inc",
                "description": "Developed web applications using JavaScript and Python. Worked with databases and version control systems."
            },
            {
                "title": "Junior Developer",
                "company": "StartUp Co",
                "description": "Built user interfaces with HTML and CSS. Collaborated with team members on various projects."
            }
        ],
        education=[
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "year": "2020"
            }
        ],
        sections={
            "summary": "Software developer with 3 years of experience...",
            "experience": "Software Developer at Tech Solutions...",
            "education": "Bachelor of Science in Computer Science..."
        }
    )

def create_sample_job_requirements() -> JobRequirements:
    """Create sample job requirements for testing"""
    return JobRequirements(
        required_skills=["React", "Node.js", "JavaScript", "Python", "AWS", "Docker"],
        preferred_skills=["TypeScript", "Kubernetes", "MongoDB", "GraphQL"],
        experience_years={"JavaScript": 3, "Python": 2, "React": 2},
        education_requirements=["Bachelor's degree in Computer Science or related field"],
        certifications=["AWS Certified Developer"],
        responsibilities=[
            "Develop scalable web applications using React and Node.js",
            "Design and implement RESTful APIs",
            "Deploy applications to AWS cloud infrastructure",
            "Collaborate with cross-functional teams in agile environment"
        ],
        keywords=["full-stack", "microservices", "agile", "scrum", "ci/cd"],
        soft_skills=["Communication", "Problem Solving", "Teamwork"],
        technologies={
            "programming_languages": ["JavaScript", "Python", "TypeScript"],
            "web_technologies": ["React", "Node.js", "HTML", "CSS"],
            "cloud_platforms": ["AWS"],
            "devops_tools": ["Docker", "Kubernetes"],
            "databases": ["MongoDB", "PostgreSQL"]
        },
        salary_range=(120000, 180000),
        job_level="Mid-Level",
        remote_work=True,
        benefits=["Health Insurance", "401k", "Flexible Hours"],
        company_size="Medium",
        industry="Technology"
    )

def demo_basic_modification():
    """Demonstrate basic resume modification"""
    print("=== AI Resume Modifier Demo ===\n")
    
    # Initialize components
    modifier = ResumeModifier()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    print("📋 ORIGINAL RESUME:")
    print(f"   Name: {sample_resume.name}")
    print(f"   Summary: {sample_resume.summary}")
    print(f"   Skills: {', '.join(sample_resume.skills)}")
    print(f"   Experience: {len(sample_resume.experience)} positions")
    
    print(f"\n🎯 TARGET JOB REQUIREMENTS:")
    print(f"   Required Skills: {', '.join(sample_job.required_skills[:5])}...")
    print(f"   Job Level: {sample_job.job_level}")
    print(f"   Industry: {sample_job.industry}")
    
    print(f"\n🤖 Applying AI modifications...")
    
    try:
        # Apply moderate modification strategy
        modification = modifier.modify_resume_for_job(
            sample_resume,
            sample_job,
            strategy='moderate',
            preserve_truthfulness=True
        )
        
        print(f"\n✅ MODIFICATION RESULTS:")
        print(f"   Match Score Before: {modification.match_score_before:.1%}")
        print(f"   Match Score After: {modification.match_score_after:.1%}")
        print(f"   Improvement: +{modification.improvement_percentage:.1f}%")
        
        print(f"\n📝 MODIFICATIONS MADE:")
        for mod in modification.modifications_made:
            print(f"   • {mod}")
        
        print(f"\n🔑 KEYWORDS ADDED:")
        for keyword in modification.keyword_additions[:8]:
            print(f"   • {keyword}")
        
        print(f"\n📋 MODIFIED RESUME:")
        print(f"   Enhanced Summary: {modification.modified_resume.summary}")
        print(f"   Updated Skills: {', '.join(modification.modified_resume.skills[:10])}...")
        
        return modification
        
    except Exception as e:
        print(f"❌ Modification failed: {str(e)}")
        return None

def demo_multiple_strategies():
    """Demonstrate multiple modification strategies"""
    print("\n=== Multiple Strategy Comparison ===\n")
    
    modifier = ResumeModifier()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    strategies = ['conservative', 'moderate', 'aggressive']
    
    print("🔄 Generating multiple resume versions...\n")
    
    try:
        versions = modifier.generate_multiple_versions(
            sample_resume,
            sample_job,
            strategies
        )
        
        print("📊 STRATEGY COMPARISON:")
        print(f"{'Strategy':<12} {'Before':<8} {'After':<8} {'Improvement':<12} {'Modifications'}")
        print("-" * 60)
        
        for strategy, modification in versions.items():
            print(f"{strategy:<12} {modification.match_score_before:<8.1%} "
                  f"{modification.match_score_after:<8.1%} "
                  f"+{modification.improvement_percentage:<11.1f}% "
                  f"{len(modification.modifications_made)}")
        
        print(f"\n🎯 STRATEGY DETAILS:\n")
        
        for strategy, modification in versions.items():
            print(f"📋 {strategy.upper()} STRATEGY:")
            print(f"   Description: {modifier.modification_strategies[strategy]['description']}")
            print(f"   Skills Added: {len(modification.keyword_additions)} keywords")
            print(f"   Top Modifications:")
            for mod in modification.modifications_made[:3]:
                print(f"     • {mod}")
            print()
        
        return versions
        
    except Exception as e:
        print(f"❌ Multiple strategy generation failed: {str(e)}")
        return {}

def demo_real_job_description():
    """Demonstrate with a real job description"""
    print("=== Real Job Description Demo ===\n")
    
    # Real job description
    job_description = """
    Senior Full Stack Developer - React/Node.js
    
    We are seeking a Senior Full Stack Developer to join our growing engineering team. 
    You will be responsible for developing and maintaining our web applications using 
    modern technologies.
    
    Required Skills:
    • 5+ years of experience in full-stack development
    • Strong proficiency in React and Node.js
    • Experience with TypeScript and modern JavaScript (ES6+)
    • Knowledge of RESTful APIs and GraphQL
    • Experience with AWS cloud services
    • Proficiency in SQL and NoSQL databases
    • Experience with Git version control
    
    Preferred Skills:
    • Experience with Docker and Kubernetes
    • Knowledge of CI/CD pipelines
    • Experience with microservices architecture
    • Familiarity with Agile/Scrum methodologies
    
    Responsibilities:
    • Design and develop scalable web applications
    • Collaborate with product and design teams
    • Write clean, maintainable, and well-tested code
    • Participate in code reviews and technical discussions
    • Mentor junior developers
    
    Benefits:
    • Competitive salary ($140,000 - $180,000)
    • Health, dental, and vision insurance
    • 401(k) with company matching
    • Flexible work arrangements
    • Professional development budget
    """
    
    print("🔍 Parsing real job description...")
    
    try:
        # Parse job description
        job_parser = JobDescriptionParser(use_ai=True)
        job_requirements = job_parser.parse_job_description(
            job_description, 
            "Senior Full Stack Developer"
        )
        
        print(f"✅ Parsed job requirements:")
        print(f"   Required Skills: {len(job_requirements.required_skills)} skills")
        print(f"   Preferred Skills: {len(job_requirements.preferred_skills)} skills")
        print(f"   Job Level: {job_requirements.job_level}")
        print(f"   Salary Range: ${job_requirements.salary_range[0]:,} - ${job_requirements.salary_range[1]:,}")
        
        # Modify resume for this job
        modifier = ResumeModifier()
        sample_resume = create_sample_resume()
        
        print(f"\n🤖 Modifying resume for this specific job...")
        
        modification = modifier.modify_resume_for_job(
            sample_resume,
            job_requirements,
            strategy='moderate'
        )
        
        print(f"\n📊 RESULTS FOR REAL JOB:")
        print(f"   Match Score: {modification.match_score_before:.1%} → {modification.match_score_after:.1%}")
        print(f"   Improvement: +{modification.improvement_percentage:.1f}%")
        
        print(f"\n🎯 KEY IMPROVEMENTS:")
        for mod in modification.modifications_made:
            print(f"   • {mod}")
        
        return modification
        
    except Exception as e:
        print(f"❌ Real job description demo failed: {str(e)}")
        return None

def demo_export_functionality():
    """Demonstrate export functionality"""
    print("\n=== Export Functionality Demo ===\n")
    
    modifier = ResumeModifier()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    try:
        # Generate modification
        modification = modifier.modify_resume_for_job(
            sample_resume,
            sample_job,
            strategy='moderate'
        )
        
        # Export in different formats
        output_dir = Path("temp/modified_resumes")
        
        formats = {
            'text': 'modified_resume.txt',
            'json': 'modified_resume.json',
            'markdown': 'modified_resume.md'
        }
        
        print("💾 Exporting modified resume in multiple formats...")
        
        for format_type, filename in formats.items():
            output_path = output_dir / filename
            success = modifier.export_modified_resume(
                modification,
                output_path,
                format_type
            )
            
            if success:
                print(f"   ✅ {format_type.upper()}: {output_path}")
            else:
                print(f"   ❌ {format_type.upper()}: Export failed")
        
        print(f"\n📁 All files saved to: {output_dir}")
        
    except Exception as e:
        print(f"❌ Export demo failed: {str(e)}")

def demo_ai_enhancement_comparison():
    """Compare AI vs non-AI enhancement"""
    print("\n=== AI Enhancement Comparison ===\n")
    
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    print("🤖 Testing AI-powered vs rule-based modifications...")
    
    try:
        # Test with AI
        ai_modifier = ResumeModifier()
        ai_modification = ai_modifier.modify_resume_for_job(
            sample_resume,
            sample_job,
            strategy='moderate'
        )
        
        print(f"📊 COMPARISON RESULTS:")
        print(f"   AI-Enhanced Match Score: {ai_modification.match_score_after:.1%}")
        print(f"   AI Modifications Made: {len(ai_modification.modifications_made)}")
        print(f"   AI Keywords Added: {len(ai_modification.keyword_additions)}")
        
        print(f"\n🎯 AI ENHANCEMENT QUALITY:")
        print(f"   Enhanced Summary Length: {len(ai_modification.modified_resume.summary)} chars")
        print(f"   Skills Optimization: {len(ai_modification.modified_resume.skills)} total skills")
        
        return ai_modification
        
    except Exception as e:
        print(f"❌ AI comparison failed: {str(e)}")
        return None

def save_demo_results(modifications):
    """Save demo results to file"""
    if not modifications:
        return
    
    output_data = {}
    
    if isinstance(modifications, dict):
        # Multiple strategies
        for strategy, modification in modifications.items():
            output_data[strategy] = {
                "match_score_before": modification.match_score_before,
                "match_score_after": modification.match_score_after,
                "improvement_percentage": modification.improvement_percentage,
                "modifications_made": modification.modifications_made,
                "keyword_additions": modification.keyword_additions,
                "modified_summary": modification.modified_resume.summary,
                "modified_skills": modification.modified_resume.skills
            }
    else:
        # Single modification
        output_data["single_modification"] = {
            "match_score_before": modifications.match_score_before,
            "match_score_after": modifications.match_score_after,
            "improvement_percentage": modifications.improvement_percentage,
            "modifications_made": modifications.modifications_made,
            "keyword_additions": modifications.keyword_additions,
            "modified_summary": modifications.modified_resume.summary,
            "modified_skills": modifications.modified_resume.skills
        }
    
    output_file = Path("temp/resume_modifier_demo.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Demo results saved to: {output_file}")

def main():
    """Main demo function"""
    print("🚀 Starting AI Resume Modifier Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Basic modification
        basic_modification = demo_basic_modification()
        
        # Demo 2: Multiple strategies
        strategy_versions = demo_multiple_strategies()
        
        # Demo 3: Real job description
        real_job_modification = demo_real_job_description()
        
        # Demo 4: Export functionality
        demo_export_functionality()
        
        # Demo 5: AI enhancement comparison
        ai_comparison = demo_ai_enhancement_comparison()
        
        # Save results
        save_demo_results(strategy_versions or basic_modification)
        
        print("\n" + "=" * 60)
        print("✅ AI Resume Modifier Demo completed successfully!")
        
        print("\nKey Features Demonstrated:")
        print("• AI-powered resume enhancement with Groq")
        print("• Multiple modification strategies")
        print("• Intelligent keyword integration")
        print("• Skill optimization and prioritization")
        print("• Experience description enhancement")
        print("• Match score calculation and improvement")
        print("• Multiple export formats")
        
        print("\nNext steps:")
        print("1. Test with your own resume and job descriptions")
        print("2. Experiment with different strategies")
        print("3. Integrate with job scraper for automated optimization")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Make sure Groq API key is configured and all dependencies are installed.")

if __name__ == "__main__":
    main()
