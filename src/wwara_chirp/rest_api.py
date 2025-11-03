#!/usr/bin/env python
"""
WWARA CHIRP REST API

This module provides a REST interface for converting WWARA repeater data
to CHIRP format. It exposes the existing conversion functionality via HTTP
endpoints for web-based usage.

Author: Tom Sayles, KE4HET, with assistance from GitHub Copilot
License: GPL-3.0 License (see LICENSE file)
"""

import io
import logging
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from wwara_chirp.chirpvalidator import ChirpValidator
from wwara_chirp.version import __version__

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web browser access

# In-memory storage for temporary files (in production, use proper storage)
temp_files = {}
TEMP_FILE_TTL = timedelta(hours=1)  # Temp files expire after 1 hour

def cleanup_expired_files():
    """Remove expired temporary files"""
    current_time = datetime.now()
    expired_keys = [
        key for key, (_, timestamp) in temp_files.items()
        if current_time - timestamp > TEMP_FILE_TTL
    ]
    for key in expired_keys:
        temp_files.pop(key, None)

def convert_wwara_to_chirp_data(wwara_csv_content):
    """
    Convert WWARA CSV content to CHIRP CSV format.
    
    Args:
        wwara_csv_content (str): CSV content as string
        
    Returns:
        tuple: (success: bool, result: str or pandas.DataFrame, error_msg: str)
    """
    try:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_temp:
            input_temp.write(wwara_csv_content)
            input_temp_path = input_temp.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as output_temp:
            output_temp_path = output_temp.name
            
        try:
            # Import required modules for conversion
            from wwara_chirp.wwara_chirp import process_row, write_output_file, CHIRP_COLUMNS
            
            # Initialize conversion variables
            channel = 0
            chirp_table = pd.DataFrame()
            
            validator = ChirpValidator()
            
            # Validate input file
            if not validator.validate_input_file(input_temp_path):
                return False, None, "Invalid input CSV format"
                
            # Read and process the CSV data
            df = pd.read_csv(input_temp_path, skiprows=[0])
            
            # Process each row
            for index, wwara_row in df.iterrows():
                # Temporarily set global channel variable
                import wwara_chirp.wwara_chirp as wwara_module
                wwara_module.channel = channel
                
                chirp_row = process_row(wwara_row)
                
                if not validator.validate_row(chirp_row):
                    log.warning(f'Invalid row data at location: {chirp_row["Location"]}')
                    continue
                    
                chirp_row_to_frame = chirp_row.to_frame().T
                if chirp_table.empty:
                    chirp_table = chirp_row_to_frame
                else:
                    chirp_table = pd.concat([chirp_table, chirp_row_to_frame], ignore_index=True)
                    
                channel += 1
            
            # Convert to CSV string
            converted_csv = chirp_table.to_csv(index=False)
            return True, converted_csv, None
            
        finally:
            # Clean up temporary files
            Path(input_temp_path).unlink(missing_ok=True)
            Path(output_temp_path).unlink(missing_ok=True)
            
    except Exception as e:
        log.error(f"Conversion error: {str(e)}")
        return False, None, str(e)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': __version__,
        'service': 'wwara-chirp-rest-api'
    })

