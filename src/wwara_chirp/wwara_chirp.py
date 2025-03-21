#!/usr/bin/env python
"""
WWARA CHIRP Export Script Update

This script replaces the Western Washington Amateur Relay Association
(WWARA) CHIRP export script. The update ensures greater reliability and
reduced error rates during import to CHIRP, and provides better error
handling and reporting.

The script reads a CSV file exported from the WWARA database and writes
a new CSV file in the format required by more recent versions of CHIRP.

The script requires the pandas library, which can be installed with the
command: pip install pandas

Author: Tom Sayles, KE4HET, with assistance from GitHub Copilot

License: MIT License (see LICENSE file)

"""
import argparse
import logging
import os
import re
import sys
from contextlib import nullcontext
from logging.handlers import RotatingFileHandler

import pandas as pd
from chirp.chirp_common import TONES, DTCS_CODES, MODES

# from .chirpvalidator import ChirpValidator
from wwara_chirp.chirpvalidator import ChirpValidator

# Set up the CSV file paths
INPUT_FILE = '../../sample_files/WWARA-rptrlist-SAMPLE.csv'
OUTPUT_FILE = '../../sample_files/wwara-chirp.csv'

# Set up the CSV column names for the wwara input file
WWARA_COLUMNS = [
    'FC_RECORD_ID', 'SOURCE', 'OUTPUT_FREQ', 'INPUT_FREQ', 'STATE', 'CITY',
    'LOCALE', 'CALL', 'SPONSOR', 'CTCSS_IN', 'CTCSS_OUT', 'DCS_CDCSS', 'DTMF',
    'LINK', 'FM_WIDE', 'FM_NARROW', 'DSTAR_DV', 'DSTAR_DD', 'DMR',
    'DMR_COLOR_CODE', 'FUSION', 'FUSION_DSQ', 'P25_PHASE_1', 'P25_PHASE_2',
    'P25_NAC', 'NXDN_DIGITAL', 'NXDN_MIXED', 'NXDN_RAN', 'ATV', 'DATV', 'RACES',
    'ARES', 'WX', 'URL', 'LATITUDE', 'LONGITUDE', 'EXPIRATION_DATE', 'COMMENT'
]

# Set up the CSV column names for the chirp output file

CHIRP_COLUMNS = [
    'Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone', 'rToneFreq',
    'cToneFreq', 'DtcsCode', 'DtcsPolarity', 'RxDtcsCode', 'CrossMode', 'Mode',
    'TStep', 'Skip', 'Power', 'Comment', 'URCALL', 'RPT1CALL', 'RPT2CALL',
    'DVCODE'
]

# Set up logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler = RotatingFileHandler('../../tests/wwara-chirp.log', maxBytes=100000, backupCount=5)
handler = RotatingFileHandler('wwara-chirp.log', maxBytes=100000, backupCount=5)
handler.setFormatter(formatter)
log.addHandler(handler)

# create a pandas dataframe for the chirp output file
chirp_table = pd.DataFrame(columns=CHIRP_COLUMNS)

"""
The constraints in this script have been revised to match those defined
in the `chirp_common.py` file from the CHIRP repository
(https://github.com/kk7ds/chirp). These constraints ensure compatibility
with the latest versions of CHIRP.

These constraints are associated with the latest versions of CHIRP as of
October 2023.
"""
# Set up the CHIRP memory channel limits
channel_min = 0
channel_max = 499

# Set up the CHIRP frequency limits
frequency_min = 10  # 1 MHz
frequency_max = 1300  # 1.3 GHz

# Set up the CHIRP offset limits, in kHz
# TODO: Check if these are the correct limits
offset_min = 0
offset_max = 99.9  # 99.999999 MHz

# Set up the valid CHIRP tones
# 50 Tones
TONES = TONES

# Set up the valid CHIRP DTCS codes
# 104 DTCS Codes
DTCS_CODES = DTCS_CODES

# Set up the CHIRP mode options
MODES = MODES

# Initialize the CHIRP memory parameters
comment = ''
channel = 0
channels = []

# # Set up the CHIRP memory channel dictionary
# channel_dict = {}
#
# # Set up the CHIRP memory channel list
# channel_list = []

