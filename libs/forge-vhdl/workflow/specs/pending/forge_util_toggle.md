# Component: Toggle Flip-Flop

**Category:** utilities
**Purpose:** Toggles output state on each rising edge of trigger input with synchronous enable control

---

## Requirements

### Functionality
- Toggle output state on rising edge of trigger input
- Synchronous enable control to gate toggle functionality
- Single-cycle pulse output when toggle occurs (debug visibility)
- Minimal architecture: registered comparison + toggle register
- Primary use case: Debug/LED toggle indicators

### Interface

**Entity:** forge_util_toggle

**Generics:** None (simple, fixed configuration)

**Ports:**
```vhdl
-- Clock & Reset
clk         : in  std_logic;
rst_n       : in  std_logic;

-- Control
enable      : in  std_logic;

-- Data Input
trigger_in  : in  std_logic;

-- Outputs
toggle_out   : out std_logic;  -- Toggle state (flips on each trigger edge when enabled)
toggle_pulse : out std_logic   -- 1-cycle pulse when toggle occurs (debug output)
```

### Behavior
- **Reset (rst_n='0'):** All outputs = '0', internal state cleared
- **Disabled (enable='0'):** Output holds current state, no toggling occurs, toggle_pulse = '0'
- **Enabled (enable='1'):** Monitor trigger_in for rising edges
  - On rising edge (0→1 transition): Toggle output state, assert toggle_pulse for 1 cycle
  - On falling edge or stable: No change, toggle_pulse = '0'
- **Edge detection:** Based on comparing current trigger_in vs. previous cycle's value
- **Output pulse:** toggle_pulse is exactly 1 clock cycle wide
- **Latency:** 1 clock cycle (registered output)

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**

1. **test_reset** - Verify all outputs = 0 after reset
   - Setup: Toggle output in arbitrary state
   - Stimulus: Assert rst_n = '0' for 5 cycles
   - Expected: toggle_out = '0', toggle_pulse = '0'
   - Duration: 10 cycles

2. **test_single_toggle** - Verify output toggles on rising edge of trigger
   - Setup: After reset, toggle_out = '0', enable = '1'
   - Stimulus: trigger_in: 0 → 1 → 0 (one rising edge)
   - Expected: toggle_out: 0 → 1, toggle_pulse: 0 → 1 → 0 (1-cycle pulse)
   - Duration: 10 cycles

3. **test_multiple_toggles** - Verify output toggles repeatedly on multiple triggers
   - Setup: enable = '1'
   - Stimulus: trigger_in: 0→1→0→1→0→1→0 (3 rising edges)
   - Expected: toggle_out: 0→1→0→1, toggle_pulse pulses 3 times (1 cycle each)
   - Duration: 15 cycles

4. **test_enable_control** - Verify enable gates the toggle functionality
   - Setup: toggle_out = '0', enable = '0'
   - Stimulus: trigger_in: 0→1→0→1→0 (2 rising edges with enable='0')
   - Expected: toggle_out stays '0' (no toggling), toggle_pulse = '0'
   - Then: Set enable = '1', apply trigger: 0→1→0
   - Expected: toggle_out: 0→1, toggle_pulse pulses once
   - Duration: 20 cycles

**Test Values:**

**P1 (Fast):**
- Total test cycles: ~55 cycles (across 4 tests)
- Trigger transitions: 0→1→0 patterns (rising edges)
- Edge spacing: 2-3 cycles between transitions
- Expected output: <20 lines with GHDL aggressive filtering

**P2 (Future - Comprehensive):**
- Edge case: Trigger held high for many cycles (verify only 1 toggle)
- Edge case: Rapid back-to-back toggles (consecutive cycles)
- Stress test: 50+ toggles to verify stability
- Total cycles: ~200 cycles

---

## Design Notes

**Architecture:** Combinational logic with registered state

**Approach:**
1. Register `trigger_in` on each clock cycle → `trigger_reg`
2. Compare current `trigger_in` vs. previous `trigger_reg`
3. Rising edge detected: `trigger_in='1' AND trigger_reg='0'`
4. If enable='1' AND rising edge detected: toggle output state
5. toggle_pulse = rising_edge_detected AND enable (1 cycle pulse)

**Dependencies:**
- Package: `ieee.std_logic_1164.all` (standard digital logic only)
- No forge-vhdl package dependencies (standalone utility)

**Constraints:**
- Minimum detectable pulse: 1 clock cycle (trigger must stay high for full cycle)
- Edge detection latency: 1 clock cycle (registered input)
- Cannot detect edges faster than clock period
- No metastability protection (assumes trigger_in already synchronized to clk domain)

