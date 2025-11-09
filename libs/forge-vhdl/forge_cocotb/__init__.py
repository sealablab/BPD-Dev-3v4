"""
forge_cocotb: CocoTB Test Infrastructure for VHDL Testing

Token-efficient progressive testing infrastructure optimized for LLM workflows.

**Key Innovation:** 98% test output reduction through GHDL filtering + progressive levels.

Progressive Test Levels:
- P1_BASIC: 2-4 essential tests, <20 lines output, <5s runtime (LLM-optimized)
- P2_INTERMEDIATE: 5-10 tests, <50 lines, <30s (standard validation)
- P3_COMPREHENSIVE: 15-25 tests, <100 lines, <2min (full coverage)
- P4_EXHAUSTIVE: Unlimited tests, full verbosity (debug mode)

Usage:
    # Test infrastructure
    from forge_cocotb.conftest import setup_clock, reset_active_high
    from forge_cocotb.test_base import TestBase, VerbosityLevel
    from forge_cocotb.ghdl_filter import GHDLOutputFilter, FilterLevel

    # Test runner
    from forge_cocotb.runner import main as runner_main, TestRunner

    # MCC utilities
    from forge_cocotb.mcc_utils import copy_sources_for_mcc

Author: Moku Instrument Forge Team
Date: 2025-11-06
Version: 1.0.0
"""

__version__ = "1.0.0"
__all__ = [
    "conftest",
    "test_base",
    "ghdl_filter",
    "runner",
    "mcc_utils",
]
