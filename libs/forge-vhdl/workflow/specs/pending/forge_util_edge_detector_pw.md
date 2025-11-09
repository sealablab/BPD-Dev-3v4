# Component: Edge Detector with Configurable Pulse Width

**Category:** utilities
**Purpose:** Detect rising, falling, or both edges with configurable output pulse width

---

## Requirements

### Functionality
- Detect rising edge (low-to-high transition)
- Detect falling edge (high-to-low transition)
- Configurable edge type (rising only, falling only, or both)
- Configurable pulse width output (1 to N clock cycles)
- Retriggerable pulse (new edge during active pulse resets counter)
- Synchronous operation with clock domain

### Interface

**Entity:** forge_util_edge_detector_pw

**Generics:**
- `EDGE_TYPE : string := "both"` - Edge detection mode: "rising", "falling", or "both"
- `PULSE_WIDTH : positive := 1` - Output pulse width in clock cycles

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
rising_edge_out : out std_logic;
falling_edge_out : out std_logic
```

### Behavior
- **Reset:** All outputs = '0', pulse counter = 0, internal state cleared
- **Disabled (enable='0'):** Outputs = '0', no edge detection, counter holds
- **Enabled (enable='1'):** Monitor signal_in for edges
  - On rising edge detection: Start pulse counter = PULSE_WIDTH
  - On falling edge detection: Start pulse counter = PULSE_WIDTH
  - Output remains high while counter > 0
  - Counter decrements each cycle when active
  - New edge during active pulse reloads counter (retriggerable)
  - `edge_detected` outputs pulse based on EDGE_TYPE generic
  - `rising_edge_out` outputs pulse only on rising edges
  - `falling_edge_out` outputs pulse only on falling edges
- **Edge detection:** Based on comparing current signal_in vs. previous cycle's value
- **Output pulse:** Width = PULSE_WIDTH clock cycles

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**
1. test_reset - Verify all outputs = 0 after reset
   - Setup: Apply reset
   - Stimulus: None
   - Expected: edge_detected=0, rising_edge_out=0, falling_edge_out=0
   - Duration: 5 cycles

2. test_rising_edge_width - Verify rising edge with 3-cycle pulse width
   - Setup: PULSE_WIDTH=3, signal_in=0, enable=1
   - Stimulus: signal_in 0→1 at cycle 3
   - Expected: rising_edge_out=1 for cycles 4,5,6 (3 cycles)
   - Duration: 10 cycles

3. test_falling_edge_width - Verify falling edge with 3-cycle pulse width
   - Setup: PULSE_WIDTH=3, signal_in=1, enable=1
   - Stimulus: signal_in 1→0 at cycle 3
   - Expected: falling_edge_out=1 for cycles 4,5,6 (3 cycles)
   - Duration: 10 cycles

4. test_enable - Verify enable control
   - Setup: signal_in transitions, enable toggling
   - Stimulus: Edges while enable=0, then enable=1
   - Expected: No output when enable=0, normal when enable=1
   - Duration: 15 cycles

**Test Values:**

**P1 (Fast):**
- PULSE_WIDTH: 3 cycles (easy to verify)
- Signal transitions: Single edges with 5-cycle spacing
- Test cycles: 10-15 cycles per test
- Expected outputs: Specific cycle-by-cycle values

**P2 (Realistic):**
- PULSE_WIDTH: 1, 5, 10 cycles (range testing)
- Signal transitions: Burst edges, retriggering tests
- Test cycles: 50-100 cycles
- Edge case: Pulse width = 1 (matches original edge_detector)

---

## Design Notes

**Architecture:** Registered input comparison + pulse stretcher (down-counter)

**Approach:**
1. Register `signal_in` on each clock cycle → `signal_reg`
2. Compare current `signal_in` vs. previous `signal_reg`
3. Rising edge: `signal_in='1' AND signal_reg='0'`
4. Falling edge: `signal_in='0' AND signal_reg='1'`
5. On edge detection: Load pulse counter = PULSE_WIDTH
6. While counter > 0: Keep output high, decrement counter
7. Retriggerable: New edge reloads counter even if pulse active
8. Output logic based on EDGE_TYPE generic

**Dependencies:**
- Package: `ieee.std_logic_1164.all`
- Package: `ieee.numeric_std.all` (unsigned counter)

**Constraints:**
- Minimum detectable pulse: 1 clock cycle
- Edge detection latency: 1 clock cycle (registered input)
- Cannot detect edges faster than clock period
- Maximum pulse width: Limited by counter size (use natural type)

**Key Design Considerations:**
- Use synchronous design (no asynchronous edge detection)
- Pulse width counter must be unsigned/natural type
- Reset must clear internal state AND counter to prevent false edges
- Retriggerable behavior provides maximum flexibility
- PULSE_WIDTH=1 should behave identically to basic edge_detector

---

## Agent Instructions

**Agent 1 (forge-vhdl-component-generator):**
- Generate entity + architecture with EDGE_TYPE and PULSE_WIDTH generics
- Use registered comparison for edge detection (same as edge_detector.md)
- Add unsigned counter for pulse stretching (natural range 0 to PULSE_WIDTH)
- Follow port order: clk, rst_n, enable, signal_in, edge_detected, rising_edge_out, falling_edge_out
- Output to: `workflow/artifacts/vhdl/forge_util_edge_detector_pw.vhd`

**Agent 2 (cocotb-progressive-test-designer):**
- Design P1 test architecture (4 tests)
- Use PULSE_WIDTH=3 for easy verification
- Create test signals with known edge patterns
- Verify pulse width by counting cycles where output=1
- Check retriggerable behavior (optional for P2)
- Output test strategy to: `workflow/artifacts/tests/edge_detector_pw_test_strategy.md`

**Agent 3 (cocotb-progressive-test-runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_edge_detector_pw_tests/`

---

## Expected Output Example

For signal sequence: `0→1` at cycle 3 with PULSE_WIDTH=3:

```
Cycle 0: signal_in=0, outputs=0 (initial)
Cycle 1: signal_in=0, outputs=0
Cycle 2: signal_in=0, outputs=0
Cycle 3: signal_in=1, rising_edge_out=0 (detection pending, 1 cycle latency)
Cycle 4: signal_in=1, rising_edge_out=1 (pulse start, counter=3)
Cycle 5: signal_in=1, rising_edge_out=1 (counter=2)
Cycle 6: signal_in=1, rising_edge_out=1 (counter=1)
Cycle 7: signal_in=1, rising_edge_out=0 (counter=0, pulse complete)
```

**Use Cases:**
- Button press detection with extended indicator (LED stays on for N cycles)
- Protocol trigger with minimum pulse width guarantee
- Glitch filtering with extended confirmation period
- Debug event marking with visible pulse width

---

## References

**Related Components:**
- forge_util_edge_detector (reference pattern - edge_detector.md)
- forge_util_pulse_stretcher (pulse stretching pattern - pulse_stretcher.md)

**Standards:**
- VHDL Coding: `docs/VHDL_CODING_STANDARDS.md`
- Testing: `docs/PROGRESSIVE_TESTING_GUIDE.md`
- Pattern source: `workflow/specs/reference/edge_detector.md` (base pattern)
- Pattern source: `workflow/specs/reference/pulse_stretcher.md` (counter pattern)
