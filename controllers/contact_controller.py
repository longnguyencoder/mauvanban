"""
Contact controller - Handle contact form submissions
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_mail import Message
from models import mail
import threading

contact_ns = Namespace('contact', description='Contact operations')

contact_model = contact_ns.model('Contact', {
    'name': fields.String(required=True),
    'email': fields.String(required=True),
    'subject': fields.String(required=True),
    'message': fields.String(required=True)
})

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")

@contact_ns.route('')
class Contact(Resource):
    @contact_ns.expect(contact_model)
    def post(self):
        """Send contact email"""
        data = request.json
        
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message_body = data.get('message')
        
        # Configure message
        msg_subject = f"[MauVanBan Contact] {subject}"
        
        # Construct email body
        body = f"""
        New Contact Message from MauVanBan Website:
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        -------------------------------------------
        {message_body}
        -------------------------------------------
        """
        
        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        if not sender:
            # Fallback if not configured, though might fail sending
            sender = current_app.config.get('MAIL_USERNAME')

        # Recipient is usually the admin/support email. 
        # User implies the sender is MAIL_USERNAME/SENDER.
        # We send TO the support email (which might be the same as sender or different).
        # Assuming we send TO the default sender (admin) FROM the system.
        # Or better: Send TO configured support email.
        # I'll assumme we send TO the MAIL_USERNAME (admin) for now.
        recipient = current_app.config.get('MAIL_USERNAME')
        
        msg = Message(
            subject=msg_subject,
            sender=sender, # Must match authenticated user usually
            recipients=[recipient],
            body=body,
            reply_to=email
        )
        
        # Send async
        # We need the real app object for async context
        # Flask-Mail usually works better with Celery but threading is okay for simple use
        app = current_app._get_current_object()
        thr = threading.Thread(target=send_async_email, args=[app, msg])
        thr.start()
        
        return {
            'success': True,
            'message': 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất.'
        }, 200
