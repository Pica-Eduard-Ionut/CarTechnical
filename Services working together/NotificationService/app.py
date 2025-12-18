from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import threading
import json
import pika
import pymysql
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from email_service import EmailService
from config import Config
from reminder_scheduler import ReminderScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

config = Config()
email_service = EmailService(config)

reminder_scheduler = ReminderScheduler(config, email_service)

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

def get_service_request_from_service(request_id):
    """Fetch service request information from RequestService API"""
    try:
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

# RabbitMQ consumer function
def start_rabbitmq_consumer():
    """Consume messages from RabbitMQ and send notifications"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                port=int(os.getenv('RABBITMQ_PORT', 5672)),
                credentials=pika.PlainCredentials(
                    username=os.getenv('RABBITMQ_USERNAME', 'guest'),
                    password=os.getenv('RABBITMQ_PASSWORD', 'guest')
                )
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue='request-queue', durable=True)

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                request_id = message.get('requestId')
                owner_email = message.get('ownerEmail')
                owner_name = message.get('ownerName')
                event_type = message.get('eventType', 'request-created')
                new_status = message.get('newStatus', message.get('status', 'PENDING'))
                mechanic_notes = message.get('mechanicNotes', None)
                total_cost = message.get('totalCost', None)
                parts_used = message.get('partsUsed', None)

                # Build email content
                if event_type == 'request-created':
                    subject = f"Service Request #{request_id} Created"
                    body_text = f"""
Dear {owner_name},

Your service request has been successfully created.

Request Details:
- Request ID: #{request_id}
- Status: {new_status}

Thank you for using our service.
"""
                elif event_type == 'request-updated':
                    subject = f"Service Request #{request_id} Status Update"
                    status_messages = {
                        'PENDING': 'is pending review',
                        'CONFIRMED': 'has been confirmed',
                        'SCHEDULED': 'has been scheduled',
                        'IN_PROGRESS': 'is now in progress',
                        'COMPLETED': 'has been completed',
                        'CANCELLED': 'has been cancelled'
                    }
                    status_message = status_messages.get(new_status, f'status changed to {new_status}')
                    body_text = f"""
Dear {owner_name},

Your service request has been updated.

Request Details:
- Request ID: #{request_id}
- New Status: {new_status} ({status_message})
"""
                    if mechanic_notes:
                        body_text += f"Mechanic Notes:\n{mechanic_notes}\n"
                    if total_cost is not None:
                        body_text += f"Total Cost: ${total_cost:.2f}\n"
                    if parts_used:
                        body_text += f"Parts Used: {parts_used}\n"

                    body_text += "\nThank you for using our service."

                else:
                    subject = f"Service Request #{request_id} Notification"
                    body_text = f"Hello {owner_name}, your request status is now {new_status}."

                # Send email
                email_service.send_email(
                    to_email=owner_email,
                    subject=subject,
                    body=body_text,
                    notification_type=event_type,
                    request_id=request_id,
                    recipient_name=owner_name,
                    user_id=message.get('ownerId')
                )

                logger.info(f"Processed message from queue: requestId={request_id}, event={event_type}")
                ch.basic_ack(delivery_tag=method.delivery_tag)

            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume(queue='request-queue', on_message_callback=callback)
        logger.info("RabbitMQ consumer started, waiting for messages...")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Failed to start RabbitMQ consumer: {e}")


# Start RabbitMQ consumer in a separate thread
threading.Thread(target=start_rabbitmq_consumer, daemon=True).start()

# Start APScheduler for reminder processing
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
        has_username = bool(config.SMTP_USERNAME)
        has_password = bool(config.SMTP_PASSWORD)
        
        return jsonify({
            "smtp_configured": has_username and has_password,
            "smtp_host": config.SMTP_HOST if config.SMTP_HOST else "Not configured",
            "smtp_port": config.SMTP_PORT,
            "from_email": config.FROM_EMAIL if config.FROM_EMAIL else "Not configured"
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
        if not request.is_json:
            return jsonify({
                "success": False, 
                "error": "Request must be JSON"
            }), 400
        
        try:
            data = request.get_json()
        except Exception as json_error:
            logger.error(f"JSON parsing error: {json_error}")
            return jsonify({
                "success": False,
                "error": f"Invalid JSON: {str(json_error)}"
            }), 400
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Empty request body"
            }), 400
        
        if 'requestId' not in data or 'ownerId' not in data:
            return jsonify({
                "success": False, 
                "error": "Missing required fields: requestId and ownerId"
            }), 400
        
        request_id = data.get('requestId')
        owner_id = data.get('ownerId')
        
        if 'ownerEmail' not in data or 'ownerName' not in data:
            user_info = get_user_from_service(owner_id)
            if not user_info:
                return jsonify({"success": False, "error": f"User {owner_id} not found"}), 404
            owner_email = user_info['email']
            owner_name = user_info['name']
        else:
            owner_email = data.get('ownerEmail')
            owner_name = data.get('ownerName')
        
        if 'status' not in data or 'serviceType' not in data:
            request_info = get_service_request_from_service(request_id)
            if not request_info:
                return jsonify({"success": False, "error": f"Request {request_id} not found"}), 404
            status = request_info.get('status', 'PENDING')
            service_type = request_info.get('serviceType', 'N/A')
            priority = request_info.get('priority', 'NORMAL')
            requested_from = request_info.get('requestedFrom', 'N/A')
            requested_to = request_info.get('requestedTo', 'N/A')
        else:
            status = data.get('status', 'PENDING')
            service_type = data.get('serviceType', 'N/A')
            priority = data.get('priority', 'NORMAL')
            requested_from = data.get('requestedFrom', 'N/A')
            requested_to = data.get('requestedTo', 'N/A')
        
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
            "success": True, 
            "message": f"Notification sent to {owner_email}"
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error sending request created notification: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
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
        if not request.is_json:
            return jsonify({
                "success": False, 
                "error": "Request must be JSON"
            }), 400
        
        try:
            data = request.get_json()
        except Exception as json_error:
            logger.error(f"JSON parsing error: {json_error}")
            return jsonify({
                "success": False,
                "error": f"Invalid JSON: {str(json_error)}"
            }), 400
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Empty request body"
            }), 400
        
        required_fields = ['requestId', 'ownerId', 'ownerEmail', 'ownerName', 'newStatus']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        request_id = data.get('requestId')
        owner_id = data.get('ownerId')
        owner_email = data.get('ownerEmail')
        owner_name = data.get('ownerName')
        new_status = data.get('newStatus')
        mechanic_notes = data.get('mechanicNotes', 'No notes provided')
        total_cost = data.get('totalCost')
        parts_used = data.get('partsUsed', 'N/A')
        
        subject = f"Service Request #{request_id} Status Update"
        
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
        
        if mechanic_notes and mechanic_notes != 'No notes provided':
            body += f"Mechanic Notes:\n{mechanic_notes}\n\n"
        
        if total_cost is not None:
            body += f"Total Cost: ${total_cost:.2f}\n\n"
        
        if parts_used and parts_used != 'N/A':
            body += f"Parts Used: {parts_used}\n\n"
        
        body += """
