"""
    Unit Tests for WWARA CSV to CHIRP CSV Conversion

    This module contains unit tests for the functions used in the WWARA CSV to CHIRP CSV conversion process.

    Purpose:
        To ensure that the functions in the wwara_csv_to_chirp_csv module work correctly and handle both valid and invalid inputs as expected.

    Usage:
        Run these tests using a test runner such as unittest.

        Example:
            python -m unittest tests/test_wwara_chirp.py

    Test Cases:
        - test_validate_input_file: Tests the validation of input file paths.
        - test_validate_output_file: Tests the validation of output file paths.
        - test_process_row: Tests the processing of WWARA rows into CHIRP rows.
"""
import subprocess
import sys
import os
import unittest
import pandas as pd

from wwara_chirp.wwara_chirp import write_output_file, main, process_row


# Add the module's directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWWARACSVToChirpCSV(unittest.TestCase):

    def test_write_output_file(self):
        write_output_file('test_files/test_output.csv', pd.DataFrame())
        self.assertTrue(os.path.exists('test_files/test_output.csv'))
        os.remove('test_files/test_output.csv')

    def test_main(self):
        main('test_files/WWARA-rptrlist-TEST.csv', 'test_files/test_output.csv')
        self.assertTrue(os.path.exists('test_files/test_output.csv'))
        # check that the output file matches the reference output file
        with open('test_files/test_output.csv', 'r') as f:
            output = f.read()
        with open('test_files/reference_output.csv', 'r') as f:
            reference_output = f.read()
        self.assertEqual(output, reference_output)
        os.remove('test_files/test_output.csv')

    def test_process_row(self):
        wwara_row = pd.Series({
            'CALL': 'K7LED',
            'OUTPUT_FREQ': 146.8200,
            'INPUT_FREQ': 146.2200,
            'CTCSS_IN': 88.5,
            'CTCSS_OUT': 88.5,
            'DTCS_CODE': 23,
            'LOCALE': 'Issaquah Alps',
            'STATE': 'WA',
            'COUNTY': 'King',
            'CITY': 'Issaquah',
            'SPONSOR': 'WWARA',
            'LINK': 'Yes',
            'URL': 'https://example.com',
            'EXPIRATION_DATE': '2024-12-31',
            'LATITUDE': '47.6062',
            'LONGITUDE': '-122.3321',
            'FM_WIDE': 'Y',
            'COMMENT': 'Test Comment',
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
        # the 'Location' field is not tested because it is dependent on how
        # may rows have been processed in the previous tests.
        # self.assertEqual(chirp_row['Location'], 434)

        self.assertEqual(chirp_row['Name'], 'K7LED')
        self.assertEqual(chirp_row['Frequency'], '146.820000')
        self.assertEqual(chirp_row['Duplex'], '+')
        self.assertEqual(chirp_row['Offset'], '0.600000')
        self.assertEqual(chirp_row['Tone'], 'Tone')
        self.assertEqual(chirp_row['rToneFreq'], 88.5)
        self.assertEqual(chirp_row['cToneFreq'], 88.5)
        self.assertEqual(chirp_row['DtcsCode'], 23)

        self.assertEqual(chirp_row['DtcsPolarity'], 'NN')
        self.assertEqual(chirp_row['RxDtcsCode'], 23)
        self.assertEqual(chirp_row['CrossMode'], 'Tone->Tone')
        self.assertEqual(chirp_row['Mode'], 'FM')
        self.assertEqual(chirp_row['TStep'], '5.00')
        self.assertEqual(chirp_row['Skip'], '')
        self.assertEqual(chirp_row['Power'], '5.0W')
        self.assertEqual(chirp_row['Comment'], 'Test Comment   Issaquah, '
                                               'WA Issaquah Alps Sponsor: WWARA '
                                               'Link: Yes URL: https://example.com '
                                               'Expiration: 2024-12-31 Lat: 47.6062, '
                                               'Lon: -122.3321 ARESRACES WX DMR '
                                               'Color Code: 1 Fusion DSQ: 123 NXDN '
                                               'Digital NXDN Mixed NXDN RAN: 2 ATV '
                                               'DATV')
        self.assertEqual(chirp_row['URCALL'], '')
        self.assertEqual(chirp_row['RPT1CALL'], '')
        self.assertEqual(chirp_row['RPT2CALL'], '')
        self.assertEqual(chirp_row['DVCODE'], '')

    ## moved to a GitHiub action. See .github/workflows/python-package.yml
    #
    # def test_command_line_execution(self):
    #     input_file = 'sample_files/WWARA-rptrlist-SAMPLE.csv'
    #     output_file = 'sample_files/test_output.csv'
    #
    #     # Print the current working directory for debugging
    #     print("Current working directory:", os.getcwd())
    #
    #     # Run the script using subprocess
    #     script_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
    #                                                '../src/wwara_chirp/wwara_chirp.py'))
    #     result = subprocess.run(
    #         ['python', script_path, input_file, output_file],
    #         capture_output=True,
    #         text=True
    #     )
    #
    #     # Print stdout and stderr for debugging
    #     print("stdout:", result.stdout)
    #     print("stderr:", result.stderr)
    #
    #     # Check that the script executed successfully
    #     self.assertEqual(result.returncode, 0)
    #
    #     # Check that the output file was created
    #     self.assertTrue(os.path.exists(output_file))
    #
    #     # Clean up the output file
    #     os.remove(output_file)

    if __name__ == '__main__':
        unittest.main()