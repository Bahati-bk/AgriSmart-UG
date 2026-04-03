import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    db_url = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(BASE_DIR, "agrismart.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    WEATHER_BASE_URL = os.getenv(
        "WEATHER_BASE_URL",
        "https://api.openweathermap.org/data/2.5/weather"
    )

    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    SMS_PROVIDER = os.getenv("SMS_PROVIDER", "console")
    SMS_API_KEY = os.getenv("SMS_API_KEY", "")
    SMS_SENDER_ID = os.getenv("SMS_SENDER_ID", "AgriSmartUG")

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}