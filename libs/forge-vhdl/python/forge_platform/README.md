# Platform Testing Framework - Quick Start Guide

**Version:** 1.0.0
**Purpose:** MokuConfig-driven simulation platform for validating FORGE control schemes
**Session:** 2025-11-07-cocotb-platform-testing

---

## Overview

The Platform Testing Framework provides a **MokuConfig-driven simulation environment** for validating FORGE control schemes (CR0[31:29] calling convention) and testing custom instruments before hardware deployment.

**Key Innovation:** Network-settable Control Register (CR) primitives with realistic ~200ms delays create an explicit boundary between "outside world" (Python test scripts) and FPGA simulation, matching real Moku Control Computer (MCC) behavior.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Python Test Script (CocoTB)                                 │
│ - Uses MokuConfig YAML for setup                            │
│ - Network CR API with 200ms delays                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SimulationBackend (platform/simulation_backend.py)          │
│ - MokuConfig parser and coordinator                         │
│ - Routes CR updates to DUT                                  │
│ - Manages simulator instances (Oscilloscope, etc.)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ NetworkCR (platform/network_cr.py)                          │
│ - 16 Control Registers (CR0-CR15)                           │
│ - 16 Status Registers (SR0-SR15)                            │
│ - Async updates with 200ms realistic delays                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ VHDL DUT (CustomInstrument)                                 │
│ - FORGE 3-layer architecture (main → shim → wrapper)        │
│ - CR0[31:29] control scheme                                 │
│ - Application logic                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### Core Infrastructure

| Component | Purpose | File |
|-----------|---------|------|
| **Backend** | Abstract interface for simulation backends | `backend.py` |
| **NetworkCR** | Network-settable Control/Status Registers | `network_cr.py` |
| **SimulationBackend** | MokuConfig-driven coordinator | `simulation_backend.py` |

### Simulators

| Simulator | Purpose | File |
|-----------|---------|------|
| **Oscilloscope** | Multi-channel capture, triggers, routing | `simulators/oscilloscope.py` |
| **CloudCompile** | Passthrough for future expansion | `simulators/cloud_compile.py` |

---

## Quick Start

### 1. Running FORGE Control Validation Tests

These tests validate the CR0[31:29] control scheme fundamentals:

```bash
cd libs/forge-vhdl
uv run python cocotb_test/run.py platform_forge_control
```

**Tests:**
- `test_forge_control_sequence()` - Power-on state, enable sequence, network delays
- `test_network_cr_primitives()` - Concurrent CR updates, network statistics

**Expected Output:**
```
P1 - BASIC tests
✅ test_forge_control_sequence (PASSED)
✅ test_network_cr_primitives (PASSED)
```

### 2. Running Counter PoC Tests

Demonstrates FORGE 3-layer architecture with a simple configurable counter:

```bash
cd libs/forge-vhdl
uv run python cocotb_test/run.py platform_counter_poc
```

**Tests:**
- `test_forge_control_sequence()` - FORGE enable sequence validation
- `test_basic_counter_operation()` - Counter incrementing with configurable max
- `test_counter_overflow()` - Overflow flag and wraparound behavior

**Expected Output:**
```
P1 - BASIC tests
✅ test_forge_control_sequence (PASSED)
✅ test_basic_counter_operation (PASSED)
✅ test_counter_overflow (PASSED)
```

### 3. Running with Custom Deployment YAML (Future)

```bash
cd libs/forge-vhdl
uv run python cocotb_test/run.py platform_bpd_deployment \
  --config ../../bpd-deployment-setup1-dummy-dut.yaml
```

---

## Network CR API Reference

### Setting Control Registers

```python
from cocotb_test.platform.network_cr import NetworkCR

# Create network CR instance
network_cr = NetworkCR(dut)

# Set Control Register (async, 200ms delay)
await network_cr.set_control(reg_num=0, value=0xE0000000)

# FORGE control scheme example (CR0[31:29])
FORGE_READY_BIT = 31
USER_ENABLE_BIT = 30
CLK_ENABLE_BIT = 29

forge_ready = 1 << FORGE_READY_BIT    # 0x80000000
user_enable = 1 << USER_ENABLE_BIT    # 0x40000000
clk_enable = 1 << CLK_ENABLE_BIT      # 0x20000000

# Enable all FORGE control bits
await network_cr.set_control(0, forge_ready | user_enable | clk_enable)
```

