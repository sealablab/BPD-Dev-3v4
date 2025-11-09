# Component: Binary Counter

**Category:** utilities
**Purpose:** Simple binary counter with configurable width, rollover detection, and maximum value flag

---

## Requirements

### Functionality
- Count upward from 0 to maximum value (2^COUNTER_WIDTH - 1)
- Automatic rollover to 0 when reaching maximum
- Single-cycle pulse output on rollover event
- Status flag indicating when counter is at maximum value
- Enable control for starting/stopping count
- Synchronous operation with reset

### Interface

**Entity:** forge_util_counter

**Generics:**
- `COUNTER_WIDTH : positive := 8` - Bit width of counter (determines maximum value)

**Ports:**
```vhdl
-- Clock & Reset
clk          : in std_logic;
rst_n        : in std_logic;

-- Control
enable       : in std_logic;

-- Outputs
count_out    : out unsigned(COUNTER_WIDTH-1 downto 0);
rollover     : out std_logic;
max_reached  : out std_logic
```

### Behavior
- **Reset:** `count_out = 0`, `rollover = '0'`, `max_reached = '0'`
- **Disabled (enable='0'):** Counter holds current value, all outputs maintain state
- **Enabled (enable='1'):** Counter increments by 1 each clock cycle
  - When count < max: `count_out` increments, `max_reached = '0'`, `rollover = '0'`
  - When count = max: `max_reached = '1'`, `rollover = '0'`
  - On max → 0 transition: `rollover = '1'` for exactly 1 cycle, then `rollover = '0'`
- **Maximum value:** `2^COUNTER_WIDTH - 1` (e.g., 255 for 8-bit counter)
- **Rollover behavior:** Wraps from maximum to 0 automatically

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**
1. **test_reset** - Verify all outputs = 0 after reset
   - Setup: Apply rst_n='0'
   - Expected: count_out=0, rollover='0', max_reached='0'
   - Duration: 5 cycles

2. **test_basic_count** - Verify counter increments correctly
   - Setup: Reset, then enable='1'
   - Stimulus: Run for 10 cycles
   - Expected: count_out = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
   - Expected: rollover='0', max_reached='0' throughout
   - Duration: 12 cycles

3. **test_rollover** - Verify rollover from max to 0
   - Setup: Use COUNTER_WIDTH=4 (max=15)
   - Stimulus: Count from 0 to 16+ cycles
   - Expected at cycle 15: count_out=15, max_reached='1', rollover='0'
   - Expected at cycle 16: count_out=0, max_reached='0', rollover='1' (1-cycle pulse)
   - Expected at cycle 17: count_out=1, rollover='0'
   - Duration: 20 cycles

4. **test_enable** - Verify enable control starts/stops counting
   - Setup: Reset, enable='1' for 5 cycles
   - Stimulus: Set enable='0' for 5 cycles, then enable='1' again
   - Expected: Counter increments to 5, holds at 5 for 5 cycles, then resumes (6, 7, 8...)
   - Duration: 20 cycles

**Test Values:**

**P1 (Fast):**
- COUNTER_WIDTH = 4 (max count = 15, rollover in 16 cycles)
- Test cycles: 20-25 cycles per test
- Enable patterns: Continuous, hold, resume

**P2 (Realistic):**
- COUNTER_WIDTH = [8, 16] (8-bit and 16-bit counters)
- Test cycles: 300+ cycles (to verify extended counting)
- Edge cases: Enable toggling at rollover boundary
- Stress test: Rapid enable toggling

---

## Design Notes

**Architecture:** Counter-based with unsigned arithmetic

**Approach:**
1. Use `unsigned` counter register of width `COUNTER_WIDTH`
2. Combinational max detection: `max_reached = '1' when count_out = (2^COUNTER_WIDTH - 1)`
3. Registered rollover detection: Compare current count vs previous count (max → 0 transition)
4. Increment logic: `count_next = count_out + 1` (wraps automatically due to unsigned overflow)
5. Enable hierarchy: `rst_n` > `enable`

**Dependencies:**
- Package: `ieee.numeric_std.all` (unsigned type and arithmetic)

**Constraints:**
- Minimum counter width: 1 bit (max value = 1)
- Maximum counter width: Limited by synthesis tool (typically 32-64 bits practical)
- Rollover pulse: Exactly 1 clock cycle wide
- Latency: 1 cycle (registered outputs)

**Key Design Considerations:**
- Use `unsigned` type for natural arithmetic wrapping behavior
- `max_reached` is combinational for immediate status
- `rollover` is registered to provide clean 1-cycle pulse
- Counter increments even when at maximum (automatic wrap)
- No explicit overflow handling needed (unsigned wraps naturally)

---

## Agent Instructions

**Agent 1 (forge-vhdl-component-generator):**
- Generate entity + architecture with COUNTER_WIDTH generic
- Use `unsigned` type for count_out and internal counter
- Implement combinational max detection and registered rollover pulse
- Follow port order: clk, rst_n, enable, count_out, rollover, max_reached
- Output to: `workflow/artifacts/vhdl/forge_util_counter.vhd`

**Agent 2 (cocotb-progressive-test-designer):**
- Design P1 test architecture (4 tests)
- Use COUNTER_WIDTH=4 for fast rollover testing
- Create test wrappers with enable control sequences
- Design constants file with test parameters
- Output test strategy to: `workflow/artifacts/tests/counter_test_strategy.md`

**Agent 3 (cocotb-progressive-test-runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL
- Verify <20 line output (GHDL filter applied)
- Verify rollover pulse is exactly 1 cycle wide
- Output to: `workflow/artifacts/tests/forge_util_counter_tests/`

---

## Expected Output Example

For COUNTER_WIDTH=4 (max=15), enable='1':

```
Cycle | count_out | max_reached | rollover | Notes
------|-----------|-------------|----------|-------------------
0     | 0         | 0           | 0        | After reset
1     | 1         | 0           | 0        | Counting
2     | 2         | 0           | 0        | Counting
...   | ...       | ...         | ...      | ...
14    | 14        | 0           | 0        | Approaching max
15    | 15        | 1           | 0        | At maximum
16    | 0         | 0           | 1        | Rollover! (1-cycle pulse)
17    | 1         | 0           | 0        | Normal counting resumes
18    | 2         | 0           | 0        | Counting
```

**Use Cases:**
- Event counting (button presses, pulses, transactions)
- Clock divider building block
- Timebase generation (combine with comparator)
- Sequence control (address generation, state indexing)
- Debug counters (error count, transaction count)

---

## References

**Related Components:**
- `forge_util_clk_divider` - Uses counter with configurable divisor
- `forge_util_pwm` (reference pattern) - Counter-based PWM generator

**Standards:**
- VHDL Coding: `docs/VHDL_CODING_STANDARDS.md`
- Testing: `docs/PROGRESSIVE_TESTING_GUIDE.md`
- Pattern source: `workflow/specs/reference/pwm_generator.md` (counter-based pattern)
