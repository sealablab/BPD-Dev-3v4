# Component: Edge Detector

**Category:** utilities
**Purpose:** Detect rising, falling, or both edges on a digital signal

---

## Requirements

### Functionality
- Detect rising edge (low-to-high transition)
- Detect falling edge (high-to-low transition)
- Configurable edge type (rising only, falling only, or both)
- Single-cycle pulse output on detected edge
- Synchronous operation with clock domain

### Interface

**Entity:** forge_util_edge_detector

**Generics:**
- `EDGE_TYPE : string := "both"` - Edge detection mode: "rising", "falling", or "both"

**Ports:**
```vhdl
-- Clock & Reset
clk         : in std_logic;
rst_n       : in std_logic;

-- Control
enable      : in std_logic;

-- Data
signal_in   : in std_logic;

-- Outputs
edge_detected : out std_logic;
rising_edge_out : out std_logic;  -- Only high on rising edge
falling_edge_out : out std_logic  -- Only high on falling edge
```

### Behavior
- **Reset:** All outputs = '0', internal state cleared
- **Disabled (enable='0'):** Outputs = '0', no edge detection
- **Enabled (enable='1'):** Monitor signal_in for edges
  - On rising edge: `rising_edge_out` pulses high for 1 cycle
  - On falling edge: `falling_edge_out` pulses high for 1 cycle
  - `edge_detected` pulses high for detected edge type based on EDGE_TYPE generic
- **Edge detection:** Based on comparing current signal_in vs. previous cycle's value
- **Output pulse:** Exactly 1 clock cycle wide

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**
1. test_reset - Verify all outputs = 0 after reset
2. test_rising_edge - Verify rising edge detection (0→1 transition)
3. test_falling_edge - Verify falling edge detection (1→0 transition)
4. test_enable_control - Verify enable starts/stops edge detection

**Test Values:**

**P1 (Fast):**
- Signal transitions: 0→1→0→1→0 (5 edges total)
- Test cycles: 20 cycles
- Edge delay: 2-3 cycles between transitions

**P2 (Realistic):**
- Signal transitions: Multiple bursts of edges
- Test cycles: 100 cycles
- Edge delay: 1-10 cycles (variable timing)
- Test all 3 EDGE_TYPE configurations

---

## Design Notes

**Architecture:** Registered input comparison

**Approach:**
1. Register `signal_in` on each clock cycle → `signal_reg`
2. Compare current `signal_in` vs. previous `signal_reg`
3. Rising edge: `signal_in='1' AND signal_reg='0'`
4. Falling edge: `signal_in='0' AND signal_reg='1'`
5. Output logic based on EDGE_TYPE generic

**Dependencies:**
- Package: `ieee.std_logic_1164.all`

**Constraints:**
- Minimum detectable pulse: 1 clock cycle
- Edge detection latency: 1 clock cycle (registered input)
- Cannot detect edges faster than clock period

**Key Design Considerations:**
- Use synchronous design (no asynchronous edge detection)
- Outputs must be exactly 1 cycle wide (no stretching)
- Reset must clear internal state to prevent false edges on startup

---

## Agent Instructions

**Agent 1 (VHDL Generator):**
- Generate entity + architecture with generic for EDGE_TYPE
- Use registered comparison for edge detection
- Follow port order: clk, rst_n, enable, signal_in, edge_detected, rising_edge_out, falling_edge_out
- Output to: `workflow/artifacts/vhdl/forge_util_edge_detector.vhd`

**Agent 2 (Test Designer):**
- Design P1 test architecture (4 tests)
- Create test signals with known edge patterns
- Verify 1-cycle pulse width on outputs
- Output test strategy to: `workflow/artifacts/tests/edge_detector_test_strategy.md`

**Agent 3 (Test Runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_edge_detector_tests/`

---

## Expected Output Example

For signal sequence: `0→1→0→1→0` over 10 cycles:

```
Cycle 0: signal_in=0, outputs=0 (initial)
Cycle 1: signal_in=1, rising_edge_out=1 (detected 0→1)
Cycle 2: signal_in=1, outputs=0
Cycle 3: signal_in=0, falling_edge_out=1 (detected 1→0)
Cycle 4: signal_in=0, outputs=0
Cycle 5: signal_in=1, rising_edge_out=1 (detected 0→1)
...
```

**Use Cases:**
- Button press detection (debounced input)
- Clock domain crossing edge detection
- Protocol start-of-frame detection
- Trigger event detection for debug
