# multilingual threat-aware training recommender

a system that analyzes your past training history and compares it with recent news or threat reports to recommend new subject areas or training courses. it supports both arabic and english languages with cross-lingual semantic analysis.

## features

- multilingual support for arabic and english
- real-time news analysis and semantic similarity
- ai-powered recommendations using ollama's phi4 model
- excel integration for training history uploads
- structured json output for easy integration

## prerequisites

- python 3.10.13
- ollama installed and running with the phi4 model
- git for cloning the repository

## setup

### install pyenv (if needed)

if you don’t have python 3.10.13 installed, use pyenv:

for mac:
```bash
brew update
brew install pyenv
```

for ubuntu:
```bash
curl https://pyenv.run | bash
```

### install python 3.10.13

```bash
pyenv install 3.10.13
pyenv global 3.10.13
```

### clone the repository

```bash
git clone <repository-url>
cd threat_aware_training_recommender
```

### create virtual environment

```bash
python -m venv venv

# activate the virtual environment
source venv/bin/activate
```

### install dependencies

```bash
pip install -r requirements.txt
```

### environment configuration

```bash
# copy environment template
cp .env.example .env

# edit .env file with your settings
```

### create required directories

```bash
mkdir uploads model_cache
```

## running the application

1. **start ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **run the flask application**:
   ```bash
   python app.py
   ```

3. **access the application**:
   open your browser to `http://localhost:5000`

## usage guide

### 1. prepare your training data

create an excel file with the following columns:
- **subject area** (المجال/المنطقة الموضوع)
- **training name** (اسم التدريب/اسم الدورة)  
- **start date** (تاريخ البداية)
- **end date** (تاريخ النهاية)

**example excel structure:**
```
subject area          | training name              | start date | end date
الأمن السيبراني         | أساسيات الحماية السيبرانية     | 2023-01-15 | 2023-01-20
cybersecurity        | network security basics   | 2023-02-10 | 2023-02-15
```

### 2. gather recent news

provide recent news through one or both methods:

**method 1: urls**
```
https://example.com/cybersecurity-news
https://another-site.com/security-alert
```

**method 2: direct text**
```
recent malware attacks targeting healthcare systems have increased by 40%...
```

### 3. process and get recommendations

1. upload your excel file
2. provide news sources
3. click "generate recommendations"
4. review the ai-generated course suggestions

### 4. export results

- **json export**: download structured recommendations
- **print**: print-friendly format
- **web sharing**: share results via url

## api usage

### post /api/recommend

**request:**
```bash
curl -X POST http://localhost:5000/api/recommend \
  -F "file=@training_data.xlsx" \
  -F "urls=https://example.com/news" \
  -F "news_text=Recent security developments..."
```

**response:**
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

## configuration

### environment variables

| variable | description | default |
|----------|-------------|---------|
| `SECRET_KEY` | flask secret key | `dev-key` |
| `SIMILARITY_THRESHOLD` | minimum similarity score | `0.3` |
| `MULTILINGUAL_MODEL` | sentence transformer model | `LaBSE` |
| `OLLAMA_HOST` | ollama server host | `localhost:11434` |
| `OLLAMA_MODEL` | ollama model name | `phi4` |
| `REQUEST_TIMEOUT` | news scraping timeout | `10` |

### advanced configuration

**custom models:**
```env
MULTILINGUAL_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**performance tuning:**
```env
CACHE_MODELS=True
MODEL_CACHE_DIR=./model_cache
SIMILARITY_THRESHOLD=0.4
```

## architecture

### components

1. **excel processing (`app/models/excel.py`)**
   - multilingual column mapping
   - language detection
   - data validation

2. **news scraping (`app/scrapers/news.py`)**
   - url content extraction
   - language detection
   - content cleaning

3. **similarity engine (`app/models/similarity.py`)**
   - multilingual embeddings
   - cross-lingual similarity
   - semantic search

4. **ollama integration (`app/models/ollama_client.py`)**
   - course generation
   - context-aware prompts
   - json response parsing

5. **main recommender (`app/models/recommender.py`)**
   - workflow orchestration
   - result formatting
   - error handling

### data flow

```
excel upload → language detection → subject extraction
                                         ↓
news sources → content scraping → language detection
                                         ↓
                            similarity analysis
                                         ↓
                            ollama ai processing
                                         ↓
                         structured recommendations
```

## development

### project structure

```
threat_aware_training_recommender/
├── app/
│   ├── models/           # core processing modules
│   ├── scrapers/         # web scraping modules
│   ├── templates/        # html templates
│   ├── static/           # css, js, assets
│   ├── __init__.py       # flask app factory
│   └── routes.py         # api routes
├── config/
│   └── config.py         # configuration classes
├── tests/                # test files
├── uploads/              # file upload directory
├── app.py               # application entry point
├── requirements.txt     # python dependencies
└── README.md           # this file
```

### running tests

```bash
# install test dependencies
pip install pytest pytest-cov

# run tests
pytest tests/

# run with coverage
pytest tests/ --cov=app
```

### adding new features

1. **new language support**: extend language detection in `excel.py` and `news.py`
2. **custom models**: add model configurations in `config.py`
3. **new input sources**: extend scraping capabilities in `scrapers/`
4. **enhanced ui**: modify templates and static assets

## troubleshooting

### common issues

1. **ollama connection error**:
   ```bash
   # check if ollama is running
   curl http://localhost:11434/api/tags
   
   # start ollama if needed
   ollama serve
   ```

2. **model loading issues**:
   ```bash
   # clear model cache
   rm -rf ./model_cache
   
   # reinstall sentence-transformers
   pip uninstall sentence-transformers
   pip install sentence-transformers
   ```

3. **excel reading errors**:
   - ensure excel file has correct column names
   - check file format (xlsx/xls)
   - verify file isn't corrupted

4. **memory issues**:
   - reduce `MAX_NEWS_DOCUMENTS` in config
   - use smaller language models
   - increase system ram or use cloud deployment

### performance optimization

1. **model caching**:
   ```env
   CACHE_MODELS=True
   MODEL_CACHE_DIR=./model_cache
   ```

2. **batch processing**:
   - process multiple files in background
   - implement queuing system
   - use celery for async processing

3. **resource management**:
   - monitor memory usage
   - implement connection pooling
   - use production wsgi server (gunicorn)

## deployment

### production deployment

1. **environment setup**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   ```

2. **using gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **docker deployment**:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

4. **nginx configuration**:
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

### cloud deployment options

- **aws**: ec2 with elb and rds
- **google cloud**: app engine or compute engine
- **azure**: app service or virtual machines
- **heroku**: direct deployment with buildpacks

## security considerations

1. **file upload security**:
   - file type validation
   - size limits
   - virus scanning (recommended)

2. **input validation**:
   - url validation
   - content filtering
   - sql injection prevention

3. **data privacy**:
   - secure file storage
   - data encryption at rest
   - gdpr compliance considerations

## support and contributing

### getting help

1. **issues**: open github issues for bugs
2. **discussions**: use github discussions for questions
3. **documentation**: check inline code documentation

### contributing

1. fork the repository
2. create feature branch
3. add tests for new features
4. submit pull request

### license

this project is licensed under the mit license. see license file for details.

---

**version**: 1.0.0  
**last updated**: 2024-01-02  
**minimum requirements**: python 3.8+, 4gb ram, ollama with phi4