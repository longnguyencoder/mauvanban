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
    @app.route('/api/uploads/documents/<path:filename>')  # Fix for Double API Frontend issue
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
    @app.route('/api/health')
    def health():
        return {
            'success': True,
            'status': 'healthy'
        }
    
    # Sitemap generation
    @app.route('/sitemap.xml')
    @app.route('/api/sitemap.xml')
    def sitemap():
        """Generate dynamic sitemap.xml"""
        from models import Document, Category
        from flask import make_response
        from datetime import datetime
        
        frontend_url = app.config.get('FRONTEND_URL', 'https://mauvanban.zluat.vn')
        
        # 1. Static pages
        pages = [
            {'loc': f"{frontend_url}/", 'changefreq': 'daily', 'priority': '1.0'},
            {'loc': f"{frontend_url}/documents", 'changefreq': 'daily', 'priority': '0.9'},
            {'loc': f"{frontend_url}/categories", 'changefreq': 'weekly', 'priority': '0.8'},
            {'loc': f"{frontend_url}/contact", 'changefreq': 'monthly', 'priority': '0.7'},
        ]
        
        # 2. Add Documents
        try:
            documents = Document.query.filter_by(is_active=True).all()
            for doc in documents:
                # Use slug if available, else ID
                doc_path = f"/documents/{doc.slug or doc.id}" if hasattr(doc, 'slug') and doc.slug else f"/documents/{doc.id}"
                lastmod = doc.updated_at.strftime('%Y-%m-%dT%H:%M:%S+07:00') if hasattr(doc, 'updated_at') and doc.updated_at else datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00')
                
                pages.append({
                    'loc': f"{frontend_url}{doc_path}",
                    'lastmod': lastmod,
                    'changefreq': 'weekly',
                    'priority': '0.8'
                })
        except Exception as e:
            app.logger.error(f"Error generating sitemap documents: {e}")

        # 3. Add Categories
        try:
            categories = Category.query.all()
            for cat in categories:
                pages.append({
                    'loc': f"{frontend_url}/documents?category={cat.id}",
                    'changefreq': 'weekly',
                    'priority': '0.7'
                })
        except Exception as e:
            app.logger.error(f"Error generating sitemap categories: {e}")

        # Build XML
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for page in pages:
            xml += '  <url>\n'
            xml += f'    <loc>{page["loc"]}</loc>\n'
            if 'lastmod' in page:
                xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
            xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
            xml += f'    <priority>{page["priority"]}</priority>\n'
            xml += '  </url>\n'
        xml += '</urlset>'
        
        response = make_response(xml)
        response.headers['Content-Type'] = 'application/xml'
        return response
    
    # Custom JSON Provider for Decimal and UUID serialization
    from flask.json.provider import DefaultJSONProvider
    from decimal import Decimal
    from uuid import UUID

    class CustomJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, UUID):
                return str(obj)
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
