"""
Platform Testing - BPD Deployment Integration Tests

Validates integration with real deployment YAML configurations.

Test Level: P1 (BASIC)
- Load bpd-deployment-setup1-dummy-dut.yaml
- Parse and validate MokuConfig
- Verify routing matrix
- Test basic simulator setup

NO VHDL DUT REQUIRED - These are platform infrastructure tests.
"""

import cocotb
from cocotb.triggers import Timer
from pathlib import Path
import yaml
from typing import Any, Dict

# Platform testing infrastructure
from cocotb_test.platform.simulation_backend import SimulationBackend
from cocotb_test.platform.network_cr import NetworkCRInterface

# Moku models (cross-workspace dependency)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "moku-models"))

from moku_models import MokuConfig, SlotConfig, MokuConnection
from moku_models.platforms.moku_go import MOKU_GO_PLATFORM


def load_deployment_yaml(yaml_path: Path) -> Dict[str, Any]:
    """
    Load BPD deployment YAML file.

    Args:
        yaml_path: Path to deployment YAML

    Returns:
        Parsed YAML data
    """
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def parse_deployment_to_moku_config(deployment: Dict[str, Any]) -> MokuConfig:
    """
    Convert BPD deployment YAML to MokuConfig.

    Args:
        deployment: Parsed deployment YAML dict

    Returns:
        MokuConfig instance
    """
    # Parse slots
    slots_dict = {}
    for slot_num_str, slot_data in deployment.get('slots', {}).items():
        slot_num = int(slot_num_str)

        slot_config = SlotConfig(
            instrument=slot_data['instrument'],
            settings=slot_data.get('settings', {}),
            control_registers=slot_data.get('control_registers'),
            bitstream=slot_data.get('bitstream')
        )
        slots_dict[slot_num] = slot_config

    # Parse routing
    routing_list = []
    for conn in deployment.get('routing', []):
        routing_list.append(
            MokuConnection(
                source=conn['source'],
                destination=conn['destination'],
                description=conn.get('description', '')
            )
        )

    # Create MokuConfig
    return MokuConfig(
        platform=MOKU_GO_PLATFORM,  # Hard-coded for now
        slots=slots_dict,
        routing=routing_list,
        metadata=deployment.get('metadata', {})
    )


