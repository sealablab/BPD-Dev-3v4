"""
Instrument Simulators for Platform Testing

Behavioral models for Moku instruments.
"""

from .oscilloscope import OscilloscopeSimulator
from .cloud_compile import CloudCompileSimulator

# Registry for automatic simulator selection
SIMULATOR_REGISTRY = {
    'Oscilloscope': OscilloscopeSimulator,
    'CloudCompile': CloudCompileSimulator,
}

__all__ = [
    'OscilloscopeSimulator',
    'CloudCompileSimulator',
    'SIMULATOR_REGISTRY',
]