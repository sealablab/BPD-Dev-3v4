"""
Test base module - re-exports from forge_cocotb package

This module provides backward compatibility for tests that import
from test_base instead of forge_cocotb.test_base.
"""

# Re-export all test base classes and enums
from forge_cocotb.test_base import (
    TestLevel,
    VerbosityLevel,
    TestBase,
)

__all__ = ['TestLevel', 'VerbosityLevel', 'TestBase']
