# Python Style Guide for WWARA CHIRP

This document provides Python-specific coding standards for the WWARA
CHIRP project. All contributions should follow these guidelines.

> **Note for External Contributors**: The 80-column line length and
> lambda avoidance rules are **mandatory for AI/agent-generated code**
> but **recommended (not required)** for external contributions. We
> welcome contributions that follow the existing 127-character style
> if that's your preference.

## Code Formatting

### Indentation and Line Length

- Use 4 spaces per indentation level (no tabs)
- Maximum line length: **80 characters** (preferred)
  - Agent-generated code: 80 characters (mandatory)
  - External contributions: 127 characters (acceptable)
- Break long statements across multiple lines with proper indentation
- Avoid trailing whitespace on any line

### Lambda Functions

**Avoid lambda functions** - use named functions instead.

Lambda functions are harder to debug, test, and document. Named functions
provide better stack traces and can include docstrings.

**Preferred:**
```python
def get_frequency(row: pd.Series) -> float:
    """Extract frequency from a data row."""
    return float(row['OUTPUT_FREQ'])

frequencies = df.apply(get_frequency, axis=1)
```

**Avoid:**
```python
# Lambda is harder to debug and cannot have docstrings
frequencies = df.apply(lambda row: float(row['OUTPUT_FREQ']), axis=1)
```

This rule is:
- **Mandatory** for agent-generated code
- **Recommended** for external contributions

### PEP 8 Compliance

Follow PEP 8 except where overridden by project-specific settings. The
project uses flake8 for linting with the following configuration:

```bash
# Syntax errors (must pass)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Style check (informational) - note: 80 col preferred, 127 accepted
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=80 --statistics
```

## Imports

### Import Ordering

Follow PEP 8 import ordering:

1. Standard library imports
2. Related third-party imports
3. Local application imports

Separate each group with a blank line.

### Import Style

- Use explicit imports; avoid wildcard imports (`from x import *`)
- Prefer absolute imports over relative imports
- Group related imports together

**Example:**

```python
import logging
import os
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from wwara_chirp.chirpvalidator import ChirpValidator
from wwara_chirp.mock_chirp import TONES, DTCS_CODES
```

## Naming Conventions

### General Rules

Follow PEP 8 naming conventions:

| Type | Convention | Example |
|------|------------|---------|
| Variables | `lower_case_with_underscores` | `output_file` |
| Functions | `lower_case_with_underscores` | `process_row` |
| Classes | `CapitalizedWords` | `ChirpValidator` |
| Constants | `UPPER_CASE_WITH_UNDERSCORES` | `CHIRP_COLUMNS` |
| Private | Single leading underscore | `_validate_tone` |

### Domain-Specific Names

Use descriptive names that match the amateur radio domain:

- `OUTPUT_FREQ`, `INPUT_FREQ` for frequency fields
- `CTCSS_IN`, `CTCSS_OUT` for tone squelch codes
- `DTCS_CODE` for digital tone codes
- `process_row`, `validate_row` for data processing functions

## Type Hints

### Function Signatures

Add type hints to all function parameters and return values:

```python
def process_row(
    row: pd.Series,
    validator: ChirpValidator
) -> Optional[Dict[str, str]]:
    """Process a single row from WWARA CSV."""
    ...
```

### Complex Types

Use the `typing` module for complex types:

```python
from typing import Dict, List, Optional, Tuple, Union

def get_frequencies(
    data: pd.DataFrame
) -> List[Tuple[str, float]]:
    """Extract frequency pairs from data."""
    ...
```

## Documentation

### Docstrings (Google Style)

Use Google-style docstrings for all public functions and classes:

```python
def validate_frequency(freq: str) -> bool:
    """Validate a frequency value for CHIRP compatibility.

    Checks that the frequency is a valid numeric string within the
    amateur radio frequency range.

    Args:
        freq: Frequency string in MHz format (e.g., "146.520").

    Returns:
        True if the frequency is valid, False otherwise.

    Raises:
        ValueError: If freq is not a valid numeric string.

    Example:
        >>> validate_frequency("146.520")
        True
        >>> validate_frequency("invalid")
        False
    """
    ...
```

### Class Docstrings

```python
class ChirpValidator:
    """Validates CHIRP CSV field formats and values.

    This class provides validation methods for all CHIRP CSV fields,
    ensuring compatibility with the CHIRP radio programming software.

    Attributes:
        valid_tones: List of valid CTCSS tone values.
        valid_modes: List of valid operating modes.

    Example:
        >>> validator = ChirpValidator()
        >>> validator.validate_row(row_data)
        True
    """
```

