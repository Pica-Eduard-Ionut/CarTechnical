"""
Test script to seed the database with a test appointment
that will trigger a reminder in 1 minute (24 hours + 1 minute from now)
"""
import pymysql
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_test_appointment():
    """Seed database with a test appointment for reminder testing"""
    
    # RequestService database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'root'),
        'database': os.getenv('DB_NAME', 'requestservice'),
        'charset': 'utf8mb4'
    }
    
    # UserService database configuration
    user_db_config = {
        'host': os.getenv('USER_DB_HOST', 'localhost'),
        'port': int(os.getenv('USER_DB_PORT', '3306')),
        'user': os.getenv('USER_DB_USER', 'root'),
        'password': os.getenv('USER_DB_PASSWORD', 'root'),
        'database': os.getenv('USER_DB_NAME', 'userservice'),
        'charset': 'utf8mb4'
    }
    
    print("=" * 60)
    print("Seeding Test Appointment for Reminder Testing")
    print("=" * 60)
    
    # Calculate appointment time: 24 hours + 1 minute from now
    now = datetime.now()
    appointment_time = now + timedelta(hours=24, minutes=1)
    
    # Calculate when reminder will be sent (23-25 hour window)
    reminder_window_start = now + timedelta(hours=23)
    reminder_window_end = now + timedelta(hours=25)
    
    print(f"\nCurrent time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Appointment time: {appointment_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Reminder window: {reminder_window_start.strftime('%Y-%m-%d %H:%M:%S')} to {reminder_window_end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Appointment is {((appointment_time - now).total_seconds() / 3600):.2f} hours away")
    print(f"Reminder will be sent when appointment is 23-25 hours away (currently: ~1 minute)")
    
    try:
        # Step 1: Create or find test user in UserService database
        print("\n" + "=" * 60)
        print("Step 1: Setting up test user in UserService database")
        print("=" * 60)
        
        user_connection = pymysql.connect(**user_db_config)
        owner_id = None
        
        try:
            with user_connection.cursor() as cursor:
                # Check if test user exists
                test_email = "pasaroiumihai@yahoo.com"
                cursor.execute("SELECT id, name, email FROM users WHERE email = %s", (test_email,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    owner_id = existing_user[0]
                    print(f"✓ Found existing test user:")
                    print(f"  - ID: {owner_id}")
                    print(f"  - Name: {existing_user[1]}")
                    print(f"  - Email: {existing_user[2]}")
                else:
                    # Create test user
                    print("Creating new test user...")
                    import hashlib
                    
                    # Simple password hash (BCrypt would be better, but this works for testing)
                    password_hash = hashlib.sha256("test123".encode()).hexdigest()
                    
                    cursor.execute("""
                        INSERT INTO users (name, email, password_hash, role)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        "Test User",
                        test_email,
                        password_hash,
                        "OWNER"
                    ))
                    owner_id = cursor.lastrowid
                    user_connection.commit()
                    print(f"✓ Created test user:")
                    print(f"  - ID: {owner_id}")
                    print(f"  - Name: Test User")
                    print(f"  - Email: {test_email}")
                    print(f"  - Role: OWNER")
        finally:
            user_connection.close()
        
        if not owner_id:
            print("✗ Failed to create/find test user")
            return False
        
        # Step 2: Create test appointment in RequestService database
        print("\n" + "=" * 60)
        print("Step 2: Creating test appointment in RequestService database")
        print("=" * 60)
        
        # Connect to RequestService database
        print("\nConnecting to RequestService database...")
        connection = pymysql.connect(**db_config)
        
        try:
            with connection.cursor() as cursor:
                
                # Check for existing vehicle_id (optional)
                print("Checking for existing vehicles...")
                try:
                    cursor.execute("SELECT id FROM vehicles LIMIT 1")
                    vehicle_result = cursor.fetchone()
                    if vehicle_result:
                        vehicle_id = vehicle_result[0]
                        print(f"  Using existing vehicle_id: {vehicle_id}")
                    else:
                        vehicle_id = None
                        print("  No vehicles found, vehicle_id will be NULL")
                except:
                    vehicle_id = None
                    print("  Vehicles table not found or empty, vehicle_id will be NULL")
                
                # Insert test appointment
                print("\nInserting test appointment...")
                
                sql = """
                    INSERT INTO service_requests 
                    (owner_id, vehicle_id, requested_from, requested_to, 
                     service_type, priority, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    owner_id,
                    vehicle_id,
                    appointment_time,
                    appointment_time + timedelta(hours=2),  # requested_to: 2 hours after
                    'MAINTENANCE',  # service_type
                    'HIGH',  # priority
                    'CONFIRMED',  # status (not CANCELLED or COMPLETED)
                    now  # created_at
                )
                
                cursor.execute(sql, values)
                request_id = cursor.lastrowid
                connection.commit()
                
                print(f"\n✓ Test appointment created successfully!")
                print(f"\nAppointment Details:")
                print(f"  - Request ID: {request_id}")
                print(f"  - Owner ID: {owner_id}")
                print(f"  - Owner Email: pasaroiumihai@yahoo.com")
                print(f"  - Vehicle ID: {vehicle_id if vehicle_id else 'NULL'}")
                print(f"  - Appointment Time: {appointment_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  - Service Type: MAINTENANCE")
                print(f"  - Priority: HIGH")
                print(f"  - Status: CONFIRMED")
                
                print("\n" + "=" * 60)
                print("Next Steps:")
                print("=" * 60)
                print("1. Make sure NotificationService is running")
                print("2. Wait ~1 minute for the scheduler to run")
                print("3. Or manually trigger: curl -X POST http://localhost:8083/reminders/process")
                print("4. Check pasaroiumihai@yahoo.com for the reminder!")
                print("5. Check logs to see if reminder was sent")
                print("\nTo clean up test data:")
                print(f"  DELETE FROM service_requests WHERE id = {request_id};")
                print(f"  DELETE FROM users WHERE id = {owner_id};")
                print("Or run: python seed_test_appointment.py --cleanup")
                print("=" * 60)
                
        finally:
            connection.close()
            
    except pymysql.Error as e:
        print(f"\n✗ Database Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MariaDB is running")
        print("2. Check database credentials in .env file")
        print("3. Verify database name is 'requestservice'")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def cleanup_test_appointments():
    """Remove test appointments and users created by this script"""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'root'),
        'database': os.getenv('DB_NAME', 'requestservice'),
        'charset': 'utf8mb4'
    }
    
    user_db_config = {
        'host': os.getenv('USER_DB_HOST', 'localhost'),
        'port': int(os.getenv('USER_DB_PORT', '3306')),
        'user': os.getenv('USER_DB_USER', 'root'),
        'password': os.getenv('USER_DB_PASSWORD', 'root'),
        'database': os.getenv('USER_DB_NAME', 'userservice'),
        'charset': 'utf8mb4'
    }
    
    try:
        # Clean up test appointments
        print("Cleaning up test appointments...")
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, owner_id, requested_from, created_at 
                    FROM service_requests 
                    WHERE service_type = 'MAINTENANCE' 
                      AND priority = 'HIGH'
                      AND created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                    ORDER BY created_at DESC
                """)
                test_appointments = cursor.fetchall()
                
                if test_appointments:
                    print(f"Found {len(test_appointments)} test appointment(s):")
                    for apt in test_appointments:
                        print(f"  - ID: {apt[0]}, Owner: {apt[1]}, Appointment: {apt[2]}, Created: {apt[3]}")
                    
                    confirm = input("\nDelete these appointments? (yes/no): ")
                    if confirm.lower() == 'yes':
                        for apt in test_appointments:
                            cursor.execute("DELETE FROM service_requests WHERE id = %s", (apt[0],))
                        connection.commit()
                        print(f"✓ Deleted {len(test_appointments)} test appointment(s)")
                    else:
                        print("Cancelled")
                else:
                    print("No test appointments found")
        finally:
            connection.close()
        
        # Clean up test users
        print("\nCleaning up test users...")
        user_connection = pymysql.connect(**user_db_config)
        try:
            with user_connection.cursor() as cursor:
                cursor.execute("SELECT id, name, email FROM users WHERE email = 'pasaroiumihai@yahoo.com'")
                test_users = cursor.fetchall()
                
                if test_users:
                    print(f"Found {len(test_users)} test user(s):")
                    for user in test_users:
                        print(f"  - ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")
                    
                    confirm = input("\nDelete these test users? (yes/no): ")
                    if confirm.lower() == 'yes':
                        for user in test_users:
                            cursor.execute("DELETE FROM users WHERE id = %s", (user[0],))
                        user_connection.commit()
                        print(f"✓ Deleted {len(test_users)} test user(s)")
                    else:
                        print("Cancelled")
                else:
                    print("No test users found")
        finally:
            user_connection.close()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_test_appointments()
    else:
        success = seed_test_appointment()
        sys.exit(0 if success else 1)

