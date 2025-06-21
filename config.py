import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/mudhumeni_db'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}