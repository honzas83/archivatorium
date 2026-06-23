# Quickstart & Verification Guide: Rename to Archivatorium

This guide details the validation steps to verify the project has been successfully renamed to `archivatorium` and that all functionality remains intact.

## 1. Prerequisites

- Python 3.12+ installed
- Current working directory at the repository root
- Virtual environment active

---

## 2. Installation and Verification

Verify that the project can be installed under the new name.

```bash
# Clean up any leftover build artifacts from ocrpolish
rm -rf build/ dist/ *.egg-info/

# Install the package in editable mode
pip install -e .
```

Verify that the CLI executable `archivatorium` is installed and functional:

```bash
# Check if the archivatorium command is available and displays the help message
archivatorium --help
```

*Expected Outcome:* The help message displays details of the toolkit with references to `archivatorium` and its subcommands, and no mentions of `ocrpolish`.

---

## 3. Test Suite Validation

Verify that all unit and integration tests discover the new package name and execute successfully:

```bash
# Run pytest with code coverage tracking
pytest
```

*Expected Outcome:* All tests pass without any `ModuleNotFoundError` or test failures.

---

## 4. Search and Linting Integrity

Confirm that `ocrpolish` references (case-insensitive) have been fully eliminated from code, comments, configurations, and documentations, while keeping historical specs untouched.

```bash
# Run static analysis/formatting checks
ruff check .
mypy .

# Verify no remaining case-insensitive occurrences of 'ocrpolish' in active directories
# (excluding specs/ except for this specific feature folder)
grep -ri "ocrpolish" --exclude-dir=specs --exclude-dir=.git --exclude-dir=.venv .
```

*Expected Outcome:*
- Ruff and Mypy pass with zero errors.
- The `grep` command returns no matches outside the `specs/` and other ignored directories.
