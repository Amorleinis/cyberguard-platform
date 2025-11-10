"""
Test Runner for Threat Intelligence Platform
Executes all unit and integration tests
"""

import unittest
import sys
import os
from pathlib import Path
from datetime import datetime
import json

def run_all_tests():
    """Run all tests and generate report"""
    
    print("=" * 80)
    print("THREAT INTELLIGENCE PLATFORM - TEST SUITE")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print()
    
    # Save results to file
    results_file = start_dir.parent / "test_results.json"
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": result.testsRun,
        "successes": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
    }
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    print()
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
