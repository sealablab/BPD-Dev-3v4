"""
Progressive CocoTB Testbench for forge_util_majority_voter

Uses TestBase framework for progressive testing (P1/P2/P3/P4).
Test level controlled by TEST_LEVEL environment variable:
- P1_BASIC (default): Minimal tests, <15 lines output
- P2_INTERMEDIATE: Full test suite

Usage:
    # P1 only (minimal output)
    uv run python cocotb_tests/run.py forge_util_majority_voter

    # P2 (all tests)
    TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py forge_util_majority_voter

Component: forge_util_majority_voter
Category: utilities
Purpose: 3-input majority logic voter for fault-tolerant digital systems

Author: forge-vhdl 3-agent workflow (test workflow validation)
Date: 2025-11-09
"""

import cocotb
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from test_base import TestBase, TestLevel
from forge_util_majority_voter_tests.P1_forge_util_majority_voter_basic import MajorityVoterBasicTests


def get_test_level() -> TestLevel:
    """Read TEST_LEVEL environment variable"""
    import os
    level_str = os.environ.get("TEST_LEVEL", "P1_BASIC")
    return TestLevel[level_str]


@cocotb.test()
async def test_forge_util_majority_voter_progressive(dut):
    """Progressive test orchestrator"""
    test_level = get_test_level()

    if test_level == TestLevel.P1_BASIC:
        tester = MajorityVoterBasicTests(dut)
        await tester.run_p1_basic()

    elif test_level == TestLevel.P2_INTERMEDIATE:
        # P2 tests not implemented yet
        tester = MajorityVoterBasicTests(dut)
        await tester.run_p1_basic()
        print("Note: P2 tests not yet implemented, running P1 only")

    elif test_level == TestLevel.P3_COMPREHENSIVE:
        # P3 tests not implemented yet
        tester = MajorityVoterBasicTests(dut)
        await tester.run_p1_basic()
        print("Note: P3 tests not yet implemented, running P1 only")

    else:
        raise ValueError(f"Unknown test level: {test_level}")