### Reading Status Registers

```python
# Read Status Register (immediate)
status_value = network_cr.get_status(reg_num=0)
```

### Network Statistics

```python
# Get CR update count
stats = network_cr.get_statistics()
print(f"CR updates: {stats['control_updates']}")
```

---

## FORGE Control Scheme: CR0[31:29]

**THIS IS MANDATORY** for all Moku custom instruments!

### The 3-Bit Calling Convention

```
CR0[31] = forge_ready   ← Set by loader after deployment complete
CR0[30] = user_enable   ← User control (GUI toggle)
CR0[29] = clk_enable    ← Clock gating control
```

Plus internal signal:
```
loader_done             ← BRAM loader FSM completion
```

### Combined Enable Logic

```vhdl
global_enable = forge_ready AND user_enable AND clk_enable AND loader_done
```

### Initialization Sequence

```python
# 1. Power-on (all bits = 0)
#    CR0 = 0x00000000
#    → global_enable = 0 (safe state)

# 2. MCC loader completes deployment
await network_cr.set_control(0, 0x80000000)  # forge_ready = 1

# 3. User enables module
await network_cr.set_control(0, 0xC0000000)  # forge_ready=1, user_enable=1

# 4. User enables clock
await network_cr.set_control(0, 0xE0000000)  # All three bits set
#    → global_enable = 1 ✓
#    → Module ENABLED!
```

---

## Counter PoC Example

The forge_counter demonstrates FORGE 3-layer architecture:

### Register Allocation

```
CR0[31:29] - FORGE control scheme (forge_ready, user_enable, clk_enable)
CR0[15:0]  - counter_max (16-bit unsigned)

SR0[31:0]  - counter_value (32-bit current count)
SR1[0]     - overflow flag
```

### Test Example

```python
import cocotb
from cocotb.clock import Clock
from cocotb_test.platform.network_cr import NetworkCR

@cocotb.test()
async def test_basic_counter_operation(dut):
    # Setup clock
    clock = Clock(dut.Clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Create network CR
    network_cr = NetworkCR(dut)

    # Reset
    dut.Reset.value = 1
    await Timer(100, units="ns")
    dut.Reset.value = 0
    await Timer(100, units="ns")

    # Configure counter_max = 10 (with global_enable=0)
    counter_max = 10
    await network_cr.set_control(0, counter_max)
    await Timer(500, units="ns")  # Wait for ready_for_updates latch

    # Enable FORGE control bits
    forge_bits = 0xE0000000  # All three FORGE bits
    await network_cr.set_control(0, forge_bits | counter_max)

    # Wait for counter to reach max
    await Timer(200, units="ns")

    # Read counter value
    counter_value = network_cr.get_status(0)
    print(f"Counter value: {counter_value}")
```

---

## Key Technical Learnings

### 1. GHDL Timing Characteristics

**Issue:** GHDL simulator is not cycle-accurate compared to real Moku platform.

**Solution:** Add timing slack (4+ cycles) for register handshaking:

```python
# Bad: Immediate enable after config
await network_cr.set_control(0, counter_max)
await network_cr.set_control(0, forge_bits | counter_max)  # Too fast!

# Good: Wait for ready_for_updates latch
await network_cr.set_control(0, counter_max)
await Timer(500, units="ns")  # 50 cycles @ 100MHz
await network_cr.set_control(0, forge_bits | counter_max)
```

### 2. Two-Phase Enable Sequence

**Pattern:** Configure first, enable second

```python
# Phase 1: Set configuration with global_enable=0
await network_cr.set_control(0, config_value)
await Timer(500, units="ns")  # Wait for latch

# Phase 2: Enable FORGE control bits
await network_cr.set_control(0, FORGE_BITS | config_value)
```

**Why:** Main app FSM must be in IDLE state with `ready_for_updates='1'` before latching new config values.

### 3. Control Register Bit Manipulation

**Critical:** Must OR FORGE control bits with config values, not overwrite!

```python
# Bad: Overwrites config
await network_cr.set_control(0, config_value)
await network_cr.set_control(0, FORGE_BITS)  # ❌ Lost config_value!

# Good: Combines both
await network_cr.set_control(0, config_value)
await network_cr.set_control(0, FORGE_BITS | config_value)  # ✓
```

---

## File Structure