Thank you for using our service.

Best regards,
Car Technical Service Team
        """
        
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
            "success": True,
            "message": f"Notification sent to {owner_email}"
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error sending request updated notification: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
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
        if not request.is_json:
            return jsonify({
                "success": False, 
                "error": "Request must be JSON"
            }), 400
        
        try:
            data = request.get_json()
        except Exception as json_error:
            logger.error(f"JSON parsing error: {json_error}")
            return jsonify({
                "success": False,
                "error": f"Invalid JSON: {str(json_error)}"
            }), 400
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Empty request body"
            }), 400
        
        required_fields = ['requestId', 'ownerId', 'ownerEmail', 'ownerName', 'newStatus']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        request_id = data.get('requestId')
        owner_id = data.get('ownerId')
        owner_email = data.get('ownerEmail')
        owner_name = data.get('ownerName')
        new_status = data.get('newStatus')
        
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
            "success": True,
            "message": f"Notification sent to {owner_email}"
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error sending status changed notification: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/reminders/process', methods=['POST'])
def manual_process_reminders():
    """Manually trigger reminder processing (for testing)"""
    try:
        count = reminder_scheduler.process_reminders()
        return jsonify({
            "success": True,
            "message": f"Processed reminders, sent {count} emails"
        }), 200
    except Exception as e:
        logger.error(f"Error processing reminders: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/reminders/stats', methods=['GET'])
def reminder_stats():
    """Get statistics about sent reminders"""
    try:
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
                cursor.execute('SELECT COUNT(*) as total_sent FROM sent_reminders')
                result = cursor.fetchone()
                
                cursor.execute('''
                    SELECT COUNT(*) as total_notifications 
                    FROM notification_history 
                    WHERE notification_type = "reminder"
                ''')
                notification_result = cursor.fetchone()
                
                return jsonify({
                    "success": True,
                    "reminders_sent": result['total_sent'],
                    "total_reminder_notifications": notification_result['total_notifications']
                }), 200
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/notifications/history', methods=['GET'])
def notification_history():
    """Get notification history"""
    try:
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
                notifications = cursor.fetchall()
                
                # Convert datetime to string
                for notification in notifications:
                    if notification.get('sent_at'):
                        notification['sent_at'] = notification['sent_at'].isoformat()
                
                return jsonify({
                    "success": True,
                    "count": len(notifications),
                    "notifications": notifications
                }), 200
        finally:
            connection.close()
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8083))
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down and NotificationService shutting down")

