"""
Forge Hierarchical Encoder Module Test Constants

Shared constants and configurations for all forge_hierarchical_encoder tests.
Single source of truth for test parameters.

Author: Moku Instrument Forge Team
Date: 2025-11-07
"""

from pathlib import Path


# Module identification
MODULE_NAME = "forge_hierarchical_encoder"

# HDL sources (relative to tests/ directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
VHDL_DIR = PROJECT_ROOT / "vhdl"

HDL_SOURCES = [
    VHDL_DIR / "debugging" / "forge_hierarchical_encoder.vhd",
]

# Top-level entity name (must be lowercase for GHDL!)
HDL_TOPLEVEL = "forge_hierarchical_encoder"

# Module parameters (digital scaling constants)
DIGITAL_UNITS_PER_STATE = 200       # Digital units per state step
DIGITAL_UNITS_PER_STATUS = 0.78125  # Digital units per status LSB (100/128)

# Default test parameters
DEFAULT_CLK_PERIOD_NS = 10

# Test timing parameters
RESET_CYCLES = 5
SETTLE_CYCLES = 2


class TestValues:
    """Test value sets for different test phases (DIGITAL DOMAIN!)"""

    # P1 - Basic test values (small states, fast tests)
    P1_STATES = [0, 1, 2, 3]  # 4 basic states (IDLE, ARMED, FIRING, COOLDOWN)
    P1_STATUS = [0x00, 0x40, 0x7F, 0x80, 0xC0]  # Normal, mid, max, fault, fault+mid

    # P2 - Intermediate test values
    P2_STATES = [0, 1, 2, 3, 4, 5, 31, 63]  # Normal + edge cases
    P2_STATUS = [0x00, 0x01, 0x3F, 0x7F, 0x80, 0x81, 0xBF, 0xFF]  # Full range

    # Expected digital outputs (NOT voltages!)
    # Formula: base = state * 200, offset = (status & 0x7F) * 100 / 128
    # Output = (base + offset) if status[7]==0 else -(base + offset)

    @staticmethod
    def calculate_expected_digital(state: int, status: int) -> int:
        """
        Calculate expected digital output value.

        Args:
            state: State value (0-63)
            status: Status byte (bit 7 = fault flag, bits 6:0 = status)

        Returns:
            Expected signed digital output value

        Examples:
            State=0, Status=0x00 → 0 digital units
            State=1, Status=0x00 → 200 digital units
            State=2, Status=0x40 → 450 digital units (400 base + 50 offset)
            State=2, Status=0xC0 → -450 digital units (fault flag set)
        """
        # Base value from state (200 digital units per state)
        base = state * DIGITAL_UNITS_PER_STATE

        # Status offset (lower 7 bits)
        status_lower = status & 0x7F
        # Offset = status_lower * 100 / 128 (integer division)
        offset = (status_lower * 100) // 128

        # Combined magnitude
        combined = base + offset

        # Apply fault flag (status bit 7)
        fault_flag = (status >> 7) & 1
        return -combined if fault_flag else combined


class ErrorMessages:
    """Standardized error messages for test assertions"""

    RESET_OUTPUT = "Output should be 0 after reset, got {}"
    STATE_PROGRESSION = "State={}, status=0x00: expected {}, got {}"
    STATUS_OFFSET_NO_OFFSET = "State={}, status=0x00: expected {}, got {}"
    STATUS_OFFSET_MAX_OFFSET = "State={}, status=0x7F: expected {}, got {}"
    STATUS_OFFSET_DIRECTION = "Status offset should increase output (no_offset={}, max_offset={})"
    FAULT_NORMAL_SIGN = "Normal output (status[7]=0) should be positive, got {}"
    FAULT_FLAG_SIGN = "Fault output (status[7]=1) should be negative, got {}"
    FAULT_MAGNITUDE = "Magnitude mismatch: normal={}, fault={}"


def get_test_description(phase: int, test_name: str) -> str:
    """
    Generate consistent test descriptions.

    Args:
        phase: Test phase (1, 2, 3, 4)
        test_name: Name of the test

    Returns:
        Formatted test description string
    """
    return f"P{phase} - {test_name}"
