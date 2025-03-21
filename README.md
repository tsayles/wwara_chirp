# WWARA CHIRP Export Script Update

This is a beta release of the WWARA CHIRP export script. 
A new version of the WWARA CHIRP export script has been developed to address 
the CHIRP file format change from XML to CSV. The updated script provides a 
(hopefully) more reliable and user-friendly way to convert WWARA repeater 
data to a format suitable for direct import into CHIRP.

## Overview
This repository contains an updated CHIRP export script for the Western
Washington Amateur Relay Association (WWARA). This update addresses a
longstanding format change for CHIRP import files, moving away from XML in favor
of CSV due to improved compatibility and reliability.

## Background
CHIRP, an open-source tool for programming amateur radios, initially supported
XML as an import format for radio frequency data. However, the XML import
feature had issues, including strict schema requirements and formatting
constraints that frequently resulted in validation errors. Users experienced
challenges due to the XML schema’s rigidity, which required fields in precise
order and allowed minimal flexibility. These limitations hindered
interoperability and led to CHIRP adopting CSV as the preferred import format.
CSV files are easier to create and maintain, and they seamlessly integrate with
CHIRP’s features, allowing users to import frequency data across a wide range of
supported radios without the schema-related errors encountered with XML.

## Installation
To use the updated WWARA CHIRP export script, follow these steps:
1. Use pip to install from the PyPi repository:
   * `pip install wwara_chirp`
2. Or clone this repository and run the script locally:
   * `git clone https://github.com/tsayles/wwara_chirp.git`

### Setting the PYTHONPATH
If you cloned the repository, set the `PYTHONPATH` to include the `src` 
and `tests` directories:

```bash
export PYTHONPATH=$(pwd)/src:$(pwd)/tests:$PYTHONPATH
```

## Usage
To export WWARA repeater data for CHIRP programming, run the script with the
following command:
* `python3 -m wwara_chirp <input_file> <output_file>`

* `<input_file>` is the CSV file containing WWARA repeater data and
* `<output_file>` is the CSV file to be generated for CHIRP import. (Be sure 
  the output_file does not exist.)
  
The script will read the daily WWARA input file, convert the data to CHIRP 
format, and write the output file in CSV format for CHIRP import. The output 
file should  be imported to a new CHIRP channel list, and specific entries can
be copy and pasted to the desired radio memory channels of the user's radio file.


## Future Plans
As CHIRP evolves, this script will be maintained to reflect any new updates or 
changes in CHIRP\’s file compatibility. Contributions and 
[bug reports](https://github.com/tsayles/wwara-chirp/issues) are welcome and 
encouraged, as the goal is to provide a reliable and user-friendly tool for 
WWARA members and other amateur radio operators.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

This project is maintained by Tom Sayles (KE4HET) on a volunteer and as time 
allows basis.

For questions, please reach out to the maintainers or open an issue on this 
repository.
