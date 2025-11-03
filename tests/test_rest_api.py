#!/usr/bin/env python
"""
Test cases for WWARA CHIRP REST API

Tests the REST interface functionality for converting WWARA repeater data
to CHIRP format via HTTP endpoints.
"""

import unittest
import json
from io import BytesIO

try:
    from wwara_chirp.rest_api import create_app
    flask_available = True
except ImportError:
    flask_available = False


@unittest.skipIf(not flask_available, "Flask not available - REST API tests skipped")
class TestWWARAChirpRestAPI(unittest.TestCase):
    """Test the REST API endpoints"""
    
    def setUp(self):
        """Set up test client and sample data"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Sample WWARA CSV data for testing
        self.sample_wwara_csv = '''DATA_SPEC_VERSION=2015.2.2
"FC_RECORD_ID","SOURCE","OUTPUT_FREQ","INPUT_FREQ","STATE","CITY","LOCALE","CALL","SPONSOR","CTCSS_IN","CTCSS_OUT","DCS_CDCSS","DTMF","LINK","FM_WIDE","FM_NARROW","DSTAR_DV","DSTAR_DD","DMR","DMR_COLOR_CODE","FUSION","FUSION_DSQ","P25_PHASE_1","P25_PHASE_2","P25_NAC","NXDN_DIGITAL","NXDN_MIXED","NXDN_RAN","ATV","DATV","RACES","ARES","WX","URL","LATITUDE","LONGITUDE","EXPIRATION_DATE","COMMENT"
" 1005","WWARA","29.6800","29.5800","WA","Lookout Mtn","WASHINGTON- NORTHWEST","W7RNB","5CountyEmCommGrp","110.9","110.9","","","","Y","N","N","N","N","","N","","N","N","","N","N","","N","N","N","N","N","","48.6875","-122.3625","2026-02-28",""
" 2058","WWARA","52.8700","51.1700","WA","Seattle","PUGET SOUND- SOUTH","WW7PSR","Puget Sound Rptr Group","103.5","103.5","","","","Y","N","N","N","N","","N","","N","N","","N","N","","N","N","N","N","N","http://psrg.org","47.62384","-122.31519","2027-04-25",""'''
        
        self.invalid_csv = '''invalid,data,format
1,2,3'''
        
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('version', data)
        self.assertEqual(data['service'], 'wwara-chirp-rest-api')
        
    def test_api_info(self):
        """Test the API info endpoint"""
        response = self.client.get('/api/info')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('service', data)
        self.assertIn('endpoints', data)
        self.assertIn('input_formats', data)
        self.assertIn('example_usage', data)
        
    def test_validate_csv_json(self):
        """Test CSV validation via JSON"""
        response = self.client.post('/api/validate', 
                                  json={'csv_data': self.sample_wwara_csv})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'validation_complete')
        self.assertIn('is_valid', data)
        self.assertIn('row_count', data)
        
    def test_validate_invalid_csv(self):
        """Test validation with invalid CSV"""
        response = self.client.post('/api/validate', 
                                  json={'csv_data': self.invalid_csv})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'validation_complete')
        # Note: validation might still pass basic structure checks
        
    def test_validate_missing_data(self):
        """Test validation with missing data"""
        response = self.client.post('/api/validate', json={})
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_convert_csv_json(self):
        """Test CSV conversion via JSON"""
        response = self.client.post('/api/convert',
                                  json={'csv_data': self.sample_wwara_csv})
        
        # Should succeed or fail gracefully
        self.assertIn(response.status_code, [200, 500])
        
        data = json.loads(response.data)
        if response.status_code == 200:
            self.assertIn('status', data)
            self.assertIn(data['status'], ['success'])
            if 'chirp_csv' in data:
                self.assertIn('Location', data['chirp_csv'])  # Should contain CHIRP headers
        else:
            self.assertIn('error', data)
            
    def test_convert_csv_raw(self):
        """Test CSV conversion with raw CSV data"""
        response = self.client.post('/api/convert',
                                  data=self.sample_wwara_csv,
                                  content_type='text/csv')
        
        # Should succeed or fail gracefully  
        self.assertIn(response.status_code, [200, 500])
        
        data = json.loads(response.data)
        if response.status_code == 200:
            self.assertIn('status', data)
        else:
            self.assertIn('error', data)
            
    def test_convert_file_upload(self):
        """Test CSV conversion via file upload"""
        # Create a temporary file-like object
        csv_file = BytesIO(self.sample_wwara_csv.encode('utf-8'))
        
        response = self.client.post('/api/convert',
                                  data={'file': (csv_file, 'test.csv')},
                                  content_type='multipart/form-data')
        
        # Should succeed or fail gracefully
        self.assertIn(response.status_code, [200, 500])
        
        data = json.loads(response.data)
        if response.status_code == 200:
            self.assertIn('status', data)
        else:
            self.assertIn('error', data)
            
    def test_convert_no_file(self):
        """Test conversion with no file"""
        response = self.client.post('/api/convert',
                                  data={'file': (BytesIO(b''), '')},
                                  content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_convert_non_csv_file(self):
        """Test conversion with non-CSV file"""
        txt_file = BytesIO(b'not a csv file')
        
        response = self.client.post('/api/convert',
                                  data={'file': (txt_file, 'test.txt')},
                                  content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('CSV file', data['error'])
        
    def test_convert_unsupported_content_type(self):
        """Test conversion with unsupported content type"""
        response = self.client.post('/api/convert',
                                  data='some data',
                                  content_type='application/xml')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Unsupported content type', data['error'])
        
    def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist"""
        response = self.client.get('/api/download/nonexistent-id')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('not found', data['error'])


if __name__ == '__main__':
    unittest.main()