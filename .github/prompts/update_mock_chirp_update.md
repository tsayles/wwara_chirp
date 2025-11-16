# Update Mock CHIRP - Rebuild Automation Solution

## Problem Statement

The `src/wwara_chirp/update_mock_chirp.py` script and its associated GitHub Action workflow (`.github/workflows/update_mock_chirp.yml`) are currently failing. This document provides detailed specifications for rebuilding a robust solution to automatically keep the mock CHIRP constants synchronized with the upstream kk7ds/chirp project.

## Context and Background

### Why This Feature Exists

The wwara_chirp project depends on constants from the kk7ds/chirp project (specifically from `chirp_common.py`):
- **TONES**: A tuple of 50 CTCSS tone frequencies (67.0-254.1 Hz)
- **DTCS_CODES**: A tuple of 104 DCS (Digital-Coded Squelch) codes
- **MODES**: A tuple of amateur radio modulation modes (WFM, FM, NFM, AM, etc.)

However, CHIRP is not published to PyPI, creating a dependency management challenge. The solution is to maintain a `mock_chirp.py` module that contains these constants as a local copy, decoupling wwara_chirp from the upstream CHIRP project while still allowing periodic synchronization.

### Current Issues (as of November 2025)

1. **Import Error**: The script fails with `ModuleNotFoundError: No module named 'github'` because:
   - The GitHub Action runs `python src/wwara_chirp/update_mock_chirp.py` directly
   - PyGithub is installed in the poetry virtualenv but not available to the system Python
   - The workflow should use `poetry run python` instead

2. **Design Flaws in Current Implementation**:
   - **Repository Re-cloning**: The script clones the wwara_chirp repo again inside the GitHub Action, which is unnecessary since the workflow already checks out the repo
   - **Incorrect Parsing**: Uses `ast.literal_eval()` to parse `mock_chirp.py`, which fails because it's a Python module, not a dictionary literal
   - **Poor Code Generation**: Writes constants as a string representation of a dictionary rather than proper Python code
   - **Missing Error Handling**: No validation or error recovery mechanisms

3. **Test Coverage Issues**:
   - Tests in `tests/test_update_mock_chirp.py` don't properly simulate the actual workflow
   - Tests create temporary files but don't test the full integration

### Related Issues
- **Issue #28**: "Establish mock interface to kk7ds/chirp" - Parent issue for creating the abstraction layer
- **Issue #30**: "Automatically Generate Pull Requests for Relevant Updates" - This specific automation feature

## Requirements and Specifications

### Functional Requirements

#### FR1: Constant Synchronization
The solution MUST:
1. Fetch the latest `chirp_common.py` from `https://raw.githubusercontent.com/kk7ds/chirp/refs/heads/master/chirp/chirp_common.py`
2. Extract the following constants (case-sensitive, uppercase only):
   - `TONES` (tuple of floats)
   - `DTCS_CODES` (tuple of integers)
   - `MODES` (tuple of strings)
3. Compare extracted constants with current values in `src/wwara_chirp/mock_chirp.py`
4. Update `mock_chirp.py` only if differences are detected
5. Preserve the existing structure and comments in `mock_chirp.py`

#### FR2: Pull Request Creation
When updates are detected, the solution MUST:
1. Create a new branch with a descriptive name (e.g., `update-mock-chirp-YYYYMMDD`)
2. Commit changes with a clear commit message
3. Create a pull request to the `dev` branch with:
   - Clear title: "Update mock_chirp.py with latest constants from CHIRP"
   - Detailed description listing what changed
   - Reference to issue #30
4. Handle the case where a PR already exists (avoid duplicates)

#### FR3: GitHub Actions Integration
The workflow MUST:
1. Run weekly (every Sunday at midnight UTC) using cron schedule
2. Support manual triggering via `workflow_dispatch`
3. Run in the poetry virtual environment
4. Use appropriate GitHub token permissions for PR creation
5. Provide clear logging for debugging

### Non-Functional Requirements

#### NFR1: Code Quality
- Follow existing code style and linting rules (flake8)
- Include comprehensive docstrings
- Handle errors gracefully with informative messages
- Use type hints where appropriate

#### NFR2: Testability
- Must be testable without actual GitHub API calls
- Tests should use mocking for external dependencies
- Should achieve >80% code coverage
- Tests must pass in the existing test suite

#### NFR3: Maintainability
- Code should be self-documenting
- Configuration should be easily modifiable
- Should not duplicate functionality
- Must integrate with existing CI/CD workflows

#### NFR4: Security
- Never commit secrets or tokens to the repository
- Use GitHub's built-in token for API access
- Validate all external input
- Follow principle of least privilege

## Technical Design

### Recommended Architecture

