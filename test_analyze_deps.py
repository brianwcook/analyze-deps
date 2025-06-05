#!/usr/bin/env python3

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from analyze_deps import (
    validate_requirements_file,
    check_package_in_index,
    process_requirements_file,
)


class TestAnalyzeDeps(unittest.TestCase):
    def setUp(self):
        self.test_requirements = "test_requirements.txt"
        self.preferred_index = "https://console.redhat.com/api/pulp-content/public-calunga/mypypi/simple"
        self.default_index = "https://pypi.org/simple"

    def test_validate_requirements_file(self):
        """Test requirements file validation."""
        # Test valid file
        self.assertTrue(validate_requirements_file(self.test_requirements))

        # Test invalid file with malformed requirement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("package name with spaces @ version\n")  # Invalid requirement format
            temp_file_path = temp_file.name

        try:
            self.assertFalse(validate_requirements_file(temp_file_path))
        finally:
            os.unlink(temp_file_path)

    @patch('analyze_deps.requests.get')
    def test_check_package_in_index(self, mock_get):
        """Test package availability checking in index."""
        # Mock successful response for urllib3
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Test urllib3 in preferred index
        self.assertTrue(check_package_in_index("urllib3", self.preferred_index))

        # Mock failed response for requests
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test requests not in preferred index
        self.assertFalse(check_package_in_index("requests", self.preferred_index))

    @patch('analyze_deps.check_package_in_index')
    def test_process_requirements_file(self, mock_check_package):
        """Test requirements file processing."""
        # Mock package availability
        def mock_check(package_name, index_url):
            return package_name == "urllib3"

        mock_check_package.side_effect = mock_check

        # Process the requirements file
        updated_content, success = process_requirements_file(
            self.test_requirements,
            self.preferred_index,
            self.default_index
        )

        self.assertTrue(success)
        
        # Split content into lines and check each package
        lines = updated_content.split('\n')
        for line in lines:
            if not line or line.startswith('#'):
                continue
            
            if 'urllib3' in line:
                self.assertIn(f"--index-url {self.preferred_index}", line)
            elif 'requests' in line:
                self.assertIn(f"--index-url {self.default_index}", line)

    def test_end_to_end(self):
        """Test the complete workflow with actual file processing."""
        # First verify that urllib3 is actually available in the preferred index
        self.assertTrue(check_package_in_index("urllib3", self.preferred_index),
                       "urllib3 should be available in the preferred index")
        
        # Verify that requests is not available in the preferred index
        self.assertFalse(check_package_in_index("requests", self.preferred_index),
                        "requests should not be available in the preferred index")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("requests>=2.31.0\nurllib3>=2.0.0\n")
            temp_file_path = temp_file.name

        try:
            # Process the temporary file
            updated_content, success = process_requirements_file(
                temp_file_path,
                self.preferred_index,
                self.default_index
            )

            self.assertTrue(success)
            
            # Verify the output
            lines = updated_content.split('\n')
            urllib3_line = next(line for line in lines if 'urllib3' in line)
            requests_line = next(line for line in lines if 'requests' in line)

            self.assertIn(f"--index-url {self.preferred_index}", urllib3_line)
            self.assertIn(f"--index-url {self.default_index}", requests_line)

        finally:
            os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main() 