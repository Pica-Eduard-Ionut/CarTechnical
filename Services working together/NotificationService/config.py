import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for NotificationService"""
    
    # SMTP Configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
    
    # Email Configuration
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@cartechservice.com')
    
    # Server Configuration
    PORT = int(os.getenv('PORT', '8083'))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Notification Database Configuration (MariaDB)
    NOTIFICATION_DB_HOST = os.getenv('NOTIFICATION_DB_HOST', 'localhost')
    NOTIFICATION_DB_PORT = int(os.getenv('NOTIFICATION_DB_PORT', '3306'))
    NOTIFICATION_DB_USER = os.getenv('NOTIFICATION_DB_USER', 'root')
    NOTIFICATION_DB_PASSWORD = os.getenv('NOTIFICATION_DB_PASSWORD', 'root')
    NOTIFICATION_DB_NAME = os.getenv('NOTIFICATION_DB_NAME', 'notificationservice')
    
    # Microservices URLs
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:8081')
    REQUEST_SERVICE_URL = os.getenv('REQUEST_SERVICE_URL', 'http://localhost:8082')
    

