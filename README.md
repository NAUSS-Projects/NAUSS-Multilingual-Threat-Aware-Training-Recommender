# Multilingual Threat-Aware Training Recommender

A sophisticated AI-powered system that analyzes your past training history and compares it with recent external news or threat reports to recommend new subject areas or training courses. Supports both Arabic and English languages with cross-lingual semantic analysis.

## Features

### 🌍 Multilingual Support
- **Arabic & English**: Full support for both languages
- **Cross-lingual Analysis**: Compare Arabic training records with English news and vice versa
- **Language Detection**: Automatic detection and processing of content language

### 🛡️ Threat-Aware Intelligence
- **Real-time News Analysis**: Scrape and analyze recent security news
- **Semantic Similarity**: Advanced AI models for content understanding
- **Context-Aware Recommendations**: Courses tailored to emerging threats

### 🤖 AI-Powered Recommendations
- **Ollama Integration**: Uses phi4 model for intelligent course suggestions
- **Multiple Recommendation Types**: New courses, outdated course updates, and new subject areas
- **Confidence Scoring**: Recommendations with reasoning and confidence levels

### 📊 Comprehensive Analysis
- **Excel Integration**: Upload training history in Excel format
- **Flexible Input**: Support for URLs and direct text input
- **Structured Output**: JSON-formatted recommendations for easy integration

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running with phi4 model:
   ```bash
   # Install Ollama (visit https://ollama.com for installation)
   ollama pull phi4
   ```
3. **Git** for cloning the repository

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd threat_aware_training_recommender
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   ```bash
   # Copy environment template
   copy .env.example .env    # Windows
   cp .env.example .env      # Linux/Mac
   
   # Edit .env file with your settings
   ```

5. **Create Required Directories**:
   ```bash
   mkdir uploads model_cache
   ```

### Running the Application

1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **Run the Flask Application**:
   ```bash
   python app.py
   ```

3. **Access the Application**:
   Open your browser to `http://localhost:5000`

## Usage Guide

### 1. Prepare Your Training Data

Create an Excel file with the following columns:
- **Subject Area** (المجال/المنطقة الموضوع)
- **Training name** (اسم التدريب/اسم الدورة)  
- **Start Date** (تاريخ البداية)
- **End Date** (تاريخ النهاية)

**Example Excel Structure:**
```
Subject Area          | Training name              | Start Date | End Date
الأمن السيبراني         | أساسيات الحماية السيبرانية     | 2023-01-15 | 2023-01-20
Cybersecurity        | Network Security Basics   | 2023-02-10 | 2023-02-15
```

### 2. Gather Recent News

Provide recent news through one or both methods:

**Method 1: URLs**
```
https://example.com/cybersecurity-news
https://another-site.com/security-alert
```

**Method 2: Direct Text**
```
Recent malware attacks targeting healthcare systems have increased by 40%...
```

### 3. Process and Get Recommendations

1. Upload your Excel file
2. Provide news sources
3. Click "Generate Recommendations"
4. Review the AI-generated course suggestions

### 4. Export Results

- **JSON Export**: Download structured recommendations
- **Print**: Print-friendly format
- **Web Sharing**: Share results via URL

## API Usage

### POST /api/recommend

**Request:**
```bash
curl -X POST http://localhost:5000/api/recommend \
  -F "file=@training_data.xlsx" \
  -F "urls=https://example.com/news" \
  -F "news_text=Recent security developments..."
```

**Response:**
```json
{
  "recommendations": [
    {
      "subject_area": "الأمن السيبراني",
      "suggested_courses": [
        {
          "course_name": "تحليل البرمجيات الخبيثة المتقدم",
          "reason": "تشابه مع أخبار حديثة عن برمجية خبيثة جديدة",
          "status": "new_course"
        }
      ]
    }
  ],
  "errors": []
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-key` |
| `SIMILARITY_THRESHOLD` | Minimum similarity score | `0.3` |
| `MULTILINGUAL_MODEL` | Sentence transformer model | `LaBSE` |
| `OLLAMA_HOST` | Ollama server host | `localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `phi4` |
| `REQUEST_TIMEOUT` | News scraping timeout | `10` |

### Advanced Configuration

**Custom Models:**
```env
MULTILINGUAL_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**Performance Tuning:**
```env
CACHE_MODELS=True
MODEL_CACHE_DIR=./model_cache
SIMILARITY_THRESHOLD=0.4
```