```
libs/forge-vhdl/cocotb_test/platform/
├── __init__.py                    # Package init
├── README.md                      # This file
├── backend.py                     # Abstract Backend interface
├── network_cr.py                  # Network CR with 200ms delays
├── simulation_backend.py          # MokuConfig-driven coordinator
└── simulators/
    ├── __init__.py
    ├── oscilloscope.py           # Multi-channel capture
    └── cloud_compile.py          # CloudCompile passthrough

libs/forge-vhdl/cocotb_test/
├── test_platform_forge_control.py           # FORGE scheme tests
├── test_platform_counter_poc.py             # Counter PoC tests
├── test_platform_counter_poc_constants.py   # Counter test constants
└── test_duts/
    └── forge_counter.vhd         # Counter PoC VHDL (3-layer FORGE)
```

---

## Test Levels (Progressive Testing)

### P1 - BASIC (Default, LLM-optimized)
- 3-5 essential tests
- <20 line output, <100 tokens
- Fast iteration for AI-assisted development

### P2 - INTERMEDIATE
- 10-15 tests with edge cases
- <50 line output
- Comprehensive feature coverage

### P3 - COMPREHENSIVE
- 20-30 tests with stress testing
- Boundary values, corner cases
- Production readiness validation

**Run with test level:**
```bash
uv run python cocotb_test/run.py platform_counter_poc --test-level P2
```

---

## Common Issues & Solutions

### Issue: "ready_for_updates never asserts"

**Cause:** Main app FSM not in IDLE state

**Solution:** Add delay after reset, ensure global_enable=0 during config

```python
dut.Reset.value = 1
await Timer(100, units="ns")
dut.Reset.value = 0
await Timer(100, units="ns")  # Let FSM reach IDLE

# Configure with global_enable=0
await network_cr.set_control(0, config_value)
await Timer(500, units="ns")  # Wait for latch
```

### Issue: "Config values lost after enabling FORGE bits"

**Cause:** Overwriting CR0 instead of ORing with config

**Solution:** Use bitwise OR to combine FORGE bits with config

```python
# Store config first
config_value = 0x00000010  # Example config in CR0[15:0]

# Enable FORGE bits while preserving config
forge_bits = 0xE0000000
await network_cr.set_control(0, forge_bits | config_value)
```

### Issue: "Simulation hangs on CR update"

**Cause:** 200ms network delay not awaited

**Solution:** Always await network_cr.set_control()

```python
# Bad: No await
network_cr.set_control(0, value)  # ❌ Returns immediately!

# Good: Await completes after 200ms
await network_cr.set_control(0, value)  # ✓ Waits for network delay
```

---

## Next Steps

### Phase 1 (Current - 90% complete)
- ✅ Platform infrastructure
- ✅ FORGE control validation tests
- ✅ Counter PoC with P1 tests
- ⏳ Integration test with deployment YAMLs
- ⏳ This documentation

### Phase 2 (BPD Deployment Validation)
- Load bpd-deployment-setup1-dummy-dut.yaml
- Load bpd-deployment-setup2-real-dut.yaml
- Validate 2-slot routing (Slot2OutD → Slot1InA)
- Test network CR updates with BPD registers

### Phase 3 (Advanced Features)
- Complete routing matrix simulation
- Oscilloscope trigger modes
- Multi-channel simultaneous capture
- Cross-platform testing (Go/Lab/Pro)

---

## Related Documentation

- **CLAUDE.md** (monorepo root) - FORGE architecture overview
- **libs/forge-vhdl/CLAUDE.md** - VHDL components, CocoTB testing
- **examples/basic-probe-driver/vhdl/FORGE_ARCHITECTURE.md** - Complete 3-layer spec
- **Obsidian/Project/Sessions/2025-11-07-cocotb-platform-testing/** - Session notes

---

## Support

For issues or questions:
- Check session plan: `Obsidian/Project/Sessions/2025-11-07-cocotb-platform-testing/2025-11-07-cocotb-platform-test-PLAN.md`
- Review FORGE architecture: `examples/basic-probe-driver/vhdl/FORGE_ARCHITECTURE.md`
- Examine counter PoC: `cocotb_test/test_duts/forge_counter.vhd`

---

**Last Updated:** 2025-11-07
**Status:** Phase 1 - 90% Complete
**Next Milestone:** Integration test with deployment YAMLs
