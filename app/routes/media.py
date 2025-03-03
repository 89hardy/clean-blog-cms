import os
from flask import Blueprint, request, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image
from config.config import Config

media = Blueprint('media', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def optimize_image(image_path):
    """Optimize the image for web use."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions while maintaining aspect ratio
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with optimized settings
            img.save(image_path, 'JPEG', quality=85, optimize=True)
    except Exception as e:
        print(f"Error optimizing image: {e}")

@media.route('/upload', methods=['POST'])
@login_required
def upload():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.IMAGES_PATH, filename)
        
        # Save the file
        file.save(filepath)
        
        # Optimize the image
        optimize_image(filepath)
        
        # Return the URL for the saved file
        return jsonify({
            'location': f'/assets/images/{filename}',
            'filename': filename
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@media.route('/images', methods=['GET'])
@login_required
def list_images():
    """List all uploaded images."""
    images = []
    if os.path.exists(Config.IMAGES_PATH):
        for filename in os.listdir(Config.IMAGES_PATH):
            if allowed_file(filename):
                images.append({
                    'url': f'/assets/images/{filename}',
                    'filename': filename
                })
    return jsonify(images) 