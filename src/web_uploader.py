# src/web_uploader.py

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path
import time

app = Flask(__name__)
app.secret_key = 'picture_frame_secret_key_change_this'
auth = HTTPBasicAuth()

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / 'images' / 'queue'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

STATE_FILE = PROJECT_ROOT / 'current_state.json'
AUTH_FILE = PROJECT_ROOT / 'config' / 'web_auth.json'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Load authentication credentials
def load_auth():
    try:
        with open(AUTH_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"username": "admin", "password": "changeme"}

credentials = load_auth()

@auth.verify_password
def verify_password(username, password):
    if username == credentials['username'] and password == credentials['password']:
        return username
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_image():
    """Get currently displaying image from state file"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get('current_image')
    except:
        pass
    return None

def get_image_list():
    """Get sorted list of images"""
    if UPLOAD_FOLDER.exists():
        images = [f for f in UPLOAD_FOLDER.iterdir() if f.is_file() and allowed_file(f.name)]
        images.sort()
        return images
    return []

@app.route('/')
@auth.login_required
def index():
    """Main page"""
    images = get_image_list()
    current_image = get_current_image()
    
    # Convert to simple names for template
    image_names = [img.name for img in images]
    current_name = Path(current_image).name if current_image else None
    
    return render_template('upload.html', 
                          images=image_names,
                          current_image=current_name,
                          image_count=len(images))

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    """Handle file uploads with validation"""
    if 'files[]' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files[]')
    uploaded = 0
    errors = []
    
    for file in files:
        if file and file.filename:
            # Validate file type
            if not allowed_file(file.filename):
                errors.append(f'{file.filename}: Invalid file type (use jpg, png, or heic)')
                continue
            
            # Validate file size
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            
            if size > MAX_FILE_SIZE:
                errors.append(f'{file.filename}: File too large (max 20MB)')
                continue
            
            # Save file
            filename = secure_filename(file.filename)
            file.save(UPLOAD_FOLDER / filename)
            uploaded += 1
    
    # Show results
    if uploaded > 0:
        flash(f'Successfully uploaded {uploaded} photo(s)!', 'success')
    if errors:
        for error in errors:
            flash(error, 'error')
    if uploaded == 0 and not errors:
        flash('No valid files uploaded', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete/<filename>')
@auth.login_required
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

@app.route('/reorder', methods=['POST'])
@auth.login_required
def reorder():
    """Reorder images by renaming with numeric prefixes"""
    try:
        data = request.get_json()
        new_order = data.get('order', [])
        
        # Rename files with numeric prefixes
        for idx, filename in enumerate(new_order):
            old_path = UPLOAD_FOLDER / secure_filename(filename)
            if old_path.exists():
                # Create temp name to avoid conflicts
                temp_name = f"_temp_{idx:04d}_{filename}"
                temp_path = UPLOAD_FOLDER / temp_name
                old_path.rename(temp_path)
        
        # Rename from temp to final
        for idx, filename in enumerate(new_order):
            temp_name = f"_temp_{idx:04d}_{filename}"
            temp_path = UPLOAD_FOLDER / temp_name
            if temp_path.exists():
                # Remove old numeric prefix if exists
                clean_name = filename.lstrip('0123456789_')
                new_name = f"{idx:04d}_{clean_name}"
                new_path = UPLOAD_FOLDER / new_name
                temp_path.rename(new_path)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    

@app.route('/image/<filename>')
@auth.login_required
def serve_image(filename):
    """Serve an image file"""
    filename = secure_filename(filename)
    file_path = UPLOAD_FOLDER / filename
    
    if file_path.exists():
        return send_file(file_path, mimetype='image/jpeg')
    return "Image not found", 404

@app.route('/current-image')
@auth.login_required
def get_current_image_preview():
    """Get the currently displaying image"""
    current = get_current_image()
    if current:
        return send_file(current, mimetype='image/jpeg')
    return "No image currently displaying", 404

@app.route('/status')
@auth.login_required
def get_status():
    """Get current status as JSON for live updates"""
    images = get_image_list()
    current_image = get_current_image()
    current_name = Path(current_image).name if current_image else None
    
    return jsonify({
        'current_image': current_name,
        'image_count': len(images),
        'images': [img.name for img in images],
        'timestamp': time.time()
    })

@app.route('/stream')
@auth.login_required
def stream():
    """Server-Sent Events stream for live updates (no auth to prevent blocking)"""
    def event_stream():
        # Check auth via query parameter
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            yield f"data: {json.dumps({'error': 'unauthorized'})}\n\n"
            return
        
        last_image = None
        last_timestamp = 0
        
        while True:
            try:
                # Read state file
                if STATE_FILE.exists():
                    with open(STATE_FILE, 'r') as f:
                        state = json.load(f)
                        current_image = state.get('current_image')
                        timestamp = state.get('timestamp', 0)
                        
                        if current_image:
                            current_name = Path(current_image).name
                            
                            # Send update if image changed OR timestamp changed
                            if current_name != last_image or timestamp != last_timestamp:
                                last_image = current_name
                                last_timestamp = timestamp
                                
                                data = json.dumps({
                                    'current_image': current_name,
                                    'timestamp': timestamp
                                })
                                yield f"data: {data}\n\n"
                
                time.sleep(1)  # Check every second for faster updates
                
            except Exception as e:
                logger.error(f"SSE stream error: {e}")
                time.sleep(2)
    
    response = Response(event_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)