class PlatformDeploymentTests:
    """
    Test suite for BPD deployment YAML integration.

    P1 (BASIC) tests only - validation and basic setup.
    """

    def __init__(self, dut):
        """Initialize test suite (no DUT needed for these tests)."""
        self.dut = dut
        self.deployment_root = Path(__file__).parent.parent.parent.parent
        self.passed = 0
        self.failed = 0

    def log(self, message: str) -> None:
        """Log message to CocoTB."""
        cocotb.log.info(f"[BPD-DEPLOYMENT] {message}")

    async def test(self, name: str, test_func) -> None:
        """Run a single test."""
        try:
            self.log(f"TEST: {name}")
            await test_func()
            self.passed += 1
            self.log(f"✓ PASS: {name}")
        except AssertionError as e:
            self.failed += 1
            self.log(f"✗ FAIL: {name} - {str(e)}")
            raise

    async def test_load_setup1_yaml(self) -> None:
        """Test: Load bpd-deployment-setup1-dummy-dut.yaml"""
        yaml_path = self.deployment_root / "bpd-deployment-setup1-dummy-dut.yaml"

        # Load YAML
        deployment = load_deployment_yaml(yaml_path)

        # Basic structure validation
        assert 'platform' in deployment, "Missing 'platform' field"
        assert 'slots' in deployment, "Missing 'slots' field"
        assert 'routing' in deployment, "Missing 'routing' field"

        assert deployment['platform'] == 'moku_go', f"Expected 'moku_go', got '{deployment['platform']}'"
        assert len(deployment['slots']) == 2, f"Expected 2 slots, got {len(deployment['slots'])}"

        self.log(f"Loaded setup1: {len(deployment['slots'])} slots, {len(deployment['routing'])} routing connections")

    async def test_load_setup2_yaml(self) -> None:
        """Test: Load bpd-deployment-setup2-real-dut.yaml"""
        yaml_path = self.deployment_root / "bpd-deployment-setup2-real-dut.yaml"

        # Load YAML
        deployment = load_deployment_yaml(yaml_path)

        # Basic structure validation
        assert 'platform' in deployment
        assert 'slots' in deployment
        assert 'routing' in deployment

        assert deployment['platform'] == 'moku_go'
        assert len(deployment['slots']) == 2

        self.log(f"Loaded setup2: {len(deployment['slots'])} slots, {len(deployment['routing'])} routing connections")

    async def test_parse_setup1_to_moku_config(self) -> None:
        """Test: Parse setup1 YAML to MokuConfig"""
        yaml_path = self.deployment_root / "bpd-deployment-setup1-dummy-dut.yaml"
        deployment = load_deployment_yaml(yaml_path)

        # Parse to MokuConfig
        config = parse_deployment_to_moku_config(deployment)

        # Validate MokuConfig
        assert config.platform.name == "Moku:Go"
        assert len(config.slots) == 2
        assert 1 in config.slots
        assert 2 in config.slots

        # Validate Slot 1 (Oscilloscope)
        slot1 = config.slots[1]
        assert slot1.instrument == "Oscilloscope"
        assert 'sample_rate' in slot1.settings
        # Note: YAML parser may return string or float for scientific notation
        sample_rate = slot1.settings['sample_rate']
        if isinstance(sample_rate, str):
            sample_rate = float(sample_rate)
        assert sample_rate == 125e6, f"Expected 125e6, got {sample_rate}"

        # Validate Slot 2 (CloudCompile/BPD)
        slot2 = config.slots[2]
        assert slot2.instrument == "CloudCompile"
        assert slot2.bitstream is not None
        assert slot2.control_registers is not None
        assert 0 in slot2.control_registers  # CR0 should exist

        self.log(f"Parsed setup1: Slot1={slot1.instrument}, Slot2={slot2.instrument}")

    async def test_validate_setup1_routing(self) -> None:
        """Test: Validate setup1 routing matrix"""
        yaml_path = self.deployment_root / "bpd-deployment-setup1-dummy-dut.yaml"
        deployment = load_deployment_yaml(yaml_path)
        config = parse_deployment_to_moku_config(deployment)

        # Validate routing
        errors = config.validate_routing()

        # No validation errors expected
        if errors:
            self.log(f"Routing validation errors: {errors}")
            assert False, f"Routing validation failed: {errors}"

        # Check for BPD-Debug-Bus routing (Slot2OutD → Slot1InA)
        debug_bus_found = False
        for conn in config.routing:
            if conn.source == "Slot2OutD" and conn.destination == "Slot1InA":
                debug_bus_found = True
                self.log(f"Found BPD-Debug-Bus: {conn.source} → {conn.destination}")
                break

        assert debug_bus_found, "BPD-Debug-Bus routing (Slot2OutD → Slot1InA) not found"

    async def test_compare_setup1_vs_setup2_routing(self) -> None:
        """Test: Compare routing differences between setup1 (dummy-DUT) and setup2 (real-DUT)"""
        # Load both configs
        setup1_path = self.deployment_root / "bpd-deployment-setup1-dummy-dut.yaml"
        setup2_path = self.deployment_root / "bpd-deployment-setup2-real-dut.yaml"

        setup1 = load_deployment_yaml(setup1_path)
        setup2 = load_deployment_yaml(setup2_path)

        config1 = parse_deployment_to_moku_config(setup1)
        config2 = parse_deployment_to_moku_config(setup2)

        # Both should have BPD-Debug-Bus (Slot2OutD → Slot1InA)
        debug_bus_1 = any(c.source == "Slot2OutD" and c.destination == "Slot1InA" for c in config1.routing)
        debug_bus_2 = any(c.source == "Slot2OutD" and c.destination == "Slot1InA" for c in config2.routing)

        assert debug_bus_1, "Setup1 missing BPD-Debug-Bus"
        assert debug_bus_2, "Setup2 missing BPD-Debug-Bus"

        # Setup1 should have synthetic trigger (Slot1OutA → Slot2InA)
        synthetic_trigger = any(c.source == "Slot1OutA" and c.destination == "Slot2InA" for c in config1.routing)
        assert synthetic_trigger, "Setup1 missing synthetic trigger routing"

        # Setup2 should have real DUT trigger (IN1 → Slot2InA)
        real_trigger = any(c.source == "IN1" and c.destination == "Slot2InA" for c in config2.routing)
        assert real_trigger, "Setup2 missing real DUT trigger routing"

        self.log(f"✓ Setup1 (dummy-DUT): synthetic trigger from Slot1OutA")
        self.log(f"✓ Setup2 (real-DUT): external trigger from IN1")

    async def run_all_tests(self) -> None:
        """Run all P1 tests."""
        self.log("=" * 60)
        self.log("BPD DEPLOYMENT INTEGRATION TESTS - P1 (BASIC)")
        self.log("=" * 60)

        await self.test("Load setup1 YAML", self.test_load_setup1_yaml)
        await self.test("Load setup2 YAML", self.test_load_setup2_yaml)
        await self.test("Parse setup1 to MokuConfig", self.test_parse_setup1_to_moku_config)
        await self.test("Validate setup1 routing", self.test_validate_setup1_routing)
        await self.test("Compare setup1 vs setup2", self.test_compare_setup1_vs_setup2_routing)

        self.log("=" * 60)
        self.log(f"SUMMARY: {self.passed} passed, {self.failed} failed")
        self.log("=" * 60)

        if self.failed > 0:
            raise AssertionError(f"{self.failed} test(s) failed")


@cocotb.test()
async def test_bpd_deployment_p1(dut):
    """
    P1 (BASIC) integration tests for BPD deployment YAMLs.

    No VHDL DUT required - these tests validate YAML parsing and
    MokuConfig integration only.
    """
    tester = PlatformDeploymentTests(dut)
    await tester.run_all_tests()
