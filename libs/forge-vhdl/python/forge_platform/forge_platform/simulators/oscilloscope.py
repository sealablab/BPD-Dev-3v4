"""
Oscilloscope Simulator

Behavioral model for Moku Oscilloscope instrument.
Captures DUT output signals for analysis in simulation.
"""

from typing import Dict, List, Any, Optional
import cocotb
from cocotb.triggers import Timer
from cocotb.handle import SimHandleBase


class OscilloscopeSimulator:
    """
    Behavioral model of Moku Oscilloscope.

    Captures time-series data from DUT signals. Provides functional
    accuracy suitable for verification (not cycle-accurate hardware simulation).

    Phase 1: Basic time-series capture
    Phase 2: Multi-channel support
    Phase 3: Trigger modes, decimation
    """

    def __init__(self, dut: Any, settings: Dict[str, Any]):
        """
        Initialize oscilloscope simulator.

        Args:
            dut: CocotB DUT handle
            settings: Configuration dict from MokuConfig, may contain:
                - sample_rate: Samples per second (default: 125e6 for Moku:Go)
                - channels: List of signal names to capture
                - trigger_mode: 'auto' | 'normal' | 'single' (Phase 3)
                - trigger_level: Trigger threshold (Phase 3)
                - decimation: Sample rate reduction factor (Phase 3)
        """
        self.dut = dut
        self.settings = settings

        # Data storage: channel_name -> list of (time, value) tuples
        self.data: Dict[str, List[tuple]] = {}

        # Settings with defaults
        self.sample_rate = settings.get('sample_rate', 125e6)  # 125 MHz for Moku:Go
        self.sample_period_ns = int(1e9 / self.sample_rate)

        # Determine which signals to capture
        self.channels = settings.get('channels', self._discover_channels())

        # Phase 3 features (placeholder)
        self.trigger_mode = settings.get('trigger_mode', 'auto')
        self.trigger_level = settings.get('trigger_level', 0)
        self.decimation = settings.get('decimation', 1)

        # Initialize data buffers
        for channel in self.channels:
            self.data[channel] = []

        # External signal routing (for inter-slot connections)
        self.external_channels = {}  # channel_name → signal_handle

        # Statistics
        self.total_samples = 0
        self.capture_active = False

    def _discover_channels(self) -> List[str]:
        """
        Auto-discover DUT output signals if not specified.

        Looks for signals matching common patterns:
        - OutputA, OutputB, OutputC, OutputD (standard Moku outputs)
        - count_out, debug_bus, etc. (common signal names)

        Returns:
            List of signal names found in DUT
        """
        discovered = []

        # Standard Moku output signals
        for suffix in ['A', 'B', 'C', 'D']:
            signal_name = f'Output{suffix}'
            if hasattr(self.dut, signal_name):
                discovered.append(signal_name)

        # Common test signal names
        for name in ['count_out', 'debug_bus', 'probe_out']:
            if hasattr(self.dut, name):
                discovered.append(name)

        # Default to OutputC if nothing found (BPD debug bus convention)
        if not discovered:
            discovered = ['OutputC']

        return discovered

    async def run(self, duration_ns: int) -> None:
        """
        Run oscilloscope capture for specified duration.

        Args:
            duration_ns: Capture duration in nanoseconds
        """
        self.capture_active = True
        start_time = cocotb.utils.get_sim_time(units='ns')

        # Apply decimation to sample period
        effective_sample_period = self.sample_period_ns * self.decimation

        # Capture loop
        elapsed_ns = 0
        while elapsed_ns < duration_ns and self.capture_active:
            current_time_ns = cocotb.utils.get_sim_time(units='ns')

            # Sample all configured channels
            for channel in self.channels:
                signal = self._get_signal(channel)
                if signal is not None:
                    value = self._read_signal_value(signal)
                    self.data[channel].append((current_time_ns, value))
                    self.total_samples += 1

            # Wait for next sample period
            await Timer(effective_sample_period, units='ns')
            elapsed_ns = current_time_ns - start_time

        self.capture_active = False

    def add_external_channel(self, channel_name: str, signal_handle: SimHandleBase) -> None:
        """
        Add external signal source for inter-slot routing.

        Args:
            channel_name: Channel name (e.g., 'InputA' for Slot1InA routing)
            signal_handle: CocoTB signal handle from source DUT
        """
        self.external_channels[channel_name] = signal_handle
        # Add to data buffer if not already present
        if channel_name not in self.data:
            self.data[channel_name] = []
        # Update channels list if not present
        if channel_name not in self.channels:
            self.channels.append(channel_name)
        cocotb.log.info(f"OscilloscopeSimulator: Added external channel '{channel_name}'")

    def _get_signal(self, channel_name: str) -> Optional[SimHandleBase]:
        """
        Get DUT signal handle by name.

        Checks external channels first (for routing), then falls back to DUT.

        Args:
            channel_name: Signal name (e.g., 'OutputC', 'count_out', 'InputA')

        Returns:
            Signal handle or None if not found
        """
        # Check external channels first (inter-slot routing)
        if channel_name in self.external_channels:
            return self.external_channels[channel_name]

        # Fall back to DUT signals
        try:
            return getattr(self.dut, channel_name)
        except AttributeError:
            cocotb.log.warning(f"OscilloscopeSimulator: Signal '{channel_name}' not found in DUT")
            return None

    def _read_signal_value(self, signal: SimHandleBase) -> int:
        """
        Read signal value and convert to integer.

        Handles both signed and unsigned signals, as well as
        undefined/high-impedance values.

        Args:
            signal: CocotB signal handle

        Returns:
            Integer value (signed if signal is signed, unsigned otherwise)
        """
        try:
            # Try to get signed value first (for signed signals)
            if hasattr(signal.value, 'signed_integer'):
                return int(signal.value.signed_integer)
            else:
                # Fall back to unsigned
                return int(signal.value)
        except Exception:
            # Handle undefined/high-impedance values
            return 0

    def stop_capture(self) -> None:
        """Stop ongoing capture (useful for early termination)."""
        self.capture_active = False

    def get_data(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve captured data.

        Args:
            channel: Optional channel name (returns all if None)

        Returns:
            Dictionary with captured data:
            {
                'channel_name': {
                    'time': [t1, t2, ...],
                    'values': [v1, v2, ...],
                    'sample_count': N
                }
            }
        """
        if channel:
            return {channel: self._format_channel_data(channel)}
        else:
            # Return all channels
            result = {}
            for ch in self.channels:
                result[ch] = self._format_channel_data(ch)
            return result

    def _format_channel_data(self, channel: str) -> Dict[str, Any]:
        """
        Format channel data for analysis.

        Args:
            channel: Channel name

        Returns:
            Dict with 'time' and 'values' lists
        """
        if channel not in self.data:
            return {'time': [], 'values': [], 'sample_count': 0}

        time_values = self.data[channel]
        times = [t for t, v in time_values]
        values = [v for t, v in time_values]

        return {
            'time': times,
            'values': values,
            'sample_count': len(values)
        }

    def get_value_at_sample(self, channel: str, sample_index: int) -> Optional[int]:
        """
        Get value at specific sample index.

        Args:
            channel: Channel name
            sample_index: Sample index (0-based)

        Returns:
            Value at that sample, or None if out of range
        """
        if channel not in self.data:
            return None

        if sample_index < 0 or sample_index >= len(self.data[channel]):
            return None

        return self.data[channel][sample_index][1]  # Return value (not time)

    def verify_incrementing(self, channel: str, start_sample: int = 0, count: int = 10) -> bool:
        """
        Verify that signal increments by 1 each sample (for counter testing).

        Args:
            channel: Channel name
            start_sample: Starting sample index
            count: Number of samples to check

        Returns:
            True if values increment correctly, False otherwise
        """
        if channel not in self.data:
            return False

        for i in range(count - 1):
            idx = start_sample + i
            if idx + 1 >= len(self.data[channel]):
                return False

            current_val = self.data[channel][idx][1]
            next_val = self.data[channel][idx + 1][1]

            # Check if incremented (with wrap-around for counter width)
            # Detect counter width from max value seen
            max_val = max(v for _, v in self.data[channel][:idx+2])
            if max_val > 0:
                counter_bits = max_val.bit_length()
                counter_mask = (1 << counter_bits) - 1
                expected = (current_val + 1) & counter_mask
            else:
                expected = current_val + 1

            if next_val != expected:
                return False

        return True

    def get_latest_value(self, channel: str) -> Optional[int]:
        """Get most recent captured value for a channel."""
        if channel not in self.data or not self.data[channel]:
            return None
        return self.data[channel][-1][1]

    def clear_data(self) -> None:
        """Clear all captured data (useful for multi-run tests)."""
        for channel in self.channels:
            self.data[channel] = []
        self.total_samples = 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get capture statistics."""
        stats = {
            'channels': self.channels,
            'sample_rate': self.sample_rate,
            'decimation': self.decimation,
            'effective_sample_rate': self.sample_rate / self.decimation,
            'total_samples': self.total_samples,
            'capture_active': self.capture_active,
            'samples_per_channel': {}
        }

        for channel in self.channels:
            stats['samples_per_channel'][channel] = len(self.data[channel])

        return stats

    def __repr__(self) -> str:
        """String representation for debugging."""
        sample_counts = {ch: len(self.data[ch]) for ch in self.channels}
        return (
            f"OscilloscopeSimulator("
            f"channels={self.channels}, "
            f"samples={sample_counts}, "
            f"rate={self.sample_rate/1e6:.1f}MHz)"
        )