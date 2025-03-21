# chirp_validator.py

"""
CHIRP_Validator

This module provides a set of validation functions encapsulated in the CHIRP_Validator class.
The purpose of this class is to validate various fields and data structures used in the CHIRP CSV conversion process.

"""

import os
import re
import logging
from chirp.chirp_common import TONES, DTCS_CODES, MODES

log = logging.getLogger(__name__)

class ChirpValidator:
    channel_min = 0
    channel_max = 499
    frequency_min = 10
    frequency_max = 1300
    offset_min = 0
    offset_max = 9999.9

    @staticmethod
    def validate_input_file(input_file):
        if not os.path.isfile(input_file):
            log.error(f'Input file not found: {input_file}')
            return False
        return True

    @staticmethod
    def validate_output_file(output_file):
        if os.path.isfile(output_file):
            log.warning(f'Output file already exists: {output_file}')
            return False
        return True

    @staticmethod
    def validate_location(location):
        if location < ChirpValidator.channel_min or location > ChirpValidator.channel_max:
            log.error(f'Invalid memory location: {location}')
            return False
        return True

    @staticmethod
    def validate_frequency(frequency):
        # TODO setup an optional band parameter to check that the frequency
        #     #  is standard for that band.  If it isn't, then log a warning.

        if not re.match(r'^\d+(\.\d+)?$', frequency):
            log.error(f'Invalid frequency: {frequency}')
            return False
        frequency_num = float(frequency)
        if frequency_num < ChirpValidator.frequency_min or frequency_num > ChirpValidator.frequency_max:
            log.error(f'Invalid frequency: {frequency}')
            return False
        return True

    @staticmethod
    def validate_duplex(duplex):
        if duplex not in ['+', '-', '']:
            log.error(f'Invalid duplex setting: {duplex}')
            return False
        return True

    @staticmethod
    def validate_offset(offset):
        # TODO setup an optional frequency_out parameter to check that the offset
        #     #  is standard for that band.  If it isn't, then log a warning.
        #     #  Also, check for cross band repeaters and log a warning.

        if offset == '':
            return True

        if not re.match(r'^\d+(\.\d+)?$', offset):
            log.error(f'Invalid offset: {offset}')
            return False

        offset_num = float(offset)
        if offset_num < ChirpValidator.offset_min or offset_num > ChirpValidator.offset_max:
            log.error(f'Invalid offset: {offset}')
            return False
        return True

    @staticmethod
    def validate_tone(tone):
        if tone not in TONES and tone != 'Tone' and tone != 'DTCS' and tone != '':
            log.error(f'Invalid tone: {tone}')
            return False
        return True

    @staticmethod
    def validate_tone_mode(tone_mode):
        if tone_mode not in ['Tone', 'DTCS'] and tone_mode != '':
            log.error(f'Invalid tone mode: {tone_mode}')
            return False
        return True

    @staticmethod
    def validate_dtcs_code(dtcs_code):
        if dtcs_code not in DTCS_CODES:
            log.error(f'Invalid DTCS code: {dtcs_code}')
            return False
        return True

    @staticmethod
    def validate_dtcs_polarity(dtcs_polarity):
        if dtcs_polarity not in ['NN', 'NR', 'RN', 'RR']:
            log.error(f'Invalid DTCS polarity: {dtcs_polarity}')
            return False
        return True

    @staticmethod
    def validate_mode(mode):
        if mode not in MODES and mode != '':
            log.error(f'Invalid mode: {mode}')
            return False
        return True

    @staticmethod
    def validate_name(name):
        if len(name) > 16:
            log.error(f'Invalid name length: {name}')
            return False
        if not re.match(r'^[\w\s-]+$', name):
            log.error(f'Invalid characters in name: {name}')
            return False
        return True

    @staticmethod
    def validate_comment(comment):
        if len(comment) > 255:
            log.error(f'Invalid comment length: {comment}')
            return False
        return True

    @staticmethod
    def validate_row(chirp_row):
        if not ChirpValidator.validate_location(chirp_row['Location']):
            return False
        if not ChirpValidator.validate_frequency(chirp_row['Frequency']):
            return False
        if not ChirpValidator.validate_duplex(chirp_row['Duplex']):
            return False
        if chirp_row['Duplex'] != '':
            if not ChirpValidator.validate_offset(chirp_row['Offset']):
                return False
        if not ChirpValidator.validate_tone(chirp_row['Tone']):
            return False
        if chirp_row['Tone'] == 'DTCS':
            if not ChirpValidator.validate_dtcs_code(chirp_row['DTCS Code']):
                return False
            if not ChirpValidator.validate_dtcs_polarity(chirp_row['DTCS Polarity']):
                return False
        if not ChirpValidator.validate_mode(chirp_row['Mode']):
            return False
        if not ChirpValidator.validate_name(chirp_row['Name']):
            return False
        if not ChirpValidator.validate_comment(chirp_row['Comment']):
            return False
        return True