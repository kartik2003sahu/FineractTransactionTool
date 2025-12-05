"""
Configuration module for loading environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Fineract API Settings
    FINERACT_BASE_URL = os.getenv("FINERACT_BASE_URL")
    FINERACT_AUTH_TOKEN = os.getenv("FINERACT_AUTH_TOKEN")
    FINERACT_TENANT_ID = os.getenv("FINERACT_TENANT_ID")
    
    # Date/Time Formats
    DATE_FORMAT = os.getenv("DATE_FORMAT", "dd MMMM yyyy")
    TIME_FORMAT = os.getenv("TIME_FORMAT", "dd MMMM yyyy HH:mm:ss")
    LOCALE = os.getenv("LOCALE", "en")
    
    # Storage Paths - desktop folder is in parent Kugelblitz directory
    _base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "desktop")
    JSON_STORAGE_PATH = os.getenv("JSON_STORAGE_PATH", os.path.join(_base_dir, "transactions.json"))
    EXCEL_EXPORT_PATH = os.getenv("EXCEL_EXPORT_PATH", os.path.join(_base_dir, "transactions.xlsx"))
    EXCEL_IMPORT_PATH = os.getenv("EXCEL_IMPORT_PATH", os.path.join(_base_dir, "transactions_updated.xlsx"))
    
    # Application Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        required = [
            "FINERACT_BASE_URL",
            "FINERACT_AUTH_TOKEN",
            "FINERACT_TENANT_ID"
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True

# Don't validate on import - allow app to start for login page
# Validation happens when actually making API calls
# Config.validate()
