#!/usr/bin/env python
"""
WWARA CHIRP Export Script Update

This script updates the Western Washington Amateur Relay Association (WWARA) CHIRP export script.
The update ensures greater reliability and reduced error rates during import to CHIRP,
and provides better error handling and reporting.

The script reads a CSV file exported from the WWARA database and writes a new CSV file
in the format required by more recent versions of CHIRP.

The script requires the pandas library, which can be installed with the command:
pip install pandas


Author: Tom Sayles, KE4HET

"""

import pandas as pd
import csv
import sys


