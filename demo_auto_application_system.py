"""
Demo script to test the Auto Application System functionality
"""

import asyncio
import json
from pathlib import Path
from src.automation.auto_application_system import ApplicationManager, ApplicationConfig, ApplicationStatus

async def demo_basic_auto_application():
    """Demonstrate basic auto application functionality"""
    print("=== Auto Application System Demo ===\n")
    
    # Initialize application manager
    manager = ApplicationManager(
        resume_path="sample_resume.pdf",  # You would use your actual resume
        output_directory="temp/applications"
    )
    
    print("🤖 CONFIGURATION:")
    
    # Create configuration
    config = manager.create_config(
        job_titles=["Software Engineer", "Python Developer"],
        locations=["Remote", "San Francisco, CA"],
        max_applications_per_day=5,  # Limited for demo
        platforms=["linkedin"],
        min_match_score=0.6,
        resume_strategy="moderate",
        cover_letter_template="professional",
        personalization_level="high",
        apply_immediately=False,  # Don't auto-apply for demo
        review_before_apply=True
    )
    
    print(f"   Job Titles: {', '.join(config.job_titles)}")
    print(f"   Locations: {', '.join(config.locations)}")
    print(f"   Max Applications/Day: {config.max_applications_per_day}")
    print(f"   Min Match Score: {config.min_match_score:.1%}")
    print(f"   Resume Strategy: {config.resume_strategy}")
    print(f"   Cover Letter Template: {config.cover_letter_template}")
    
    print(f"\n🔍 Starting job search and application creation...")
    
    try:
        # Run auto application (creation only, no submission)
        results = await manager.run_with_review(config)
        
        print(f"\n✅ APPLICATION CYCLE COMPLETED:")
        print(f"   Jobs Found: {results['session_stats']['jobs_found']}")
        print(f"   Jobs Analyzed: {results['session_stats']['jobs_analyzed']}")
        print(f"   Applications Created: {results['session_stats']['applications_created']}")
        
        if results.get('pending_applications'):
            print(f"\n📋 PENDING APPLICATIONS FOR REVIEW:")
            for i, app in enumerate(results['pending_applications'][:5], 1):
                print(f"   {i}. {app['job_title']} at {app['company_name']}")
                print(f"      Match Score: {app['match_score']:.1%}")
                print(f"      Job ID: {app['job_id']}")
                print(f"      URL: {app['job_url'][:60]}...")
                print()
        
        # Get session summary
        summary = manager.get_application_summary()
        print(f"📊 SESSION STATISTICS:")
        print(f"   Total Applications: {summary['applications_in_session']}")
        print(f"   Daily Count: {summary['daily_application_count']}")
        print(f"   Session Duration: Started at {summary['session_start']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Auto application failed: {str(e)}")
        return None

async def demo_application_review_and_approval():
    """Demonstrate application review and approval process"""
    print("\n=== Application Review & Approval Demo ===\n")
    
    # This would typically follow the basic demo
    print("📝 MANUAL REVIEW PROCESS:")
    print("   1. Review generated applications")
    print("   2. Check resume modifications")
    print("   3. Review cover letters")
    print("   4. Approve or reject applications")
    
    # Simulate approval process
    print(f"\n✅ SIMULATED APPROVAL PROCESS:")
    
    # In a real scenario, you would:
    # 1. Review the pending applications
    # 2. Select which ones to approve
    # 3. Call manager.approve_and_submit(selected_job_ids)
    
    sample_job_ids = ["TechCorp_Software_Engineer_123", "DataInc_Python_Developer_456"]
    
    print(f"   Approving applications: {sample_job_ids}")
    print(f"   ✅ Application 1: Approved and submitted")
    print(f"   ✅ Application 2: Approved and submitted")
    
    # Simulate results
    approval_results = {
        "TechCorp_Software_Engineer_123": True,
        "DataInc_Python_Developer_456": True
    }
    
    return approval_results

