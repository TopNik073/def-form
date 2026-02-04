<div style="padding-top: 30px; text-align: center;">
  <img src="https://raw.githubusercontent.com/TopNik073/def-form/main/assets/logo-transparent.png" alt="def-form logo" width="300">

  <p style="margin: 0; font-size: 18px;">Python function definition formatter</p>

  [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
  [![PyPI](https://img.shields.io/pypi/v/def-form.svg)](https://pypi.python.org/pypi/def-form)
  [![PyPI](https://img.shields.io/pypi/dm/def-form.svg)](https://pypi.python.org/pypi/def-form)
  [![Coverage Status](https://coveralls.io/repos/github/TopNik073/def-form/badge.svg?branch=init)](https://coveralls.io/github/TopNik073/def-form?branch=init)

</div>

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

### Example

You can check your code with `check` command and see the result

```text
(.venv) user@MacBook-Pro def-form % def-form check test_file.py
Checking test_file.py

                           Configuration                           
 ───────────────────────────────────────────────────────────────── 
  Config Path:       /Users/user/Documents/def-form/pyproject.toml  
  Max Inline Args:   2                                             
  Max Def Length:    100                                           
  Indent Size:       4 spaces                                      
  Show Skipped:      No                                            
  Excluded:          .venv, tests/cases, build                     
 ───────────────────────────────────────────────────────────────── 

Found 1 errors in 1 files

/Users/user/Documents/def-form/test_file.py:19
  • Invalid multiline function parameters indentation (expected 4 spaces)

           Summary           
 ─────────────────────────── 
  Files processed:     1     
  Files with issues:   1     
  Total errors:        1     
  Success rate:        0.0%  
 ─────────────────────────── 

Code style violations found
```

Or use `format`
```text
(.venv) user@MacBook-Pro def-form % def-form format test_file.py
Formatting test_file.py

                           Configuration                           
 ───────────────────────────────────────────────────────────────── 
  Config Path:       /Users/user/Documents/def-form/pyproject.toml  
  Max Inline Args:   2                                             
  Max Def Length:    100                                           
  Indent Size:       4 spaces                                      
  Show Skipped:      No                                            
  Excluded:          build, .venv, tests/cases                     
 ───────────────────────────────────────────────────────────────── 

Found 1 errors in 1 files

/Users/user/Documents/def-form/test_file.py:19
  • Invalid multiline function parameters indentation (expected 4 spaces)

           Summary           
 ─────────────────────────── 
  Files processed:     1     
  Files with issues:   1     
  Total errors:        1     
  Success rate:        0.0%  
 ─────────────────────────── 

Formatting completed
```

## Command line options

There is global options

```text
Usage: def-form [OPTIONS] COMMAND [ARGS]...

Options:
  --verbose  Enable verbose output
  --quiet    Disable all output
  --help     Show this message and exit.

Commands:
  check
  format
```

And specific options for check/format

```text
Usage: def-form format [OPTIONS] [PATH]

Options:
  --config FILE              Path to pyproject.toml configuration file
  --show-skipped             Show skipped files and directories
  --exclude PATH             Paths to exclude from processing
  --indent-size INTEGER      Indent size in spaces (default: 4)
  --max-inline-args INTEGER  Maximum number of inline arguments
  --max-def-length INTEGER   Maximum length of function definition
  --help                     Show this message and exit.
```

## Configuration

Create a pyproject.toml file in your project root:

```toml
[tool.def-form]
max_def_length = 100  # Maximum allowed characters in a single-line function definition
max_inline_args = 2   # Maximum number of arguments allowed in inline format
indent_size = 4       # Indent for arguments in spaces
exclude = [           # Files or directories you want to exclude
    '.venv',
    'migrations'
]
```