## Architecture

### Components

1. **Excel Processing (`app/models/excel.py`)**
   - Multilingual column mapping
   - Language detection
   - Data validation

2. **News Scraping (`app/scrapers/news.py`)**
   - URL content extraction
   - Language detection
   - Content cleaning

3. **Similarity Engine (`app/models/similarity.py`)**
   - Multilingual embeddings
   - Cross-lingual similarity
   - Semantic search

4. **Ollama Integration (`app/models/ollama_client.py`)**
   - Course generation
   - Context-aware prompts
   - JSON response parsing

5. **Main Recommender (`app/models/recommender.py`)**
   - Workflow orchestration
   - Result formatting
   - Error handling

### Data Flow

```
Excel Upload → Language Detection → Subject Extraction
                                         ↓
News Sources → Content Scraping → Language Detection
                                         ↓
                            Similarity Analysis
                                         ↓
                            Ollama AI Processing
                                         ↓
                         Structured Recommendations
```

## Development

### Project Structure

```
threat_aware_training_recommender/
├── app/
│   ├── models/           # Core processing modules
│   ├── scrapers/         # Web scraping modules
│   ├── templates/        # HTML templates
│   ├── static/           # CSS, JS, assets
│   ├── __init__.py       # Flask app factory
│   └── routes.py         # API routes
├── config/
│   └── config.py         # Configuration classes
├── tests/                # Test files
├── uploads/              # File upload directory
├── app.py               # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app
```

### Adding New Features

1. **New Language Support**: Extend language detection in `excel.py` and `news.py`
2. **Custom Models**: Add model configurations in `config.py`
3. **New Input Sources**: Extend scraping capabilities in `scrapers/`
4. **Enhanced UI**: Modify templates and static assets

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Start Ollama if needed
   ollama serve
   ```

2. **Model Loading Issues**:
   ```bash
   # Clear model cache
   rm -rf ./model_cache
   
   # Reinstall sentence-transformers
   pip uninstall sentence-transformers
   pip install sentence-transformers
   ```

3. **Excel Reading Errors**:
   - Ensure Excel file has correct column names
   - Check file format (xlsx/xls)
   - Verify file isn't corrupted

4. **Memory Issues**:
   - Reduce `MAX_NEWS_DOCUMENTS` in config
   - Use smaller language models
   - Increase system RAM or use cloud deployment

### Performance Optimization

1. **Model Caching**:
   ```env
   CACHE_MODELS=True
   MODEL_CACHE_DIR=./model_cache
   ```

2. **Batch Processing**:
   - Process multiple files in background
   - Implement queuing system
   - Use celery for async processing

3. **Resource Management**:
   - Monitor memory usage
   - Implement connection pooling
   - Use production WSGI server (gunicorn)

## Deployment

### Production Deployment

1. **Environment Setup**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   ```

2. **Using Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Docker Deployment**:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

4. **Nginx Configuration**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Cloud Deployment Options

- **AWS**: EC2 with ELB and RDS
- **Google Cloud**: App Engine or Compute Engine
- **Azure**: App Service or Virtual Machines
- **Heroku**: Direct deployment with buildpacks

## Security Considerations

1. **File Upload Security**:
   - File type validation
   - Size limits
   - Virus scanning (recommended)

2. **Input Validation**:
   - URL validation
   - Content filtering
   - SQL injection prevention

3. **Data Privacy**:
   - Secure file storage
   - Data encryption at rest
   - GDPR compliance considerations

## Support and Contributing

### Getting Help

1. **Issues**: Open GitHub issues for bugs
2. **Discussions**: Use GitHub discussions for questions
3. **Documentation**: Check inline code documentation

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

### License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-02  
**Minimum Requirements**: Python 3.8+, 4GB RAM, Ollama with phi4