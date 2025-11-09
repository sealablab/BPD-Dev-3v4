# Component: forge_util_pwm_generator

**Category:** utilities
**Purpose:** Generate PWM signal for LED dimming with configurable frequency and duty cycle

---

## Requirements

### Functionality
- Generate pulse-width modulated (PWM) output signal for LED brightness control
- Counter-based architecture with free-running counter
- Configurable PWM frequency via generic (default 1 kHz for flicker-free operation)
- Configurable duty cycle percentage via generic (0-100%)
- Active-high PWM output (pwm_out='1' = LED on)
- Enable control for starting/stopping PWM generation
- Clean reset to known state (counter=0, output=0)

### Interface

**Entity:** forge_util_pwm_generator

**Generics:**
- CLK_FREQ_HZ : positive := 125_000_000 -- System clock frequency (Moku standard: 125 MHz)
- PWM_FREQ_HZ : positive := 1000 -- PWM output frequency (1 kHz default, range 100 Hz - 1 kHz typical)
- DUTY_CYCLE_PERCENT : natural range 0 to 100 := 50 -- Duty cycle percentage (50% = half brightness)

**Ports:**
```vhdl
-- Clock & Reset
clk         : in  std_logic;  -- System clock
rst_n       : in  std_logic;  -- Active-low asynchronous reset

-- Control
enable      : in  std_logic;  -- PWM generator enable (1=active, 0=disabled)

-- Output
pwm_out     : out std_logic;  -- PWM output signal to LED (active-high)
```

### Behavior

**Reset (rst_n='0'):**
- Counter reset to 0
- pwm_out = '0' (LED off)

**Disabled (enable='0'):**
- Counter holds current value (no increment)
- pwm_out = '0' (LED off)
- Resumes from held value when re-enabled

**Enabled (enable='1'):**
- Counter increments every clock cycle: 0, 1, 2, ..., period-1, 0, 1, ...
- Period calculation: `period = CLK_FREQ_HZ / PWM_FREQ_HZ`
- Duty threshold calculation: `duty_threshold = (period * DUTY_CYCLE_PERCENT) / 100`
- PWM output logic:
  - `pwm_out = '1'` when `counter < duty_threshold`
  - `pwm_out = '0'` when `counter >= duty_threshold`
- Counter wraps to 0 when reaching period value

**Edge Cases:**
- DUTY_CYCLE_PERCENT = 0: pwm_out always '0' (LED always off)
- DUTY_CYCLE_PERCENT = 100: pwm_out always '1' (LED always on, full brightness)
- DUTY_CYCLE_PERCENT = 50: pwm_out toggles at midpoint (half brightness)

**Example (1 kHz PWM at 125 MHz clock):**
- Period = 125,000,000 / 1,000 = 125,000 cycles
- For 50% duty: duty_threshold = (125,000 * 50) / 100 = 62,500
- Counter 0-62,499: pwm_out='1'
- Counter 62,500-124,999: pwm_out='0'
- Repeat

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Test Strategy:**
- Use fast PWM frequency for simulation (e.g., PWM_FREQ_HZ=125_000 → period=1000 cycles)
- Keep test duration short (<50 cycles per test)
- Verify duty cycle accuracy by counting high/low cycles

**Required Tests:**

1. **test_reset** - Verify clean reset behavior
   - Setup: Apply reset (rst_n='0')
   - Stimulus: Release reset, enable='1'
   - Expected: pwm_out='0' immediately after reset, then starts PWM
   - Duration: 5 cycles

2. **test_50_percent_duty** - Verify 50% duty cycle (half brightness)
   - Setup: DUTY_CYCLE_PERCENT=50, PWM_FREQ_HZ=125_000 (period=1000)
   - Stimulus: Enable PWM (enable='1'), observe 1 complete period
   - Expected: pwm_out='1' for 500 cycles, pwm_out='0' for 500 cycles
   - Duration: 1010 cycles (1 period + margin)

3. **test_0_percent_duty** - Verify 0% duty cycle (LED always off)
   - Setup: DUTY_CYCLE_PERCENT=0, PWM_FREQ_HZ=125_000
   - Stimulus: Enable PWM, observe 1 complete period
   - Expected: pwm_out='0' continuously
   - Duration: 1010 cycles

4. **test_100_percent_duty** - Verify 100% duty cycle (LED full brightness)
   - Setup: DUTY_CYCLE_PERCENT=100, PWM_FREQ_HZ=125_000
   - Stimulus: Enable PWM, observe 1 complete period
   - Expected: pwm_out='1' continuously
   - Duration: 1010 cycles

**Test Values:**

**P1 (Fast simulation):**
- CLK_FREQ_HZ = 125_000_000 (standard)
- PWM_FREQ_HZ = 125_000 (fast test frequency, period=1000 cycles)
- Test durations: <1100 cycles each
- GHDL filter: AGGRESSIVE (target <20 lines output)

**P2 (Realistic validation):**
- CLK_FREQ_HZ = 125_000_000
- PWM_FREQ_HZ = 1000 (production frequency, period=125,000 cycles)
- DUTY_CYCLE_PERCENT: 10, 25, 50, 75, 90, 100
- Additional tests: enable control, mid-period disable/re-enable
- Test durations: 200,000+ cycles each

---

## Design Notes

**Architecture:** Counter-based PWM generator

**Approach:**
1. **Counter implementation:**
   - Use `unsigned` type from `ieee.numeric_std`
   - Counter width must accommodate maximum period value
   - Width calculation: `ceil(log2(CLK_FREQ_HZ / min(PWM_FREQ_HZ)))`
   - For 125 MHz / 100 Hz = 1,250,000 → 21 bits minimum
   - Safe choice: 24 bits (supports down to ~7.5 Hz)

