# Component: forge_util_edge_detector

**Category:** utilities
**Purpose:** Detect rising, falling, or both edges on input signal with configurable edge type

---

## Requirements

### Functionality
- Detect transitions (edges) on a digital input signal
- Configurable edge type via generic: RISING, FALLING, or BOTH
- Generate 1-cycle pulse output when edge is detected
- Enable control to start/stop edge detection
- Registered comparison architecture (compare current vs. previous cycle)
- 1-cycle latency (edge detected on cycle after transition occurs)
- Clean reset behavior (output cleared, internal state reset)

### Interface

**Entity:** forge_util_edge_detector

**Generics:**
- EDGE_TYPE : string := "RISING" -- Detection mode: "RISING", "FALLING", or "BOTH"

**Ports:**
```vhdl
-- Clock & Reset
clk           : in  std_logic;
rst_n         : in  std_logic;

-- Control
enable        : in  std_logic;

-- Data inputs
signal_in     : in  std_logic;

-- Data outputs
edge_detected : out std_logic;
```

### Behavior
- **Reset (rst_n='0'):**
  - edge_detected = '0'
  - Internal registered state (signal_in_prev) cleared to '0'

- **Disabled (enable='0'):**
  - edge_detected = '0'
  - Internal state tracking paused (signal_in_prev holds last value)

- **Enabled (enable='1'):**
  - **RISING mode (EDGE_TYPE="RISING"):**
    - edge_detected = '1' for one cycle when signal_in transitions from '0' to '1'
    - edge_detected = '0' otherwise
  - **FALLING mode (EDGE_TYPE="FALLING"):**
    - edge_detected = '1' for one cycle when signal_in transitions from '1' to '0'
    - edge_detected = '0' otherwise
  - **BOTH mode (EDGE_TYPE="BOTH"):**
    - edge_detected = '1' for one cycle on any transition (0→1 or 1→0)
    - edge_detected = '0' otherwise
  - Internal register updates: signal_in_prev <= signal_in (on each clock cycle)

- **Edge cases:**
  - Multiple consecutive edges detected correctly (no missed edges)
  - Glitches shorter than 1 clock cycle not guaranteed to be detected (synchronous design)
  - Enable transitions: Disabling during edge detection clears output immediately

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**

1. **test_reset** - Verify reset behavior
   - Setup: Apply reset (rst_n='0')
   - Stimulus: None
   - Expected: edge_detected='0', internal state cleared
   - Duration: 5 cycles

2. **test_rising_edge** - Verify rising edge detection (EDGE_TYPE="RISING")
   - Setup: enable='1', signal_in='0' stable
   - Stimulus: signal_in transitions 0→1
   - Expected: edge_detected='1' for exactly 1 cycle on cycle after transition
   - Duration: 10 cycles
   - Pattern: Apply multiple rising edges, verify each detected

3. **test_falling_edge** - Verify falling edge detection (EDGE_TYPE="FALLING")
   - Setup: enable='1', signal_in='1' stable
   - Stimulus: signal_in transitions 1→0
   - Expected: edge_detected='1' for exactly 1 cycle on cycle after transition
   - Duration: 10 cycles
   - Pattern: Apply multiple falling edges, verify each detected

4. **test_enable_control** - Verify enable control
   - Setup: signal_in toggling with edges
   - Stimulus: Toggle enable='0'/'1' around edge events
   - Expected:
     - enable='0': edge_detected='0' (edges ignored)
     - enable='1': edge_detected='1' on edges
   - Duration: 15 cycles

**Test Values:**

**P1 (Fast):**
- EDGE_TYPE generic: Test with "RISING", "FALLING", "BOTH" in separate test runs
- signal_in patterns: Simple toggles (0→1→0→1)
- Edge spacing: 3-4 cycles apart (easily observable)
- Expected outputs: Exact cycle-by-cycle edge_detected values

**P2 (Realistic):**
- Rapid edge sequences (back-to-back transitions)
- Enable toggling during edge detection
- Randomized edge timing
- Stress test: 100+ edges with comprehensive checking

---

## Design Notes

**Architecture:** Registered comparison (combinational + sequential)

**Approach:**
1. **Sequential logic (clocked process):**
   - Register previous signal value: `signal_in_prev <= signal_in`
   - Update on rising edge of clk when enable='1'
   - Reset clears signal_in_prev to '0'

2. **Combinational logic:**
   - Rising edge detection: `rising_edge_comb = (signal_in='1') AND (signal_in_prev='0')`
   - Falling edge detection: `falling_edge_comb = (signal_in='0') AND (signal_in_prev='1')`
   - Mode selection: Use EDGE_TYPE generic to select output:
     - "RISING" → edge_detected = rising_edge_comb
     - "FALLING" → edge_detected = falling_edge_comb
     - "BOTH" → edge_detected = rising_edge_comb OR falling_edge_comb