# define function to process a wwara row and return a chirp row
def process_row(wwara_row):
    global channel

    chirp_row = pd.Series({
        'Location': 0,
        'Name': '',
        'Frequency': 0,
        'Duplex': '',
        'Offset': '',
        'Tone': '',
        'rToneFreq': '88.5',
        'cToneFreq': '88.5',
        'DtcsCode': 0,
        'DtcsPolarity': 'NN',
        'RxDtcsCode': '23',
        'CrossMode': 'Tone->Tone',
        'Mode': '',
        'TStep': '5.00',
        'Skip': '',
        'Power': '5.00W',
        'Comment': '',
        'URCALL': '',
        'RPT1CALL': '',
        'RPT2CALL': '',
        'DVCODE': ''
    })

    # Set up the default CHIRP memory parameters
    tone = ''
    c_tone_freq = '88.5'
    r_tone_freq = '88.5'
    # dtcs_code = '023'
    dtcs_code = 23
    dtcs_polarity = 'NN'
    mode = ''

    location = channel
    name = wwara_row['CALL']

    # wwara_row['OUTPUT_FREQ'] and wwara_row['INPUT_FREQ'] are in MHz
    # Convert to Hz for chirp
    frequency_out = wwara_row['OUTPUT_FREQ']
    frequency_in = wwara_row['INPUT_FREQ']

    if frequency_out > frequency_in:
        duplex = '+'
        offset = (frequency_out - frequency_in)
    else:
        duplex = '-'
        offset = (frequency_in - frequency_out)

    if wwara_row['CTCSS_IN'] != '':
        tone = 'Tone'
        r_tone_freq = wwara_row['CTCSS_IN']

    if r_tone_freq != '':
        tone = 'Tone'
        if wwara_row['CTCSS_OUT'] != '':
            c_tone_freq = wwara_row['CTCSS_OUT']
    elif wwara_row['DCS_CDCSS'] != '':
        tone = 'DTCS'
        dtcs_code = wwara_row['DCS_CDCSS']



    if wwara_row['FM_WIDE'] == 'Y':
        mode = 'FM'
    elif wwara_row['FM_NARROW'] == 'Y':
        mode = 'NFM'
    elif wwara_row['DSTAR_DV'] == 'Y':
        mode = 'DV'
    elif wwara_row['DSTAR_DD'] == 'Y':
        # TODO: Check if this is the correct mode for DSTAR_DD
        mode = 'DIG'
    elif wwara_row['DMR'] == 'Y':
        mode = 'DMR'
    elif wwara_row['P25_PHASE_1'] == 'Y' or wwara_row['P25_PHASE_2'] == 'Y':
        mode = 'P25'
    elif wwara_row['ATV'] == 'Y':
        # TODO: Check if this is the correct mode for ATV
        mode = 'DIG'


    comment = wwara_row['COMMENT']
    #check that the comment is a string or empty string
    if not isinstance(comment, str):
        comment = ''

    comment_len = len(comment)
    if comment_len > 0:
        aux_comment = ' '
    else:
        aux_comment = ''

    # construct meaningful comment from wwara data
    geographic_location = ''
    if wwara_row['CITY'] != '':
        geographic_location = wwara_row['CITY']
    if wwara_row['STATE'] != '':
        if geographic_location != '':
            geographic_location += ', '
        geographic_location += wwara_row['STATE']
    if wwara_row['LOCALE'] != '':
        if geographic_location != '':
            geographic_location += ' '
        geographic_location += wwara_row['LOCALE']

    if (comment_len + len(aux_comment) + len(geographic_location)) <= 255:
        if len(comment) > 0:
            aux_comment += ' '
        aux_comment += f' {geographic_location}'

    if wwara_row['SPONSOR'] != '' and (comment_len + len(aux_comment) + len(
            f' Sponsor: {wwara_row["SPONSOR"]}')) <= 255:
        aux_comment += f' Sponsor: {wwara_row["SPONSOR"]}'
    if wwara_row['LINK'] != '' and (comment_len + len(aux_comment) + len(
            f' Link: {wwara_row["LINK"]}')) <= 255:
        aux_comment += f' Link: {wwara_row["LINK"]}'
    if wwara_row['URL'] != '' and (comment_len + len(aux_comment) + len(
            f' URL: {wwara_row["URL"]}')) <= 255:
        aux_comment += f' URL: {wwara_row["URL"]}'
    if wwara_row['EXPIRATION_DATE'] != '' and (
            comment_len + len(aux_comment) + len(
            f' Expiration: {wwara_row["EXPIRATION_DATE"]}')) <= 255:
        aux_comment += f' Expiration: {wwara_row["EXPIRATION_DATE"]}'
    if wwara_row['LATITUDE'] != '' and wwara_row['LONGITUDE'] != '' and (
            comment_len + len(aux_comment) + len(
            f' Lat: {wwara_row["LATITUDE"]}, Lon: {wwara_row["LONGITUDE"]}')) <= 255:
        aux_comment += f' Lat: {wwara_row["LATITUDE"]}, Lon: {wwara_row["LONGITUDE"]}'
    if wwara_row['ARES'] == 'Y' and (comment_len + len(aux_comment) + len(
            ' ARES')) <= 255:
        aux_comment += ' ARES'
    if wwara_row['RACES'] == 'Y' and (comment_len + len(aux_comment) + len(
            ' RACES')) <= 255:
        aux_comment += 'RACES'
    if wwara_row['WX'] == 'Y' and (comment_len + len(aux_comment) + len(
            ' WX')) <= 255:
        aux_comment += ' WX'
    if wwara_row['DMR_COLOR_CODE'] != '' and (comment_len + len(aux_comment) + len(
            f' DMR Color Code: {wwara_row["DMR_COLOR_CODE"]}')) <= 255:
        aux_comment += f' DMR Color Code: {wwara_row["DMR_COLOR_CODE"]}'
    if wwara_row['FUSION_DSQ'] != '' and (comment_len + len(aux_comment) + len(
            f' Fusion DSQ: {wwara_row["FUSION_DSQ"]}')) <= 255:
        aux_comment += f' Fusion DSQ: {wwara_row["FUSION_DSQ"]}'
    if wwara_row['NXDN_DIGITAL'] == 'Y' and (comment_len + len(aux_comment) + len(
            ' NXDN Digital')) <= 255:
        aux_comment += ' NXDN Digital'
    if wwara_row['NXDN_MIXED'] == 'Y' and (comment_len + len(aux_comment) + len(
            ' NXDN Mixed')) <= 255:
        aux_comment += ' NXDN Mixed'
    if wwara_row['NXDN_RAN'] != '' and (comment_len + len(aux_comment) + len(
            f' NXDN RAN: {wwara_row["NXDN_RAN"]}')) <= 255:
        aux_comment += f' NXDN RAN: {wwara_row["NXDN_RAN"]}'
    if wwara_row['ATV'] == 'Y' and (comment_len + len(aux_comment) + len(
            ' ATV')) <= 255:
        aux_comment += ' ATV'
    if wwara_row['DATV'] == 'Y' and (comment_len + len(aux_comment) + len(
            ' DATV')) <= 255:
        aux_comment += ' DATV'

    comment += aux_comment

    # check if c_tone_freq or r_tone_freq are NaN and set them to 88.5 if they are
    if pd.isna(c_tone_freq):
        c_tone_freq = '88.5'
    if pd.isna(r_tone_freq):
        r_tone_freq = '88.5'

    chirp_row = pd.Series({
        'Location': location,
        'Name': name,
        'Frequency': f'{frequency_out:.6f}',
        'Duplex': duplex,
        'Offset': f'{offset:.6f}',
        'Tone': tone,
        'rToneFreq': r_tone_freq,
        'cToneFreq': c_tone_freq,
        'DtcsCode': dtcs_code,
        'DtcsPolarity': dtcs_polarity,
        'RxDtcsCode': 23,
        'CrossMode': 'Tone->Tone',
        'Mode': mode,
        'TStep': '5.00',
        'Skip': '',
        'Power': '5.0W',
        'Comment': comment,
        'URCALL': '',
        'RPT1CALL': '',
        'RPT2CALL': '',
        'DVCODE': ''
    })

    channel += 1

    return chirp_row

