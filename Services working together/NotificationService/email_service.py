import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import pymysql
import os

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self, config):
        """
        Initialize the email service with configuration.
        
        Args:
            config: Config object containing SMTP settings
        """
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_username = config.SMTP_USERNAME
        self.smtp_password = config.SMTP_PASSWORD
        self.from_email = config.FROM_EMAIL
        self.use_tls = config.SMTP_USE_TLS
        self.use_ssl = config.SMTP_USE_SSL
        
        # Notification database connection settings (MariaDB)
        self.notification_db_config = {
            'host': os.getenv('NOTIFICATION_DB_HOST', 'localhost'),
            'port': int(os.getenv('NOTIFICATION_DB_PORT', '3306')),
            'user': os.getenv('NOTIFICATION_DB_USER', 'root'),
            'password': os.getenv('NOTIFICATION_DB_PASSWORD', 'root'),
            'database': os.getenv('NOTIFICATION_DB_NAME', 'notificationservice'),
            'charset': 'utf8mb4'
        }
        
    def save_notification_history(self, notification_type, request_id, recipient_email, 
                                  recipient_name, subject, status='sent', error_message=None, user_id=None):
        """Save notification to history database"""
        try:
            connection = pymysql.connect(**self.notification_db_config)
            try:
                with connection.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO notification_history 
                        (notification_type, request_id, user_id, recipient_email, recipient_name, subject, status, error_message)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (notification_type, request_id, user_id, recipient_email, recipient_name, subject, status, error_message))
                connection.commit()
            finally:
                connection.close()
        except Exception as e:
            logger.error(f"Failed to save notification history: {e}")
    
    def send_email(self, to_email, subject, body, is_html=False, notification_type='general', 
                   request_id=None, recipient_name=None, user_id=None):
        """
        Send an email via SMTP and save to history.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            is_html: Whether the body is HTML (default: False)
            notification_type: Type of notification (e.g., 'request-created', 'request-updated', 'reminder')
            request_id: Optional request ID associated with this notification
            recipient_name: Optional recipient name
            user_id: Optional user ID (owner_id) associated with this notification
            
        Raises:
            Exception: If email sending fails
        """
        error_message = None
        status = 'sent'
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send email
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            if self.use_tls and not self.use_ssl:
                server.starttls()
            
            # Login if credentials are provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email} with subject: {subject}")
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication error: {str(e)}")
            error_msg = (
                f"SMTP authentication failed. "
                f"For Gmail, make sure you're using an App Password (not your regular password). "
                f"Get one at: https://myaccount.google.com/apppasswords"
            )
            status = 'failed'
            error_message = str(e)
            # Save failed notification to history
            self.save_notification_history(notification_type, request_id, to_email, recipient_name, 
                                         subject, status, error_message, user_id)
            raise Exception(error_msg)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending email to {to_email}: {str(e)}")
            status = 'failed'
            error_message = str(e)
            # Save failed notification to history
            self.save_notification_history(notification_type, request_id, to_email, recipient_name, 
                                         subject, status, error_message, user_id)
            raise Exception(f"Failed to send email: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while sending email to {to_email}: {str(e)}")
            status = 'failed'
            error_message = str(e)
            # Save failed notification to history
            self.save_notification_history(notification_type, request_id, to_email, recipient_name, 
                                         subject, status, error_message, user_id)
            raise Exception(f"Failed to send email: {str(e)}")
        
        # Save successful notification to history
        self.save_notification_history(notification_type, request_id, to_email, recipient_name, 
                                     subject, status, error_message, user_id)