3. **Enable control:**
   - When enable='0': force edge_detected='0' (gate the output)
   - When enable='0': optionally pause signal_in_prev updates (design choice)

**Dependencies:**
- Package: ieee.std_logic_1164.all

**Constraints:**
- Timing: 1-cycle latency inherent to registered comparison
- Metastability: Input signal_in should be synchronized if from async domain
- Glitch immunity: Single-cycle glitches may not be detected (synchronous design)

**Key Design Considerations:**
- **Why registered comparison?** Simplest, most reliable edge detection pattern in VHDL
- **Why string generic?** VHDL-2008 allows string generics, cleaner than integer encoding
- **Why 1-cycle pulse?** Standard for trigger/event applications (vs. level output)
- **Alternative architectures:**
  - XOR-based: `edge = signal_in XOR signal_in_prev` (detects both edges always)
  - Rising_edge() function: Not suitable (only for clock signals per VHDL standard)

---

## Agent Instructions

**Agent 1 (forge-vhdl-component-generator):**
- Generate entity + architecture for forge_util_edge_detector
- Use registered comparison pattern (1 internal signal: signal_in_prev)
- Implement mode selection via EDGE_TYPE generic with if-generate or conditional assignment
- Follow port order: clk, rst_n, enable, signal_in, edge_detected
- Include header comment with component purpose and usage example
- Output to: `workflow/artifacts/vhdl/forge_util_edge_detector.vhd`

**Agent 2 (cocotb-progressive-test-designer):**
- Design P1 test architecture (4 tests as specified above)
- Create test strategy with concrete signal patterns and expected outputs
- Design for <20 line total output (GHDL filter applied)
- Specify test wrapper if needed (unlikely - simple std_logic ports)
- Output test strategy to: `workflow/artifacts/tests/forge_util_edge_detector_test_strategy.md`

**Agent 3 (cocotb-progressive-test-runner):**
- Implement P1 tests from strategy
- Use CocoTB + GHDL with filter (GHDL_FILTER_LEVEL=aggressive)
- Run tests and verify <20 line output
- Test all three EDGE_TYPE modes: "RISING", "FALLING", "BOTH"
- Output to: `workflow/artifacts/tests/forge_util_edge_detector_tests/`
- Generate test execution report

---

## Expected Output Example

**Example: RISING edge detection (EDGE_TYPE="RISING")**

```
Cycle | signal_in | signal_in_prev | edge_detected | notes
------|-----------|----------------|---------------|------------------
0     | 0         | 0              | 0             | reset complete
1     | 0         | 0              | 0             | stable low
2     | 1         | 0              | 1             | rising edge! (0→1)
3     | 1         | 1              | 0             | stable high
4     | 1         | 1              | 0             | stable high
5     | 0         | 1              | 0             | falling (ignored in RISING mode)
6     | 0         | 0              | 0             | stable low
7     | 1         | 0              | 1             | rising edge! (0→1)
```

**Example: BOTH edge detection (EDGE_TYPE="BOTH")**

```
Cycle | signal_in | signal_in_prev | edge_detected | notes
------|-----------|----------------|---------------|------------------
0     | 0         | 0              | 0             | reset complete
1     | 0         | 0              | 0             | stable low
2     | 1         | 0              | 1             | rising edge! (0→1)
3     | 1         | 1              | 0             | stable high
4     | 0         | 1              | 1             | falling edge! (1→0)
5     | 0         | 0              | 0             | stable low
6     | 1         | 0              | 1             | rising edge! (0→1)
```

**Use Cases:**
- **Trigger generation:** Convert level signals to single-cycle trigger pulses for FSMs
- **Event counting:** Count button presses, encoder ticks, communication frame starts
- **Synchronization:** Detect async signal transitions for clock domain crossing preparation
- **Protocol decoding:** Detect start/stop bits, frame boundaries in serial communication

---

## References

**Related Components:**
- forge_util_synchronizer (CDC metastability mitigation - use before edge detector on async signals)
- forge_util_debouncer (mechanical switch debouncing - use before edge detector on button inputs)
- forge_hierarchical_encoder (can use edge_detected output for FSM state change detection)

**Standards:**
- VHDL Coding: `docs/VHDL_CODING_STANDARDS.md`
- Testing: `docs/PROGRESSIVE_TESTING_GUIDE.md`
- Pattern source: `workflow/specs/reference/edge_detector.md`

---

**Specification Version:** 1.0.0
**Created:** 2025-11-09
**Workflow:** AI-First requirements (pattern: edge_detector.md)