2. **Constant calculations (in architecture):**
   - `period = CLK_FREQ_HZ / PWM_FREQ_HZ` (integer division)
   - `duty_threshold = (period * DUTY_CYCLE_PERCENT) / 100`
   - Both calculated as constants (compile-time, no runtime overhead)

3. **PWM generation logic:**
   - Clocked process: Increment counter on rising_edge(clk)
   - Combinational comparison: `pwm_out <= '1' when counter < duty_threshold else '0'`
   - Counter wrap: `if counter >= period-1 then counter <= 0`

4. **Reset hierarchy:**
   - Primary: `rst_n='0'` → immediate reset (asynchronous)
   - Secondary: `enable='0'` → hold counter, force output low

**Dependencies:**
- Package: `ieee.numeric_std.all` (for unsigned arithmetic)
- Components: none

**Constraints:**
- PWM_FREQ_HZ must be <= CLK_FREQ_HZ (synthesis will fail if violated)
- Minimum practical PWM_FREQ_HZ: ~7.5 Hz (24-bit counter limit)
- Duty cycle resolution: 1% (granularity = period / 100)

**Key Design Considerations:**
- **Counter-based vs. DDS:** Counter approach is simpler, lower resource usage for fixed-frequency PWM
- **Compile-time vs. runtime configuration:** Fixed generics chosen per user requirements (simpler, no dynamic control logic)
- **Active-high output:** Standard for most LED drivers (matches user expectation)
- **Enable behavior:** Hold counter (not reset) to allow pause/resume without phase discontinuity

---

## Agent Instructions

**Agent 1 (forge-vhdl-component-generator):**
- Generate entity `forge_util_pwm_generator` with specified interface
- Architecture: Counter-based with unsigned counter
- Calculate `period` and `duty_threshold` as constants in architecture declarative region
- Use clocked process for counter increment with synchronous enable check
- Use concurrent assignment for PWM output comparison
- Follow port order: clk, rst_n, enable, pwm_out
- Include header comment with component purpose
- Output to: `workflow/artifacts/vhdl/forge_util_pwm_generator.vhd`

**Agent 2 (cocotb-progressive-test-designer):**
- Design P1 test architecture (4 tests as specified above)
- Create test strategy document with:
  - Test values (fast PWM frequency for simulation)
  - Expected waveforms (counter behavior, pwm_out timing)
  - Success criteria (cycle-accurate duty cycle validation)
- No test wrapper needed (entity uses only std_logic types)
- Output test strategy to: `workflow/artifacts/tests/forge_util_pwm_generator_test_strategy.md`

**Agent 3 (cocotb-progressive-test-runner):**
- Implement P1 tests from strategy
- Use CocoTB's clock driver for stimulus
- Implement duty cycle measurement (count high cycles vs total cycles)
- Run via CocoTB + GHDL with AGGRESSIVE filter
- Verify <20 line output (P1 requirement)
- Output to: `workflow/artifacts/tests/forge_util_pwm_generator_tests/`
- Execution report: `workflow/artifacts/tests/forge_util_pwm_generator_test_execution_report.md`

---

## Expected Output Example

**Scenario: 50% duty cycle, period=10 cycles (for illustration)**

```
Cycle | enable | counter | duty_threshold | period | pwm_out | notes
------|--------|---------|----------------|--------|---------|------------------
0     | 0      | 0       | 5              | 10     | 0       | reset complete
1     | 1      | 0       | 5              | 10     | 1       | enabled, 0<5
2     | 1      | 1       | 5              | 10     | 1       | 1<5
3     | 1      | 2       | 5              | 10     | 1       | 2<5
4     | 1      | 3       | 5              | 10     | 1       | 3<5
5     | 1      | 4       | 5              | 10     | 1       | 4<5
6     | 1      | 5       | 5              | 10     | 0       | 5>=5 (threshold)
7     | 1      | 6       | 5              | 10     | 0       | 6>=5
8     | 1      | 7       | 5              | 10     | 0       | 7>=5
9     | 1      | 8       | 5              | 10     | 0       | 8>=5
10    | 1      | 9       | 5              | 10     | 0       | 9>=5
11    | 1      | 0       | 5              | 10     | 1       | wrap to 0, 0<5
```

**Use Cases:**
- LED dimming control (0-100% brightness via DUTY_CYCLE_PERCENT generic)
- Status indicator PWM (differentiate states by brightness)
- Simple analog output approximation (low-pass filtered PWM)
- Integration example:
  ```vhdl
  -- Instantiate 25% brightness PWM for status LED
  status_pwm : entity work.forge_util_pwm_generator
    generic map (
      CLK_FREQ_HZ        => 125_000_000,
      PWM_FREQ_HZ        => 1000,  -- 1 kHz (flicker-free)
      DUTY_CYCLE_PERCENT => 25     -- 25% brightness
    )
    port map (
      clk     => system_clk,
      rst_n   => system_rst_n,
      enable  => status_active,
      pwm_out => status_led
    );
  ```

---

## References

**Related Components:**
- `forge_util_clk_divider` - Similar counter-based pattern
- PWM reference pattern (future reference spec)

**Standards:**
- VHDL Coding: `docs/VHDL_CODING_STANDARDS.md`
- Testing: `docs/PROGRESSIVE_TESTING_GUIDE.md`
- Pattern source: Counter-based utility pattern (adapted from pwm_generator.md reference)

**Generated via:** AI-First Requirements Workflow (2-question specification)
**Date:** 2025-11-09
**Version:** 1.0.0
