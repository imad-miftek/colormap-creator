#!/usr/bin/env python
"""
Run the tests for the Colormap Creator application.
"""

import unittest
import sys
from tests.test_num_colors import TestNumColors

if __name__ == "__main__":
    # Create a test suite
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(TestNumColors))
    
    # Run the test
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful()) 