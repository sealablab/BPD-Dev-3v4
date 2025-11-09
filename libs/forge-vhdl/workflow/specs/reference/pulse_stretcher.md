# Component: Pulse Stretcher

**Category:** utilities
**Purpose:** Stretch short pulses to guaranteed minimum width for clock domain crossing or visual indication

---

## Requirements

### Functionality
- Detect input pulses of any width (≥1 clock cycle)
- Stretch output pulse to configurable minimum width
- Multiple input pulses during stretch period extend the output
- Configurable stretch time in clock cycles or milliseconds
- Useful for CDC (slow→fast clock crossing) and LED visual feedback

### Interface

**Entity:** forge_util_pulse_stretcher

**Generics:**
- `CLK_FREQ_HZ : positive := 125_000_000` - Clock frequency in Hz (for time-based mode)
- `STRETCH_CYCLES : positive := 100` - Minimum output pulse width in clock cycles
- `USE_TIME_MODE : boolean := false` - If true, use STRETCH_TIME_MS instead
- `STRETCH_TIME_MS : positive := 100` - Minimum output pulse width in ms (if USE_TIME_MODE=true)

**Ports:**
```vhdl
-- Clock & Reset
clk         : in std_logic;
rst_n       : in std_logic;

-- Control
enable      : in std_logic;

-- Input pulse (can be 1+ cycles wide)
pulse_in    : in std_logic;

-- Stretched output pulse
pulse_out   : out std_logic
```

### Behavior
- **Reset:** `pulse_out = '0'`, counter cleared
- **Disabled (enable='0'):** `pulse_out = '0'`, counter cleared
- **Enabled (enable='1'):**
  - When `pulse_in` goes high, start counter and set `pulse_out = '1'`
  - Count down from stretch duration
  - If `pulse_in` goes high again during countdown, restart counter (extend pulse)
  - When counter reaches 0, set `pulse_out = '0'`
- **Stretch duration calculation:**
  - If `USE_TIME_MODE = false`: duration = STRETCH_CYCLES
  - If `USE_TIME_MODE = true`: duration = CLK_FREQ_HZ * STRETCH_TIME_MS / 1000

---

## Testing Requirements

**Test Level:** P1 (5 essential tests)

**Required Tests:**
1. test_reset - Verify pulse_out = 0 after reset
2. test_single_pulse - Single input pulse stretched to minimum width
3. test_pulse_extension - Multiple input pulses extend output pulse
4. test_minimum_width - Verify exact stretch duration
5. test_enable_control - Verify enable starts/stops stretching

**Test Values:**

**P1 (Fast - cycle mode):**
- `USE_TIME_MODE = false`
- `STRETCH_CYCLES = 10` (short for fast testing)
- Test patterns:
  - Single 1-cycle pulse → 10-cycle output
  - Two pulses 5 cycles apart → extended output (15 cycles total)
  - Rapid pulses (every 3 cycles) → continuous output

**P2 (Realistic - time mode):**
- `USE_TIME_MODE = true`
- `CLK_FREQ_HZ = 125_000_000`
- `STRETCH_TIME_MS = 100` (100ms typical for LED)
- Test various pulse patterns with realistic timing

---

## Design Notes

**Architecture:** Retriggerable down-counter

**Approach:**
1. Detect rising edge of `pulse_in` (use edge detector pattern)
2. On rising edge OR while counting, load counter with stretch duration
3. Count down each cycle while counter > 0
4. `pulse_out = '1'` when counter > 0, else '0'

**State Variables:**
- `pulse_in_reg : std_logic` - Registered input for edge detection
- `counter : unsigned(N downto 0)` - Stretch counter (N = ceil(log2(max_stretch_cycles)))
- `stretching : std_logic` - High when counter > 0

**Dependencies:**
- Package: `ieee.numeric_std.all` (for unsigned counter)

**Constraints:**
- Counter width must accommodate max stretch duration
- For time mode: max 24-bit counter (16.7M cycles = 134ms at 125MHz)
- Input pulse must be at least 1 clock cycle wide (should be synchronized)

