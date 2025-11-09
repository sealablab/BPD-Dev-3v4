# Component: PWM Generator

**Category:** utilities
**Purpose:** Generate PWM signal with configurable frequency and duty cycle

---

## Requirements

### Functionality
- Generate PWM output at configurable frequency (1Hz - 10MHz on 125MHz clock)
- 8-bit duty cycle resolution (0-255 → 0-100%)
- Enable/disable control
- Active-high PWM output

### Interface

**Entity:** forge_util_pwm

**Ports:**
```vhdl
-- Clock & Reset
clk          : in std_logic;
rst_n        : in std_logic;

-- Control
enable       : in std_logic;

-- Configuration
frequency_div: in unsigned(23 downto 0);  -- Clock divider for frequency
duty_cycle   : in unsigned(7 downto 0);   -- 0-255 (0-100%)

-- Output
pwm_out      : out std_logic
```

### Behavior
- **Reset:** `pwm_out = '0'`, counters cleared
- **Disabled (enable='0'):** `pwm_out = '0'`, counters hold
- **Enabled (enable='1'):** Generate PWM at configured frequency/duty
- **Frequency:** `f_pwm = 125MHz / frequency_div`
- **Duty cycle:** High time = `(duty_cycle / 255) * period`

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**
1. test_reset - Verify pwm_out=0 after reset
2. test_basic_pwm - Verify PWM toggles with 50% duty (duty_cycle=127)
3. test_duty_cycle - Verify different duty cycles (25%, 75%, 100%)
4. test_enable_control - Verify enable starts/stops PWM

**Test Values:**

**P1 (Fast):**
- `frequency_div = 125` (1MHz PWM on 125MHz clock)
- `duty_cycle = [0, 64, 127, 191, 255]` (0%, 25%, 50%, 75%, 100%)

**P2 (Realistic):**
- `frequency_div = [125, 1250, 12500]` (1MHz, 100kHz, 10kHz)
- `duty_cycle = [0, 32, 64, 96, 127, 159, 191, 223, 255]` (every 12.5%)

---

## Design Notes

**Architecture:** Counter-based PWM generation

**Approach:**
1. Use counter clocked by `clk`
2. Counter resets at `frequency_div` (defines period)
3. Compare counter against `duty_cycle * (frequency_div/255)` for output
4. `pwm_out = '1' when counter < duty_threshold, else '0'`

**Dependencies:**
- Package: `ieee.numeric_std.all` (for unsigned)

**Constraints:**
- Frequency range: 1Hz - 10MHz (on 125MHz clock)
- Duty cycle quantization: ~0.4% per step (8-bit)
- Minimum pulse width: 1 clock cycle (8ns at 125MHz)

---

## Agent Instructions

**Agent 1 (VHDL Generator):**
- Generate entity + architecture for counter-based PWM
- Use `unsigned` for counters and arithmetic
- Follow port order: clk, rst_n, enable, frequency_div, duty_cycle, pwm_out
- Output to: `workflow/artifacts/vhdl/forge_util_pwm.vhd`

**Agent 2 (Test Designer):**
- Design P1 test architecture (4 tests)
- Calculate expected duty cycles for verification
- Use small `frequency_div` values for fast tests
- Output test strategy to: `workflow/artifacts/tests/pwm_test_strategy.md`

**Agent 3 (Test Runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_pwm_tests/`

---

## Expected Output Example

For `frequency_div=100`, `duty_cycle=50` (19.6% duty):

```
Period: 100 cycles
High time: 19-20 cycles
Low time: 80-81 cycles
PWM frequency: 1.25MHz (at 125MHz clock)
```
