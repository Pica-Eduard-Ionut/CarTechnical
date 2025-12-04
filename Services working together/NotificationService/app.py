from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from email_service import EmailService
from config import Config
from reminder_scheduler import ReminderScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from Java services

# Load configuration
config = Config()
email_service = EmailService(config)

# Initialize reminder scheduler
reminder_scheduler = ReminderScheduler(config, email_service)

# Helper function to fetch user info from UserService
def get_user_from_service(user_id):
    """Fetch user information from UserService API"""
    try:
        response = requests.get(
            f"{config.USER_SERVICE_URL}/users/{user_id}",
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
            logger.warning(f"Failed to fetch user {user_id}: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching user {user_id} from UserService: {e}")
        return None

# Helper function to fetch service request from RequestService
def get_service_request_from_service(request_id):
    """Fetch service request information from RequestService API"""
    try:
        # Note: This assumes RequestService has a GET endpoint for individual requests
        # If not available, we'll need to add it or use the status endpoint
        response = requests.get(
            f"{config.REQUEST_SERVICE_URL}/service-requests/{request_id}",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to fetch request {request_id}: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching request {request_id} from RequestService: {e}")
        return None

# Setup background scheduler for reminders
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=reminder_scheduler.process_reminders,
    trigger=IntervalTrigger(hours=1),  # Run every hour
    id='reminder_job',
    name='Process appointment reminders',
    replace_existing=True
)
scheduler.start()
logger.info("Reminder scheduler started - will check for reminders every hour")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "NotificationService"}), 200

