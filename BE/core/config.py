import os
from typing import List
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

class Settings:
    # Apollo API Configuration
    APOLLO_API_KEY: str = os.getenv("APOLLO_API_KEY", "")
    APOLLO_API_URL: str = "https://api.apollo.io/v1"
    APOLLO_BASE_URL: str = "https://app.apollo.io"

    # AI/Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "60"))
    AI_MAX_TOKENS_PER_REQUEST: int = int(os.getenv("AI_MAX_TOKENS_PER_REQUEST", "4096"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_TOP_P: float = float(os.getenv("AI_TOP_P", "0.9"))
    AI_TOP_K: int = int(os.getenv("AI_TOP_K", "40"))

    # Outreach Configuration
    DEFAULT_MESSAGE_TONE: str = os.getenv("DEFAULT_MESSAGE_TONE", "professional")
    DEFAULT_PERSONALIZATION_LEVEL: str = os.getenv("DEFAULT_PERSONALIZATION_LEVEL", "medium")
    MAX_BULK_MESSAGES: int = int(os.getenv("MAX_BULK_MESSAGES", "50"))
    MESSAGE_QUALITY_THRESHOLD: float = float(os.getenv("MESSAGE_QUALITY_THRESHOLD", "7.0"))
    
    # Feature Flags
    ENABLE_AI_OUTREACH: bool = os.getenv("ENABLE_AI_OUTREACH", "true").lower() == "true"
    ENABLE_MESSAGE_ANALYSIS: bool = os.getenv("ENABLE_MESSAGE_ANALYSIS", "true").lower() == "true"
    ENABLE_BULK_GENERATION: bool = os.getenv("ENABLE_BULK_GENERATION", "true").lower() == "true"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        # "https://(your-frontend-domain)"
    ]
    
    # API Settings
    DEFAULT_PAGE_SIZE: int = 25
    MAX_PAGE_SIZE: int = 50
    REQUEST_TIMEOUT: float = 30.0
    
    # Scraping Settings
    SCRAPING_DELAY: float = 1.0  
    MAX_RETRIES: int = 3
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # File Settings
    EXPORT_DIR: str = os.getenv("EXPORT_DIR", "./exports")
    
    @property
    def is_apollo_configured(self) -> bool:
        # Check if Apollo API is Properly Configured
        return bool(self.APOLLO_API_KEY)
    
    @property
    def is_gemini_configured(self) -> bool:
        # Check if Gemini AI is Properly Configured
        return bool(self.GEMINI_API_KEY)
    
    @property
    def can_generate_outreach(self) -> bool:
        # Check if Outreach Generation is Enabled & Configured
        return self.ENABLE_AI_OUTREACH and self.is_gemini_configured

# Create Settings Instance
settings = Settings()