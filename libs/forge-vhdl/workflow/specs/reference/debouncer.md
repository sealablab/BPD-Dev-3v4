# Component: Button Debouncer

**Category:** utilities
**Purpose:** Debounce mechanical button/switch inputs with configurable timing

---

## Requirements

### Functionality
- Remove mechanical bounce from button presses
- Configurable debounce time (default: 20ms typical for mechanical switches)
- Synchronous operation (no asynchronous inputs)
- Produces clean, single-transition output
- Optional output modes: level, rising edge pulse, falling edge pulse

### Interface

**Entity:** forge_util_debouncer

**Generics:**
- `CLK_FREQ_HZ : positive := 125_000_000` - Clock frequency in Hz
- `DEBOUNCE_TIME_MS : positive := 20` - Debounce time in milliseconds
- `OUTPUT_MODE : string := "level"` - Output mode: "level", "rising_pulse", "falling_pulse"

**Ports:**
```vhdl
-- Clock & Reset
clk          : in std_logic;
rst_n        : in std_logic;

-- Input (from button/switch, already synchronized)
button_in    : in std_logic;

-- Debounced Output
button_out   : out std_logic
```

### Behavior
- **Reset:** `button_out = '0'`, counter cleared
- **Debouncing algorithm:**
  1. When `button_in` changes, start counter
  2. If `button_in` remains stable for DEBOUNCE_TIME_MS, update `button_out`
  3. If `button_in` changes during debounce period, restart counter
- **Output modes:**
  - `"level"`: `button_out` tracks debounced button state
  - `"rising_pulse"`: Single-cycle pulse on rising edge of debounced signal
  - `"falling_pulse"`: Single-cycle pulse on falling edge of debounced signal
- **Debounce time calculation:** `debounce_cycles = CLK_FREQ_HZ * DEBOUNCE_TIME_MS / 1000`

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**
1. test_reset - Verify button_out = 0 after reset
2. test_stable_press - Verify clean button press (no bounces in input)
3. test_bouncy_press - Verify debouncing of rapid transitions
4. test_debounce_timing - Verify DEBOUNCE_TIME_MS enforcement

**Test Values:**

**P1 (Fast - use accelerated timing):**
- `CLK_FREQ_HZ = 1_000_000` (1MHz for fast simulation)
- `DEBOUNCE_TIME_MS = 1` (1ms → 1000 cycles at 1MHz)
- Test patterns:
  - Stable press: 0→1 (hold >1ms) → detect
  - Bouncy press: 0→1→0→1→0→1 (each <0.5ms) → ignore bounces
  - Short glitch: 0→1 (hold 0.5ms) →0 → ignore

**P2 (Realistic):**
- `CLK_FREQ_HZ = 125_000_000` (125MHz production clock)
- `DEBOUNCE_TIME_MS = 20` (20ms standard debounce)
- Test patterns: Multiple button presses with realistic bounce patterns

---

## Design Notes

**Architecture:** Counter-based stable detection

**Approach:**
1. Counter counts up while `button_in` is stable
2. When counter reaches `debounce_cycles`, update output
3. If `button_in` changes before counter reaches threshold, reset counter
4. Optional edge detector for pulse output modes

**State Variables:**
- `button_in_reg : std_logic` - Registered input for change detection
- `counter : unsigned(N downto 0)` - Debounce counter (N = ceil(log2(debounce_cycles)))
- `button_stable : std_logic` - Stable debounced level

**Dependencies:**
- Package: `ieee.numeric_std.all` (for unsigned counter)

**Constraints:**
- Counter width must accommodate `debounce_cycles`
- For 125MHz, 20ms: `debounce_cycles = 2,500,000` → need 22-bit counter
- Maximum debounce time: Limited by counter width (use 24-bit for flexibility)

**Key Design Considerations:**
- Input should be pre-synchronized (use forge_util_synchronizer if async)
- Counter width auto-calculated from generics
- Output mode generic allows single component for multiple use cases

---

## Agent Instructions

**Agent 1 (VHDL Generator):**
- Generate entity + architecture with generics for CLK_FREQ_HZ, DEBOUNCE_TIME_MS, OUTPUT_MODE
- Calculate counter width dynamically: `ceil(log2(CLK_FREQ_HZ * DEBOUNCE_TIME_MS / 1000))`
- Implement counter-based debounce with optional edge detection
- Follow port order: clk, rst_n, button_in, button_out
- Add comments explaining debounce algorithm
- Output to: `workflow/artifacts/vhdl/forge_util_debouncer.vhd`

**Agent 2 (Test Designer):**
- Design P1 test architecture (4 tests)
- Use FAST generics: CLK_FREQ_HZ=1_000_000, DEBOUNCE_TIME_MS=1 (for simulation speed)
- Create button patterns: stable, bouncy, short glitch
- Verify debounce timing enforcement
- Output test strategy to: `workflow/artifacts/tests/debouncer_test_strategy.md`

**Agent 3 (Test Runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL with fast generics
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_debouncer_tests/`

---

## Expected Output Example

For DEBOUNCE_TIME_MS=1ms, CLK_FREQ_HZ=1MHz (1000 cycles):

**Bouncy button press pattern:**
```
Input:  0 1 0 1 0 1 1 1 1... (stable after cycle 6)
        ↑ ↑ ↑ ↑ ↑ ↑
        Each transition <1ms (bounces)

Counter: 0 1 0 1 0 1 2 3 4 ... 1000
                      ↑ Counting stable '1'

Output (level mode):
Cycle 0-1005: button_out=0
Cycle 1006+:  button_out=1 (stable after 1000 cycles of '1')
```

**Output (rising_pulse mode):**
```
Cycle 1006: button_out=1 (single cycle pulse)
Cycle 1007+: button_out=0
```

---

## Use Cases

**Primary Use Cases:**
- User interface buttons (tactile switches)
- Mechanical switch inputs (toggle, slide, rotary)
- Relay contact debouncing
- Reed switch debouncing

**Typical Integration:**
```vhdl
-- External button → synchronizer → debouncer → application logic
button_sync : entity work.forge_util_synchronizer
    port map (clk => clk, rst_n => rst_n,
              async_in => button_raw, sync_out => button_sync_out);

button_debounce : entity work.forge_util_debouncer
    generic map (CLK_FREQ_HZ => 125_000_000, DEBOUNCE_TIME_MS => 20)
    port map (clk => clk, rst_n => rst_n,
              button_in => button_sync_out, button_out => button_clean);
```

---

## Design Alternatives Considered

**Alternative 1: Shift register majority vote**
- Pros: Simpler logic
- Cons: Fixed timing (hard to configure), less flexible
- Decision: Counter approach chosen for configurable timing

**Alternative 2: Asynchronous input**
- Pros: One less component in chain
- Cons: Metastability risk, violates synchronous design principle
- Decision: Require pre-synchronized input (use synchronizer separately)

---

## References

**Industry Standards:**
- Ganssle, Jack. "A Guide to Debouncing" (2008)
- Xilinx XAPP1174 - "Switch Debounce Macro"

**Debounce Timing Guidelines:**
- Tactile switches: 5-10ms
- Toggle switches: 10-20ms
- Relays: 20-50ms
- Reed switches: 1-5ms