### Comments

- Comments should explain "why", not "what"
- Avoid obvious comments that restate the code
- Use inline comments sparingly
- Keep comments up to date with code changes

## Logging

### Setup

Use Python's `logging` module with module-level loggers:

```python
import logging

logger = logging.getLogger(__name__)
```

### Log Levels

Use appropriate log levels:

| Level | Usage |
|-------|-------|
| `DEBUG` | Detailed diagnostic information |
| `INFO` | General operational messages |
| `WARNING` | Recoverable issues or unusual situations |
| `ERROR` | Failures that don't stop execution |
| `CRITICAL` | Severe errors that may cause termination |

### Best Practices

```python
def process_data_file(filepath: str) -> int:
    """Process a data file and return the number of records."""
    logger.info(f"Starting processing of file: {filepath}")
    try:
        df = pd.read_csv(filepath)
        record_count = len(df)
        logger.debug(f"Read {record_count} records from {filepath}")
        
        # Processing logic...
        
        logger.info(f"Successfully processed {record_count} records")
        return record_count
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Failed to process {filepath}: {e}", exc_info=True)
        raise
```

- Log file operations with paths and record counts
- Include relevant context in log messages
- Never log sensitive information
- Use `exc_info=True` when logging exceptions

## Error Handling

### Exception Types

Use specific exception types rather than generic `Exception`:

```python
try:
    df = pd.read_csv(input_path)
except FileNotFoundError:
    logger.error(f"Input file not found: {input_path}")
    raise
except pd.errors.EmptyDataError:
    logger.error(f"Input file is empty: {input_path}")
    raise
except pd.errors.ParserError as e:
    logger.error(f"CSV parsing error in {input_path}: {e}")
    raise
```

### Context Managers

Use context managers for resource cleanup:

```python
with open(output_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)
```

### Error Messages

Include helpful information in error messages:

```python
if not os.path.exists(input_path):
    raise FileNotFoundError(
        f"Input file not found: {input_path}. "
        f"Please verify the file path and try again."
    )
```

## Testing

### Test Structure

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_<what_is_being_tested>`

### Test Style

Follow the Arrange-Act-Assert pattern:

```python
def test_process_row_handles_empty_ctcss():
    """Test that empty CTCSS values are handled correctly."""
    # Arrange
    row = pd.Series({
        'OUTPUT_FREQ': '146.520',
        'CTCSS_IN': '',
    })
    validator = ChirpValidator()
    
    # Act
    result = process_row(row, validator)
    
    # Assert
    assert result['Tone'] == ''
    assert result['Frequency'] == '146.520'
```

### Mocking

Mock external dependencies for deterministic tests:

```python
from unittest.mock import patch, mock_open

def test_read_csv_file():
    """Test CSV file reading."""
    mock_data = "col1,col2\nval1,val2\n"
    with patch('builtins.open', mock_open(read_data=mock_data)):
        result = read_csv_file('test.csv')
    assert len(result) == 1
```

## Architecture and Design

### SOLID Principles

- **Single Responsibility**: Each function/class should do one thing
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Prefer small, specific interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Code Organization

- Keep modules focused on a single responsibility
- Separate data validation (`chirpvalidator.py`) from processing
  (`wwara_chirp.py`)
- Use constants modules (`mock_chirp.py`) for shared values

### Acceptable Complexity

Some functions (like `ChirpValidator.validate_row` and `process_row`)
have higher complexity due to domain requirements. This is acceptable
when:

- The complexity is inherent to the problem domain
- The function is well-documented
- Edge cases are thoroughly tested

## Security

- Validate all user-provided input (especially CSV files)
- Prevent directory traversal in file paths
- Never commit sensitive data (API keys, credentials)
- Verify dependencies are from trusted sources
- Keep dependencies up to date for security patches

## Quick Reference

Before submitting code, verify:

- [ ] Code follows PEP 8 (80 char lines preferred, 127 acceptable)
- [ ] No lambda functions (use named functions instead)
- [ ] Functions have type hints
- [ ] Public APIs have Google-style docstrings
- [ ] Logging is implemented for important operations
- [ ] Tests are written and passing
- [ ] Linting passes (`flake8 --select=E9,F63,F7,F82`)
- [ ] No hardcoded secrets
- [ ] Imports are organized and explicit

### Agent-Generated Code Requirements

Code generated by GitHub Copilot or other AI agents **must**:
- Use 80-character line length
- Avoid lambda functions entirely
- Follow all other style guidelines strictly
