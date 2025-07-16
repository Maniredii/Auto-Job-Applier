# 🤖 Smart Auto Job Applier

An intelligent job application automation system that uses AI to customize resumes and cover letters, then automatically applies to relevant job postings with advanced bot detection evasion.

## 🌟 Features

- **🔍 Multi-Platform Job Scraping**: Scrapes jobs from 10+ platforms including LinkedIn, Indeed, Glassdoor, Naukri, Internshala, Unstop, AngelList, Dice, Monster, and ZipRecruiter
- **📄 AI-Powered Resume Optimization**: Uses Groq API to tailor resumes for each job
- **📝 Dynamic Cover Letter Generation**: Creates personalized cover letters using AI
- **🤖 Stealth Auto-Application**: Applies to jobs with advanced bot detection evasion
- **📊 Application Tracking**: Comprehensive dashboard to monitor applications
- **🛡️ Anti-Detection Measures**: Undetected browser automation with human-like behavior

## 🌐 Supported Platforms

The system supports job scraping and automated applications across multiple platforms:

### **Primary Platforms** (Fully Implemented)
- **LinkedIn** - Professional networking and job search
- **Indeed** - Global job search engine
- **Glassdoor** - Jobs with company reviews and salary insights
- **Naukri.com** - Leading Indian job portal

### **Specialized Platforms** (Fully Implemented)
- **Internshala** - Internships and entry-level opportunities
- **Unstop** (formerly Dare2Compete) - Competitions, hackathons, and jobs
- **AngelList/Wellfound** - Startup and tech company jobs
- **Dice** - Technology and IT jobs

### **Additional Platforms** (Fully Implemented)
- **Monster** - General job search platform
- **ZipRecruiter** - Quick apply job platform

Each platform includes:
- ✅ Intelligent job scraping with anti-detection
- ✅ Platform-specific search filters and criteria
- ✅ Automated login and session management
- ✅ Rate limiting and respectful scraping
- ✅ Platform-optimized application automation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Auto_job_applier_linkedIn-main

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required: GROQ_API_KEY
# Optional: LinkedIn credentials for automation
```

### 3. Run the Application

```bash
# Start the dashboard
python main.py --mode dashboard

# Or run specific modes
python main.py --mode scrape --job-title "Software Engineer" --location "Remote"
python main.py --mode apply --resume "./data/resumes/my_resume.pdf" --job-title "Python Developer"
```

## 📁 Project Structure

```
Auto_job_applier_linkedIn-main/
├── src/
│   ├── ai/                 # AI modules (Groq integration)
│   ├── scrapers/           # Job scraping modules
│   ├── parsers/            # Resume and job description parsers
│   ├── automation/         # Browser automation and form filling
│   ├── database/           # Database models and operations
│   ├── ui/                 # Streamlit dashboard
│   └── utils/              # Utility functions
├── data/
│   ├── resumes/            # User resumes
│   ├── cover_letters/      # Generated cover letters
│   └── applications/       # Application tracking data
├── logs/                   # Application logs
├── temp/                   # Temporary files
├── browser_profiles/       # Browser profiles for stealth mode
├── config.py              # Configuration management
├── main.py                # Main application entry point
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for AI features | ✅ |
| `LINKEDIN_EMAIL` | LinkedIn email for automation | ❌ |
| `LINKEDIN_PASSWORD` | LinkedIn password | ❌ |
| `LINKEDIN_PHONE` | LinkedIn phone number | ❌ |
| `MAX_APPLICATIONS_PER_DAY` | Daily application limit | ❌ |
| `DELAY_BETWEEN_APPLICATIONS` | Delay between applications (seconds) | ❌ |

### Application Settings

- **Stealth Mode**: Advanced bot detection evasion
- **Custom Browser Profiles**: Persistent browser sessions
- **Smart Delays**: Human-like timing patterns
- **Form Auto-Fill**: Intelligent form completion

## 🎯 Usage Modes

### 1. Dashboard Mode (Default)
```bash
python main.py --mode dashboard
```
Interactive web interface for managing applications, viewing statistics, and configuring settings.

### 2. Scraping Mode
```bash
python main.py --mode scrape --job-title "Data Scientist" --location "New York"
```
Scrape job listings without applying.

### 3. Auto-Apply Mode
```bash
python main.py --mode apply --resume "./my_resume.pdf" --job-title "Software Engineer" --max-applications 10
```
Automatically apply to jobs with AI-optimized resumes and cover letters.

### 4. Test Mode
```bash
python main.py --mode test
```
Run system tests and validation checks.

## 🛡️ Anti-Detection Features

- **Undetected Chrome Driver**: Bypasses basic bot detection
- **Human-like Behavior**: Random delays, mouse movements, typing patterns
- **Browser Fingerprinting**: Consistent browser profiles
- **Session Management**: Persistent login sessions
- **Captcha Handling**: Manual intervention prompts

## 📊 AI Features

### Resume Optimization
- Analyzes job descriptions to identify key requirements
- Tailors resume content to match job keywords
- Maintains factual accuracy while optimizing presentation
- Preserves original formatting and structure

### Cover Letter Generation
- Creates personalized cover letters for each application
- Incorporates company research and job-specific details
- Maintains professional tone and structure
- Highlights relevant experience and skills

## 🔒 Security & Privacy

- **Local Data Storage**: All data stored locally
- **Encrypted Credentials**: Secure credential management
- **No Data Sharing**: No external data transmission except API calls
- **Audit Logs**: Comprehensive logging for transparency

## 🧪 Testing

```bash
# Run all tests
python main.py --mode test

# Run specific test modules
pytest src/tests/test_resume_parser.py
pytest src/tests/test_job_scraper.py
```

## 📈 Monitoring & Analytics

- Application success rates
- Resume optimization effectiveness
- Response tracking
- Performance metrics
- Error monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## ⚠️ Disclaimer

This tool is for educational and personal use only. Users are responsible for:
- Complying with platform terms of service
- Ensuring accuracy of application materials
- Respecting rate limits and anti-spam policies
- Using the tool ethically and responsibly

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Join our community discussions

---

**Built with ❤️ using Groq AI, Python, and modern automation technologies**
