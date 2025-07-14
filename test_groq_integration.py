#!/usr/bin/env python3
"""
Groq Integration Test Script
Tests all Groq AI-powered features with your API key
"""

import os
import sys
import time
import json
from datetime import datetime

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.helpers import print_lg

def test_groq_connection():
    """Test basic Groq API connection."""
    print_lg("🔌 Testing Groq API connection...")
    
    try:
        from modules.ai.groqConnections import groq_create_client
        from config.secrets import groq_api_key, groq_model
        
        if not groq_api_key:
            print_lg("❌ Groq API key not configured")
            return False
        
        # Create client
        client = groq_create_client(groq_api_key, groq_model)
        
        if client:
            print_lg("✅ Groq API connection successful!")
            print_lg(f"🤖 Model: {groq_model}")
            return True
        else:
            print_lg("❌ Failed to create Groq client")
            return False
            
    except Exception as e:
        print_lg(f"❌ Groq connection test failed: {e}")
        return False

def test_cover_letter_generation():
    """Test AI-powered cover letter generation."""
    print_lg("\n📝 Testing cover letter generation...")
    
    try:
        from modules.ai.groqConnections import groq_create_client
        from config.secrets import groq_api_key, groq_model
        
        client = groq_create_client(groq_api_key, groq_model)
        
        # Test data
        job_description = """
        Software Engineer Position at TechCorp
        
        We are looking for a skilled Python developer with experience in:
        - Python programming (3+ years)
        - Django/Flask frameworks
        - Database design (PostgreSQL, MySQL)
        - RESTful API development
        - Git version control
        - Agile development methodologies
        
        The ideal candidate will have strong problem-solving skills and experience
        working in collaborative team environments.
        """
        
        user_profile = {
            'name': 'John Doe',
            'experience_years': 4,
            'skills': ['Python', 'Django', 'PostgreSQL', 'REST APIs', 'Git'],
            'education': 'Bachelor of Science in Computer Science',
            'career_goals': ['Software Engineering', 'Full-stack Development']
        }
        
        company_info = {
            'name': 'TechCorp',
            'industry': 'Technology',
            'size': 'Mid-size'
        }
        
        # Generate cover letter
        start_time = time.time()
        cover_letter = client.generate_cover_letter(job_description, user_profile, company_info)
        generation_time = time.time() - start_time
        
        print_lg(f"✅ Cover letter generated in {generation_time:.2f} seconds")
        print_lg(f"📄 Length: {len(cover_letter)} characters")
        print_lg(f"📝 Preview: {cover_letter[:200]}...")
        
        # Save to file
        os.makedirs("test_outputs", exist_ok=True)
        with open("test_outputs/test_cover_letter.txt", "w") as f:
            f.write(cover_letter)
        
        print_lg("💾 Cover letter saved to test_outputs/test_cover_letter.txt")
        return True
        
    except Exception as e:
        print_lg(f"❌ Cover letter generation failed: {e}")
        return False

def test_resume_optimization():
    """Test AI-powered resume optimization."""
    print_lg("\n🎯 Testing resume optimization...")
    
    try:
        from modules.ai.groqConnections import groq_create_client
        from config.secrets import groq_api_key, groq_model
        
        client = groq_create_client(groq_api_key, groq_model)
        
        # Test resume sections
        resume_sections = {
            "professional_summary": "Experienced software developer with 4 years of experience in web development.",
            "skills": ["Python", "JavaScript", "HTML", "CSS", "SQL"],
            "experience": [
                {
                    "title": "Software Developer",
                    "company": "ABC Corp",
                    "duration": "2020-2024",
                    "description": "Developed web applications using Python and Django"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "school": "University of Technology",
                    "year": "2020"
                }
            ]
        }
        
        job_description = """
        Senior Python Developer Position
        
        Requirements:
        - 3+ years Python experience
        - Django framework expertise
        - Database design skills
        - API development experience
        - Team collaboration
        """
        
        # Optimize resume
        start_time = time.time()
        optimized_resume = client.optimize_resume_content(resume_sections, job_description)
        optimization_time = time.time() - start_time
        
        print_lg(f"✅ Resume optimized in {optimization_time:.2f} seconds")
        
        # Save optimized resume
        with open("test_outputs/test_optimized_resume.json", "w") as f:
            json.dump(optimized_resume, f, indent=2)
        
        print_lg("💾 Optimized resume saved to test_outputs/test_optimized_resume.json")
        return True
        
    except Exception as e:
        print_lg(f"❌ Resume optimization failed: {e}")
        return False

