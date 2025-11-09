# Platform Integration Tests

CocoTB tests that interact with platform backend (simulation or real MCC hardware).

## What Are Platform Tests?

Platform tests validate integration with the Moku Control Computer (MCC) interface:
- FORGE control scheme (CR0[31:29] enable sequence)
- Network-accessible Control Registers (CR0-CR15)
- Status Registers (SR0-SR15, future)
- Physical outputs (OutputA/B/C/D to oscilloscope)
- Signal routing and coordination

## Backend Modes

**Simulation Backend** (default)
- Pure GHDL simulation
- Control Registers set directly in test code
- Fast, no hardware required

**Cloud Compile Backend** (future)
- Compile to bitstream, deploy to real Moku hardware
- Network-accessible Control Registers via MCC API
- Physical oscilloscope capture via Moku API

## Available Platform Tests

**test_platform_forge_control.py**
- Validates CR0[31:29] FORGE control scheme
- Tests 4-condition enable sequence

**test_platform_oscilloscope_capture.py**
- Captures physical outputs (OutputD)
- Decodes HVS encoding
- Validates state + status visible on oscilloscope

**test_platform_routing_integration.py**
- Tests signal routing between DUT and platform
- Multi-slot coordination (if applicable)

## Running Platform Tests

```bash
# Simulation backend (default)
uv run python cocotb_tests/run.py platform_forge_control

# With oscilloscope capture
uv run python cocotb_tests/run.py platform_oscilloscope_capture
```

Platform tests demonstrate "train like you fight" - same bitstream for development and production.
