# Contributing to WWARA CHIRP

Thank you for your interest in contributing to WWARA CHIRP! This project
converts Western Washington Amateur Relay Association (WWARA) repeater
data to CHIRP-compatible CSV format for amateur radio programming.

## Code of Conduct

By participating in this project, you agree to abide by our
[Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check existing [issues](https://github.com/tsayles/wwara_chirp/issues)
   to avoid duplicates
2. Use the bug report template when creating a new issue
3. Include:
   - Python version and OS
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Sample input file (if applicable, with sensitive data removed)

### Suggesting Features

1. Open an issue using the feature request template
2. Describe the use case and expected behavior
3. Consider how it fits with CHIRP compatibility requirements

### Submitting Code Changes

1. Fork the repository
2. Create a feature branch from `master`
3. Make your changes following our [Style Guide](docs/STYLE_GUIDE.md)
4. Write or update tests as needed
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.10 or later
- Poetry (recommended) or pip

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/wwara_chirp.git
cd wwara_chirp

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Set Python path
export PYTHONPATH=$(pwd)/src:$(pwd)/tests

# Run all tests
cd tests && pytest

# Run with verbose output
cd tests && pytest -v
```

### Linting

```bash
# Syntax check (must pass for CI)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Full style check
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### End-to-End Validation

Before submitting a PR, validate the full conversion workflow:

```bash
export PYTHONPATH=$(pwd)/src
python -m wwara_chirp.wwara_chirp \
    tests/test_files/WWARA-rptrlist-TEST.csv \
    /tmp/test_output.csv

# Compare against reference
diff /tmp/test_output.csv tests/test_files/reference_output.csv
```

## Coding Standards

### Style Guide

- Follow PEP 8 with 127 character line length
- Use 4 spaces for indentation (no tabs)
- Add type hints to function signatures
- Write Google-style docstrings for public APIs
- See [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md) for full details

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (Add, Fix, Update, Remove)
- Keep the first line under 72 characters
- Add details in the body if needed

Examples:
```
Add support for D-STAR mode conversion

Fix CTCSS tone validation for edge cases

Update reference output for new test cases
```

### Pull Request Guidelines

- Reference any related issues
- Describe what changes you made and why
- Ensure CI checks pass
- Request review from maintainers
- Be responsive to feedback

## Project Structure

```
wwara_chirp/
├── .github/              # GitHub configuration
│   ├── workflows/        # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/   # Issue templates
│   └── copilot-instructions.md
├── docs/                 # Documentation
│   └── STYLE_GUIDE.md    # Python style guide
├── src/wwara_chirp/      # Source code
│   ├── wwara_chirp.py    # Main CLI application
│   ├── chirpvalidator.py # CSV validation
│   └── mock_chirp.py     # CHIRP constants
├── tests/                # Test suite
│   ├── test_files/       # Test data
│   └── test_*.py         # Test modules
├── CONTRIBUTING.md       # This file
├── CODE_OF_CONDUCT.md    # Community guidelines
├── LICENSE.txt           # GPL-3.0 license
└── README.md             # Project overview
```

## Testing Guidelines

- All new functions must include unit tests
- Use pytest as the testing framework
- Place tests in `tests/` following existing patterns
- Use reference output files for validation
- Mock external dependencies for deterministic tests

## License

By contributing to WWARA CHIRP, you agree that your contributions will
be licensed under the GPL-3.0 license, which ensures compatibility with
the upstream CHIRP project.

## Questions?

- Open an issue for questions about contributing
- Check the README for project documentation
- Review existing issues and PRs for context

Thank you for helping improve WWARA CHIRP!