def test_job_match_analysis():
    """Test AI-powered job match analysis."""
    print_lg("\n🔍 Testing job match analysis...")
    
    try:
        from modules.ai.groqConnections import groq_create_client
        from config.secrets import groq_api_key, groq_model
        
        client = groq_create_client(groq_api_key, groq_model)
        
        # Test data
        job_description = """
        Data Scientist Position at DataCorp
        
        We are seeking a Data Scientist with:
        - Python programming (pandas, numpy, scikit-learn)
        - Machine learning experience
        - Statistical analysis skills
        - SQL database knowledge
        - Data visualization (matplotlib, seaborn)
        - 2+ years experience in data science
        """
        
        user_profile = {
            'skills': ['Python', 'Machine Learning', 'SQL', 'Statistics', 'Data Analysis'],
            'experience_years': 3,
            'education': 'Master of Science in Data Science',
            'career_goals': ['Data Science', 'Machine Learning Engineering']
        }
        
        # Analyze job match
        start_time = time.time()
        analysis = client.analyze_job_match(job_description, user_profile)
        analysis_time = time.time() - start_time
        
        print_lg(f"✅ Job analysis completed in {analysis_time:.2f} seconds")
        print_lg(f"📊 Match percentage: {analysis.get('match_percentage', 0)}%")
        print_lg(f"🎯 Recommendation: {analysis.get('recommendation', 'unknown')}")
        print_lg(f"✅ Matching skills: {', '.join(analysis.get('matching_skills', [])[:3])}")
        
        # Save analysis
        with open("test_outputs/test_job_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)
        
        print_lg("💾 Job analysis saved to test_outputs/test_job_analysis.json")
        return True
        
    except Exception as e:
        print_lg(f"❌ Job match analysis failed: {e}")
        return False

def test_connection_message():
    """Test AI-powered LinkedIn connection message generation."""
    print_lg("\n🤝 Testing connection message generation...")
    
    try:
        from modules.ai.groqConnections import groq_create_client
        from config.secrets import groq_api_key, groq_model
        
        client = groq_create_client(groq_api_key, groq_model)
        
        # Test target profile
        target_profile = {
            'name': 'Sarah Johnson',
            'title': 'Senior Software Engineer',
            'company': 'Google',
            'industry': 'Technology'
        }
        
        # Generate connection message
        start_time = time.time()
        message = client.generate_connection_message(target_profile, "job_search")
        generation_time = time.time() - start_time
        
        print_lg(f"✅ Connection message generated in {generation_time:.2f} seconds")
        print_lg(f"📝 Message length: {len(message)} characters")
        print_lg(f"💬 Message: {message}")
        
        # Save message
        with open("test_outputs/test_connection_message.txt", "w") as f:
            f.write(message)
        
        print_lg("💾 Connection message saved to test_outputs/test_connection_message.txt")
        return True
        
    except Exception as e:
        print_lg(f"❌ Connection message generation failed: {e}")
        return False

def performance_benchmark():
    """Run performance benchmark for all AI features."""
    print_lg("\n⚡ GROQ PERFORMANCE BENCHMARK")
    print_lg("="*50)
    
    tests = [
        ("Cover Letter Generation", test_cover_letter_generation),
        ("Resume Optimization", test_resume_optimization),
        ("Job Match Analysis", test_job_match_analysis),
        ("Connection Message", test_connection_message)
    ]
    
    total_start = time.time()
    passed_tests = 0
    
    for test_name, test_func in tests:
        print_lg(f"\n🧪 Running: {test_name}")
        if test_func():
            passed_tests += 1
        else:
            print_lg(f"❌ {test_name} failed")
    
    total_time = time.time() - total_start
    
    print_lg(f"\n🏁 BENCHMARK RESULTS:")
    print_lg(f"   ✅ Passed: {passed_tests}/{len(tests)} tests")
    print_lg(f"   ⚡ Total time: {total_time:.2f} seconds")
    print_lg(f"   📊 Average per test: {total_time/len(tests):.2f} seconds")
    
    if passed_tests == len(tests):
        print_lg("🏆 ALL TESTS PASSED! Groq integration is working perfectly!")
    else:
        print_lg(f"⚠️ {len(tests) - passed_tests} tests failed. Check configuration.")

def main():
    """Main test function."""
    print_lg("🚀 GROQ AI INTEGRATION TEST SUITE")
    print_lg("="*60)
    print_lg("🔑 Testing with your configured API key")
    print_lg(f"⏰ Started at: {datetime.now()}")
    
    # Create output directory
    os.makedirs("test_outputs", exist_ok=True)
    
    # Test basic connection first
    if not test_groq_connection():
        print_lg("❌ Basic connection failed. Please check your API key.")
        return
    
    # Run comprehensive tests
    performance_benchmark()
    
    print_lg(f"\n🏁 Testing completed at: {datetime.now()}")
    print_lg("📁 Test outputs saved in test_outputs/ directory")
    
    print_lg("\n🎯 NEXT STEPS:")
    print_lg("1. Review test outputs in test_outputs/ directory")
    print_lg("2. If all tests passed, your Groq integration is ready!")
    print_lg("3. Run the enhanced job bot: python run_stealth_bot.py")
    print_lg("4. Enjoy ultra-fast AI-powered job applications! 🚀")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_lg("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print_lg(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
