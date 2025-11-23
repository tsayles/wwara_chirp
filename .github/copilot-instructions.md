# WWARA CHIRP Export Script

## About This File
This file provides custom instructions for GitHub Copilot when working on the WWARA CHIRP repository. These instructions help ensure consistency, efficiency, and quality when making changes to the codebase.

## Project Overview
WWARA CHIRP is a Python CLI tool that converts Western Washington Amateur Relay Association (WWARA) repeater CSV data to CHIRP-compatible CSV format for amateur radio programming. The project:
- Supports Python 3.10, 3.11, 3.12, and 3.13
- Uses pandas for CSV processing
- Validates CHIRP CSV format requirements
- Is licensed under GPL-3.0 for compatibility with the CHIRP project

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively
- Bootstrap, build, and test the repository:
  - `pip install --upgrade pip` -- often fails due to network timeouts. Skip if already installed.
  - `pip install flake8 pytest pandas numpy poetry PyGithub` -- often fails due to network timeouts. Use poetry instead.
  - `poetry install` -- takes 3 seconds with lock file. NEVER CANCEL. Set timeout to 120+ seconds.
- Test the code:
  - `export PYTHONPATH=$(pwd)/src:$(pwd)/tests`
  - `cd tests && pytest` -- takes 1 second. All 23 tests should pass.
- Lint the code:
  - `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` -- syntax check, takes 1 second
  - `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics` -- style check, shows 78 warnings but takes 1 second
- Run the CLI tool:
  - ALWAYS run the bootstrapping steps first.
  - `export PYTHONPATH=$(pwd)/src`
  - `python -m wwara_chirp.wwara_chirp input.csv output.csv` -- converts WWARA CSV to CHIRP CSV
  - `python -m wwara_chirp.wwara_chirp --help` -- shows usage information

## Validation
- Always manually validate any new code by running through complete user scenarios.
- ALWAYS run through at least one complete end-to-end scenario after making changes:
  - Use test file: `tests/test_files/WWARA-rptrlist-TEST.csv`
  - Run: `python -m wwara_chirp.wwara_chirp tests/test_files/WWARA-rptrlist-TEST.csv /tmp/test_output.csv`
  - Verify output file is created and contains valid CHIRP CSV data
  - Compare against reference: `diff /tmp/test_output.csv tests/test_files/reference_output.csv` should show no differences
- Test help command: `python -m wwara_chirp.wwara_chirp --help` should show "WWARA CHIRP Export Script Update"
- Always run `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` before you are done or the CI (.github/workflows/python-package.yml) will fail.
- **COMPLETE VALIDATION WORKFLOW** (matches GitHub Actions):
  ```bash
  # Set up environment
  export PYTHONPATH=$(pwd)/src
  input_file=tests/test_files/WWARA-rptrlist-TEST.csv
  output_file=/tmp/validation_test.csv
  reference_output_file=tests/test_files/reference_output.csv
  
  # Run conversion
  python -m wwara_chirp.wwara_chirp $input_file $output_file
  
  # Verify output file was created
  if [ ! -f $output_file ]; then
    echo "Output file not created"
    exit 1
  fi
  
  # Verify output matches reference
  if ! diff -q $output_file $reference_output_file; then
    echo "Output file does not match reference output"
    exit 1
  fi
  
  echo "Validation successful"
  ```

## Build and Packaging
- Package building: `python -m build` -- FAILS due to network timeouts. Do not attempt to build.
- The package works fine without building using the direct CLI approach above.
- CI workflows test both direct execution and built package installation.

## Common tasks
The following are outputs from frequently run commands. Reference them instead of viewing, searching, or running bash commands to save time.

### Repository structure
```
.
├── .github/workflows/        # CI/CD pipelines
├── docs/                    # Documentation scripts
├── sample_files/           # Sample WWARA CSV files
├── src/wwara_chirp/        # Main source code
│   ├── __init__.py
│   ├── wwara_chirp.py      # Main CLI entry point
│   ├── chirpvalidator.py   # CSV validation logic
│   ├── mock_chirp.py       # CHIRP constants
│   ├── update_mock_chirp.py # GitHub automation
│   └── version.py
├── tests/                  # Unit tests
│   ├── test_files/         # Test CSV files
│   ├── test_chirp_validator.py
│   ├── test_update_mock_chirp.py
│   └── test_wwara_chirp.py
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
└── .gitignore
```

### Key files and their purpose
- `src/wwara_chirp/wwara_chirp.py`: Main CLI application that converts WWARA CSV to CHIRP CSV format
- `src/wwara_chirp/chirpvalidator.py`: Validates CHIRP CSV field formats and values
- `src/wwara_chirp/mock_chirp.py`: Contains constants from CHIRP project (tones, DTCS codes, modes)
- `tests/test_files/WWARA-rptrlist-TEST.csv`: Sample WWARA input file for testing
- `tests/test_files/reference_output.csv`: Expected output for validation
- `.github/workflows/python-package.yml`: Main CI pipeline that tests Python 3.10-3.13

