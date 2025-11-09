# edge_detector_pw_constants.py
from pathlib import Path

# Module identification
MODULE_NAME = "forge_util_edge_detector_pw"

# HDL sources (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
HDL_SOURCES = [
    PROJECT_ROOT / "workflow" / "artifacts" / "vhdl" / "forge_util_edge_detector_pw.vhd",
]
HDL_TOPLEVEL = "forge_util_edge_detector_pw"  # lowercase!

# Test values (progressive sizing)
class TestValues:
    # P1: Small, fast values
    P1_PULSE_WIDTH = 3        # Easy to verify (3 cycles)
    P1_EDGE_TYPE = "both"     # Default mode
    P1_TEST_CYCLES = 10       # Short test duration

    # P2: Realistic values
    P2_PULSE_WIDTHS = [1, 3, 5, 10]  # Range testing
    P2_EDGE_TYPES = ["rising", "falling", "both"]  # All modes
    P2_TEST_CYCLES = 50       # Longer tests

# Helper functions (signal access patterns)
def get_edge_detected(dut) -> int:
    """Extract edge_detected output (std_logic → int)"""
    return int(dut.edge_detected.value)

def get_rising_edge_out(dut) -> int:
    """Extract rising_edge_out output (std_logic → int)"""
    return int(dut.rising_edge_out.value)

def get_falling_edge_out(dut) -> int:
    """Extract falling_edge_out output (std_logic → int)"""
    return int(dut.falling_edge_out.value)

# Error messages (consistent formatting)
class ErrorMessages:
    WRONG_EDGE_DETECTED = "Expected edge_detected={}, got {}"
    WRONG_RISING_EDGE = "Expected rising_edge_out={}, got {}"
    WRONG_FALLING_EDGE = "Expected falling_edge_out={}, got {}"
    UNEXPECTED_OUTPUT = "Expected all outputs=0 during cycle {}, but got edge_detected={}, rising={}, falling={}"
    PULSE_WIDTH_MISMATCH = "Expected pulse width {} cycles, but pulse was {} cycles"