```
update_mock_chirp/
├── __init__.py
├── fetcher.py          # Fetches and parses chirp_common.py
├── comparator.py       # Compares constants and detects changes
├── generator.py        # Generates updated mock_chirp.py content
└── git_ops.py          # Handles Git operations and PR creation
```

### Module Responsibilities

#### fetcher.py
```python
class ChirpConstantsFetcher:
    """Fetches and extracts constants from upstream CHIRP project."""
    
    def fetch_chirp_common(self, url: str) -> str:
        """Download chirp_common.py content."""
        
    def extract_constants(self, source_code: str) -> dict:
        """Parse source and extract TONES, DTCS_CODES, MODES."""
```

#### comparator.py
```python
class ConstantComparator:
    """Compares constants and identifies differences."""
    
    def load_current_constants(self, filepath: str) -> dict:
        """Load constants from current mock_chirp.py."""
        
    def compare(self, current: dict, upstream: dict) -> tuple[bool, dict]:
        """Returns (has_changes, diff_details)."""
```

#### generator.py
```python
class MockChirpGenerator:
    """Generates properly formatted mock_chirp.py content."""
    
    def generate(self, constants: dict, template: str) -> str:
        """Generate new mock_chirp.py content preserving structure."""
```

#### git_ops.py
```python
class GitOperations:
    """Handles Git operations and GitHub PR creation."""
    
    def create_branch(self, branch_name: str):
        """Create and checkout new branch."""
        
    def commit_changes(self, filepath: str, message: str):
        """Stage and commit changes."""
        
    def push_branch(self, branch_name: str):
        """Push branch to origin."""
        
    def create_pull_request(self, title: str, body: str, 
                          head: str, base: str) -> int:
        """Create PR using PyGithub, returns PR number."""
```

### Data Flow

1. **Fetch Phase**:
   ```
   GitHub Action triggers → Fetch chirp_common.py → Parse constants
   ```

2. **Comparison Phase**:
   ```
   Load current mock_chirp.py → Compare constants → Detect changes
   ```

3. **Update Phase** (if changes detected):
   ```
   Generate new content → Create branch → Commit → Push → Create PR
   ```

4. **No-op Phase** (if no changes):
   ```
   Log "No updates needed" → Exit successfully
   ```

### Configuration

Use environment variables and class constants:

```python
CHIRP_COMMON_URL = "https://raw.githubusercontent.com/kk7ds/chirp/refs/heads/master/chirp/chirp_common.py"
MOCK_CHIRP_PATH = "src/wwara_chirp/mock_chirp.py"
BASE_BRANCH = "dev"
BRANCH_PREFIX = "update-mock-chirp"
REPO_NAME = "tsayles/wwara_chirp"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
```

## Test-First Development Plan

### Phase 1: Unit Tests (TDD Approach)

Write tests BEFORE implementing each component:

#### 1.1 Test Fetcher
```python
def test_fetch_chirp_common_success():
    """Test successful fetch of chirp_common.py."""
    
def test_extract_constants_tones():
    """Test extraction of TONES constant."""
    
def test_extract_constants_dtcs_codes():
    """Test extraction of DTCS_CODES constant."""
    
def test_extract_constants_modes():
    """Test extraction of MODES constant."""
    
def test_extract_constants_ignores_lowercase():
    """Test that lowercase variables are ignored."""
```

#### 1.2 Test Comparator
```python
def test_compare_no_changes():
    """Test when constants are identical."""
    
def test_compare_tones_changed():
    """Test detection of TONES changes."""
    
def test_compare_new_constant_added():
    """Test detection of new constant in upstream."""
    
def test_compare_constant_removed():
    """Test detection of removed constant."""
```

#### 1.3 Test Generator
```python
def test_generate_preserves_structure():
    """Test that generated code preserves module structure."""
    
def test_generate_formats_constants_correctly():
    """Test proper Python formatting of constants."""
    
def test_generate_includes_comments():
    """Test that comments and docstrings are preserved."""
```

#### 1.4 Test Git Operations (with mocking)
```python
def test_create_branch(mock_subprocess):
    """Test branch creation."""
    
def test_commit_changes(mock_subprocess):
    """Test committing changes."""
    
def test_create_pull_request(mock_github):
    """Test PR creation via PyGithub."""
    
def test_handle_existing_pr(mock_github):
    """Test handling when PR already exists."""
```

### Phase 2: Integration Tests

```python
def test_end_to_end_with_changes(tmp_path):
    """Test complete flow when updates are needed."""
    
def test_end_to_end_no_changes(tmp_path):
    """Test complete flow when no updates needed."""
    
def test_workflow_in_github_action_environment(monkeypatch):
    """Test that script works in GitHub Actions context."""
```

### Phase 3: Implementation

After writing tests:

1. Implement `fetcher.py` until tests pass
2. Implement `comparator.py` until tests pass
3. Implement `generator.py` until tests pass
4. Implement `git_ops.py` until tests pass
5. Create main script that orchestrates components
6. Update GitHub workflow to use poetry

