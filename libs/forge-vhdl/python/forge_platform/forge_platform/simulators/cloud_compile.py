"""
CloudCompile Simulator

Passthrough simulator for CloudCompile custom instruments.
The DUT itself IS the CloudCompile instrument, so this simulator
mainly manages control register application.
"""

from typing import Dict, Any, Optional
import cocotb
from cocotb.triggers import Timer


class CloudCompileSimulator:
    """
    CloudCompile instrument simulator (passthrough).

    Since CloudCompile slots run custom VHDL (like BPD), the DUT
    itself provides the functionality. This simulator:
    - Applies control registers to DUT
    - Validates FORGE control scheme
    - Monitors status registers (future)
    """

    def __init__(self, dut: Any, settings: Dict[str, Any]):
        """
        Initialize CloudCompile simulator.

        Args:
            dut: CocotB DUT handle
            settings: Configuration from MokuConfig SlotConfig:
                - control_registers: Dict[int, int] of initial CR values
                - bitstream: Path to bitstream (informational only in sim)
        """
        self.dut = dut
        self.settings = settings
        self.control_registers = settings.get('control_registers', {})
        self.bitstream = settings.get('bitstream', None)

        # Track applied CR values
        self.applied_crs: Dict[int, int] = {}

        # FORGE control state
        self.forge_state = {
            'forge_ready': False,
            'user_enable': False,
            'clk_enable': False,
            'loader_done': True  # Assume loaded in simulation
        }

    async def apply_control_registers(self) -> None:
        """
        Apply control register values to DUT.

        Maps CR values from MokuConfig to DUT Control0-Control15 ports.
        This happens atomically without network delay (direct to DUT).
        """
        for reg_num in range(16):
            reg_name = f'Control{reg_num}'

            # Get value from settings or default to 0
            value = self.control_registers.get(reg_num, 0)

            # Apply to DUT if port exists
            if hasattr(self.dut, reg_name):
                getattr(self.dut, reg_name).value = value
                self.applied_crs[reg_num] = value

                # Track FORGE control bits from CR0
                if reg_num == 0:
                    self._update_forge_state(value)

            await Timer(1, units='ns')  # Allow propagation

    async def set_control_register(self, register: int, value: int) -> None:
        """
        Set a single control register (immediate, no network delay).

        This is used by the simulation backend after network delay
        has been applied.

        Args:
            register: Control register number (0-15)
            value: 32-bit value
        """
        if register < 0 or register > 15:
            raise ValueError(f"Register {register} out of range (0-15)")

        reg_name = f'Control{register}'
        if hasattr(self.dut, reg_name):
            getattr(self.dut, reg_name).value = value
            self.applied_crs[register] = value
            self.control_registers[register] = value

            # Update FORGE state if CR0
            if register == 0:
                self._update_forge_state(value)

            await Timer(1, units='ns')  # Propagation delay

    def get_control_register(self, register: int) -> int:
        """
        Get current control register value.

        Args:
            register: Control register number (0-15)

        Returns:
            Current value or 0 if not set
        """
        return self.control_registers.get(register, 0)

    def _update_forge_state(self, cr0_value: int) -> None:
        """
        Update FORGE control state from CR0 value.

        Args:
            cr0_value: 32-bit CR0 value
        """
        self.forge_state['forge_ready'] = bool((cr0_value >> 31) & 1)
        self.forge_state['user_enable'] = bool((cr0_value >> 30) & 1)
        self.forge_state['clk_enable'] = bool((cr0_value >> 29) & 1)

    def get_forge_state(self) -> Dict[str, bool]:
        """
        Get current FORGE control state.

        Returns:
            Dictionary with forge_ready, user_enable, clk_enable, loader_done
        """
        return self.forge_state.copy()

    def is_enabled(self) -> bool:
        """
        Check if instrument is fully enabled per FORGE scheme.

        Returns:
            True if all 4 FORGE conditions are met
        """
        return all([
            self.forge_state['forge_ready'],
            self.forge_state['user_enable'],
            self.forge_state['clk_enable'],
            self.forge_state['loader_done']
        ])

    async def run(self, duration_ns: int) -> None:
        """
        Run CloudCompile instrument for duration.

        For CloudCompile, the DUT does the actual work.
        This method just ensures control registers stay applied.

        Args:
            duration_ns: Simulation duration in nanoseconds
        """
        # CloudCompile is passthrough - DUT runs itself
        # Just wait for the duration
        await Timer(duration_ns, units='ns')

    def get_status_registers(self) -> Dict[int, int]:
        """
        Read status registers from DUT (SR0-SR15).

        Note: Status registers will be network-readable in future MCC.

        Returns:
            Dictionary of status register values
        """
        status = {}

        for reg_num in range(16):
            reg_name = f'Status{reg_num}'
            if hasattr(self.dut, reg_name):
                try:
                    value = int(getattr(self.dut, reg_name).value)
                    status[reg_num] = value
                except:
                    status[reg_num] = 0

        return status

    def get_data(self) -> Dict[str, Any]:
        """
        Get instrument data (mainly status for CloudCompile).

        Returns:
            Dictionary with control/status register state
        """
        return {
            'control_registers': self.control_registers.copy(),
            'applied_crs': self.applied_crs.copy(),
            'status_registers': self.get_status_registers(),
            'forge_state': self.get_forge_state(),
            'enabled': self.is_enabled(),
            'bitstream': self.bitstream
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        enabled = "ENABLED" if self.is_enabled() else "DISABLED"
        forge_bits = (
            f"F={'1' if self.forge_state['forge_ready'] else '0'}"
            f"U={'1' if self.forge_state['user_enable'] else '0'}"
            f"C={'1' if self.forge_state['clk_enable'] else '0'}"
        )
        return f"CloudCompileSimulator({enabled}, FORGE={forge_bits}, CRs={len(self.applied_crs)})"