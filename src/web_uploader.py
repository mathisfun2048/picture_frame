# src/web_uploader.py

from flask import Flask, render_template, request, redirect, url_for, flash
import os
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'picture_frame_secret_key_change_this'  # For flash messages

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / 'images' / 'queue'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page - show upload form and current images"""
    # Get list of images in queue
    images = []
    if UPLOAD_FOLDER.exists():
        images = [f for f in UPLOAD_FOLDER.iterdir() if f.is_file() and allowed_file(f.name)]
        images.sort()
    
    return render_template('upload.html', 
                          images=images, 
                          image_count=len(images))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'files[]' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files[]')
    uploaded = 0
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(UPLOAD_FOLDER / filename)
            uploaded += 1
    
    if uploaded > 0:
        flash(f'Successfully uploaded {uploaded} file(s)!', 'success')
    else:
        flash('No valid files uploaded', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete/<filename>')
def delete_file(filename):
    """Delete a file from the queue"""
    filename = secure_filename(filename)
    file_path = UPLOAD_FOLDER / filename
    
    if file_path.exists():
        file_path.unlink()
        flash(f'Deleted {filename}', 'success')
    else:
        flash(f'File not found: {filename}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