**Key Design Considerations:**
- Retriggerable: New input pulse restarts counter (extends output)
- Output is continuous if input pulses arrive faster than stretch period
- Cycle mode vs. time mode: Cycle mode is simpler, time mode is more intuitive for users

---

## Agent Instructions

**Agent 1 (VHDL Generator):**
- Generate entity + architecture with generics for both cycle and time modes
- Calculate counter width dynamically based on USE_TIME_MODE
- Implement retriggerable down-counter with edge detection
- Follow port order: clk, rst_n, enable, pulse_in, pulse_out
- Add comments explaining retriggerable behavior
- Output to: `workflow/artifacts/vhdl/forge_util_pulse_stretcher.vhd`

**Agent 2 (Test Designer):**
- Design P1 test architecture (5 tests)
- Use FAST generics: USE_TIME_MODE=false, STRETCH_CYCLES=10
- Create pulse patterns: single, double, rapid
- Verify exact stretch timing and retriggering
- Output test strategy to: `workflow/artifacts/tests/pulse_stretcher_test_strategy.md`

**Agent 3 (Test Runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL with fast generics
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_pulse_stretcher_tests/`

---

## Expected Output Example

For STRETCH_CYCLES=10, input pattern: pulse at cycle 5, pulse at cycle 12

```
Cycle 0-4:  pulse_in=0, counter=0, pulse_out=0
Cycle 5:    pulse_in=1, counter=10, pulse_out=1 (first pulse detected)
Cycle 6:    pulse_in=0, counter=9, pulse_out=1 (counting down)
Cycle 7-11: pulse_in=0, counter=8,7,6,5,4, pulse_out=1
Cycle 12:   pulse_in=1, counter=10, pulse_out=1 (retriggered! reset to 10)
Cycle 13:   pulse_in=0, counter=9, pulse_out=1
Cycle 14-21: pulse_in=0, counter=8..1, pulse_out=1
Cycle 22:   pulse_in=0, counter=0, pulse_out=0 (stretch complete)
```

**Total output width:** 17 cycles (5→22) instead of separate 10-cycle pulses

---

## Use Cases

**Primary Use Cases:**

**1. Clock Domain Crossing (Slow→Fast):**
```
Slow clock pulse (1 cycle @ 1MHz)
  → Pulse stretcher (stretch to 100 cycles)
  → Fast clock (125MHz can reliably capture)
```

**2. LED Visual Feedback:**
```
Short event pulse (1 cycle)
  → Pulse stretcher (stretch to 100ms)
  → LED (visible to human eye)
```

**3. Trigger Holdoff:**
```
Trigger event → Pulse stretcher → Busy signal (prevents re-triggering)
```

**Typical Integration:**
```vhdl
-- Example: LED blinker for error events
error_led_driver : entity work.forge_util_pulse_stretcher
    generic map (
        CLK_FREQ_HZ => 125_000_000,
        USE_TIME_MODE => true,
        STRETCH_TIME_MS => 200  -- 200ms visible blink
    )
    port map (
        clk => clk,
        rst_n => rst_n,
        enable => '1',
        pulse_in => error_pulse,  -- 1-cycle error event
        pulse_out => led_out      -- 200ms LED pulse
    );
```

---

## Design Alternatives Considered

**Alternative 1: Non-retriggerable (one-shot)**
- Pros: Simpler, guaranteed output width
- Cons: Ignores input pulses during stretch (can miss events)
- Decision: Retriggerable chosen for flexibility

**Alternative 2: Pulse counter (output after N pulses)**
- Pros: Noise filtering
- Cons: Different use case (frequency detection vs. stretching)
- Decision: Out of scope (different component: pulse_counter)

---

## References

**Common Applications:**
- Xilinx XAPP1097 - "Clock Domain Crossing Techniques"
- ARM AMBA AXI Protocol - "Pulse synchronization"
- Visual feedback design guidelines (100-500ms for user-visible events)

**Related Components:**
- `forge_util_edge_detector` - Detect edges before stretching
- `forge_util_synchronizer` - Synchronize before pulse stretching
