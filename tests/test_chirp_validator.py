# tests/test_chirp_validator.py

"""
Unit Tests for CHIRP_Validator

This module contains unit tests for the CHIRP_Validator class, which provides validation functions for various fields and data structures used in the CHIRP CSV conversion process.

Purpose:
    To ensure that the validation methods in the CHIRP_Validator class work correctly and handle both valid and invalid inputs as expected.

Usage:
    Run these tests using a test runner such as pytest or unittest.

    Example:
        pytest tests/test_chirp_validator.py
        or
        python -m unittest tests/test_chirp_validator.py

Test Cases:
    - test_validate_input_file: Tests the validation of input file paths.
    - test_validate_output_file: Tests the validation of output file paths.
    - test_validate_location: Tests the validation of memory locations.
    - test_validate_frequency: Tests the validation of frequency values.
    - test_validate_duplex: Tests the validation of duplex settings.
    - test_validate_offset: Tests the validation of offset values.
    - test_validate_tone: Tests the validation of tone values.
    - test_validate_tone_mode: Tests the validation of tone mode values.
    - test_validate_dtcs_code: Tests the validation of DTCS codes.
    - test_validate_dtcs_polarity: Tests the validation of DTCS polarity values.
    - test_validate_mode: Tests the validation of mode values.
    - test_validate_name: Tests the validation of name values.
    - test_validate_comment: Tests the validation of comment values.
    - test_validate_row: Tests the validation of complete CHIRP rows.
"""

import unittest
from chirp_validator import CHIRP_Validator


class TestCHIRPValidator(unittest.TestCase):
    def test_validate_input_file(self):
        assert CHIRP_Validator.validate_input_file(
            'test_files/valid_input.csv') == True
        assert CHIRP_Validator.validate_input_file(
            'test_files/invalid_input.txt') == True
        assert CHIRP_Validator.validate_input_file(
            'test_files/non_existent_file.csv') == False

    def test_validate_output_file(self):
            assert CHIRP_Validator.validate_output_file(
                'test_files/new_output.csv') == True
            assert CHIRP_Validator.validate_output_file(
                'test_files/existing_output.csv') == False

    def test_validate_location(self):
        assert CHIRP_Validator.validate_location(100) == True
        assert CHIRP_Validator.validate_location(-1) == False
        assert CHIRP_Validator.validate_location(500) == False

    def test_validate_frequency(self):
        assert CHIRP_Validator.validate_frequency('145.000') == True
        assert CHIRP_Validator.validate_frequency('abc') == False
        assert CHIRP_Validator.validate_frequency('2000.000') == False

    def test_validate_duplex(self):
        assert CHIRP_Validator.validate_duplex('+') == True
        assert CHIRP_Validator.validate_duplex('-') == True
        assert CHIRP_Validator.validate_duplex('') == True
        assert CHIRP_Validator.validate_duplex('invalid') == False

    def test_validate_offset(self):
        assert CHIRP_Validator.validate_offset('0.600') == True
        assert CHIRP_Validator.validate_offset('') == True
        assert CHIRP_Validator.validate_offset('abc') == False
        assert CHIRP_Validator.validate_offset('100.0') == False

    def test_validate_tone(self):
        assert CHIRP_Validator.validate_tone('Tone') == True
        assert CHIRP_Validator.validate_tone('DTCS') == True
        assert CHIRP_Validator.validate_tone('') == True
        assert CHIRP_Validator.validate_tone('invalid') == False

    def test_validate_tone_mode(self):
        assert CHIRP_Validator.validate_tone_mode('Tone') == True
        assert CHIRP_Validator.validate_tone_mode('DTCS') == True
        assert CHIRP_Validator.validate_tone_mode('') == True
        assert CHIRP_Validator.validate_tone_mode('invalid') == False

    def test_validate_dtcs_code(self):
        assert CHIRP_Validator.validate_dtcs_code('23') == True
        assert CHIRP_Validator.validate_dtcs_code('invalid') == False

    def test_validate_dtcs_polarity(self):
        assert CHIRP_Validator.validate_dtcs_polarity('NN') == True
        assert CHIRP_Validator.validate_dtcs_polarity('NR') == True
        assert CHIRP_Validator.validate_dtcs_polarity('invalid') == False

    def test_validate_mode(self):
        assert CHIRP_Validator.validate_mode('FM') == True
        assert CHIRP_Validator.validate_mode('') == True
        assert CHIRP_Validator.validate_mode('invalid') == False

    def test_validate_name(self):
        assert CHIRP_Validator.validate_name('Repeater') == True
        assert CHIRP_Validator.validate_name('A' * 17) == False
        assert CHIRP_Validator.validate_name('Invalid@Name') == False

    def test_validate_comment(self):
        assert CHIRP_Validator.validate_comment('This is a comment.') == True
        assert CHIRP_Validator.validate_comment('A' * 256) == False

    def test_validate_row(self):
        chirp_row = {
            'Location': 100,
            'Frequency': '145.000',
            'Duplex': '+',
            'Offset': '0.600',
            'Tone': 'Tone',
            'DTCS Code': '023',
            'DTCS Polarity': 'NN',
            'Mode': 'FM',
            'Name': 'Repeater',
            'Comment': 'This is a comment.'
        }
        assert CHIRP_Validator.validate_row(chirp_row) == True

        invalid_chirp_row = {
            'Location': 500,
            'Frequency': 'invalid',
            'Duplex': 'invalid',
            'Offset': 'invalid',
            'Tone': 'invalid',
            'DTCS Code': 'invalid',
            'DTCS Polarity': 'invalid',
            'Mode': 'invalid',
            'Name': 'A' * 17,
            'Comment': 'A' * 256
        }
        assert CHIRP_Validator.validate_row(invalid_chirp_row) == False


if __name__ == '__main__':
    unittest.main()
