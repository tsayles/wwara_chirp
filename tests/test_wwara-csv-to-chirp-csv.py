import sys
import os
import pandas as pd

# Add the module's directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wwara_csv_to_chirp_csv import validate_input_file, validate_output_file, process_row

# Test to check that the validate_input_file function works
def test_validate_input_file():
    assert validate_input_file('test.csv') == True
    assert validate_input_file('test.txt') == False
    assert validate_input_file('test') == False
    assert validate_input_file('') == False

# Test to check that the validate_output_file function works
def test_validate_output_file():
    assert validate_output_file('test.csv') == True
    assert validate_output_file('test.txt') == False
    assert validate_output_file('test') == False
    assert validate_output_file('') == False

# Test to check that the process_row function works
def test_process_row():
    wwara_row = pd.Series({
        'LOCALE': 'Seattle',
        'SPONSOR': 'WWARA',
        'LINK': 'Yes',
        'URL': 'http://example.com',
        'EXPIRATION_DATE': '2024-12-31',
        'LATITUDE': '47.6062',
        'LONGITUDE': '-122.3321',
        'ARES': 'Y',
        'RACES': 'Y',
        'WX': 'Y',
        'DMR_COLOR_CODE': '1',
        'FUSION_DSQ': '123',
        'NXDN_DIGITAL': 'Y',
        'NXDN_MIXED': 'Y',
        'NXDN_RAN': '2',
        'ATV': 'Y',
        'DATV': 'Y'
    })
    chirp_row = process_row(wwara_row)
    assert chirp_row['Location'] == 0
    assert chirp_row['Name'] == ''
    assert chirp_row['Frequency'] == '0.000000'
    assert chirp_row['Duplex'] == ''
    assert chirp_row['Offset'] == '0.000000'
    assert chirp_row['Tone'] == ''
    assert chirp_row['rToneFreq'] == '88.5'
    assert chirp_row['cToneFreq'] == '88.5'
    assert chirp_row['DtcsCode'] == 0
    assert chirp_row['DtcsPolarity'] == ''
    assert chirp_row['RxDtcsCode'] == '023'
    assert chirp_row['CrossMode'] == 'Tone->Tone'
    assert chirp_row['Mode'] == ''
    assert chirp_row['TStep'] == '5.00'
    assert chirp_row['Skip'] == ''
    assert chirp_row['Power'] == '5.0W'
    assert chirp_row['Comment'] == ' Seattle Sponsor: WWARA Link: Yes URL: http://example.com Expiration: 2024-12-31 Lat: 47.6062, Lon: -122.3321 ARES RACES WX DMR Color Code: 1 Fusion DSQ: 123 NXDN Digital NXDN Mixed NXDN RAN: 2 ATV DATV'
    assert chirp_row['URCALL'] == ''
    assert chirp_row['RPT1CALL'] == ''
    assert chirp_row['RPT2CALL'] == ''
    assert chirp_row['DVCODE'] == ''