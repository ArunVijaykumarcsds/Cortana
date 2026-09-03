"""
CORTANA — Unified Test Suite Runner.
Executes all Stage 2 (ML core), Stage 3 (Database persistence), and Stage 4 (FastAPI backend) tests.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.tests.test_models import TestModelLoaders
from backend.tests.test_rules import TestRulesEngine
from backend.tests.test_calibration import TestCalibrationEngine
from backend.tests.test_fusion import TestRiskFusionEngine
from backend.tests.test_boundaries import TestBoundaries
from backend.tests.test_isolation import TestDatasetIsolation
from backend.tests.test_inference import TestInferenceEngine
from backend.tests.test_database import TestDatabasePersistence
from backend.tests.test_api import TestFastAPIBackend
from backend.tests.test_explanation import TestExplanationLayer


def run_suite() -> bool:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # Stage 2 ML Core Tests (25 tests)
    suite.addTests(loader.loadTestsFromTestCase(TestModelLoaders))
    suite.addTests(loader.loadTestsFromTestCase(TestRulesEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestCalibrationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskFusionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundaries))
    suite.addTests(loader.loadTestsFromTestCase(TestDatasetIsolation))
    suite.addTests(loader.loadTestsFromTestCase(TestInferenceEngine))

    # Stage 3 Database & Persistence Tests (18 tests)
    suite.addTests(loader.loadTestsFromTestCase(TestDatabasePersistence))

    # Stage 4 FastAPI Backend API Tests (21 tests)
    suite.addTests(loader.loadTestsFromTestCase(TestFastAPIBackend))

    # Stage 6A AI Explanation Layer Tests (8 tests)
    suite.addTests(loader.loadTestsFromTestCase(TestExplanationLayer))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()



if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
