# def-form

Python function definition formatter

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI](https://img.shields.io/pypi/v/def-form.svg)](https://pypi.python.org/pypi/def-form)
[![PyPI](https://img.shields.io/pypi/dm/def-form.svg)](https://pypi.python.org/pypi/def-form)
[![Coverage Status](https://coveralls.io/repos/github/TopNik073/def-form/badge.svg?branch=polish-docs)](https://coveralls.io/github/TopNik073/def-form?branch=polish-docs)

## Overview

`def-form` is a code formatting tool that focuses specifically on Python function definitions. It helps maintain consistent formatting of function signatures by automatically organizing arguments vertically when they exceed specified thresholds.

## Features

- **Automatic argument formatting**: Converts inline function arguments to vertical format based on configurable rules
- **CI/CD integration**: Provides both `format` and `check` commands for use in development pipelines
- **Configuration file support**: Uses `pyproject.toml` for project-specific settings
- **Customizable thresholds**: Control when arguments should be formatted vertically

## Installation

```bash
pip install def-form
```

## Usage

### Format code

* Format all Python files in a directory:

```bash
def-form format src/
```

* Format a specific file:

```bash
def-form format my_module.py
```

### Check code without formatting

* Check if code follows formatting rules:

```bash
def-form check src/
```

### Command line options

```text
def-form format [OPTIONS] [PATH]

Options:
  --max-def-length INTEGER  Maximum length of function definition
  --max-inline-args INTEGER Maximum number of inline arguments
  --indent-size INTEGER     indent size in spaces (default: 4)
  --exclude TEXT            Paths or files to exclude from checking/formatting
  --show-skipped            Show skipped files/directories
  --config TEXT             Path to pyproject.toml configuration file
```

### Configuration

Create a pyproject.toml file in your project root:

```toml
[tool.def-form]
max_def_length = 100
max_inline_args = 2
indent_size = 4
exclude = [
    '.venv',
    'migrations'
]
```

### Configuration options

* max_def_length: Maximum allowed characters in a single-line function definition
* max_inline_args: Maximum number of arguments allowed in inline format
* indent_size: Indent for arguments in spaces
* exclude: Files or directories you want to exclude