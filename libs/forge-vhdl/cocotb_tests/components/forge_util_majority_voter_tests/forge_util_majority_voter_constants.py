"""
Constants and helper functions for forge_util_majority_voter tests

Module: forge_util_majority_voter
Category: utilities
"""
from pathlib import Path

# Module identification
MODULE_NAME = "forge_util_majority_voter"

# HDL sources (relative paths for artifacts, will be updated during integration)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
HDL_SOURCES = [
    PROJECT_ROOT / "vhdl" / "components" / "utilities" / "forge_util_majority_voter.vhd"
]
HDL_TOPLEVEL = "forge_util_majority_voter"  # lowercase!

# Test values
class TestValues:
    """Progressive test value sizing"""

    # P1: All 8 input combinations (exhaustive for 3-bit input)
    # Format: (A, B, C, Expected Output)
    P1_COMBINATIONS = [
        (0, 0, 0, 0),  # No inputs high
        (0, 0, 1, 0),  # One input high
        (0, 1, 0, 0),  # One input high
        (0, 1, 1, 1),  # Two inputs high ← MAJORITY
        (1, 0, 0, 0),  # One input high
        (1, 0, 1, 1),  # Two inputs high ← MAJORITY
        (1, 1, 0, 1),  # Two inputs high ← MAJORITY
        (1, 1, 1, 1),  # Three inputs high ← MAJORITY
    ]

    # P2: Additional test patterns for rapid toggling
    P2_RAPID_TOGGLE_CYCLES = 50
    P2_GLITCH_PATTERNS = [
        (0, 0, 0),  # All low
        (1, 1, 1),  # All high
        (0, 1, 0),  # Toggle pattern
    ]


# Expected value calculation
def calculate_majority(a: int, b: int, c: int) -> int:
    """
    Calculate majority vote result

    Logic: (A AND B) OR (A AND C) OR (B AND C)

    Returns 1 if 2 or more inputs are 1, otherwise 0.

    Args:
        a: Input A (0 or 1)
        b: Input B (0 or 1)
        c: Input C (0 or 1)

    Returns:
        1 if majority (2+ inputs high), 0 otherwise
    """
    return 1 if (a + b + c) >= 2 else 0


# Helper functions
def set_inputs(dut, a: int, b: int, c: int):
    """
    Set all three input signals

    Args:
        dut: Device under test
        a: Input A value (0 or 1)
        b: Input B value (0 or 1)
        c: Input C value (0 or 1)
    """
    dut.input_a.value = a
    dut.input_b.value = b
    dut.input_c.value = c


def get_output(dut) -> int:
    """
    Read majority_out signal

    Args:
        dut: Device under test

    Returns:
        Current value of majority_out (0 or 1)
    """
    return int(dut.majority_out.value)


# Error messages
class ErrorMessages:
    """Consistent error message templates"""

    WRONG_OUTPUT = "Inputs (A,B,C)=({},{},{}): Expected {}, got {}"
    RESET_FAILED = "Reset failed: Expected 0, got {}"
    ENABLE_HOLD_FAILED = "Enable hold failed: Output changed from {} to {}"
    LATENCY_ERROR = "Registered mode latency error: Expected {} after {} cycles, got {}"
    SETUP_FAILED = "Test setup failed: {}"
