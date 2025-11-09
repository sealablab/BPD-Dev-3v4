"""
Progressive Test Orchestrator for forge_util_edge_detector_pw

Dynamically loads and runs test levels based on TEST_LEVEL environment variable.

Environment Variables:
- TEST_LEVEL: P1_BASIC (default), P2_INTERMEDIATE, P3_COMPREHENSIVE, P4_EXHAUSTIVE
- COCOTB_VERBOSITY: MINIMAL (default), NORMAL, VERBOSE, DEBUG

Usage:
    # P1 tests (default, LLM-optimized)
    uv run python cocotb_tests/run.py forge_util_edge_detector_pw

    # P2 tests
    TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py forge_util_edge_detector_pw

Author: cocotb-progressive-test-runner
Date: 2025-11-09
"""

import cocotb
import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python" / "forge_cocotb"))
sys.path.insert(0, str(Path(__file__).parent))

from forge_cocotb.test_base import TestLevel


def get_test_level() -> TestLevel:
    """Read TEST_LEVEL environment variable"""
    level_str = os.environ.get("TEST_LEVEL", "P1_BASIC")
    return TestLevel[level_str]


@cocotb.test()
async def test_edge_detector_pw_progressive(dut):
    """Progressive test orchestrator"""
    test_level = get_test_level()

    if test_level == TestLevel.P1_BASIC:
        from forge_util_edge_detector_pw_tests.P1_edge_detector_pw_basic import EdgeDetectorPwBasicTests
        tester = EdgeDetectorPwBasicTests(dut)
        await tester.run_p1_basic()

    elif test_level == TestLevel.P2_INTERMEDIATE:
        from forge_util_edge_detector_pw_tests.P2_edge_detector_pw_intermediate import EdgeDetectorPwIntermediateTests
        tester = EdgeDetectorPwIntermediateTests(dut)
        await tester.run_p2_intermediate()

    elif test_level == TestLevel.P3_COMPREHENSIVE:
        from forge_util_edge_detector_pw_tests.P3_edge_detector_pw_comprehensive import EdgeDetectorPwComprehensiveTests
        tester = EdgeDetectorPwComprehensiveTests(dut)
        await tester.run_p3_comprehensive()

    else:
        raise ValueError(f"Unknown test level: {test_level}")
