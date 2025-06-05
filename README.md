# analyze-deps

A Python tool for analyzing dependencies in requirements files and generating hashes.

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python analyze_deps.py [input_file] [-o OUTPUT] [-p PREFERRED_INDEX] [-d DEFAULT_INDEX]
```

### Arguments

- `input_file`: Required. Path to the requirements.txt style file to analyze
- `-o, --output`: Optional. Path to write the output file
- `-p, --preferred-index`: Optional. URL of the preferred PyPI index
- `-d, --default-index`: Optional. URL of the default PyPI index (default: https://pypi.org/simple)

### Examples

Basic usage:
```bash
python analyze_deps.py requirements.txt
```

With output file:
```bash
python analyze_deps.py requirements.txt -o output.txt
```

With preferred index:
```bash
python analyze_deps.py requirements.txt -p https://custom.pypi.org/simple
```

With custom default index:
```bash
python analyze_deps.py requirements.txt -d https://alternative.pypi.org/simple
```

## Features

- Validates input requirements file
- Checks package availability in preferred index
- Adds appropriate index URLs to requirements
- Generates hashes for all dependencies
- Supports output to file or terminal
- Handles both preferred and default PyPI indices
