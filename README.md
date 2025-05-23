# WWARA CHIRP Export Script Update

### **Note: This is a work in progress. The script is mostly functional, and the documentation is aspirational.** 
Please report any issues or bugs you encounter, and feel free to contribute to the
documentation or code.

## Overview
This repository contains an updated CHIRP export script for the Western
Washington Amateur Relay Association ([WWARA](https://www.wwara.org/)). 

WWARA maintains a database of coordinated repeaters west of the Cascade
Mountains in Washington State, between the Canadian border and the Oregon
borders. WWARA publishes a nightly extract of their database in various CSV 
variations. 

This script is intended to be used with the WWARA-rptrlist-DATE.csv file. The 
v2.x.x updates address a longstanding format change for CHIRP import files, 
moving away from XML in favor of CSV due to improved compatibility and 
reliability. These updates also implement a modern Python packaging structure
to facilitate installation, especially managing dependencies.

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

## Prerequisites
wwara_chirp is tested on python 3.10, 3.11, 3.12, and 3.13

## Installation
To install the package, you can use pip to install the package from PyPI for 
the latest stable release. 
    ```bash
    pip install -i wwara-chirp
    ```    
or from the test PyPI for the latest pre-release version.

   ```bash
   pip install -i https://test.pypi.org/simple/ wwara-chirp
   ```  

you can also upgrade the package to the latest stable version.
    ```bash
    pip install -i --upgrade wwara-chirp
    ```

## Usage
To export WWARA repeater data for CHIRP programming, run the script with the
following command:
* `wwara_chirp <input_file> <output_file>`

* `<input_file>` is the CSV file containing WWARA repeater data and
* `<output_file>` is the CSV file to be generated for CHIRP import. (Be sure the
  output_file does not exist.)
  
The script is intended to read the daily WWARA input file, convert the data to
CHIRP format, and write the output file in CSV format for CHIRP import. The
output file should be imported to a new CHIRP channel list, and specific entries
can be copy and pasted to the desired radio memory channels of the user's radio
file.


## Future Plans
As CHIRP evolves, this script will be maintained to reflect any new updates or 
changes in CHIRP\’s file compatibility. Contributions and 
[bug reports](https://github.com/tsayles/wwara-chirp/issues) are welcome and 
encouraged, as the goal is to provide a reliable and user-friendly tool for 
WWARA members and other amateur radio operators.

## License
This project is now licensed under the GPL-3.0 License to allow the reuse of
code from the code from the [chirp project](https://github.com/kk7ds/chirp),
which is also licensed under GPL-3.0. This change ensures compatibility and
compliance with the licensing terms of the chirp project.

If the chirp project is ever published to PyPi under a more permissive license,
such as the MIT License, we can consider switching back to the MIT License for
this project. This would allow for greater flexibility and ease of use for
contributors and users.

For more details, see the LICENSE.txt file in this repository.

## Contact

This project is maintained by Tom Sayles (KE4HET) on a volunteer and as time 
allows basis.

For questions, please reach out to the maintainers or open an issue on this 
repository.