def write_output_file(output_file, chirp_table):
    chirp_table.to_csv(output_file, index=False)

    log.info(f'Output file written: {output_file}')
    log.info(f'Number of memory channels written: {len(chirp_table)}')

def main(input_file, output_file):
    log.info('WWARA CHIRP Export Script Update')

    if input_file is None and output_file is None:
        log.info('Using command line or default input and output files')

        parser = argparse.ArgumentParser(description='WWARA CHIRP Export Script Update')
        parser.add_argument('input_file', help='Path to the input CSV file')
        parser.add_argument('output_file', help='Path to the output CSV file')
        args = parser.parse_args()

        if not args.input_file:
            args.input_file = INPUT_FILE
        if not args.output_file:
            args.output_file = OUTPUT_FILE

        input_file = args.input_file
        output_file = args.output_file

    log.debug('Script started')
    log.debug(f'Input file: {INPUT_FILE}')
    log.debug(f'Output file: {OUTPUT_FILE}')

    global chirp_table

    validator = ChirpValidator()

    if not validator.validate_input_file(input_file):
        sys.exit(1)
    if not validator.validate_output_file(output_file):
        sys.exit(1)

    log.debug(f'Reading input file: {input_file}')
    # Read the input file, skipping the first row.
    # The second row contains the column names.
    df = pd.read_csv(input_file, skiprows=[0])

    log.debug(f'Number of memory channels read: {len(df)}')

    for index, wwara_row in df.iterrows():
        chirp_row = process_row(wwara_row)

        if not validator.validate_row(chirp_row):
            error_location = chirp_row['Location']
            log.error(f'Invalid row data: {error_location}')
            continue

        chirp_row_to_frame = chirp_row.to_frame().T
        if chirp_table.empty:
            chirp_table = chirp_row_to_frame
        else:
            chirp_table = pd.concat([chirp_table, chirp_row_to_frame],
                                ignore_index=True)


    write_output_file(output_file, chirp_table)


if __name__ == '__main__':

    main(None, None)