"""
Test Constants for Platform Routing Integration Tests

Shared constants for progressive testing of 2-slot signal routing with
oscilloscope capture of externally routed signals.
"""

from pathlib import Path

MODULE_NAME = "platform_routing_integration"
HDL_SOURCES = [Path("test_duts/forge_counter_with_encoder.vhd")]
HDL_TOPLEVEL = "forge_counter_with_encoder"

# Additional dependencies (packages and encoder)
HDL_DEPENDENCIES = [
    Path("../vhdl/packages/forge_common_pkg.vhd"),
    Path("../vhdl/debugging/forge_hierarchical_encoder.vhd")
]


class TestValues:
    """Test parameters for different test levels"""

    # P1 - BASIC (LLM-optimized)
    P1_COUNTER_MAX = 15              # Small max for fast testing
    P1_CAPTURE_DURATION_NS = 1000    # 1us capture (~125 samples @ 125MHz)
    MIN_SAMPLES = 50                 # Minimum samples for valid capture
    MIN_UNIQUE_STATES = 5            # Minimum unique states for validation

    # Oscilloscope settings
    SAMPLE_RATE = 125e6              # 125 MHz (Moku:Go default)
    DECIMATION = 1                   # No decimation for P1

    # P2 - INTERMEDIATE (Future)
    P2_COUNTER_MAX = 31
    P2_CAPTURE_DURATION_NS = 2000    # 2us capture

    # P3 - COMPREHENSIVE (Future)
    P3_COUNTER_MAX = 63
    P3_CAPTURE_DURATION_NS = 5000    # 5us capture


class EncodingConstants:
    """Hierarchical voltage encoding parameters (must match VHDL)"""

    DIGITAL_UNITS_PER_STATE = 200    # State × 200 digital units
    DIGITAL_UNITS_PER_STATUS = 0.78125  # 100/128 digital units per status LSB

    # State encoding range (6-bit state)
    MIN_STATE = 0
    MAX_STATE = 63

    # Status encoding (8-bit status)
    FAULT_BIT = 7  # status[7] = overflow_flag


class ForgeControlBits:
    """FORGE control scheme CR0[31:29] bit patterns"""

    POWER_ON = 0x00000000          # All disabled
    FORGE_READY = 0x80000000       # CR0[31] = 1
    USER_ENABLED = 0xC0000000      # CR0[31:30] = 11
    FULLY_ENABLED = 0xE0000000     # CR0[31:29] = 111


class ErrorMessages:
    """Error messages for test assertions"""

    NO_SAMPLES_CAPTURED = "Oscilloscope captured 0 samples"
    INSUFFICIENT_SAMPLES = "Oscilloscope captured only {1} samples (expected >= {0})"
    INSUFFICIENT_STATE_PROGRESSION = "Only {1} unique states captured (expected >= {0})"
    ROUTING_NOT_APPLIED = "Routing matrix does not contain expected connection: {0}"
    EXTERNAL_CHANNEL_MISSING = "External channel '{0}' not found in oscilloscope"
    SIGNAL_HANDLE_NOT_WIRED = "External channel '{0}' not wired to DUT signal '{1}'"
    INVALID_STATE_RANGE = "State {0} out of range (0-{1})"