### Phase 4: Workflow Updates

Update `.github/workflows/update_mock_chirp.yml`:

```yaml
name: Update Mock Chirp

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday at midnight UTC

jobs:
  update-mock-chirp:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
    - uses: actions/checkout@v5
      with:
        fetch-depth: 0  # Need full history for git operations
    
    - name: Set up Python
      uses: actions/setup-python@v6
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    
    - name: Run update script
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        poetry run python -m update_mock_chirp.main
    
    - name: Report status
      if: always()
      run: echo "Update check completed"
```

## Success Criteria

The solution is considered successful when:

1. ✅ All unit tests pass
2. ✅ All integration tests pass
3. ✅ Code coverage > 80%
4. ✅ Flake8 linting passes with no errors
5. ✅ GitHub Action workflow runs successfully
6. ✅ Manual workflow trigger works correctly
7. ✅ PR is created when constants change
8. ✅ No PR created when constants unchanged
9. ✅ Existing tests in repository still pass
10. ✅ Documentation is updated

## Continuous Deployment Considerations

### Versioning Strategy
- When constants are updated via PR, consider whether a new release is needed
- Could be automated with a secondary workflow that:
  - Triggers on merge to dev branch
  - Runs tests
  - Creates a release candidate
  - Publishes to PyPI (if configured)

### Notification Strategy
- PR creation serves as notification
- Consider adding:
  - PR labels (e.g., "automated", "dependencies")
  - Assignee (repository owner)
  - Slack/Discord webhook notifications (optional)

### Rollback Strategy
- If updates break tests, PR won't be merged
- Repository owner reviews PR before merge
- Can revert PR if issues discovered post-merge

## Implementation Notes

### Current File Structure to Preserve

The `mock_chirp.py` file should maintain its current structure:

```python
# This module provides a mock chirp class which abstracts the functions and
# methods from the kk7ds/chirp project, and decouples the direct dependency on
# the kk7ds/chirp project.

import difflib

class MockChirp(object):
    def __init__(self):
        self.channels = []

    # Sources in the CHIRP project that need to be checked for updates
    CHIRP_SOURCES = ['https://raw.githubusercontent.com/kk7ds/chirp/refs/heads/master/chirp/chirp_common.py']

    # 50 Tones
    TONES = (
        # ... values ...
    )

    # 104 DTCS Codes
    DTCS_CODES = (
        # ... values ...
    )

    # Master list of modes
    MODES = (
        # ... values ...
    )

class CheckMockChirp:
    # ... existing code ...
```

### Parsing Strategy

Instead of `ast.literal_eval()`, use proper AST parsing:

```python
import ast

def extract_constants(source_code: str) -> dict:
    """Extract constant values from Python source code."""
    tree = ast.parse(source_code)
    constants = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    # Safely evaluate the constant value
                    constants[target.id] = ast.literal_eval(node.value)
    
    return constants
```

### Error Handling

Include comprehensive error handling:

```python
class UpdateError(Exception):
    """Base exception for update errors."""
    pass

class FetchError(UpdateError):
    """Failed to fetch upstream constants."""
    pass

class ParseError(UpdateError):
    """Failed to parse constants."""
    pass

class GitError(UpdateError):
    """Git operation failed."""
    pass
```

## Migration Path

### Step 1: Deprecate Old Script
- Move `src/wwara_chirp/update_mock_chirp.py` to `src/wwara_chirp/update_mock_chirp.old.py`
- Add deprecation notice

### Step 2: Implement New Solution
- Create new package structure
- Implement with tests
- Update workflow

### Step 3: Validate
- Run new solution in test mode
- Compare output with expected results
- Get code review

### Step 4: Deploy
- Merge to dev branch
- Monitor first automated run
- Clean up deprecated code after successful run

## References

- Issue #28: https://github.com/tsayles/wwara_chirp/issues/28
- Issue #30: https://github.com/tsayles/wwara_chirp/issues/30
- CHIRP Project: https://github.com/kk7ds/chirp
- CHIRP Common Module: https://github.com/kk7ds/chirp/blob/master/chirp/chirp_common.py
- PyGithub Documentation: https://pygithub.readthedocs.io/
- Poetry Documentation: https://python-poetry.org/docs/

## Questions for Implementer

Before starting implementation, consider:

1. Should the update check run more/less frequently than weekly?
2. Should PRs be auto-merged if tests pass, or always require manual review?
3. Are there other constants from chirp_common.py that should be tracked?
4. Should the solution support tracking multiple source files beyond chirp_common.py?
5. What's the preferred error notification method (GitHub issue, email, etc.)?

---

**Last Updated**: November 16, 2025  
**Status**: Ready for Implementation  
**Priority**: High (blocks issue #30)
