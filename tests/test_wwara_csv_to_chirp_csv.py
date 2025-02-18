"""
    Unit Tests for WWARA CSV to CHIRP CSV Conversion

    This module contains unit tests for the functions used in the WWARA CSV to CHIRP CSV conversion process.

    Purpose:
        To ensure that the functions in the wwara_csv_to_chirp_csv module work correctly and handle both valid and invalid inputs as expected.

    Usage:
        Run these tests using a test runner such as unittest.

        Example:
            python -m unittest tests/test_wwara_csv_to_chirp_csv.py

    Test Cases:
        - test_validate_input_file: Tests the validation of input file paths.
        - test_validate_output_file: Tests the validation of output file paths.
        - test_process_row: Tests the processing of WWARA rows into CHIRP rows.
"""

import sys
import os
import unittest
import pandas as pd

from wwara_csv_to_chirp_csv import (
    write_output_file, process_row, main)


# Add the module's directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWWARACSVToChirpCSV(unittest.TestCase):

    def test_write_output_file(self):
        write_output_file('test_files/test_output.csv', pd.DataFrame())
        self.assertTrue(os.path.exists('test_files/test_output.csv'))
        os.remove('test_files/test_output.csv')

    def test_main(self):
        main('test_files/WWARA-rptrlist-TEST.csv',
             'test_files/test_output.csv')
        self.assertTrue(os.path.exists('test_files/test_output.csv'))
        #check that the output file matches the reference output file
        with open('test_files/test_output.csv', 'r') as f:
            output = f.read()
        with open('test_files/reference_output.csv', 'r') as f:
            reference_output = f.read()
        self.assertEqual(output, reference_output)
        # os.remove('test_files/test_output.csv')

    def test_process_row(self):
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
        self.assertEqual(chirp_row['Location'], 0)
        self.assertEqual(chirp_row['Name'], '')
        self.assertEqual(chirp_row['Frequency'], '0.000000')
        self.assertEqual(chirp_row['Duplex'], '')
        self.assertEqual(chirp_row['Offset'], '0.000000')
        self.assertEqual(chirp_row['Tone'], '')
        self.assertEqual(chirp_row['rToneFreq'], '88.5')
        self.assertEqual(chirp_row['cToneFreq'], '88.5')
        self.assertEqual(chirp_row['DtcsCode'], 0)
        self.assertEqual(chirp_row['DtcsPolarity'], '')
        self.assertEqual(chirp_row['RxDtcsCode'], '023')
        self.assertEqual(chirp_row['CrossMode'], 'Tone->Tone')
        self.assertEqual(chirp_row['Mode'], '')
        self.assertEqual(chirp_row['TStep'], '5.00')
        self.assertEqual(chirp_row['Skip'], '')
        self.assertEqual(chirp_row['Power'], '5.0W')
        self.assertEqual(chirp_row['Comment'], ' Seattle Sponsor: WWARA Link: Yes URL: http://example.com Expiration: 2024-12-31 Lat: 47.6062, Lon: -122.3321 ARES RACES WX DMR Color Code: 1 Fusion DSQ: 123 NXDN Digital NXDN Mixed NXDN RAN: 2 ATV DATV')
        self.assertEqual(chirp_row['URCALL'], '')
        self.assertEqual(chirp_row['RPT1CALL'], '')
        self.assertEqual(chirp_row['RPT2CALL'], '')
        self.assertEqual(chirp_row['DVCODE'], '')

    if __name__ == '__main__':
        unittest.main()