@app.route('/api/convert', methods=['POST'])
def convert_data():
    """
    Convert WWARA CSV data to CHIRP format.
    
    Accepts:
    - File upload (multipart/form-data with 'file' field)
    - Raw CSV data (text/csv or application/json with 'csv_data' field)
    
    Returns:
    - JSON with converted CSV data
    - Or download link for large files
    """
    cleanup_expired_files()
    
    try:
        wwara_csv_content = None
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Check file extension
            if not file.filename.lower().endswith('.csv'):
                return jsonify({'error': 'File must be a CSV file'}), 400
                
            wwara_csv_content = file.read().decode('utf-8')
            
        # Handle raw CSV data
        elif request.content_type == 'text/csv':
            wwara_csv_content = request.get_data(as_text=True)
            
        # Handle JSON with CSV data
        elif request.is_json:
            json_data = request.get_json()
            if 'csv_data' not in json_data:
                return jsonify({'error': 'Missing csv_data field in JSON'}), 400
            wwara_csv_content = json_data['csv_data']
            
        else:
            return jsonify({
                'error': 'Unsupported content type. Send CSV file, raw CSV data, or JSON with csv_data field.'
            }), 400
            
        if not wwara_csv_content:
            return jsonify({'error': 'No CSV data provided'}), 400
            
        # Convert the data
        success, result, error_msg = convert_wwara_to_chirp_data(wwara_csv_content)
        
        if not success:
            return jsonify({'error': f'Conversion failed: {error_msg}'}), 500
            
        # For small files, return data directly
        if len(result) < 10 * 1024 * 1024:  # 10MB limit for direct response
            return jsonify({
                'status': 'success',
                'chirp_csv': result,
                'size_bytes': len(result)
            })
        else:
            # For large files, store temporarily and return download link
            file_id = str(uuid.uuid4())
            temp_files[file_id] = (result, datetime.now())
            
            return jsonify({
                'status': 'success',
                'download_url': f'/api/download/{file_id}',
                'size_bytes': len(result),
                'expires_in_seconds': int(TEMP_FILE_TTL.total_seconds())
            })
            
    except Exception as e:
        log.error(f"API error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download converted CSV file by ID"""
    cleanup_expired_files()
    
    if file_id not in temp_files:
        return jsonify({'error': 'File not found or expired'}), 404
        
    csv_content, _ = temp_files[file_id]
    
    # Create a file-like object from the CSV content
    csv_buffer = io.BytesIO(csv_content.encode('utf-8'))
    
    # Remove the file after serving (one-time download)
    temp_files.pop(file_id, None)
    
    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name='wwara-chirp-converted.csv',
        mimetype='text/csv'
    )

@app.route('/api/validate', methods=['POST'])
def validate_data():
    """
    Validate WWARA CSV data format.
    
    Returns validation results without conversion.
    """
    try:
        wwara_csv_content = None
        
        # Handle different input types (same as convert endpoint)
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            wwara_csv_content = file.read().decode('utf-8')
            
        elif request.content_type == 'text/csv':
            wwara_csv_content = request.get_data(as_text=True)
            
        elif request.is_json:
            json_data = request.get_json()
            if 'csv_data' not in json_data:
                return jsonify({'error': 'Missing csv_data field in JSON'}), 400
            wwara_csv_content = json_data['csv_data']
            
        else:
            return jsonify({
                'error': 'Unsupported content type. Send CSV file, raw CSV data, or JSON with csv_data field.'
            }), 400
            
        if not wwara_csv_content:
            return jsonify({'error': 'No CSV data provided'}), 400
            
        # Create temporary file for validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(wwara_csv_content)
            temp_file_path = temp_file.name
            
        try:
            validator = ChirpValidator()
            is_valid = validator.validate_input_file(temp_file_path)
            
            # Basic CSV structure validation
            df = pd.read_csv(temp_file_path, skiprows=[0])
            row_count = len(df)
            
            return jsonify({
                'status': 'validation_complete',
                'is_valid': is_valid,
                'row_count': row_count,
                'message': 'Valid WWARA CSV format' if is_valid else 'Invalid CSV format or structure'
            })
            
        finally:
            Path(temp_file_path).unlink(missing_ok=True)
            
    except Exception as e:
        log.error(f"Validation error: {str(e)}")
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information and usage"""
    return jsonify({
        'service': 'WWARA CHIRP REST API',
        'version': __version__,
        'description': 'Convert WWARA repeater CSV data to CHIRP format via REST API',
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/info': 'API information',
            'POST /api/validate': 'Validate WWARA CSV format',
            'POST /api/convert': 'Convert WWARA CSV to CHIRP format',
            'GET /api/download/<id>': 'Download converted file'
        },
        'input_formats': [
            'File upload (multipart/form-data with file field)',
            'Raw CSV data (Content-Type: text/csv)',
            'JSON with csv_data field'
        ],
        'example_usage': {
            'curl_file_upload': 'curl -X POST -F "file=@wwara-data.csv" http://localhost:5000/api/convert',
            'curl_raw_csv': 'curl -X POST -H "Content-Type: text/csv" --data-binary @wwara-data.csv http://localhost:5000/api/convert',
            'curl_json': 'curl -X POST -H "Content-Type: application/json" -d \'{"csv_data":"...csv content..."}\' http://localhost:5000/api/convert'
        }
    })

def create_app():
    """Factory function to create Flask app"""
    return app

def run_server(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask development server"""
    log.info(f"Starting WWARA CHIRP REST API server on {host}:{port}")
    log.info(f"API documentation available at: http://{host}:{port}/api/info")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server(debug=True)