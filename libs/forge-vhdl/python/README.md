# FORGE Python Utilities

Python packages for FORGE development, testing, and platform interaction.

## forge_cocotb/

CocoTB progressive testing framework for VHDL simulation.

**Purpose:** LLM-friendly VHDL testing with 98% output reduction
- Progressive test levels (P1/P2/P3)
- GHDL output filtering
- Test base classes and utilities
- MCC Control Register helpers

See `forge_cocotb/README.md` for detailed usage.

## forge_platform/

Platform abstraction for simulation and hardware backends.

**Purpose:** Unified interface for MCC interaction
- Simulation backend (pure GHDL)
- Cloud compile backend (real hardware, future)
- Network Control Register API
- Oscilloscope capture and decoding

See `forge_platform/README.md` for backend documentation.

## forge_tools/

Standalone tools and utilities for FORGE development.

**Purpose:** Debugging and analysis tools
- HVS decoder (hierarchical voltage decoding)
- Register value converters
- Bitstream analysis tools (future)

See `forge_tools/README.md` for tool documentation.

## Installation

These packages are installed as part of the vhdl-forge project:

```bash
uv sync
```

## Import Pattern

```python
from forge_cocotb import TestBase
from forge_platform import SimulationBackend
from forge_tools import hierarchical_decoder
```
