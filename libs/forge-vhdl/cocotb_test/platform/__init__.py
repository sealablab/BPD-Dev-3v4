"""
CocoTB Platform Testing Framework

MokuConfig-driven simulation platform for FORGE control scheme validation.
"""

from .backend import Backend
from .network_cr import NetworkCRInterface, ControlRegisterBank

__all__ = [
    'Backend',
    'NetworkCRInterface',
    'ControlRegisterBank',
]