"""
File upload controller - Handle document file uploads
"""
import os
from flask import request, current_app
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename
from middleware import admin_required

# Create namespace
upload_ns = Namespace('upload', description='File upload operations')

# Allowed extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    """Check if image extension is allowed"""
    IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS


@upload_ns.route('/document')
class UploadDocument(Resource):
    """Document file upload endpoint"""
    
    @admin_required
    @upload_ns.doc(description='Upload document file (PDF, DOC, DOCX)', security='Bearer')
    def post(self, current_user):
        """Upload document file"""
        
        # Check if file is in request
        if 'file' not in request.files:
            return {
                'success': False,
                'message': 'No file provided'
            }, 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return {
                'success': False,
                'message': 'No file selected'
            }, 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return {
                'success': False,
                'message': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }, 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Generate unique filename
        import uuid
        from datetime import datetime
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
        
        # Save file
        upload_folder = config['development'].UPLOAD_FOLDER
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Generate file URL
        file_url = f"/uploads/documents/{unique_filename}"
        
        return {
            'success': True,
            'message': 'File uploaded successfully',
            'data': {
                'filename': unique_filename,
                'original_filename': filename,
                'file_url': file_url,
                'file_type': file_ext,
                'file_size': os.path.getsize(file_path)
            }
        }, 201


@upload_ns.route('/document/<string:filename>')
class DeleteDocument(Resource):
    """Delete uploaded document"""
    
    @admin_required
    @upload_ns.doc(description='Delete uploaded document file', security='Bearer')
    def delete(self, current_user, filename):
        """Delete document file"""
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, secure_filename(filename))
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'message': 'File not found'
            }, 404
        
        try:
            os.remove(file_path)
            return {
                'success': True,
                'message': 'File deleted successfully'
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting file: {str(e)}'
            }, 500


@upload_ns.route('/image')
class UploadImage(Resource):
    """Image upload endpoint"""
    
    @admin_required
    @upload_ns.doc(description='Upload image file (JPG, PNG, etc).', security='Bearer')
    def post(self, current_user):
        """Upload image file"""
        
        if 'file' not in request.files:
            return {'success': False, 'message': 'No file provided'}, 400
        
        file = request.files['file']
        
        if file.filename == '':
            return {'success': False, 'message': 'No file selected'}, 400
            
        if not allowed_image(file.filename):
            return {'success': False, 'message': 'Invalid image type'}, 400
            
        filename = secure_filename(file.filename)
        import uuid
        from datetime import datetime
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
        
        # Save to uploads/documents/images for organization
        upload_folder = current_app.config['UPLOAD_FOLDER']
        images_folder = os.path.join(upload_folder, 'images')
        os.makedirs(images_folder, exist_ok=True)
        
        file_path = os.path.join(images_folder, unique_filename)
        file.save(file_path)
        
        # Return URL relative to /uploads/documents mount point
        # Since main.py strips /uploads/documents/, we need path INSIDE UPLOAD_FOLDER
        # URL: /uploads/documents/images/filename.jpg
        file_url = f"/uploads/documents/images/{unique_filename}"
        
        return {
            'success': True,
            'message': 'Image uploaded successfully',
            'data': {
                'filename': unique_filename,
                'file_url': file_url
            }
        }, 201
