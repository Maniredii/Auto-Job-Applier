"""
Demo script to test the AI Cover Letter Generator functionality
"""

import json
from pathlib import Path
from src.ai.cover_letter_generator import CoverLetterGenerator
from src.parsers.resume_parser import ResumeData
from src.parsers.job_description_parser import JobRequirements

def create_sample_resume() -> ResumeData:
    """Create a sample resume for testing"""
    return ResumeData(
        raw_text="Sample resume text",
        name="Sarah Johnson",
        email="sarah.johnson@email.com",
        phone="(555) 987-6543",
        summary="Experienced software engineer with 5 years of full-stack development experience. Passionate about creating scalable web applications and leading development teams.",
        skills=[
            "JavaScript", "Python", "React", "Node.js", "AWS", "Docker", 
            "PostgreSQL", "Git", "Agile", "TypeScript", "GraphQL", "MongoDB"
        ],
        experience=[
            {
                "title": "Senior Software Engineer",
                "company": "TechFlow Solutions",
                "description": "Led development of microservices architecture using Node.js and React. Implemented CI/CD pipelines and mentored junior developers. Increased application performance by 40%."
            },
            {
                "title": "Full Stack Developer",
                "company": "InnovateCorp",
                "description": "Developed responsive web applications using React and Python. Collaborated with product teams to deliver features on time. Built RESTful APIs and integrated third-party services."
            },
            {
                "title": "Software Developer",
                "company": "StartupTech",
                "description": "Built user interfaces with JavaScript and CSS. Worked with databases and version control systems. Participated in agile development processes."
            }
        ],
        education=[
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "State University",
                "year": "2018"
            }
        ],
        sections={}
    )

def create_sample_job_requirements() -> JobRequirements:
    """Create sample job requirements for testing"""
    return JobRequirements(
        required_skills=["React", "Node.js", "JavaScript", "Python", "AWS", "PostgreSQL"],
        preferred_skills=["TypeScript", "Docker", "Kubernetes", "GraphQL", "Microservices"],
        experience_years={"JavaScript": 3, "React": 2, "Node.js": 2},
        education_requirements=["Bachelor's degree in Computer Science or related field"],
        certifications=["AWS Certified Developer"],
        responsibilities=[
            "Design and develop scalable web applications",
            "Lead technical architecture decisions",
            "Mentor junior developers and conduct code reviews",
            "Collaborate with product teams to deliver features"
        ],
        keywords=["full-stack", "microservices", "agile", "leadership", "scalable"],
        soft_skills=["Leadership", "Communication", "Problem Solving", "Mentoring"],
        technologies={
            "programming_languages": ["JavaScript", "Python", "TypeScript"],
            "web_technologies": ["React", "Node.js", "HTML", "CSS"],
            "cloud_platforms": ["AWS"],
            "databases": ["PostgreSQL", "MongoDB"]
        },
        salary_range=(140000, 180000),
        job_level="Senior",
        remote_work=True,
        benefits=["Health Insurance", "401k", "Stock Options", "Flexible Hours"],
        company_size="Medium",
        industry="Technology"
    )

def demo_basic_generation():
    """Demonstrate basic cover letter generation"""
    print("=== AI Cover Letter Generator Demo ===\n")
    
    # Initialize components
    generator = CoverLetterGenerator()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    print("👤 CANDIDATE PROFILE:")
    print(f"   Name: {sample_resume.name}")
    print(f"   Experience: {len(sample_resume.experience)} positions")
    print(f"   Skills: {', '.join(sample_resume.skills[:8])}...")
    
    print(f"\n🎯 TARGET POSITION:")
    print(f"   Job Title: Senior Full Stack Developer")
    print(f"   Company: TechVision Inc.")
    print(f"   Required Skills: {', '.join(sample_job.required_skills[:5])}...")
    print(f"   Job Level: {sample_job.job_level}")
    
    print(f"\n🤖 Generating cover letter...")
    
    try:
        # Generate cover letter
        cover_letter = generator.generate_cover_letter(
            resume_data=sample_resume,
            job_requirements=sample_job,
            company_name="TechVision Inc.",
            job_title="Senior Full Stack Developer",
            template='professional',
            personalization_level='high'
        )
        
        print(f"\n✅ GENERATION RESULTS:")
        print(f"   Word Count: {cover_letter.word_count}")
        print(f"   Personalization Score: {cover_letter.personalization_score:.1%}")
        print(f"   Template Used: {cover_letter.template_used}")
        print(f"   Key Points: {len(cover_letter.key_points)}")
        
        print(f"\n📝 GENERATED COVER LETTER:")
        print("-" * 60)
        print(cover_letter.content)
        print("-" * 60)
        
        print(f"\n🎯 KEY POINTS HIGHLIGHTED:")
        for i, point in enumerate(cover_letter.key_points, 1):
            print(f"   {i}. {point[:100]}...")
        
        return cover_letter
        
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        return None

