import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # Similarity Engine Settings
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', '0.3'))
    MULTILINGUAL_MODEL = os.environ.get('MULTILINGUAL_MODEL', 'sentence-transformers/LaBSE')
    
    # Ollama Settings
    OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'phi4')
    
    # News Scraping Settings
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '10'))
    MAX_NEWS_DOCUMENTS = int(os.environ.get('MAX_NEWS_DOCUMENTS', '20'))
    
    # Language Detection Settings
    SUPPORTED_LANGUAGES = ['en', 'ar']
    DEFAULT_LANGUAGE = 'en'
    
    # Logging Settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Model Caching (for sentence transformers)
    CACHE_MODELS = os.environ.get('CACHE_MODELS', 'True').lower() == 'true'
    MODEL_CACHE_DIR = os.environ.get('MODEL_CACHE_DIR', './model_cache')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    EXPLAIN_TEMPLATE_LOADING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Enhanced security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    SIMILARITY_THRESHOLD = 0.1  # Lower threshold for testing
    REQUEST_TIMEOUT = 5  # Shorter timeout for tests


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}