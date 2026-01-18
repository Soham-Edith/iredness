"""
Flask Application for Digital Eye Fatigue Analyzer
Provides web interface for uploading eye images and analyzing fatigue levels.
"""

import os
import cv2
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from digital_eye_fatigue_analyzer_api import DigitalEyeFatigueAnalyzerEye
# Flask app configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}

# Initialize analyzer
analyzer = DigitalEyeFatigueAnalyzerEye()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render main upload page."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Handle image upload and perform eye fatigue analysis.
    Returns JSON with redness, dryness, and fatigue scores.
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, BMP, GIF'
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Verify image can be loaded
        image = cv2.imread(filepath)
        if image is None:
            os.remove(filepath)
            return jsonify({'success': False, 'error': 'Invalid image file'}), 400
        
        # Get optional parameters
        screen_time = float(request.form.get('screen_time', 8.0))
        condition = request.form.get('condition', 'Normal')
        
        # Analyze image
        results = analyzer.analyze_image(filepath, screen_time_hours=screen_time, condition=condition)
        
        # Clean up temporary file
        try:
            os.remove(filepath)
        except:
            pass
        
        if results['success']:
            return jsonify({
                'success': True,
                'redness': results['redness'],
                'dryness': results['dryness'],
                'fatigue': results['fatigue']
            })
        else:
            return jsonify({
                'success': False,
                'error': results.get('error', 'Analysis failed')
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/results', methods=['GET'])
def results():
    """Render results page."""
    return render_template('result.html')


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeded error."""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size: 16MB'
    }), 413


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
