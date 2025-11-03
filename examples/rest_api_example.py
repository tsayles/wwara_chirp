#!/usr/bin/env python
"""
Example script demonstrating WWARA CHIRP REST API usage

This script shows how to use the REST API for converting WWARA repeater data
to CHIRP format through various methods.
"""

import requests
import sys

def test_rest_api(base_url="http://localhost:5000"):
    """Test the REST API endpoints"""
    
    print("=" * 60)
    print("WWARA CHIRP REST API Example")
    print("=" * 60)
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✓ Service is healthy: {health['service']} v{health['version']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to REST API server")
        print("  Please start the server with: python -c \"from wwara_chirp.rest_api import run_server; run_server()\"")
        return
    
    # Test API info
    print("\n2. Getting API information...")
    response = requests.get(f"{base_url}/api/info")
    if response.status_code == 200:
        info = response.json()
        print(f"✓ Service: {info['service']}")
        print("✓ Available endpoints:")
        for endpoint, description in info['endpoints'].items():
            print(f"   {endpoint}: {description}")
    
    # Sample WWARA CSV data for testing
    sample_data = '''DATA_SPEC_VERSION=2015.2.2
"FC_RECORD_ID","SOURCE","OUTPUT_FREQ","INPUT_FREQ","STATE","CITY","LOCALE","CALL","SPONSOR","CTCSS_IN","CTCSS_OUT","DCS_CDCSS","DTMF","LINK","FM_WIDE","FM_NARROW","DSTAR_DV","DSTAR_DD","DMR","DMR_COLOR_CODE","FUSION","FUSION_DSQ","P25_PHASE_1","P25_PHASE_2","P25_NAC","NXDN_DIGITAL","NXDN_MIXED","NXDN_RAN","ATV","DATV","RACES","ARES","WX","URL","LATITUDE","LONGITUDE","EXPIRATION_DATE","COMMENT"
" 1005","WWARA","146.9200","146.3200","WA","Seattle","PUGET SOUND","W7TEST","Test Group","103.5","103.5","","","","Y","N","N","N","N","","N","","N","N","","N","N","","N","N","N","N","N","http://example.com","47.6062","-122.3321","2026-02-28","Test repeater"'''
    
    # Test validation
    print("\n3. Testing CSV validation...")
    response = requests.post(f"{base_url}/api/validate", 
                           json={'csv_data': sample_data})
    if response.status_code == 200:
        validation = response.json()
        print(f"✓ Validation: {validation['message']}")
        print(f"✓ Row count: {validation['row_count']}")
    else:
        print(f"✗ Validation failed: {response.status_code}")
    
    # Test conversion
    print("\n4. Testing CSV conversion...")
    response = requests.post(f"{base_url}/api/convert", 
                           json={'csv_data': sample_data})
    if response.status_code == 200:
        conversion = response.json()
        if conversion['status'] == 'success':
            print(f"✓ Conversion successful!")
            print(f"✓ Output size: {conversion['size_bytes']} bytes")
            
            # Show first few lines of converted data
            if 'chirp_csv' in conversion:
                lines = conversion['chirp_csv'].split('\n')
                print("\n✓ First few lines of CHIRP CSV:")
                for i, line in enumerate(lines[:3]):
                    print(f"   {i+1}: {line}")
                print(f"   ... (total {len(lines)} lines)")
            elif 'download_url' in conversion:
                print(f"✓ Large file available for download at: {conversion['download_url']}")
        else:
            print(f"✗ Conversion failed: {conversion.get('error', 'Unknown error')}")
    else:
        print(f"✗ Conversion request failed: {response.status_code}")
        try:
            error = response.json()
            print(f"   Error: {error.get('error', 'Unknown error')}")
        except Exception:
            print(f"   Response: {response.text}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("\nTo use with a file:")
    print(f"  curl -X POST -F 'file=@your-wwara-file.csv' {base_url}/api/convert")
    print("\nTo use with raw CSV:")
    print(f"  curl -X POST -H 'Content-Type: text/csv' --data-binary @your-file.csv {base_url}/api/convert")
    print("=" * 60)

if __name__ == '__main__':
    # Allow custom base URL from command line
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    test_rest_api(base_url)