**Key Design Considerations:**
- Use synchronous design (no asynchronous toggle)
- Reset overrides everything (rst_n > enable hierarchy)
- Output must be registered (no combinational outputs)
- toggle_pulse must be exactly 1 cycle wide
- Similar pattern to edge_detector reference spec

**Edge Cases Handled:**
- Reset during toggle: Reset wins, output goes to '0'
- Enable toggles simultaneously with trigger: If enable='0', no toggle
- Trigger pulse shorter than 1 clock cycle: Won't be detected
- Trigger stays high for multiple cycles: Only toggles once (on rising edge only)
- First cycle after reset: trigger_reg starts at '0', valid rising edge allowed

---

## Agent Instructions

**Agent 1 (forge-vhdl-component-generator):**
- Generate entity + architecture for toggle flip-flop
- Use registered comparison for edge detection (similar to edge_detector pattern)
- Follow port order: clk, rst_n, enable, trigger_in, toggle_out, toggle_pulse
- VHDL-2008 syntax only
- Output to: `workflow/artifacts/vhdl/forge_util_toggle.vhd`
- Reference: `workflow/specs/reference/edge_detector.md` for architectural guidance

**Agent 2 (cocotb-progressive-test-designer):**
- Design P1 test architecture (4 tests)
- Create test signals with known toggle patterns
- Verify 1-cycle pulse width on toggle_pulse output
- Design constants file with test values
- Output test strategy to: `workflow/artifacts/tests/toggle_test_strategy.md`

**Agent 3 (cocotb-progressive-test-runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL with aggressive filtering
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_toggle_tests/`
- Ensure all 4 P1 tests pass

---

## Expected Output Example

For trigger sequence: `0→1→0→1→0→1→0` over 15 cycles with enable='1':

```
Cycle 0:  trigger_in=0, enable=1, toggle_out=0, toggle_pulse=0 (initial after reset)
Cycle 1:  trigger_in=1, enable=1, toggle_out=1, toggle_pulse=1 (rising edge detected, toggled)
Cycle 2:  trigger_in=0, enable=1, toggle_out=1, toggle_pulse=0 (output holds)
Cycle 3:  trigger_in=0, enable=1, toggle_out=1, toggle_pulse=0 (stable)
Cycle 4:  trigger_in=1, enable=1, toggle_out=0, toggle_pulse=1 (rising edge detected, toggled back)
Cycle 5:  trigger_in=0, enable=1, toggle_out=0, toggle_pulse=0 (output holds)
Cycle 6:  trigger_in=0, enable=1, toggle_out=0, toggle_pulse=0 (stable)
Cycle 7:  trigger_in=1, enable=1, toggle_out=1, toggle_pulse=1 (rising edge detected, toggled)
Cycle 8:  trigger_in=0, enable=1, toggle_out=1, toggle_pulse=0 (output holds)
...
```

**With enable='0':**
```
Cycle 0:  trigger_in=0, enable=0, toggle_out=0, toggle_pulse=0 (initial)
Cycle 1:  trigger_in=1, enable=0, toggle_out=0, toggle_pulse=0 (rising edge ignored, disabled)
Cycle 2:  trigger_in=0, enable=0, toggle_out=0, toggle_pulse=0 (no change)
Cycle 3:  trigger_in=1, enable=0, toggle_out=0, toggle_pulse=0 (still ignored)
...
```

**Use Cases:**
- LED toggle for debug/status indication
- Frequency divider (divide-by-2)
- Event counter parity detector (odd/even)
- Manual state toggle for test fixtures
- Pulse train generation trigger

---

## Implementation Notes

**Target Files:**
- VHDL: `vhdl/components/utilities/forge_util_toggle.vhd`
- Tests: `cocotb_tests/components/forge_util_toggle_tests/`
  - `forge_util_toggle_constants.py`
  - `P1_forge_util_toggle_basic.py`

**Integration:**
- Standalone component (no FORGE dependencies)
- No voltage domain packages needed (pure digital)
- No HVS encoding needed (simple utility)
- Works in any clock domain (assumes synchronized inputs)

**References:**
- VHDL Standards: `CLAUDE.md` (Section: VHDL Coding Standards)
- Testing Guide: `docs/PROGRESSIVE_TESTING_GUIDE.md`
- Similar Pattern: `workflow/specs/reference/edge_detector.md`
- CocoTB Troubleshooting: `docs/COCOTB_TROUBLESHOOTING.md`

---

**Specification Version:** 1.0.0
**Generated:** 2025-11-09
**Method:** Interactive requirements gathering (7-phase conversational)
**Status:** Ready for automated agent workflow