def demo_multiple_templates():
    """Demonstrate multiple template generation"""
    print("\n=== Multiple Template Demo ===\n")
    
    generator = CoverLetterGenerator()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    templates = ['professional', 'enthusiastic', 'technical', 'concise']
    
    print("🔄 Generating multiple cover letter versions...\n")
    
    try:
        versions = generator.generate_multiple_versions(
            sample_resume,
            sample_job,
            "DataTech Solutions",
            "Lead Software Engineer",
            templates=templates,
            personalization_level='high'
        )
        
        print("📊 TEMPLATE COMPARISON:")
        print(f"{'Template':<15} {'Words':<8} {'Score':<8} {'Description'}")
        print("-" * 60)
        
        for template_name, cover_letter in versions.items():
            template_info = generator.templates[template_name]
            print(f"{template_name:<15} {cover_letter.word_count:<8} "
                  f"{cover_letter.personalization_score:<8.1%} {template_info.description}")
        
        print(f"\n📋 TEMPLATE DETAILS:\n")
        
        for template_name, cover_letter in versions.items():
            template_info = generator.templates[template_name]
            print(f"🎨 {template_name.upper()} TEMPLATE:")
            print(f"   Tone: {template_info.tone}")
            print(f"   Length: {template_info.length}")
            print(f"   Use Cases: {', '.join(template_info.use_cases)}")
            print(f"   Word Count: {cover_letter.word_count}")
            print(f"   Personalization: {cover_letter.personalization_score:.1%}")
            print(f"   Preview: {cover_letter.content[:150]}...")
            print()
        
        return versions
        
    except Exception as e:
        print(f"❌ Multiple template generation failed: {str(e)}")
        return {}

def demo_personalization_levels():
    """Demonstrate different personalization levels"""
    print("=== Personalization Levels Demo ===\n")
    
    generator = CoverLetterGenerator()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    levels = ['low', 'medium', 'high']
    
    print("🎯 Testing different personalization levels...\n")
    
    results = {}
    
    for level in levels:
        try:
            print(f"Generating {level} personalization level...")
            
            cover_letter = generator.generate_cover_letter(
                sample_resume,
                sample_job,
                "CloudScale Systems",
                "Principal Software Engineer",
                template='professional',
                personalization_level=level
            )
            
            results[level] = cover_letter
            
        except Exception as e:
            print(f"❌ Failed to generate {level} level: {str(e)}")
    
    if results:
        print("📊 PERSONALIZATION COMPARISON:")
        print(f"{'Level':<10} {'Words':<8} {'Score':<8} {'Key Points'}")
        print("-" * 40)
        
        for level, cover_letter in results.items():
            print(f"{level:<10} {cover_letter.word_count:<8} "
                  f"{cover_letter.personalization_score:<8.1%} {len(cover_letter.key_points)}")
        
        print(f"\n📝 CONTENT COMPARISON:\n")
        
        for level, cover_letter in results.items():
            print(f"📋 {level.upper()} PERSONALIZATION:")
            print(f"   First paragraph: {cover_letter.content.split('.')[0][:200]}...")
            print()
    
    return results

def demo_quality_analysis():
    """Demonstrate cover letter quality analysis"""
    print("=== Quality Analysis Demo ===\n")
    
    generator = CoverLetterGenerator()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    try:
        # Generate a cover letter
        cover_letter = generator.generate_cover_letter(
            sample_resume,
            sample_job,
            "InnovateAI Corp",
            "Senior Software Architect",
            template='technical',
            personalization_level='high'
        )
        
        # Analyze quality
        quality_metrics = generator.analyze_cover_letter_quality(cover_letter)
        
        print("📊 QUALITY ANALYSIS RESULTS:")
        print(f"   Overall Score: {quality_metrics['overall_score']:.1%}")
        print()
        
        print("📈 DETAILED METRICS:")
        for metric, score in quality_metrics.items():
            if metric != 'overall_score':
                metric_name = metric.replace('_', ' ').title()
                print(f"   {metric_name:<20}: {score:.1%}")
        
        print(f"\n💡 QUALITY INSIGHTS:")
        
        # Provide insights based on scores
        if quality_metrics['personalization_score'] >= 0.8:
            print("   ✅ Excellent personalization - highly tailored to the job")
        elif quality_metrics['personalization_score'] >= 0.6:
            print("   ⚠️ Good personalization - could be more specific")
        else:
            print("   ❌ Low personalization - needs more job-specific content")
        
        if quality_metrics['length_score'] >= 0.8:
            print("   ✅ Optimal length - appropriate for the role")
        else:
            print("   ⚠️ Length could be improved - too short or too long")
        
        if quality_metrics['enthusiasm_score'] >= 0.8:
            print("   ✅ Great enthusiasm - shows genuine interest")
        else:
            print("   ⚠️ Could show more enthusiasm and passion")
        
        return quality_metrics
        
    except Exception as e:
        print(f"❌ Quality analysis failed: {str(e)}")
        return {}

