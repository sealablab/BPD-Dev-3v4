"""
Abstract Backend Interface for Moku Platform Simulation

Unified interface for simulation and (future) hardware backends.
Part of the cocotb-platform-testing framework.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Backend(ABC):
    """
    Abstract base class for platform backends (simulation or hardware).

    Defines the unified interface that all backends must implement.
    Focuses on FORGE control scheme validation and multi-instrument coordination.
    """

    @abstractmethod
    async def setup(self) -> None:
        """
        Initialize the backend and create instrument simulators.

        Should:
        - Validate MokuConfig
        - Create instrument instances for each slot
        - Setup routing matrix
        - Initialize control registers to safe defaults
        """
        pass

    @abstractmethod
    async def run(self, duration_ms: float) -> Dict[str, Any]:
        """
        Run the platform for specified duration and collect data.

        Args:
            duration_ms: Simulation/execution duration in milliseconds

        Returns:
            Dictionary with captured data from all instruments
            Format: {slot_num: instrument_data}
        """
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """
        Clean up resources and gracefully shutdown.
        """
        pass

    @abstractmethod
    def get_instrument(self, slot_or_name: int | str) -> Any:
        """
        Access an instrument by slot number or type name.

        Args:
            slot_or_name: Slot number (1, 2) or instrument name ('Oscilloscope')

        Returns:
            Instrument simulator instance or None if not found
        """
        pass

    @abstractmethod
    async def set_control_register(
        self,
        slot: int,
        register: int,
        value: int,
        delay_ms: float = 200.0
    ) -> None:
        """
        Set a control register value with network-realistic delay.

        This is THE key primitive for simulating MCC network API behavior.
        The delay simulates real-world network latency for CR updates.

        Args:
            slot: Slot number (1-based)
            register: Control register number (0-15)
            value: 32-bit register value
            delay_ms: Network delay in milliseconds (default 200ms)
        """
        pass

    @abstractmethod
    async def get_control_register(self, slot: int, register: int) -> int:
        """
        Read a control register value.

        Args:
            slot: Slot number (1-based)
            register: Control register number (0-15)

        Returns:
            32-bit register value
        """
        pass

    @abstractmethod
    async def get_status_register(self, slot: int, register: int) -> int:
        """
        Read a status register value.

        Note: Status registers are read-only from network perspective.

        Args:
            slot: Slot number (1-based)
            register: Status register number (0-15)

        Returns:
            32-bit register value
        """
        pass

    def validate_forge_control(self, slot: int) -> Dict[str, bool]:
        """
        Validate FORGE control scheme for a slot.

        Checks the CR0[31:29] calling convention:
        - CR0[31] = forge_ready
        - CR0[30] = user_enable
        - CR0[29] = clk_enable

        Args:
            slot: Slot number to check

        Returns:
            Dictionary with validation results:
            {
                'forge_ready': bool,
                'user_enable': bool,
                'clk_enable': bool,
                'global_enable': bool  # All conditions met
            }
        """
        # Default implementation - subclasses can override
        return {
            'forge_ready': False,
            'user_enable': False,
            'clk_enable': False,
            'global_enable': False
        }