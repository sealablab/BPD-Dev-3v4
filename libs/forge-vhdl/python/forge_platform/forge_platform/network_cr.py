"""
Network Control Register Primitives

Simulates MCC network API behavior with realistic delays.
Key innovation: Explicit network boundary with ~200ms latency.
"""

import asyncio
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import cocotb
from cocotb.triggers import Timer


@dataclass
class ControlRegisterBank:
    """
    Simulates a bank of 16 control registers for a slot.

    Maintains register values and tracks network access patterns.
    """
    slot: int
    registers: Dict[int, int] = field(default_factory=lambda: {i: 0 for i in range(16)})
    access_log: list = field(default_factory=list)

    def set_register(self, reg: int, value: int) -> None:
        """Set register value with logging."""
        if reg < 0 or reg > 15:
            raise ValueError(f"Register {reg} out of range (0-15)")

        old_value = self.registers[reg]
        self.registers[reg] = value & 0xFFFFFFFF  # Ensure 32-bit

        # Log the access
        self.access_log.append({
            'timestamp': datetime.now(),
            'type': 'write',
            'register': reg,
            'old_value': old_value,
            'new_value': value
        })

    def get_register(self, reg: int) -> int:
        """Get register value."""
        if reg < 0 or reg > 15:
            raise ValueError(f"Register {reg} out of range (0-15)")
        return self.registers[reg]

    def get_forge_control_bits(self) -> Dict[str, bool]:
        """Extract FORGE control scheme bits from CR0."""
        cr0 = self.registers[0]
        return {
            'forge_ready': bool((cr0 >> 31) & 1),
            'user_enable': bool((cr0 >> 30) & 1),
            'clk_enable': bool((cr0 >> 29) & 1)
        }


class NetworkCRInterface:
    """
    Simulates network-settable control registers with realistic delays.

    This class provides the critical boundary between the "outside world"
    (Python scripts setting CRs over network) and the FPGA simulation.

    Key features:
    - Configurable network delay (default 200ms)
    - Access logging for debugging
    - FORGE control scheme validation
    - Atomic register updates (no partial writes)
    """

    def __init__(self, default_delay_ms: float = 200.0):
        """
        Initialize network CR interface.

        Args:
            default_delay_ms: Default network delay in milliseconds
        """
        self.default_delay_ms = default_delay_ms
        self.slots: Dict[int, ControlRegisterBank] = {}
        self.network_busy = False
        self.total_network_ops = 0

    def add_slot(self, slot: int, initial_values: Optional[Dict[int, int]] = None) -> None:
        """
        Add a slot with control registers.

        Args:
            slot: Slot number (1-based)
            initial_values: Optional initial register values
        """
        self.slots[slot] = ControlRegisterBank(slot)

        if initial_values:
            for reg, value in initial_values.items():
                self.slots[slot].set_register(reg, value)

    async def set_control_register(
        self,
        slot: int,
        register: int,
        value: int,
        delay_ms: Optional[float] = None
    ) -> None:
        """
        Set a control register with network delay.

        This simulates the real MCC network API call:
        1. Network request initiated
        2. ~200ms network + processing delay
        3. Register updated atomically
        4. Response returned

        Args:
            slot: Slot number
            register: Control register number (0-15)
            value: 32-bit value to write
            delay_ms: Optional custom delay (uses default if None)
        """
        if slot not in self.slots:
            raise ValueError(f"Slot {slot} not configured")

        # Simulate network busy state
        self.network_busy = True
        self.total_network_ops += 1

        # Apply network delay (use CocoTB Timer instead of asyncio.sleep)
        delay = delay_ms if delay_ms is not None else self.default_delay_ms
        if delay > 0:
            delay_ns = int(delay * 1e6)  # Convert ms to ns
            await Timer(delay_ns, units='ns')

        # Atomic register update
        self.slots[slot].set_register(register, value)

        self.network_busy = False

    async def get_control_register(self, slot: int, register: int) -> int:
        """
        Read a control register (no delay for reads in simulation).

        In real hardware, reads also have network delay, but for
        simulation we make reads instant to simplify testing.

        Args:
            slot: Slot number
            register: Control register number

        Returns:
            Current register value
        """
        if slot not in self.slots:
            raise ValueError(f"Slot {slot} not configured")

        return self.slots[slot].get_register(register)

    def get_forge_status(self, slot: int) -> Dict[str, bool]:
        """
        Get FORGE control scheme status for a slot.

        Returns:
            Dictionary with forge_ready, user_enable, clk_enable, global_enable
        """
        if slot not in self.slots:
            return {
                'forge_ready': False,
                'user_enable': False,
                'clk_enable': False,
                'global_enable': False
            }

        bits = self.slots[slot].get_forge_control_bits()
        bits['global_enable'] = all([
            bits['forge_ready'],
            bits['user_enable'],
            bits['clk_enable']
            # Note: loader_done is internal to FPGA, not visible via CR
        ])

        return bits

    async def set_forge_control(
        self,
        slot: int,
        forge_ready: bool = False,
        user_enable: bool = False,
        clk_enable: bool = False,
        delay_ms: Optional[float] = None
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
        # Read current CR0
        cr0 = await self.get_control_register(slot, 0)

        # Clear FORGE bits
        cr0 &= ~(0x7 << 29)  # Clear bits 31:29

        # Set new bits
        if forge_ready:
            cr0 |= (1 << 31)
        if user_enable:
            cr0 |= (1 << 30)
        if clk_enable:
            cr0 |= (1 << 29)

        # Write back with network delay
        await self.set_control_register(slot, 0, cr0, delay_ms)

    def get_access_log(self, slot: int) -> list:
        """Get network access log for a slot."""
        if slot not in self.slots:
            return []
        return self.slots[slot].access_log

    def get_stats(self) -> Dict[str, any]:
        """Get network interface statistics."""
        return {
            'total_operations': self.total_network_ops,
            'network_busy': self.network_busy,
            'configured_slots': list(self.slots.keys()),
            'default_delay_ms': self.default_delay_ms
        }