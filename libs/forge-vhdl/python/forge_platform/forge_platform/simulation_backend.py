"""
Simulation Backend for CocoTB Platform Testing

MokuConfig-driven backend that creates and coordinates instrument simulators.
"""

import asyncio
from typing import Dict, Any, Optional, List
import cocotb
from cocotb.triggers import Timer

from .backend import Backend
from .network_cr import NetworkCRInterface
from .simulators import SIMULATOR_REGISTRY


class SimulationBackend(Backend):
    """
    CocoTB simulation backend for platform testing.

    Creates behavioral instrument models from MokuConfig and coordinates
    their execution with network-realistic control register updates.
    """

    def __init__(self, config: Any, dut: Any):
        """
        Initialize simulation backend.

        Args:
            config: MokuConfig instance with platform/slot/routing specs
            dut: CocoTB DUT handle
        """
        self.config = config
        self.dut = dut
        self.simulators = {}
        self.network_cr = NetworkCRInterface()
        self.routing_matrix = {}
        self.setup_complete = False

    async def setup(self) -> None:
        """Initialize simulators and routing from MokuConfig."""
        # Validate routing configuration
        errors = self.config.validate_routing()
        if errors:
            for error in errors:
                cocotb.log.warning(f"Routing validation: {error}")

        # Create simulator for each configured slot
        for slot_num, slot_config in self.config.slots.items():
            await self._create_simulator(slot_num, slot_config)

        # Setup routing matrix
        self._setup_routing()

        # Apply initial control registers
        await self._apply_initial_control_registers()

        self.setup_complete = True
        cocotb.log.info(f"SimulationBackend setup complete: {len(self.simulators)} instruments")

    async def _create_simulator(self, slot_num: int, slot_config: Any) -> None:
        """Create simulator instance for a slot."""
        instrument_type = slot_config.instrument
        simulator_class = SIMULATOR_REGISTRY.get(instrument_type)

        if simulator_class:
            # Create simulator with settings
            simulator = simulator_class(self.dut, slot_config.settings)
            self.simulators[slot_num] = simulator

            # Add slot to network CR interface
            initial_crs = slot_config.control_registers or {}
            self.network_cr.add_slot(slot_num, initial_crs)

            cocotb.log.info(f"Slot {slot_num}: Created {instrument_type} simulator")
        else:
            cocotb.log.warning(f"Slot {slot_num}: No simulator for {instrument_type}")

    def _setup_routing(self) -> None:
        """
        Setup routing matrix from MokuConfig.

        Configures signal routing between slots and physical outputs.
        For oscilloscope instruments, updates channel mappings to capture
        routed signals.
        """
        for connection in self.config.routing:
            src = connection.source
            dst = connection.destination
            self.routing_matrix[f"{src}->{dst}"] = connection
            cocotb.log.info(f"Routing: {src} -> {dst}")

            # Apply routing to destination instrument
            self._apply_routing_connection(src, dst)

    def _apply_routing_connection(self, src: str, dst: str) -> None:
        """
        Apply routing connection between source and destination.

        Handles different routing patterns:
        - SlotNOutX → SlotMInY: Inter-slot signal routing
        - SlotNOutX → OUTY: Slot output to physical port
        - INX → SlotNInY: Physical input to slot input

        Args:
            src: Source identifier (e.g., 'Slot2OutD', 'IN1')
            dst: Destination identifier (e.g., 'Slot1InA', 'OUT1')
        """
        # Parse source and destination
        src_slot, src_port = self._parse_signal_name(src)
        dst_slot, dst_port = self._parse_signal_name(dst)

        # Inter-slot routing (e.g., Slot2OutD → Slot1InA)
        if src_slot is not None and dst_slot is not None:
            src_simulator = self.simulators.get(src_slot)
            dst_simulator = self.simulators.get(dst_slot)

            if src_simulator and dst_simulator:
                # Get source signal from DUT
                if hasattr(self.dut, src_port):
                    source_signal = getattr(self.dut, src_port)

                    # Configure destination simulator to use this signal
                    if hasattr(dst_simulator, 'add_external_channel'):
                        dst_simulator.add_external_channel(dst_port, source_signal)
                        cocotb.log.info(
                            f"  Wired: Slot{src_slot}.{src_port} → "
                            f"Slot{dst_slot}.{dst_port}"
                        )
                    else:
                        cocotb.log.warning(
                            f"  Destination Slot{dst_slot} does not support "
                            f"external channels"
                        )
                else:
                    cocotb.log.warning(f"  Source signal {src_port} not found in DUT")

    def _parse_signal_name(self, signal: str) -> tuple:
        """
        Parse signal name to extract slot number and port name.

        Args:
            signal: Signal identifier (e.g., 'Slot2OutD', 'IN1', 'OUT2')

        Returns:
            Tuple of (slot_number or None, port_name)
        """
        if signal.startswith('Slot'):
            # Extract slot number (e.g., 'Slot2OutD' → (2, 'OutputD'))
            import re
            match = re.match(r'Slot(\d+)(Out|In)([A-D])', signal)
            if match:
                slot = int(match.group(1))
                direction = match.group(2)
                channel = match.group(3)
                port_name = f"Output{channel}" if direction == "Out" else f"Input{channel}"
                return (slot, port_name)
        # Physical port (IN1, OUT1, etc.)
        return (None, signal)

    async def _apply_initial_control_registers(self) -> None:
        """Apply initial control registers to CloudCompile instruments."""
        for slot_num, simulator in self.simulators.items():
            if hasattr(simulator, 'apply_control_registers'):
                await simulator.apply_control_registers()
                cocotb.log.info(f"Slot {slot_num}: Applied initial control registers")

    async def run(self, duration_ms: float) -> Dict[str, Any]:
        """
        Run all simulators for specified duration.

        Args:
            duration_ms: Duration in milliseconds

        Returns:
            Dictionary with data from all instruments
        """
        if not self.setup_complete:
            await self.setup()

        duration_ns = int(duration_ms * 1e6)
        cocotb.log.info(f"Running simulation for {duration_ms}ms ({duration_ns}ns)")

        # Start all simulators concurrently
        tasks = []
        for slot_num, simulator in self.simulators.items():
            if hasattr(simulator, 'run'):
                task = cocotb.start_soon(simulator.run(duration_ns))
                tasks.append((slot_num, task))

        # Wait for duration
        await Timer(duration_ns, units='ns')

        # Collect data from all simulators
        data = {}
        for slot_num, simulator in self.simulators.items():
            if hasattr(simulator, 'get_data'):
                data[slot_num] = simulator.get_data()

        cocotb.log.info(f"Simulation complete, collected data from {len(data)} instruments")
        return data

    async def teardown(self) -> None:
        """Clean up resources."""
        # Stop any active captures
        for simulator in self.simulators.values():
            if hasattr(simulator, 'stop_capture'):
                simulator.stop_capture()

        cocotb.log.info("SimulationBackend teardown complete")

    def get_instrument(self, slot_or_name: int | str) -> Any:
        """
        Get instrument simulator by slot or type.

        Args:
            slot_or_name: Slot number or instrument type name

        Returns:
            Simulator instance or None
        """
        if isinstance(slot_or_name, int):
            return self.simulators.get(slot_or_name)
        else:
            # Find by instrument type
            for slot_num, slot_config in self.config.slots.items():
                if slot_config.instrument == slot_or_name:
                    return self.simulators.get(slot_num)
        return None

    async def set_control_register(
        self,
        slot: int,
        register: int,
        value: int,
        delay_ms: float = 200.0
    ) -> None:
        """
        Set control register with network delay.

        Args:
            slot: Slot number
            register: Control register number (0-15)
            value: 32-bit value
            delay_ms: Network delay in milliseconds
        """
        cocotb.log.info(
            f"Network CR update: Slot{slot}.CR{register} = 0x{value:08X} "
            f"(delay={delay_ms}ms)"
        )

        # Apply network delay
        await self.network_cr.set_control_register(slot, register, value, delay_ms)

        # Apply to simulator (CloudCompile only)
        simulator = self.simulators.get(slot)
        if simulator and hasattr(simulator, 'set_control_register'):
            await simulator.set_control_register(register, value)

    async def get_control_register(self, slot: int, register: int) -> int:
        """Get control register value."""
        return await self.network_cr.get_control_register(slot, register)

    async def get_status_register(self, slot: int, register: int) -> int:
        """
        Get status register value.

        For CloudCompile instruments, reads from DUT.
        """
        simulator = self.simulators.get(slot)
        if simulator and hasattr(simulator, 'get_status_registers'):
            status_regs = simulator.get_status_registers()
            return status_regs.get(register, 0)
        return 0

    def validate_forge_control(self, slot: int) -> Dict[str, bool]:
        """Validate FORGE control scheme for a slot."""
        return self.network_cr.get_forge_status(slot)

    async def set_forge_control(
        self,
        slot: int,
        forge_ready: bool = False,
        user_enable: bool = False,
        clk_enable: bool = False,
        delay_ms: float = 200.0
    ) -> None:
        """
        Convenience method to set FORGE control bits.

        Args:
            slot: Slot number
            forge_ready: Set CR0[31]
            user_enable: Set CR0[30]
            clk_enable: Set CR0[29]
            delay_ms: Network delay
        """
        await self.network_cr.set_forge_control(
            slot, forge_ready, user_enable, clk_enable, delay_ms
        )

        # Apply to CloudCompile simulator
        cr0 = await self.network_cr.get_control_register(slot, 0)
        simulator = self.simulators.get(slot)
        if simulator and hasattr(simulator, 'set_control_register'):
            await simulator.set_control_register(0, cr0)

    def get_routing_info(self) -> List[str]:
        """Get human-readable routing information."""
        return [f"{src}->{dst}" for src, dst in self.routing_matrix.keys()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics."""
        stats = {
            'platform': self.config.platform.name,
            'slots': len(self.simulators),
            'routing_connections': len(self.routing_matrix),
            'network_stats': self.network_cr.get_stats()
        }

        # Add per-instrument stats
        for slot_num, simulator in self.simulators.items():
            if hasattr(simulator, 'get_statistics'):
                stats[f'slot{slot_num}'] = simulator.get_statistics()

        return stats