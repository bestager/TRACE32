import os

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'english_learning.db')
CLAUDE_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
MAX_AI_SENTENCES_PER_REQUEST = 100
