import requests
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import re
from urllib.parse import urlparse
import json

# Seed for consistent results
DetectorFactory.seed = 0

def detect_language(text):
    """Detect if text is Arabic or English."""
    if not text:
        return 'unknown'
    
    # Simple heuristic: if contains Arabic characters, it's Arabic
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F]')
    if arabic_pattern.search(str(text)):
        return 'ar'
    
    try:
        lang = detect(str(text))
        if lang == 'ar':
            return 'ar'
        else:
            return 'en'
    except LangDetectException:
        return 'en'  # default to English


def clean_text(text):
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    #print(text)
    return text


def scrape_url(url, timeout=10):
    """
    Scrape content from a single URL.
    Returns dict with title, content, publish_date, and language.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = clean_text(title_tag.get_text())
        
        # Extract content from all headings, paragraphs, and divs across the page
        # Remove non-content elements site-wide
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'])
        texts = []
        for elem in elements:
            txt = elem.get_text(separator=' ', strip=True)
            txt = clean_text(txt)
            if txt:
                texts.append(txt)
        content = clean_text(' '.join(texts))

        # Fallback: use body content if nothing was collected
        if not content:
            body = soup.find('body')
            if body:
                content = clean_text(body.get_text(separator=' ', strip=True))
        
        # Try to extract publish date
        publish_date = None
        date_selectors = [
            'time[datetime]',
            '.publish-date',
            '.date',
            '[class*="date"]',
            'meta[property="article:published_time"]',
            'meta[name="publish-date"]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if date_elem.has_attr('datetime'):
                    publish_date = date_elem['datetime']
                elif date_elem.has_attr('content'):
                    publish_date = date_elem['content']
                else:
                    publish_date = clean_text(date_elem.get_text())
                break
        
        # Detect language
        sample_text = (title + " " + content[:500]).strip()
        language = detect_language(sample_text)
        print(language)
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'publish_date': publish_date,
            'language': language,
            'source': 'scraped'
        }
        
    except Exception as e:
        return {
            'url': url,
            'title': "",
            'content': "",
            'publish_date': None,
            'language': 'unknown',
            'source': 'scraped',
            'error': str(e)
        }


def process_raw_text(text):
    """
    Process raw text input into structured format.
    """
    if not text:
        return []
    
    text = clean_text(text)
    language = detect_language(text)
    
    # Split into paragraphs if it's very long
    paragraphs = text.split('\n\n')
    if len(paragraphs) > 1:
        # Treat as multiple articles
        docs = []
        for i, para in enumerate(paragraphs):
            if len(para.strip()) > 50:  # Skip very short paragraphs
                docs.append({
                    'title': f"Article {i+1}",
                    'content': clean_text(para),
                    'publish_date': None,
                    'language': detect_language(para),
                    'source': 'raw_text'
                })
        return docs
    else:
        # Single article
        return [{
            'title': "Raw Text Input",
            'content': text,
            'publish_date': None,
            'language': language,
            'source': 'raw_text'
        }]


def process_news_inputs(urls=None, raw_text=None):
    """
    Process news inputs from URLs and/or raw text.
    Returns list of processed news documents.
    """
    documents = []
    
    # Process URLs
    if urls:
        if isinstance(urls, str):
            # Try to parse as JSON first
            try:
                url_list = json.loads(urls)
            except json.JSONDecodeError:
                # Split by lines or commas
                url_list = [u.strip() for u in re.split(r'[,\n]', urls) if u.strip()]
        else:
            url_list = urls
        
        for url in url_list:
            url = url.strip()
            if url and urlparse(url).scheme:  # Valid URL
                doc = scrape_url(url)
                documents.append(doc)
    
    # Process raw text
    if raw_text:
        raw_docs = process_raw_text(raw_text)
        documents.extend(raw_docs)
    
    # Filter out empty documents
    documents = [doc for doc in documents if doc.get('content') or doc.get('title')]
    
    return documents


def summarize_news_documents(documents):
    """
    Create a summary of processed news documents.
    """
    if not documents:
        return {}
    
    total_docs = len(documents)
    scraped_docs = len([d for d in documents if d.get('source') == 'scraped'])
    raw_text_docs = len([d for d in documents if d.get('source') == 'raw_text'])
    
    languages = [d.get('language', 'unknown') for d in documents]
    ar_count = languages.count('ar')
    en_count = languages.count('en')
    unknown_count = languages.count('unknown')
    
    return {
        'total_documents': total_docs,
        'scraped_documents': scraped_docs,
        'raw_text_documents': raw_text_docs,
        'languages': {
            'arabic': ar_count,
            'english': en_count,
            'unknown': unknown_count
        }
    }