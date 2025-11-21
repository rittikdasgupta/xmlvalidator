"""
Flask Web Application for XML Validator
Provides a web UI for uploading and validating zip files containing XML.
"""
import os
import tempfile
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from xmlvalidator import XMLValidator

app = Flask(__name__)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['SECRET_KEY'] = os.urandom(24)
# Note: Uploaded files use tempfile.mkstemp() for unique, secure temporary files
# Extracted files use tempfile.mkdtemp() - both are automatically cleaned up

ALLOWED_EXTENSIONS = {'zip'}


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and validation."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    target_xml = request.form.get('target_xml', '').strip() or None
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Only ZIP files are allowed.'}), 400
    
    # Check Content-Length header if available (Flask's MAX_CONTENT_LENGTH will also enforce this)
    content_length = request.content_length
    if content_length and content_length > MAX_FILE_SIZE:
        return jsonify({
            'success': False, 
            'error': f'File size ({content_length / 1024 / 1024:.2f} MB) exceeds maximum allowed size of 50 MB.'
        }), 400
    
    # Create a unique temporary file for the uploaded ZIP
    # This ensures no filename conflicts and better security
    file_handle = None
    filepath = None
    
    try:
        # Create unique temporary file with .zip extension
        file_handle, filepath = tempfile.mkstemp(suffix='.zip', prefix='xmlvalidator_upload_')
        os.close(file_handle)  # Close the file handle, we'll use file.save() instead
        
        # Save uploaded file to the unique temp file
        file.save(filepath)
        
        # Process the zip file
        validator = XMLValidator(filepath)
        result = validator.process_zip(target_xml)
        
        # Clean up extracted files (uses temp directory automatically)
        validator.cleanup()
        
        # Format result for JSON response
        # Create a mapping of XML filenames to their timestamps
        xml_timestamps_dict = {}
        for xml_path, timestamp in result.get('xml_timestamps', {}).items():
            xml_filename = os.path.basename(xml_path)
            xml_timestamps_dict[xml_filename] = timestamp
        
        # Get the actual XML filename that was read (for display purposes)
        actual_xml_filename = result.get('xml_filename')
        if actual_xml_filename and actual_xml_filename in xml_timestamps_dict:
            # Use the actual filename from the result
            pass
        elif result.get('xml_files') and len(result['xml_files']) > 0:
            # Fallback to first XML file if no specific filename was set
            actual_xml_filename = os.path.basename(result['xml_files'][0])
        
        response = {
            'success': result['success'],
            'message': result['message'],
            'extracted_files': result['extracted_files'],
            'xml_files': [os.path.basename(f) for f in result['xml_files']],
            'xml_timestamps': xml_timestamps_dict,
            'xml_content': result['xml_content'],
            'xml_filename': actual_xml_filename
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing file: {str(e)}'}), 500
        
    finally:
        # Always clean up uploaded file, even if processing fails
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as cleanup_error:
                # Log cleanup errors but don't fail the request
                print(f"Warning: Could not cleanup temp file {filepath}: {cleanup_error}")


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle file size limit exceeded error."""
    return jsonify({
        'success': False,
        'error': 'File size exceeds maximum allowed size of 50 MB. Please upload a smaller file.'
    }), 413


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    # For development
    # In production, platforms like Render/Railway use gunicorn and set PORT env var
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
    # For production deployment, use: gunicorn app:app

