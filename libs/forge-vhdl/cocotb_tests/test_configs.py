"""
Test configurations for forge-vhdl CocoTB tests.
Auto-discovered by run.py - no Makefile needed!

Module categories:
- utilities: Reusable VHDL utility components
- packages: VHDL packages with functions/constants
- debugging: Debug infrastructure components
- loaders: Memory initialization components

Author: Moku Instrument Forge Team (adapted from EZ-EMFI)
Date: 2025-11-04
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
VHDL = PROJECT_ROOT / "vhdl"
VHDL_PKG = VHDL / "packages"
VHDL_UTIL = VHDL / "components" / "utilities"
VHDL_DEBUG = VHDL / "components" / "debugging"
VHDL_LOADER = VHDL / "components" / "loader"
TESTS = PROJECT_ROOT / "cocotb_tests"  # Test directory (contains cocotb_test_wrappers/ and platform test files)


@dataclass
class TestConfig:
    """Configuration for a single CocoTB test"""
    name: str
    sources: List[Path]
    toplevel: str
    test_module: str
    category: str = "misc"
    ghdl_args: List[str] = field(default_factory=lambda: ["--std=08"])


# ==================================================================================
# Test Configurations
# ==================================================================================

TESTS_CONFIG = {
    # === Utilities (forge_util_*) ===

    "forge_util_clk_divider": TestConfig(
        name="forge_util_clk_divider",
        sources=[
            VHDL_UTIL / "forge_util_clk_divider.vhd",
        ],
        toplevel="forge_util_clk_divider",
        test_module="components.test_forge_util_clk_divider_progressive",
        category="utilities",
    ),

    "forge_util_majority_voter": TestConfig(
        name="forge_util_majority_voter",
        sources=[
            VHDL_UTIL / "forge_util_majority_voter.vhd",
        ],
        toplevel="forge_util_majority_voter",
        test_module="components.test_forge_util_majority_voter_progressive",
        category="utilities",
    ),

    "forge_util_edge_detector_pw": TestConfig(
        name="forge_util_edge_detector_pw",
        sources=[
            PROJECT_ROOT / "workflow" / "artifacts" / "vhdl" / "forge_util_edge_detector_pw.vhd",
        ],
        toplevel="forge_util_edge_detector_pw",
        test_module="components.test_forge_util_edge_detector_pw_progressive",
        category="utilities",
    ),

    # === Packages ===

    "forge_lut_pkg": TestConfig(
        name="forge_lut_pkg",
        sources=[
            VHDL_PKG / "forge_lut_pkg.vhd",              # LUT package
            TESTS / "cocotb_test_wrappers" / "forge_lut_pkg_tb_wrapper.vhd",      # Testbench wrapper
        ],
        toplevel="forge_lut_pkg_tb_wrapper",
        test_module="components.test_forge_lut_pkg_progressive",
        category="packages",
    ),

    "forge_voltage_3v3_pkg": TestConfig(
        name="forge_voltage_3v3_pkg",
        sources=[
            VHDL_PKG / "forge_voltage_3v3_pkg.vhd",
            TESTS / "cocotb_test_wrappers" / "forge_voltage_3v3_pkg_tb_wrapper.vhd",
        ],
        toplevel="forge_voltage_3v3_pkg_tb_wrapper",
        test_module="components.test_forge_voltage_3v3_pkg_progressive",
        category="packages",
    ),

    "forge_voltage_5v0_pkg": TestConfig(
        name="forge_voltage_5v0_pkg",
        sources=[
            VHDL_PKG / "forge_voltage_5v0_pkg.vhd",
            TESTS / "cocotb_test_wrappers" / "forge_voltage_5v0_pkg_tb_wrapper.vhd",
        ],
        toplevel="forge_voltage_5v0_pkg_tb_wrapper",
        test_module="components.test_forge_voltage_5v0_pkg_progressive",
        category="packages",
    ),

    "forge_voltage_5v_bipolar_pkg": TestConfig(
        name="forge_voltage_5v_bipolar_pkg",
        sources=[
            VHDL_PKG / "forge_voltage_5v_bipolar_pkg.vhd",
            TESTS / "cocotb_test_wrappers" / "forge_voltage_5v_bipolar_pkg_tb_wrapper.vhd",
        ],
        toplevel="forge_voltage_5v_bipolar_pkg_tb_wrapper",
        test_module="components.test_forge_voltage_5v_bipolar_pkg_progressive",
        category="packages",
    ),

    # === Debugging (forge_debug_*) ===

    "forge_hierarchical_encoder": TestConfig(
        name="forge_hierarchical_encoder",
        sources=[
            VHDL_DEBUG / "forge_hierarchical_encoder.vhd",
        ],
        toplevel="forge_hierarchical_encoder",
        test_module="components.forge_hierarchical_encoder_tests.P1_forge_hierarchical_encoder_basic",
        category="debugging",
    ),

    # === Platform Tests (test_duts/) ===

    "platform_counter_poc": TestConfig(
        name="platform_counter_poc",
        sources=[
            VHDL_PKG / "forge_common_pkg.vhd",               # FORGE control scheme
            TESTS / "test_duts" / "forge_counter.vhd",       # Counter DUT
        ],
        toplevel="forge_counter",
        test_module="integration.test_platform_counter_poc",
        category="platform",
    ),

    "platform_bpd_deployment": TestConfig(
        name="platform_bpd_deployment",
        sources=[
            TESTS / "test_duts" / "platform_test_dummy.vhd",  # Minimal dummy entity
        ],
        toplevel="platform_test_dummy",
        test_module="integration.test_platform_bpd_deployment",
        category="platform",
    ),

    "platform_oscilloscope_capture": TestConfig(
        name="platform_oscilloscope_capture",
        sources=[
            VHDL_PKG / "forge_common_pkg.vhd",                        # FORGE control scheme
            VHDL_DEBUG / "forge_hierarchical_encoder.vhd",            # Hierarchical encoder
            TESTS / "test_duts" / "forge_counter_with_encoder.vhd",  # Full 3-layer DUT
        ],
        toplevel="forge_counter_with_encoder",
        test_module="integration.test_platform_oscilloscope_capture",
        category="platform",
    ),

    "platform_routing_integration": TestConfig(
        name="platform_routing_integration",
        sources=[
            VHDL_PKG / "forge_common_pkg.vhd",                        # FORGE control scheme
            VHDL_DEBUG / "forge_hierarchical_encoder.vhd",            # Hierarchical encoder
            TESTS / "test_duts" / "forge_counter_with_encoder.vhd",  # Full 3-layer DUT
        ],
        toplevel="forge_counter_with_encoder",
        test_module="integration.test_platform_routing_integration",
        category="platform",
    ),

    # Note: Additional components that can have tests added:
    # - forge_voltage_threshold_trigger_core (utilities)
    # - fsm_observer (debugging)
    # - forge_bram_loader (loaders)
    # - forge_common_pkg (packages)
}


# ==================================================================================
# Helper Functions
# ==================================================================================

def get_test_names() -> List[str]:
    """Get sorted list of all test names"""
    return sorted(TESTS_CONFIG.keys())


def get_tests_by_category(category: str) -> dict:
    """Get tests filtered by category"""
    return {
        name: config
        for name, config in TESTS_CONFIG.items()
        if config.category == category
    }


def get_categories() -> List[str]:
    """Get sorted list of all unique categories"""
    return sorted(set(config.category for config in TESTS_CONFIG.values()))


def validate_test_files() -> dict:
    """
    Validate that all configured test files exist.
    Returns dict of {test_name: missing_files}
    """
    issues = {}

    for test_name, config in TESTS_CONFIG.items():
        missing = []

        # Check VHDL sources
        for source in config.sources:
            if not source.exists():
                missing.append(str(source))

        # Check Python test module (handle dotted paths like "components.test_name")
        test_module_path = config.test_module.replace(".", "/") + ".py"
        test_file = TESTS / test_module_path
        if not test_file.exists():
            missing.append(str(test_file))

        if missing:
            issues[test_name] = missing

    return issues


if __name__ == "__main__":
    # CLI for validating configuration
    print("forge-vhdl CocoTB Test Configuration")
    print("=" * 70)
    print(f"Total tests: {len(TESTS_CONFIG)}")
    print(f"\nCategories: {', '.join(get_categories())}")
    print(f"\nTests by category:")
    for category in get_categories():
        tests = get_tests_by_category(category)
        print(f"  {category}: {len(tests)} tests")
        for test_name in sorted(tests.keys()):
            print(f"    - {test_name}")

    # Validate files
    print("\nValidating test files...")
    issues = validate_test_files()
    if issues:
        print(f"\n⚠️  Found {len(issues)} tests with missing files:")
        for test_name, missing_files in issues.items():
            print(f"\n  {test_name}:")
            for file in missing_files:
                print(f"    - {file}")
    else:
        print("✅ All test files validated successfully!")
