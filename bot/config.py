"""
Bot configuration from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env.bot.secret
load_dotenv('.env.bot.secret')


class Config:
    """Bot configuration."""
    
    # Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # Backend API
    LMS_API_BASE_URL = os.getenv('LMS_API_BASE_URL', 'http://localhost:42002')
    LMS_API_KEY = os.getenv('LMS_API_KEY', '')
    
    # LLM (for Task 3)
    LLM_API_BASE_URL = os.getenv('LLM_API_BASE_URL', 'http://localhost:42005/v1')
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_API_MODEL = os.getenv('LLM_API_MODEL', 'coder-model')
    
    @classmethod
    def validate(cls) -> bool:
        """Check that required settings are present."""
        # In test mode, BOT_TOKEN is optional
        if os.getenv('_TEST_MODE') == '1':
            return bool(cls.LMS_API_KEY)
        return bool(cls.BOT_TOKEN and cls.LMS_API_KEY)