### Project dependencies
From pyproject.toml:
- Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.13)
- pandas ~2.2.3 (CSV data processing)
- numpy ~2.2.4 (numerical operations)
- requests >=2.26.0 (HTTP requests for automation)
- PyGithub >=1.55.0 (GitHub API integration)

### CLI usage examples
```bash
# Basic conversion
wwara_chirp input.csv output.csv

# Using module syntax (development)
python -m wwara_chirp.wwara_chirp input.csv output.csv

# Show help
python -m wwara_chirp.wwara_chirp --help
```

### Sample input/output format
Input (WWARA CSV): Contains fields like FC_RECORD_ID, CALL, OUTPUT_FREQ, INPUT_FREQ, CTCSS_IN, etc.
Output (CHIRP CSV): Contains Location, Name, Frequency, Duplex, Offset, Tone, etc.

### Test execution patterns
```bash
# Run all tests
cd tests && pytest

# Run specific test file
cd tests && pytest test_wwara_chirp.py

# Run with verbose output
cd tests && pytest -v
```

### Linting and code quality
- 78 style warnings exist but do not prevent functionality
- Focus on E9, F63, F7, F82 errors (syntax issues)
- Code complexity warnings in ChirpValidator.validate_row and process_row functions are acceptable
- Many E712 warnings about boolean comparisons in tests are acceptable

### Timing expectations
- Dependencies installation: Often fails due to network timeouts. Use `poetry install` instead.
- Poetry install: 3 seconds (with lock file). NEVER CANCEL. Set timeout to 120+ seconds.
- Test execution: 1 second for all 23 tests
- Linting: 1 second
- CLI conversion: <1 second for typical files
- Package building: FAILS - do not attempt

### GitHub workflows
- `.github/workflows/python-package.yml`: Tests on multiple Python versions, runs pytest and CLI validation
- `.github/workflows/cli-test-push.yml`: Tests packaged CLI tool installation and execution
- `.github/workflows/update_mock_chirp.yml`: Automated updates from upstream CHIRP project

## Code Style and Conventions
- Follow PEP 8 style guidelines with max line length of 127 characters
- Use descriptive variable names that match the domain (e.g., `OUTPUT_FREQ`, `INPUT_FREQ`, `CTCSS_IN`)
- Add docstrings to functions and classes following Google style
- Use type hints where helpful for clarity
- Keep functions focused on a single responsibility
- Complex functions (like `ChirpValidator.validate_row` and `process_row`) are acceptable given the domain complexity
- Use logging (not print statements) for debugging and user feedback
- Maintain consistency with existing code patterns in the repository

## Security Considerations
- Never commit sensitive data (API keys, credentials, etc.) to the repository
- The project processes user-provided CSV files - validate input thoroughly
- File paths must be validated to prevent directory traversal attacks
- Output files should not overwrite existing files without explicit user consent
- Dependencies are pinned to specific versions to ensure reproducible builds
- The GPL-3.0 license ensures code compatibility with the upstream CHIRP project
- When adding new dependencies, verify they are from trusted sources

## Common Tasks and Patterns
### Adding a new field to the conversion
1. Update `WWARA_COLUMNS` list in `wwara_chirp.py` if adding input field
2. Update `CHIRP_COLUMNS` list if adding output field
3. Modify `process_row()` function to handle the mapping
4. Add validation logic in `ChirpValidator` if needed
5. Update test files (`WWARA-rptrlist-TEST.csv`, `reference_output.csv`)
6. Run full validation workflow

### Adding support for a new tone or mode
1. Update constants in `mock_chirp.py` (sourced from CHIRP project)
2. Update validation logic in `ChirpValidator.validate_row()`
3. Add test cases in `test_chirp_validator.py`
4. Run pytest to verify changes

### Debugging conversion issues
1. Check the logs in `wwara-chirp.log` (created during execution)
2. Run with test file: `python -m wwara_chirp.wwara_chirp tests/test_files/WWARA-rptrlist-TEST.csv /tmp/debug_output.csv`
3. Compare output with reference: `diff /tmp/debug_output.csv tests/test_files/reference_output.csv`
4. Use Python debugger or add logging statements in `process_row()` function

## Tips for Effective Changes
- Make minimal, focused changes that address a specific issue
- Always run linting and tests before finalizing changes
- Use the existing test infrastructure - don't add new testing frameworks
- Documentation changes generally don't require tests unless there are doc-specific tests
- When updating dependencies, check for breaking changes in release notes
- The project prioritizes reliability and compatibility over new features