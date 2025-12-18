"""
Main application file - Flask REST API for Document Management System
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db, migrate
from controllers import api


def create_app(config_name='development'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    from models import mail
    mail.init_app(app)
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
    JWTManager(app)
    
    # Initialize API
    api.init_app(app)
    
    # Create upload folder if not exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Serve uploaded files
    @app.route('/uploads/documents/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded document files"""
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Health check endpoint
    @app.route('/')
    def index():
        return {
            'success': True,
            'message': 'Mẫu Văn Bản API is running',
            'version': '1.0',
            'docs': '/api/docs'
        }
    
    @app.route('/health')
    def health():
        return {
            'success': True,
            'status': 'healthy'
        }
    
    # Custom JSON Provider for Decimal serialization
    from flask.json.provider import DefaultJSONProvider
    from decimal import Decimal

    class CustomJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super().default(obj)

    app.json = CustomJSONProvider(app)

    return app


if __name__ == '__main__':
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(env)
    
    # Run app
    port = int(os.getenv('PORT', 5000))
    debug = env == 'development'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           Mẫu Văn Bản API - Document Management          ║
    ║                                                           ║
    ║   Environment: {env:^42} ║
    ║   Port:        {port:^42} ║
    ║   Debug:       {str(debug):^42} ║
    ║                                                           ║
    ║   API Docs:    http://localhost:{port}/api/docs{' ' * (42 - len(str(port)) - 26)} ║
    ║   Health:      http://localhost:{port}/health{' ' * (42 - len(str(port)) - 24)} ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
