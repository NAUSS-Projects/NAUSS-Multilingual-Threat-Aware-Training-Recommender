
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
## features

- multilingual support for arabic and english
- real-time news analysis and semantic similarity
- ai-powered recommendations using ollama's phi4 model
- excel integration for training history uploads
- structured json output for easy integration

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