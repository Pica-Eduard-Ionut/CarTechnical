import smtplib
from email.mime.text import MIMEText

# Gmail SMTP settings
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_username = "pasaroiumihai2003@gmail.com"
smtp_password = 'xkocglnakrovhkdf' # App Password
from_email = "pasaroiumihai2003@gmail.com"
to_email = "pasaroiumihai2003@gmail.com"

print(f"Testing SMTP connection to {smtp_host}:{smtp_port}...")
print(f"Username: {smtp_username}")
print(f"Password length: {len(smtp_password)} characters")
print(f"Password (first 4 chars): {smtp_password[:4]}...")

try:
    # Create a test message
    msg = MIMEText("This is a test email from NotificationService")
    msg['Subject'] = "Test Email - SMTP Connection"
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Connect to SMTP server
    print("\n1. Connecting to SMTP server...")
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    
    print("2. Starting TLS...")
    server.starttls()
    
    print("3. Logging in...")
    server.login(smtp_username, smtp_password)
    
    print("4. Sending email...")
    server.sendmail(from_email, to_email, msg.as_string())
    
    print("5. Closing connection...")
    server.quit()
    
    print("\n✅ SUCCESS! Email sent successfully!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION ERROR: {e}")
    print("\nMake sure you're using a Gmail App Password, not your regular password.")
    print("Get one at: https://myaccount.google.com/apppasswords")
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP ERROR: {e}")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