async def demo_configuration_options():
    """Demonstrate different configuration options"""
    print("\n=== Configuration Options Demo ===\n")
    
    manager = ApplicationManager(
        resume_path="sample_resume.pdf",
        output_directory="temp/applications"
    )
    
    # Conservative configuration
    conservative_config = manager.create_config(
        job_titles=["Senior Software Engineer"],
        locations=["Remote"],
        max_applications_per_day=3,
        min_match_score=0.8,  # High threshold
        resume_strategy="conservative",
        cover_letter_template="professional",
        personalization_level="medium",
        exclude_companies=["Company A", "Company B"],
        exclude_keywords=["unpaid", "internship"]
    )
    
    print("🛡️ CONSERVATIVE CONFIGURATION:")
    print(f"   High match threshold: {conservative_config.min_match_score:.1%}")
    print(f"   Conservative resume changes")
    print(f"   Limited daily applications: {conservative_config.max_applications_per_day}")
    print(f"   Excluded companies: {conservative_config.exclude_companies}")
    
    # Aggressive configuration
    aggressive_config = manager.create_config(
        job_titles=["Software Engineer", "Full Stack Developer", "Backend Engineer"],
        locations=["Remote", "San Francisco", "New York", "Seattle"],
        max_applications_per_day=25,
        min_match_score=0.5,  # Lower threshold
        resume_strategy="aggressive",
        cover_letter_template="enthusiastic",
        personalization_level="high",
        apply_immediately=True,  # Auto-apply
        review_before_apply=False
    )
    
    print(f"\n🚀 AGGRESSIVE CONFIGURATION:")
    print(f"   Lower match threshold: {aggressive_config.min_match_score:.1%}")
    print(f"   Aggressive resume optimization")
    print(f"   High daily applications: {aggressive_config.max_applications_per_day}")
    print(f"   Multiple job titles: {len(aggressive_config.job_titles)}")
    print(f"   Auto-apply enabled: {aggressive_config.apply_immediately}")
    
    # Targeted configuration
    targeted_config = manager.create_config(
        job_titles=["Machine Learning Engineer"],
        locations=["San Francisco, CA"],
        max_applications_per_day=10,
        min_match_score=0.7,
        resume_strategy="moderate",
        cover_letter_template="technical",
        personalization_level="high",
        min_salary=150000,
        max_experience_years=8
    )
    
    print(f"\n🎯 TARGETED CONFIGURATION:")
    print(f"   Specific role: {targeted_config.job_titles[0]}")
    print(f"   Specific location: {targeted_config.locations[0]}")
    print(f"   Salary requirement: ${targeted_config.min_salary:,}+")
    print(f"   Technical cover letter template")
    
    return {
        'conservative': conservative_config,
        'aggressive': aggressive_config,
        'targeted': targeted_config
    }

