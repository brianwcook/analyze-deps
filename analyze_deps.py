#!/usr/bin/env python3

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import requests
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet


def validate_requirements_file(file_path: str) -> bool:
    """Validate that the file is a valid requirements file."""
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    Requirement(line)
        return True
    except Exception as e:
        print(f"Error validating requirements file: {e}", file=sys.stderr)
        return False


def check_package_in_index(package_name: str, index_url: str) -> bool:
    """Check if a package is available in the specified index."""
    try:
        response = requests.get(f"{index_url}/{package_name}/")
        return response.status_code == 200
    except requests.RequestException:
        return False


def process_requirements_file(
    input_file: str,
    preferred_index: Optional[str],
    default_index: str
) -> Tuple[str, bool]:
    """Process the requirements file and return the updated content."""
    updated_lines = []
    success = True

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                updated_lines.append(line)
                continue

            try:
                req = Requirement(line)
                package_name = req.name

                if preferred_index and check_package_in_index(package_name, preferred_index):
                    updated_lines.append(f"{line} --index-url {preferred_index}")
                else:
                    updated_lines.append(f"{line} --index-url {default_index}")
            except Exception as e:
                print(f"Error processing line '{line}': {e}", file=sys.stderr)
                success = False
                updated_lines.append(line)

    return '\n'.join(updated_lines), success


def main():
    parser = argparse.ArgumentParser(description='Analyze Python dependencies and generate hashes.')
    parser.add_argument('input_file', help='Input requirements file')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-p', '--preferred-index', help='Preferred PyPI index URL')
    parser.add_argument('-d', '--default-index', 
                       default='https://pypi.org/simple',
                       help='Default PyPI index URL (default: https://pypi.org/simple)')

    args = parser.parse_args()

    # Validate input file
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not validate_requirements_file(args.input_file):
        sys.exit(1)

    # Process requirements file
    updated_content, success = process_requirements_file(
        args.input_file,
        args.preferred_index,
        args.default_index
    )

    if not success:
        sys.exit(1)

    # Create temporary file with updated requirements
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(updated_content)
        temp_file_path = temp_file.name

    try:
        # Run pip-compile with --generate-hashes
        result = subprocess.run(
            ['pip-compile', '--generate-hashes', temp_file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error running pip-compile: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        # Print output to terminal
        print(result.stdout)

        # Write to output file if specified
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result.stdout)

    finally:
        # Clean up temporary file
        Path(temp_file_path).unlink()


if __name__ == '__main__':
    main() 