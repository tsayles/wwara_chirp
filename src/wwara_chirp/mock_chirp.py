# This module provides a mock chirp class which abstracts the functions and
# methods from the kk7ds/chirp project, and decouples the direct  dependency on
# the kk7ds/chirp project.

import difflib

class MockChirp(object):
    def __init__(self):
        self.channels = []

    # Sources in the CHIRP project that need to be checked for updates
    CHIRP_SOURCES = ['https://raw.githubusercontent.com/kk7ds/chirp/refs/heads/master/chirp/chirp_common.py']

    # 50 Tones
    TONES = (
        67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5,
        85.4, 88.5, 91.5, 94.8, 97.4, 100.0, 103.5,
        107.2, 110.9, 114.8, 118.8, 123.0, 127.3,
        131.8, 136.5, 141.3, 146.2, 151.4, 156.7,
        159.8, 162.2, 165.5, 167.9, 171.3, 173.8,
        177.3, 179.9, 183.5, 186.2, 189.9, 192.8,
        196.6, 199.5, 203.5, 206.5, 210.7, 218.1,
        225.7, 229.1, 233.6, 241.8, 250.3, 254.1,
    )

    # 104 DTCS Codes
    DTCS_CODES = (
        23, 25, 26, 31, 32, 36, 43, 47, 51, 53, 54,
        65, 71, 72, 73, 74, 114, 115, 116, 122, 125, 131,
        132, 134, 143, 145, 152, 155, 156, 162, 165, 172, 174,
        205, 212, 223, 225, 226, 243, 244, 245, 246, 251, 252,
        255, 261, 263, 265, 266, 271, 274, 306, 311, 315, 325,
        331, 332, 343, 346, 351, 356, 364, 365, 371, 411, 412,
        413, 423, 431, 432, 445, 446, 452, 454, 455, 462, 464,
        465, 466, 503, 506, 516, 523, 526, 532, 546, 565, 606,
        612, 624, 627, 631, 632, 654, 662, 664, 703, 712, 723,
        731, 732, 734, 743, 754,
    )

    # This is the "master" list of modes, and in general things should not be
    # added here without significant consideration. These must remain stable and
    # universal to allow importing memories between different radio vendors and
    # models.
    MODES = ("WFM", "FM", "NFM", "AM", "NAM", "DV", "USB", "LSB", "CW", "RTTY",
             "DIG", "PKT", "NCW", "NCWR", "CWR", "P25", "Auto", "RTTYR",
             "FSK", "FSKR", "DMR", "DN")

class CheckMockChirp:
    @staticmethod
    def compare_constants(name, mock_value, chirp_value):
        if mock_value != chirp_value:
            diff = difflib.unified_diff(
                mock_value.splitlines(), chirp_value.splitlines(),
                fromfile=f'mock_chirp.{name}', tofile=f'chirp_common.{name}'
            )
            with open('diff.txt', 'a') as f:
                f.writelines(diff)