async def demo_application_tracking():
    """Demonstrate application tracking and reporting"""
    print("\n=== Application Tracking Demo ===\n")
    
    # Simulate application data
    sample_applications = [
        {
            'job_id': 'TechCorp_SWE_001',
            'job_title': 'Senior Software Engineer',
            'company_name': 'TechCorp Inc.',
            'match_score': 0.85,
            'status': 'applied',
            'created_at': '2024-01-15T10:30:00',
            'applied_at': '2024-01-15T11:45:00'
        },
        {
            'job_id': 'DataInc_ML_002',
            'job_title': 'Machine Learning Engineer',
            'company_name': 'DataInc Solutions',
            'match_score': 0.78,
            'status': 'in_progress',
            'created_at': '2024-01-15T14:20:00',
            'applied_at': None
        },
        {
            'job_id': 'StartupXYZ_FS_003',
            'job_title': 'Full Stack Developer',
            'company_name': 'StartupXYZ',
            'match_score': 0.65,
            'status': 'failed',
            'created_at': '2024-01-15T16:10:00',
            'applied_at': None
        }
    ]
    
    print("📊 APPLICATION TRACKING DASHBOARD:")
    print(f"{'Job Title':<25} {'Company':<20} {'Score':<8} {'Status':<12} {'Applied'}")
    print("-" * 80)
    
    for app in sample_applications:
        applied_status = "✅ Yes" if app['applied_at'] else "⏳ No"
        print(f"{app['job_title']:<25} {app['company_name']:<20} "
              f"{app['match_score']:<8.1%} {app['status']:<12} {applied_status}")
    
    # Statistics
    total_apps = len(sample_applications)
    applied_apps = len([app for app in sample_applications if app['applied_at']])
    avg_score = sum(app['match_score'] for app in sample_applications) / total_apps
    
    print(f"\n📈 STATISTICS:")
    print(f"   Total Applications: {total_apps}")
    print(f"   Successfully Applied: {applied_apps}")
    print(f"   Success Rate: {applied_apps/total_apps:.1%}")
    print(f"   Average Match Score: {avg_score:.1%}")
    
    # Status breakdown
    status_counts = {}
    for app in sample_applications:
        status = app['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n📋 STATUS BREAKDOWN:")
    for status, count in status_counts.items():
        print(f"   {status.title()}: {count}")

async def demo_export_functionality():
    """Demonstrate export and reporting functionality"""
    print("\n=== Export & Reporting Demo ===\n")
    
    # Simulate export process
    output_dir = Path("temp/reports")
    output_dir.mkdir(exist_ok=True)
    
    print("💾 EXPORT OPTIONS:")
    
    # Application report
    report_file = output_dir / "applications_report.json"
    print(f"   📄 Applications Report: {report_file}")
    
    # Session summary
    session_file = output_dir / "session_summary.json"
    print(f"   📊 Session Summary: {session_file}")
    
    # Individual application folders
    print(f"   📁 Individual Applications:")
    print(f"      - temp/applications/TechCorp_SWE_001/")
    print(f"        ├── resume.txt")
    print(f"        ├── cover_letter.txt")
    print(f"        ├── application_summary.json")
    print(f"        └── resume_analysis.json")
    
    # Create sample report
    sample_report = {
        "generated_at": "2024-01-15T18:00:00",
        "session_statistics": {
            "jobs_found": 25,
            "jobs_analyzed": 15,
            "applications_created": 8,
            "applications_submitted": 5,
            "session_duration": "2 hours 30 minutes"
        },
        "top_applications": [
            {
                "job_title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "match_score": 0.85,
                "status": "applied"
            },
            {
                "job_title": "Machine Learning Engineer", 
                "company": "DataInc Solutions",
                "match_score": 0.78,
                "status": "in_progress"
            }
        ]
    }
    
    with open(report_file, 'w') as f:
        json.dump(sample_report, f, indent=2)
    
    print(f"\n✅ Sample report generated: {report_file}")

async def main():
    """Main demo function"""
    print("🚀 Starting Auto Application System Demo")
    print("=" * 70)
    
    try:
        # Demo 1: Basic auto application
        basic_results = await demo_basic_auto_application()
        
        # Demo 2: Application review and approval
        approval_results = await demo_application_review_and_approval()
        
        # Demo 3: Configuration options
        config_options = await demo_configuration_options()
        
        # Demo 4: Application tracking
        await demo_application_tracking()
        
        # Demo 5: Export functionality
        await demo_export_functionality()
        
        print("\n" + "=" * 70)
        print("✅ Auto Application System Demo completed successfully!")
        
        print("\nKey Features Demonstrated:")
        print("• Automated job search and filtering")
        print("• AI-powered resume modification for each job")
        print("• Personalized cover letter generation")
        print("• Application review and approval workflow")
        print("• Comprehensive tracking and reporting")
        print("• Flexible configuration options")
        print("• Export and documentation capabilities")
        
        print("\nNext steps:")
        print("1. Configure with your actual resume and credentials")
        print("2. Set up LinkedIn login credentials")
        print("3. Customize job search criteria")
        print("4. Run with review mode first to test")
        print("5. Enable auto-apply for trusted configurations")
        
        print("\n⚠️ Important Notes:")
        print("• Always review applications before submission")
        print("• Respect platform rate limits and terms of service")
        print("• Monitor application success rates")
        print("• Adjust match score thresholds based on results")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Make sure all dependencies are installed and configured.")

if __name__ == "__main__":
    asyncio.run(main())
