import os
from flask import Flask
from flask_mail import Mail, Message
from config import config
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def test_send_email():
    app = Flask(__name__)
    
    # Manually load config to be sure
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    _pwd = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_PASSWORD'] = _pwd.replace(' ', '') if _pwd else None
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

    print("--- EMAIL CONFIG ---")
    print(f"Server: {app.config['MAIL_SERVER']}")
    print(f"Port: {app.config['MAIL_PORT']}")
    print(f"Username: {app.config['MAIL_USERNAME']}")
    final_pwd = app.config['MAIL_PASSWORD']
    print(f"Password provided: {'Yes' if final_pwd else 'No'}")
    print(f"Password length: {len(final_pwd) if final_pwd else 0} (Should be 16)")
    print("--------------------")

    mail = Mail(app)

    with app.app_context():
        try:
            print("Attempting to send email...")
            msg = Message(
                subject="Test Email from MauVanBan",
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[app.config['MAIL_USERNAME']],
                body="This is a test email to verify SMTP configuration."
            )
            mail.send(msg)
            print("\n✅ Email sent successfully! Check your inbox.")
        except Exception as e:
            print("\n❌ Failed to send email.")
            print(f"Error: {e}")

if __name__ == "__main__":
    test_send_email()
