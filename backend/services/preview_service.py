"""
Preview service for generating document previews
"""
import os
import logging
from config import config
# from pdf2image import convert_from_path # Replaced by fitz
import io
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

from flask import current_app

class PreviewService:
    """Service to handle preview generation"""
    
    @staticmethod
    def generate_preview(file_path, original_filename):
        """
        Generate preview image for a document
        
        Args:
            file_path: Absolute path to the file
            original_filename: Original filename to extract extension
            
        Returns:
            str: Relative URL to the preview image, or None if not possible
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        
        if file_ext == 'pdf':
            return PreviewService._generate_pdf_preview(file_path)
        
        # For other file types, we might return a default icon or look for a way to preview later
        # For now, only PDF is supported for visual preview
        return None
    
    @staticmethod
    def _generate_pdf_preview(file_path):
        """Generate preview for PDF (Page 1 with Blur) using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
            
            # 1. Open PDF
            doc = fitz.open(file_path)
            if doc.page_count < 1:
                return None
                
            # 2. Get first page
            page = doc.load_page(0)
            
            # 3. Render page to image (pixmap)
            # matrix=fitz.Matrix(2, 2) for higher resolution (optional)
            pix = page.get_pixmap(alpha=False) 
            
            # 4. Convert to PIL Image
            img_data = pix.tobytes("ppm")
            image = Image.open(io.BytesIO(img_data))
            
            doc.close()
            
            # 5. Add Watermark (Logo)
            try:
                # Load watermark
                watermark_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'watermark.png')
                if os.path.exists(watermark_path):
                    watermark = Image.open(watermark_path).convert("RGBA")
                    
                    # Calculate size (e.g., 50% of page width)
                    target_width = int(image.width * 0.5)
                    ratio = target_width / float(watermark.width)
                    target_height = int(watermark.height * ratio)
                    
                    watermark = watermark.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # Calculate position (Center)
                    x = int((image.width - target_width) / 2)
                    y = int((image.height - target_height) / 2)
                    
                    # Create transparent layer for watermark
                    transparent = Image.new('RGBA', image.size, (0,0,0,0))
                    transparent.paste(watermark, (x, y))
                    
                    # Ensure original is compatible
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                        
                    watermarked_image = Image.alpha_composite(image, transparent)
                    
                    # Convert back to RGB for JPEG saving
                    final_image = watermarked_image.convert('RGB')
                else:
                    logger.warning("Watermark file not found, skipping watermark.")
                    final_image = image  # No watermark
            
            except Exception as wm_error:
                logger.error(f"Failed to apply watermark: {wm_error}")
                final_image = image # Fallback to original
            
            # 6. Save preview image
            # Use runtime config from current_app
            upload_folder = current_app.config['UPLOAD_FOLDER']
            previews_folder = os.path.join(upload_folder, 'previews')
            os.makedirs(previews_folder, exist_ok=True)
            
            filename = os.path.basename(file_path)
            preview_filename = f"{os.path.splitext(filename)[0]}_preview.jpg"
            preview_path = os.path.join(previews_folder, preview_filename)
            
            # Save as JPEG with high quality
            final_image.save(preview_path, 'JPEG', quality=90)
            
            # Construct return URL relative to uploads folder
            # Assuming UPLOAD_FOLDER is like 'uploads/documents' or '/var/www/.../uploads/documents'
            # We want to return /uploads/documents/previews/...
            # To be safe, let's keep it consistent with the existing serving route: /uploads/documents/<filename>
            return f"/uploads/documents/previews/{preview_filename}"
            
        except Exception as e:
            logger.error(f"Error generating PDF preview: {str(e)}")
            return None