@app.route('/config/check', methods=['GET'])
def check_config():
    """Check SMTP configuration (without exposing sensitive data)"""
    try:
        # Check if credentials are set
        has_username = bool(config.SMTP_USERNAME)
        has_password = bool(config.SMTP_PASSWORD)
        
        return jsonify({
            "smtp_host": config.SMTP_HOST,
            "smtp_port": config.SMTP_PORT,
            "from_email": config.FROM_EMAIL,
            "has_username": has_username,
            "has_password": has_password,
            "use_tls": config.SMTP_USE_TLS,
            "use_ssl": config.SMTP_USE_SSL,
            "configured": has_username and has_password
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/notifications/request-created', methods=['POST'])
def notify_request_created():
    """
    Endpoint to send email notification when a service request is created.
    
    Expected JSON payload (minimal - will fetch missing data from services):
    {
        "requestId": 123,
        "ownerId": 456
    }
    
    OR full payload:
    {
        "requestId": 123,
        "ownerId": 456,
        "ownerEmail": "user@example.com",
        "ownerName": "John Doe",
        "status": "PENDING",
        "serviceType": "MAINTENANCE",
        "priority": "HIGH",
        "requestedFrom": "2024-01-15T10:00:00",
        "requestedTo": "2024-01-15T12:00:00"
    }
    """
    try:
        # Better error handling for JSON parsing
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "received_content_type": request.content_type
            }), 400
        
        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            logger.error(f"JSON parsing error: {str(json_error)}")
            return jsonify({
                "error": "Invalid JSON format",
                "details": str(json_error),
                "hint": "Make sure all Postman variables ({{serviceRequestId}}, {{ownerUserId}}) are set, or use actual values instead of variables"
            }), 400
        
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "hint": "Ensure request body contains valid JSON"
            }), 400
        
        # Validate required fields
        if 'requestId' not in data or 'ownerId' not in data:
            return jsonify({
                "error": "Missing required fields: requestId and ownerId are required"
            }), 400
        
        request_id = data.get('requestId')
        owner_id = data.get('ownerId')
        
        # Fetch user info from UserService if not provided
        if 'ownerEmail' not in data or 'ownerName' not in data:
            user_info = get_user_from_service(owner_id)
            if not user_info:
                return jsonify({
                    "error": f"Could not fetch user information for ownerId {owner_id}"
                }), 404
            owner_email = user_info.get('email')
            owner_name = user_info.get('name', 'Valued Customer')
        else:
            owner_email = data.get('ownerEmail')
            owner_name = data.get('ownerName')
        
        # Fetch service request details from RequestService if not provided
        if 'status' not in data or 'serviceType' not in data:
            service_request = get_service_request_from_service(request_id)
            if service_request:
                status = service_request.get('status', data.get('status', 'PENDING'))
                service_type = service_request.get('serviceType', data.get('serviceType', 'N/A'))
                priority = service_request.get('priority', data.get('priority', 'N/A'))
                requested_from = service_request.get('requestedFrom', data.get('requestedFrom', 'N/A'))
                requested_to = service_request.get('requestedTo', data.get('requestedTo', 'N/A'))
            else:
                # Use provided data or defaults
                status = data.get('status', 'PENDING')
                service_type = data.get('serviceType', 'N/A')
                priority = data.get('priority', 'N/A')
                requested_from = data.get('requestedFrom', 'N/A')
                requested_to = data.get('requestedTo', 'N/A')
        else:
            status = data.get('status')
            service_type = data.get('serviceType', 'N/A')
            priority = data.get('priority', 'N/A')
            requested_from = data.get('requestedFrom', 'N/A')
            requested_to = data.get('requestedTo', 'N/A')
        
        # Prepare email content
        subject = f"Service Request #{request_id} Created"
        body = f"""
Dear {owner_name},

Your service request has been successfully created.

Request Details:
- Request ID: #{request_id}
- Status: {status}
- Service Type: {service_type}
- Priority: {priority}
- Requested Time: {requested_from} to {requested_to}

We will process your request and keep you updated on its status.

Thank you for using our service.

Best regards,
Car Technical Service Team
        """
        
        # Send email
        email_service.send_email(
            to_email=owner_email,
            subject=subject,
            body=body,
            notification_type='request-created',
            request_id=request_id,
            recipient_name=owner_name,
            user_id=owner_id
        )
        
        return jsonify({
            "message": "Notification sent successfully",
            "requestId": request_id,
            "recipient": owner_email
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error sending request created notification: {str(e)}")
        return jsonify({
            "error": "Failed to send notification",
            "details": str(e)
        }), 500

@app.route('/notifications/request-updated', methods=['POST'])
def notify_request_updated():
    """
    Endpoint to send email notification when a service request is updated/edited.
    
    Expected JSON payload:
    {
        "requestId": 123,
        "ownerId": 456,
        "ownerEmail": "user@example.com",
        "ownerName": "John Doe",
        "newStatus": "IN_PROGRESS",
        "mechanicNotes": "Replaced brake pads",
        "totalCost": 150.00,
        "partsUsed": "Brake pads, brake fluid"
    }
    """
    try:
        # Better error handling for JSON parsing
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "received_content_type": request.content_type
            }), 400
        
        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            logger.error(f"JSON parsing error: {str(json_error)}")
            return jsonify({
                "error": "Invalid JSON format",
                "details": str(json_error),
                "hint": "Make sure all Postman variables are set, or use actual values instead of variables"
            }), 400
        
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "hint": "Ensure request body contains valid JSON"
            }), 400
        
        # Validate required fields
        required_fields = ['requestId', 'ownerId', 'ownerEmail', 'ownerName', 'newStatus']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400
        
        # Extract data
        request_id = data.get('requestId')
        owner_id = data.get('ownerId')
        owner_email = data.get('ownerEmail')
        owner_name = data.get('ownerName')
        new_status = data.get('newStatus')
        mechanic_notes = data.get('mechanicNotes', 'No notes provided')
        total_cost = data.get('totalCost')
        parts_used = data.get('partsUsed', 'N/A')
        
        # Prepare email content
        subject = f"Service Request #{request_id} Status Update"
        
        # Build status-specific message
        status_messages = {
            'PENDING': 'is pending review',
            'CONFIRMED': 'has been confirmed',
            'SCHEDULED': 'has been scheduled',
            'IN_PROGRESS': 'is now in progress',
            'COMPLETED': 'has been completed',
            'CANCELLED': 'has been cancelled'
        }
        status_message = status_messages.get(new_status, f'status changed to {new_status}')
        
        body = f"""
Dear {owner_name},

Your service request has been updated.

Request Details:
- Request ID: #{request_id}
- New Status: {new_status}
- Status: Your request {status_message}

"""
        
        # Add mechanic notes if available
        if mechanic_notes and mechanic_notes != 'No notes provided':
            body += f"Mechanic Notes:\n{mechanic_notes}\n\n"
        
        # Add cost information if available
        if total_cost is not None:
            body += f"Total Cost: ${total_cost:.2f}\n"
        
        # Add parts used if available
        if parts_used and parts_used != 'N/A':
            body += f"Parts Used: {parts_used}\n"
        
        body += """
Thank you for using our service.

Best regards,
Car Technical Service Team
        """
        
        # Send email
        email_service.send_email(
            to_email=owner_email,
            subject=subject,
            body=body,
            notification_type='request-updated',
            request_id=request_id,
            recipient_name=owner_name,
            user_id=owner_id
        )
        
        return jsonify({
            "message": "Notification sent successfully",
            "requestId": request_id,
            "recipient": owner_email
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error sending request updated notification: {str(e)}")
        return jsonify({
            "error": "Failed to send notification",
            "details": str(e)
        }), 500

@app.route('/notifications/status-changed', methods=['POST'])
def notify_status_changed():
    """
    Endpoint to send email notification when a service request status changes.
    This is a more generic endpoint that can be used for status change events.
    
    Expected JSON payload:
    {
        "requestId": 123,
        "ownerId": 456,
        "ownerEmail": "user@example.com",
        "ownerName": "John Doe",
        "newStatus": "COMPLETED"
    }
    """
    try:
        # Better error handling for JSON parsing
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "received_content_type": request.content_type
            }), 400
        
        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            logger.error(f"JSON parsing error: {str(json_error)}")
            return jsonify({
                "error": "Invalid JSON format",
                "details": str(json_error),
                "hint": "Make sure all Postman variables are set, or use actual values instead of variables"
            }), 400
        
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "hint": "Ensure request body contains valid JSON"
            }), 400
        
        # Validate required fields
        required_fields = ['requestId', 'ownerId', 'ownerEmail', 'ownerName', 'newStatus']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400
        
        # Extract data
        request_id = data.get('requestId')
        owner_id = data.get('ownerId')
        owner_email = data.get('ownerEmail')
        owner_name = data.get('ownerName')
        new_status = data.get('newStatus')
        
        # Prepare email content
        subject = f"Service Request #{request_id} Status Changed"
        
        status_messages = {
            'PENDING': 'is pending review',
            'CONFIRMED': 'has been confirmed',
            'SCHEDULED': 'has been scheduled',
            'IN_PROGRESS': 'is now in progress',
            'COMPLETED': 'has been completed',
            'CANCELLED': 'has been cancelled'
        }
        status_message = status_messages.get(new_status, f'status changed to {new_status}')
        
        body = f"""
Dear {owner_name},

Your service request status has been updated.

Request Details:
- Request ID: #{request_id}
- New Status: {new_status}
- Status: Your request {status_message}

We will keep you updated on any further changes.

Thank you for using our service.

Best regards,
Car Technical Service Team
        """
        
        # Send email
        email_service.send_email(
            to_email=owner_email,
            subject=subject,
            body=body,
            notification_type='status-changed',
            request_id=request_id,
            recipient_name=owner_name,
            user_id=owner_id
        )
        
        return jsonify({
            "message": "Notification sent successfully",
            "requestId": request_id,
            "recipient": owner_email
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error sending status changed notification: {str(e)}")
        return jsonify({
            "error": "Failed to send notification",
            "details": str(e)
        }), 500

@app.route('/reminders/process', methods=['POST'])
def manual_process_reminders():
    """Manually trigger reminder processing (for testing)"""
    try:
        count = reminder_scheduler.process_reminders()
        return jsonify({
            "message": "Reminders processed",
            "sent_count": count
        }), 200
    except Exception as e:
        logger.error(f"Error processing reminders: {e}")
        return jsonify({
            "error": "Failed to process reminders",
            "details": str(e)
        }), 500

@app.route('/reminders/stats', methods=['GET'])
def reminder_stats():
    """Get statistics about sent reminders"""
    try:
        import pymysql
        import os
        
        notification_db_config = {
            'host': os.getenv('NOTIFICATION_DB_HOST', 'localhost'),
            'port': int(os.getenv('NOTIFICATION_DB_PORT', '3306')),
            'user': os.getenv('NOTIFICATION_DB_USER', 'root'),
            'password': os.getenv('NOTIFICATION_DB_PASSWORD', 'root'),
            'database': os.getenv('NOTIFICATION_DB_NAME', 'notificationservice'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**notification_db_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) as count FROM sent_reminders')
                result = cursor.fetchone()
                count = result[0] if result else 0
        finally:
            connection.close()
        
        return jsonify({
            "total_reminders_sent": count
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to get stats",
            "details": str(e)
        }), 500

@app.route('/notifications/history', methods=['GET'])
def notification_history():
    """Get notification history"""
    try:
        import pymysql
        import os
        
        limit = request.args.get('limit', default=50, type=int)
        notification_type = request.args.get('type', default=None, type=str)
        request_id = request.args.get('request_id', default=None, type=int)
        user_id = request.args.get('user_id', default=None, type=int)
        
        notification_db_config = {
            'host': os.getenv('NOTIFICATION_DB_HOST', 'localhost'),
            'port': int(os.getenv('NOTIFICATION_DB_PORT', '3306')),
            'user': os.getenv('NOTIFICATION_DB_USER', 'root'),
            'password': os.getenv('NOTIFICATION_DB_PASSWORD', 'root'),
            'database': os.getenv('NOTIFICATION_DB_NAME', 'notificationservice'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**notification_db_config)
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                query = 'SELECT * FROM notification_history WHERE 1=1'
                params = []
                
                if notification_type:
                    query += ' AND notification_type = %s'
                    params.append(notification_type)
                
                if request_id:
                    query += ' AND request_id = %s'
                    params.append(request_id)
                
                if user_id:
                    query += ' AND user_id = %s'
                    params.append(user_id)
                
                query += ' ORDER BY sent_at DESC LIMIT %s'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                notifications = []
                for row in rows:
                    notifications.append({
                        'id': row['id'],
                        'notification_type': row['notification_type'],
                        'request_id': row['request_id'],
                        'user_id': row.get('user_id'),
                        'recipient_email': row['recipient_email'],
                        'recipient_name': row['recipient_name'],
                        'subject': row['subject'],
                        'sent_at': str(row['sent_at']) if row['sent_at'] else None,
                        'status': row['status'],
                        'error_message': row['error_message']
                    })
                
                # Get total count with same filters (excluding LIMIT)
                count_query = 'SELECT COUNT(*) as total FROM notification_history WHERE 1=1'
                count_params = []
                
                if notification_type:
                    count_query += ' AND notification_type = %s'
                    count_params.append(notification_type)
                
                if request_id:
                    count_query += ' AND request_id = %s'
                    count_params.append(request_id)
                
                if user_id:
                    count_query += ' AND user_id = %s'
                    count_params.append(user_id)
                
                cursor.execute(count_query, count_params)
                total_count = cursor.fetchone()['total']
        finally:
            connection.close()
        
        return jsonify({
            "total_notifications": total_count,
            "returned": len(notifications),
            "notifications": notifications
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to get notification history",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8083))
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down")

