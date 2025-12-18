"""
Reminder Scheduler
Checks for appointments 24 hours before and sends reminder emails.
"""
import pymysql
import requests
from datetime import datetime, timedelta
import logging
import os
from email_service import EmailService
from config import Config

logger = logging.getLogger(__name__)

class ReminderScheduler:
    """Scheduler for sending appointment reminders"""
    
    def __init__(self, config, email_service):
        self.config = config
        self.email_service = email_service
        
        # MariaDB connection settings (from RequestService)
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'database': os.getenv('DB_NAME', 'requestservice'),
            'charset': 'utf8mb4'
        }
        
        # UserService database connection settings
        self.user_db_config = {
            'host': os.getenv('USER_DB_HOST', 'localhost'),
            'port': int(os.getenv('USER_DB_PORT', '3306')),
            'user': os.getenv('USER_DB_USER', 'root'),
            'password': os.getenv('USER_DB_PASSWORD', 'root'),
            'database': os.getenv('USER_DB_NAME', 'userservice'),
            'charset': 'utf8mb4'
        }
        
        # Microservices API endpoints
        self.user_service_url = os.getenv('USER_SERVICE_URL', 'http://localhost:8081')
        self.request_service_url = os.getenv('REQUEST_SERVICE_URL', 'http://localhost:8082')
        
        # Notification database connection settings (MariaDB)
        self.notification_db_config = {
            'host': os.getenv('NOTIFICATION_DB_HOST', 'localhost'),
            'port': int(os.getenv('NOTIFICATION_DB_PORT', '3306')),
            'user': os.getenv('NOTIFICATION_DB_USER', 'root'),
            'password': os.getenv('NOTIFICATION_DB_PASSWORD', 'root'),
            'database': os.getenv('NOTIFICATION_DB_NAME', 'notificationservice'),
            'charset': 'utf8mb4'
        }
        
        # Initialize reminder tracking database (MariaDB)
        self.init_reminder_tracking()
    
    def init_reminder_tracking(self):
        """Initialize MariaDB database to track sent reminders and notification history"""
        try:
            connection = pymysql.connect(**self.notification_db_config)
            try:
                with connection.cursor() as cursor:
                    # Table for tracking sent reminders (to avoid duplicates)
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS sent_reminders (
                            request_id INT PRIMARY KEY,
                            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Table for notification history (all notifications sent)
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS notification_history (
                            id INT PRIMARY KEY AUTO_INCREMENT,
                            notification_type VARCHAR(50) NOT NULL,
                            request_id INT,
                            user_id INT,
                            recipient_email VARCHAR(255) NOT NULL,
                            recipient_name VARCHAR(255),
                            subject VARCHAR(500) NOT NULL,
                            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            status VARCHAR(20) DEFAULT 'sent',
                            error_message TEXT
                        )
                    ''')
                    
                    # Add user_id column if it doesn't exist (for existing databases)
                    try:
                        cursor.execute('ALTER TABLE notification_history ADD COLUMN user_id INT')
                    except pymysql.Error:
                        # Column already exists, ignore
                        pass
                    
                connection.commit()
                logger.info("Notification tracking database initialized")
            finally:
                connection.close()
        except Exception as e:
            logger.error(f"Failed to initialize notification tracking database: {e}")
            raise
    
    def get_user_info(self, owner_id):
        """Get user information from UserService API"""
        try:
            response = requests.get(
                f"{self.user_service_url}/users/{owner_id}",
                timeout=5
            )
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'id': user_data.get('id'),
                    'name': user_data.get('name', 'Valued Customer'),
                    'email': user_data.get('email'),
                    'role': user_data.get('role', 'OWNER')
                }
            else:
                logger.warning(f"User {owner_id} not found via API: HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user {owner_id} from UserService API: {e}")
            return None
    
    def has_reminder_been_sent(self, request_id):
        """Check if reminder has already been sent for this request"""
        try:
            connection = pymysql.connect(**self.notification_db_config)
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SELECT request_id FROM sent_reminders WHERE request_id = %s', (request_id,))
                    result = cursor.fetchone()
                    return result is not None
            finally:
                connection.close()
        except Exception as e:
            logger.error(f"Error checking reminder status for request {request_id}: {e}")
            return False
    
    def mark_reminder_sent(self, request_id):
        """Mark reminder as sent for this request"""
        try:
            connection = pymysql.connect(**self.notification_db_config)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT IGNORE INTO sent_reminders (request_id) VALUES (%s)',
                        (request_id,)
                    )
                connection.commit()
            finally:
                connection.close()
        except Exception as e:
            logger.error(f"Error marking reminder as sent for request {request_id}: {e}")
    
    def get_appointments_needing_reminders(self):
        """Query RequestService API for appointments that need reminders (24 hours before)"""
        appointments = []
        
        try:
            # Calculate time window: 23-25 hours before (1 hour window to catch them)
            now = datetime.now()
            target_time_start = now + timedelta(hours=23)
            target_time_end = now + timedelta(hours=25)
            
            logger.info(f"Reminder window: {target_time_start} to {target_time_end}")
            logger.info(f"Current time: {now}")
            
            # Get all pending/confirmed/scheduled requests from RequestService
            statuses = ['PENDING', 'CONFIRMED', 'SCHEDULED', 'IN_PROGRESS']
            
            for status in statuses:
                try:
                    response = requests.get(
                        f"{self.request_service_url}/service-requests/status/{status}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        requests_list = response.json()
                        logger.info(f"Found {len(requests_list)} requests with status {status}")
                        
                        for req in requests_list:
                            logger.info(f"Processing request {req.get('id')}: status={req.get('status')}, requestedFrom={req.get('requestedFrom')}")
                            
                            # Parse requested_from if it's a string
                            requested_from_str = req.get('requestedFrom')
                            if not requested_from_str:
                                logger.warning(f"Request {req.get('id')} has no requestedFrom field")
                                continue
                                
                            logger.info(f"Request {req.get('id')} requestedFrom: {requested_from_str} (type: {type(requested_from_str)})")
                            
                            try:
                                # Handle ISO format datetime strings
                                if isinstance(requested_from_str, str):
                                    # Remove 'Z' and parse
                                    requested_from_str = requested_from_str.replace('Z', '')
                                    if '+' in requested_from_str or requested_from_str.endswith('00:00'):
                                        # Has timezone info
                                        requested_from = datetime.fromisoformat(requested_from_str.replace('+00:00', ''))
                                    else:
                                        requested_from = datetime.fromisoformat(requested_from_str)
                                else:
                                    requested_from = requested_from_str
                                
                                logger.info(f"Parsed datetime: {requested_from}")
                                time_diff_hours = (requested_from - now).total_seconds() / 3600
                                logger.info(f"Time difference: {time_diff_hours:.2f} hours from now")
                                logger.info(f"Window check: {target_time_start} <= {requested_from} <= {target_time_end}")
                                logger.info(f"Start check: {target_time_start <= requested_from} (diff: {(requested_from - target_time_start).total_seconds() / 3600:.2f} hours)")
                                logger.info(f"End check: {requested_from <= target_time_end} (diff: {(target_time_end - requested_from).total_seconds() / 3600:.2f} hours)")
                                
                                # Check if within reminder window
                                if target_time_start <= requested_from <= target_time_end:
                                    logger.info(f"✓ Request {req.get('id')} is in reminder window!")
                                    appointments.append({
                                        'id': req.get('id'),
                                        'owner_id': req.get('ownerId'),
                                        'requested_from': requested_from,
                                        'requested_to': req.get('requestedTo'),
                                        'service_type': req.get('serviceType', 'N/A'),
                                        'status': req.get('status', 'N/A'),
                                        'priority': req.get('priority', 'N/A')
                                    })
                                else:
                                    logger.info(f"✗ Request {req.get('id')} is NOT in reminder window (diff: {time_diff_hours:.2f} hours, window: 23-25 hours)")
                                    
                            except (ValueError, AttributeError) as e:
                                logger.warning(f"Could not parse requestedFrom for request {req.get('id')}: {e}")
                                logger.warning(f"Raw value: {requested_from_str}")
                                continue
                    else:
                        logger.warning(f"Failed to fetch {status} requests: HTTP {response.status_code}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Error fetching {status} requests: {e}")
                    continue
            
            logger.info(f"Found {len(appointments)} appointments in reminder window")
                    
        except Exception as e:
            logger.error(f"Error querying appointments: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return appointments
    
    
    def send_reminder_email(self, appointment, user_info):
        """Send reminder email for an appointment"""
        try:
            owner_email = user_info.get('email')
            owner_name = user_info.get('name', 'Valued Customer')
            
            # Format appointment time
            requested_from = appointment['requested_from']
            if isinstance(requested_from, str):
                appointment_time = datetime.fromisoformat(requested_from.replace('Z', '+00:00'))
            else:
                appointment_time = requested_from
            
            formatted_time = appointment_time.strftime('%Y-%m-%d %H:%M')
            
            subject = f"Reminder: Service Appointment Tomorrow - Request #{appointment['id']}"
            
            body = f"""
Dear {owner_name},

This is a friendly reminder about your upcoming service appointment.

Appointment Details:
- Request ID: #{appointment['id']}
- Service Type: {appointment.get('service_type', 'N/A')}
- Priority: {appointment.get('priority', 'N/A')}
- Scheduled Time: {formatted_time}
- Status: {appointment.get('status', 'N/A')}

Your appointment is scheduled for tomorrow. Please make sure to arrive on time.

If you need to reschedule or cancel, please contact us as soon as possible.

Thank you for choosing our service!

Best regards,
Car Technical Service Team
            """
            
            self.email_service.send_email(
                to_email=owner_email,
                subject=subject,
                body=body,
                notification_type='reminder',
                request_id=appointment['id'],
                recipient_name=owner_name,
                user_id=user_info.get('id')
            )
            
            logger.info(f"Reminder email sent to {owner_email} for request {appointment['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending reminder email for request {appointment['id']}: {e}")
            return False
    
    def process_reminders(self):
        """Main method to process and send reminders"""
        logger.info("Processing reminders...")
        
        appointments = self.get_appointments_needing_reminders()
        logger.info(f"Found {len(appointments)} appointments needing reminders")
        
        sent_count = 0
        skipped_count = 0
        
        for appointment in appointments:
            request_id = appointment['id']
            
            if self.has_reminder_been_sent(request_id):
                logger.debug(f"Reminder already sent for request {request_id}, skipping")
                skipped_count += 1
                continue
            
            user_info = self.get_user_info(appointment['owner_id'])
            if not user_info:
                logger.warning(f"Could not get user info for owner_id {appointment['owner_id']}, skipping request {request_id}")
                continue
            
            if self.send_reminder_email(appointment, user_info):
                self.mark_reminder_sent(request_id)
                sent_count += 1
            else:
                logger.error(f"Failed to send reminder for request {request_id}")
        
        logger.info(f"Reminder processing complete: {sent_count} sent, {skipped_count} skipped")
        return sent_count

