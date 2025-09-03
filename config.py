import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Jagriti portal settings
    JAGRITI_BASE_URL = "https://e-jagriti.gov.in"
    JAGRITI_SEARCH_URL = f"{JAGRITI_BASE_URL}/advance-case-search"
    # Main search endpoint
    JAGRITI_API_URL = f"{JAGRITI_BASE_URL}/advance-case-search"

    # API settings
    API_TITLE = "Lexi Jagriti API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "API for searching District Consumer Court cases via Jagriti portal"

    # Request settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3

    # Cache settings (for state/commission mappings)
    CACHE_TTL = 3600  # 1 hour

    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # CORS
    CORS_ALLOW_ORIGINS = (
        os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
        if os.getenv("CORS_ALLOW_ORIGINS")
        else ["*"]
    )