def demo_export_functionality():
    """Demonstrate export functionality"""
    print("\n=== Export Functionality Demo ===\n")
    
    generator = CoverLetterGenerator()
    sample_resume = create_sample_resume()
    sample_job = create_sample_job_requirements()
    
    try:
        # Generate cover letter
        cover_letter = generator.generate_cover_letter(
            sample_resume,
            sample_job,
            "FutureTech Innovations",
            "Staff Software Engineer",
            template='enthusiastic',
            personalization_level='high'
        )
        
        # Export in different formats
        output_dir = Path("temp/cover_letters")
        
        formats = {
            'text': 'cover_letter.txt',
            'json': 'cover_letter.json',
            'markdown': 'cover_letter.md'
        }
        
        print("💾 Exporting cover letter in multiple formats...")
        
        for format_type, filename in formats.items():
            output_path = output_dir / filename
            success = generator.export_cover_letter(
                cover_letter,
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

def save_demo_results(cover_letters):
    """Save demo results to file"""
    if not cover_letters:
        return
    
    output_data = {}
    
    if isinstance(cover_letters, dict):
        # Multiple cover letters
        for name, cover_letter in cover_letters.items():
            output_data[name] = {
                "content": cover_letter.content,
                "job_title": cover_letter.job_title,
                "company_name": cover_letter.company_name,
                "word_count": cover_letter.word_count,
                "personalization_score": cover_letter.personalization_score,
                "template_used": cover_letter.template_used,
                "key_points": cover_letter.key_points,
                "generated_at": cover_letter.generated_at
            }
    else:
        # Single cover letter
        output_data["single_cover_letter"] = {
            "content": cover_letters.content,
            "job_title": cover_letters.job_title,
            "company_name": cover_letters.company_name,
            "word_count": cover_letters.word_count,
            "personalization_score": cover_letters.personalization_score,
            "template_used": cover_letters.template_used,
            "key_points": cover_letters.key_points,
            "generated_at": cover_letters.generated_at
        }
    
    output_file = Path("temp/cover_letter_generator_demo.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Demo results saved to: {output_file}")

def main():
    """Main demo function"""
    print("🚀 Starting AI Cover Letter Generator Demo")
    print("=" * 70)
    
    all_cover_letters = {}
    
    try:
        # Demo 1: Basic generation
        basic_cover_letter = demo_basic_generation()
        if basic_cover_letter:
            all_cover_letters['basic'] = basic_cover_letter
        
        # Demo 2: Multiple templates
        template_versions = demo_multiple_templates()
        all_cover_letters.update(template_versions)
        
        # Demo 3: Personalization levels
        personalization_results = demo_personalization_levels()
        
        # Demo 4: Quality analysis
        quality_metrics = demo_quality_analysis()
        
        # Demo 5: Export functionality
        demo_export_functionality()
        
        # Save results
        save_demo_results(all_cover_letters)
        
        print("\n" + "=" * 70)
        print("✅ AI Cover Letter Generator Demo completed successfully!")
        
        print("\nKey Features Demonstrated:")
        print("• AI-powered personalized cover letter generation")
        print("• Multiple professional templates")
        print("• Personalization level control")
        print("• Quality analysis and scoring")
        print("• Multiple export formats")
        print("• Template comparison and optimization")
        
        print("\nNext steps:")
        print("1. Test with your own resume and job descriptions")
        print("2. Experiment with different templates and personalization levels")
        print("3. Integrate with job scraper for automated cover letter generation")
        print("4. Customize templates for specific industries or roles")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Make sure Groq API key is configured and all dependencies are installed.")

if __name__ == "__main__":
    main()
