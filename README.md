# 🎯 Resume Analysis System
## 🌐 Live Demo  
**Deployed on Render**: (https://ai-resume-analyzer-l7ei.onrender.com)

An intelligent Flask web application that automatically analyzes resumes against job descriptions using AI, provides matching scores, and sends personalized email responses to candidates. Built with LangChain, Groq AI, and modern web technologies.

## ✨ Key Features

- **📄 Bulk PDF Processing**: Upload and analyze multiple resumes simultaneously
- **🤖 AI-Powered Analysis**: Uses Groq's Llama models for intelligent resume evaluation
- **📊 Detailed Scoring**: Provides matching percentages and detailed feedback
- **📧 Automated Email Responses**: Sends personalized emails to candidates based on their scores
- **📈 Analytics Dashboard**: View comprehensive analysis results and statistics
- **🔒 Secure File Handling**: Safe file upload and processing with automatic cleanup
- **💾 Data Export**: Download results as CSV files for further processing

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key (free at [https://console.groq.com/](https://console.groq.com/))
- Gmail account or SMTP credentials for email functionality

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd resume-analysis-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (Optional)
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   PORT=5000
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

### Dependencies (requirements.txt)

```txt
Flask>=2.3.0
pandas>=1.5.0
PyMuPDF>=1.23.0
yagmail>=0.15.0
python-dotenv>=1.0.0
langchain-core>=0.1.0
langchain-groq>=0.1.0
Werkzeug>=2.3.0
pathlib
```

## 📖 How to Use

### Step 1: Setup Configuration
1. **Get Groq API Key**: Visit [https://console.groq.com/](https://console.groq.com/) and create a free account
2. **Prepare Job Description**: Write a clear, detailed job description
3. **Gather Resumes**: Collect PDF resumes you want to analyze

### Step 2: Configure Analysis
1. **Enter Job Description**: Paste the job requirements in the text area
2. **Add API Key**: Enter your Groq API key
3. **Select Model**: Choose from available Llama models:
   - `llama3-70b-8192` (Recommended - Most accurate)
   - `llama3-8b-8192` (Faster processing)
   - `mixtral-8x7b-32768` (Alternative option)
4. **Set Temperature**: Adjust creativity (0.0 = consistent, 1.0 = creative)

### Step 3: Upload and Analyze
1. **Upload PDFs**: Select multiple resume files (up to 50MB total)
2. **Start Analysis**: Click "Analyze Resumes"
3. **Wait for Processing**: Progress will be shown for each resume
4. **View Results**: Automatically redirected to results page

### Step 4: Review Results
- **Summary Statistics**: See total candidates, perfect matches, okay matches
- **Individual Scores**: View detailed analysis for each candidate
- **Sorting**: Results automatically sorted by matching score
- **Export Data**: Download results as CSV file

### Step 5: Send Emails (Optional)
1. **Configure Email**: Enter sender Gmail credentials
2. **Automated Responses**: 
   - Candidates with 70%+ scores get acceptance emails
   - Candidates below 70% get rejection emails with improvement suggestions
3. **Bulk Send**: All emails sent automatically

## 🎯 Analysis Output

For each resume, the system provides:

```json
{
  "Name": "Candidate Name",
  "email": "candidate@email.com",
  "is_perfect": true/false,
  "is_okay": true/false,
  "Matching Score in percentage": "85%",
  "strong zone": "Python, Machine Learning, Data Science",
  "Lack of Knowledge": "Cloud platforms, DevOps experience"
}
```

### Scoring Criteria
- **90-100%**: Perfect match - All requirements met
- **70-89%**: Good match - Most requirements met
- **50-69%**: Partial match - Some requirements met
- **Below 50%**: Poor match - Major gaps in requirements

## 📧 Email Templates

### Acceptance Email (Score ≥ 70%)
```
Hello [Candidate Name],

Thank you for your application for the Machine Learning position 
in our company. We are pleased to consider you for the further process.

Best Regards,
HR Team
```

### Rejection Email (Score < 70%)
```
Hello [Candidate Name],

Thank you for your application for the Machine Learning position 
in our company. Unfortunately, we cannot consider you for the 
further process. We found some areas that don't match with our 
requirements:

[Specific areas for improvement]

You can upgrade yourself and try later.

Best Regards,
HR Team
```

## 🔧 Technical Architecture

### Core Components
- **Flask Backend**: Web server and API endpoints
- **LangChain Integration**: Prompt management and LLM orchestration
- **Groq AI**: Advanced language model processing
- **PyMuPDF**: PDF text extraction with link preservation
- **Yagmail**: Simplified email sending
- **Pandas**: Data processing and CSV operations

### File Structure
```
resume-analysis-system/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── index.html        # Upload page
│   ├── results.html      # Results dashboard
│   ├── 404.html          # Error pages
│   └── 500.html
├── static/               # CSS, JS, images
├── uploads/              # Temporary file storage
├── results/              # Analysis results storage
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md            # This file
```

### Security Features
- **File Size Limits**: 50MB maximum upload size
- **Secure Filenames**: Prevents directory traversal attacks
- **Session Management**: Secure session handling
- **Input Validation**: Comprehensive form validation
- **Automatic Cleanup**: Temporary files automatically removed

## ⚙️ Configuration Options

### Environment Variables
```env
SECRET_KEY=your-flask-secret-key
PORT=5000
MAX_CONTENT_LENGTH=52428800  # 50MB in bytes
```

### Model Options
- **llama3-70b-8192**: Best accuracy, slower processing
- **llama3-8b-8192**: Faster processing, good accuracy
- **mixtral-8x7b-32768**: Alternative model with different strengths

### Temperature Settings
- **0.0**: Most consistent, factual responses
- **0.3**: Balanced creativity and consistency (recommended)
- **0.7**: More creative but less predictable
- **1.0**: Maximum creativity, less consistent

## 🚨 Troubleshooting

### Common Issues

**1. "Error initializing LLM"**
- ✅ Verify your Groq API key is correct
- ✅ Check internet connection
- ✅ Ensure API key has sufficient credits
- ✅ Try a different model option

**2. "Could not extract text from PDF"**
- ✅ Ensure PDFs are text-based (not scanned images)
- ✅ Check if PDFs are password-protected
- ✅ Try with different PDF files
- ✅ Use PDFs with selectable text

**3. "Email sending failed"**
- ✅ Enable "Less secure app access" in Gmail settings
- ✅ Use App Passwords for Gmail accounts with 2FA
- ✅ Check email credentials are correct
- ✅ Verify internet connection

**4. "File upload errors"**
- ✅ Check file size (must be under 50MB total)
- ✅ Ensure files are PDF format
- ✅ Try uploading fewer files at once
- ✅ Check disk space availability

**5. "Analysis results missing"**
- ✅ Wait for processing to complete
- ✅ Check browser console for errors
- ✅ Refresh the page
- ✅ Try re-running analysis

### Performance Optimization

**For Large Batches:**
- Process resumes in smaller batches (5-10 at a time)
- Allow extra time for processing
- Monitor system resources

**For Better Accuracy:**
- Use detailed, specific job descriptions
- Include required skills, experience levels, and qualifications
- Use consistent formatting in job descriptions

**For Faster Processing:**
- Use llama3-8b-8192 model for speed
- Set lower temperature values (0.0-0.3)
- Process during off-peak hours

## 📊 API Endpoints

### Main Routes
- `GET /` - Main upload page
- `POST /upload` - Process resume uploads
- `GET /results` - View analysis results
- `GET /download_results` - Download CSV results
- `POST /send_emails` - Send candidate emails

### Response Formats
All API endpoints return JSON responses:
```json
{
  "success": true/false,
  "message": "Status message",
  "results": [...],  // For successful analysis
  "error": "Error message"  // For failures
}
```

## 🔒 Privacy & Security

### Data Handling
- **Temporary Storage**: Files automatically deleted after processing
- **No Permanent Storage**: Resume content not stored permanently
- **Session Security**: Secure session management
- **Input Sanitization**: All inputs validated and sanitized

### Email Security
- **Credentials**: Email credentials not stored permanently
- **Session Only**: Credentials exist only during active session
- **SSL/TLS**: All email communications encrypted

## 🚀 Deployment Options

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker (create Dockerfile)
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

### Cloud Platforms
- **Heroku**: Ready for deployment with Procfile
- **AWS EC2**: Compatible with standard Linux deployments
- **Google Cloud**: Works with App Engine and Compute Engine
- **Azure**: Compatible with App Service

## 📈 Future Enhancements

### Planned Features
- **Multi-language Support**: Support for non-English resumes
- **Advanced Analytics**: More detailed matching insights
- **Integration APIs**: Connect with ATS systems
- **Custom Email Templates**: User-customizable email templates
- **Batch Processing Queue**: Handle very large resume batches
- **Database Integration**: Persistent storage options

### Customization Options
- **Custom Scoring Algorithms**: Implement domain-specific scoring
- **Additional File Formats**: Support for DOC, DOCX files
- **Advanced Email Features**: HTML emails, attachments
- **User Management**: Multi-user support with authentication

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed correctly
3. Ensure API keys are valid
4. Create an issue in the repository

---

**Happy Resume Analyzing! 🎯📊**

## 🔧 Quick Setup Script

For rapid deployment, save this as `setup.sh`:

```bash
#!/bin/bash
echo "Setting up Resume Analysis System..."

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads results templates static

# Set environment variables
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')" > .env
echo "PORT=5000" >> .env

echo "Setup complete! Run 'python app.py' to start the application."
```

Run with: `bash setup.sh`
