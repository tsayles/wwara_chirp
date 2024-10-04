# WWARA CHIRP Export Script Update

This is a work in progress. A new version of the WWARA CHIRP export script is being developed to address the format change from XML to CSV. The updated script will provide a more reliable and user-friendly way to export WWARA repeater data for CHIRP programming.

## Overview
This repository contains an updated CHIRP export script for the Western Washington Amateur Relay Association (WWARA). This update addresses a longstanding format change for CHIRP import files, moving away from XML in favor of CSV due to improved compatibility and reliability.

## Background
CHIRP, an open-source tool for programming amateur radios, initially supported XML as an import format for radio frequency data. However, the XML import feature had issues, including strict schema requirements and formatting constraints that frequently resulted in validation errors. Users experienced challenges due to the XML schema’s rigidity, which required fields in precise order and allowed minimal flexibility. These limitations hindered interoperability and led to CHIRP adopting CSV as the preferred import format. CSV files are easier to create and maintain, and they seamlessly integrate with CHIRP’s features, allowing users to import frequency data across a wide range of supported radios without the schema-related errors encountered with XML&#8203;:contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}&#8203;:contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}.

## Purpose of Update
The WWARA CHIRP export script has been updated to align with CHIRP’s current standard, using CSV for export rather than XML. This update ensures:
- Greater reliability and reduced error rates during import to CHIRP.
- Simplified data maintenance and editing, as CSV files are compatible with spreadsheet software.
- Improved compatibility with the latest versions of CHIRP, which no longer support XML import.

## Usage
To use this script:
1. Clone the repository.
2. Ensure you have your WWARA frequency data available in the required format.
3. Run the script, which will output a CHIRP-compatible CSV file for easy import.

## Future Plans
As CHIRP evolves, this script will be maintained to reflect any new updates or changes in CHIRP’s file compatibility. Contributions are welcome to help keep this tool current and efficient for WWARA members.

---

For questions, please reach out to the maintainers or open an issue on this repository.
