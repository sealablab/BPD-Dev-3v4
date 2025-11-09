"""
Constants for forge_counter platform test PoC

This test validates the platform testing framework with a real FORGE-compliant DUT.
"""
from pathlib import Path

# Module identification
MODULE_NAME = "forge_counter"

# HDL sources (relative to cocotb_test/ directory)
PROJECT_ROOT = Path(__file__).parent
HDL_SOURCES = [
    PROJECT_ROOT / "test_duts" / "forge_counter.vhd",
]
HDL_TOPLEVEL = "forge_counter"  # lowercase!

# Test values (progressive sizing)
class TestValues:
    """Test values sized for progressive test levels"""

    # P1: Small, fast values
    P1_COUNTER_MAX = 10      # Fast overflow
    P1_WAIT_CYCLES = 5       # Partial count
    P1_OVERFLOW_CYCLES = 12  # 2 extra for GHDL

    # P2: Realistic values
    P2_COUNTER_MAX = 100
    P2_OVERFLOW_CYCLES = 102

    # P3: Boundary values
    P3_COUNTER_MAX = 0xFFFF  # 16-bit max
    P3_OVERFLOW_CYCLES = 0xFFFF + 2

# FORGE Control Register bit patterns
class ForgeControlBits:
    """CR0[31:29] control scheme patterns"""
    FORGE_READY_BIT = 31
    USER_ENABLE_BIT = 30
    CLK_ENABLE_BIT = 29

    # Bit patterns for sequential enable
    POWER_ON        = 0x00000000  # All disabled
    FORGE_READY     = 0x80000000  # CR0[31] = 1
    USER_ENABLED    = 0xC0000000  # CR0[31:30] = 11
    FULLY_ENABLED   = 0xE0000000  # CR0[31:29] = 111

# Expected value calculation
def calculate_expected_count(cycles_waited: int) -> int:
    """
    Calculate expected counter value after N cycles.

    Args:
        cycles_waited: Number of clock cycles after enable

    Returns:
        Expected counter value (VHDL increments on rising edge)

    Note:
        Counter starts at 0, increments on each clock.
        After 1 cycle: counter = 1
        After 2 cycles: counter = 2
        etc.
    """
    # Counter increments every cycle when enabled
    return cycles_waited

# Helper functions (signal access)
def get_counter_value(dut) -> int:
    """Extract counter value from SR0[31:0]"""
    return int(dut.Status0.value)

def get_overflow_flag(dut) -> bool:
    """Extract overflow flag from SR1[0]"""
    sr1 = int(dut.Status1.value)
    return (sr1 & 0x1) == 1

def set_counter_max(dut, max_value: int):
    """
    Set counter_max via CR0[15:0]

    Args:
        dut: DUT instance
        max_value: Maximum count value (16-bit)

    Note:
        Preserves CR0[31:16] (FORGE control bits and reserved)
    """
    current_cr0 = int(dut.Control0.value)
    # Preserve CR0[31:16], replace CR0[15:0]
    new_cr0 = (current_cr0 & 0xFFFF0000) | (max_value & 0xFFFF)
    dut.Control0.value = new_cr0

# Error messages
class ErrorMessages:
    WRONG_COUNT = "Expected counter value {}, got {}"
    OVERFLOW_NOT_SET = "Expected overflow flag=True, got False"
    OVERFLOW_UNEXPECTED = "Expected overflow flag=False, got True"
    COUNTING_WHILE_DISABLED = "Counter incremented while global_enable=0"
    NOT_COUNTING_WHILE_ENABLED = "Counter did not increment while global_enable=1"
