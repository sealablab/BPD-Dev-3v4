# Component: Majority Voter

**Category:** utilities
**Purpose:** 3-input majority logic voter for fault-tolerant digital systems

---

## Requirements

### Functionality
- Accept 3 digital input signals (A, B, C)
- Output logic high when 2 or more inputs are high
- Output logic low when less than 2 inputs are high
- Optional registered output for pipeline stages
- Synchronous operation within clock domain

### Interface

**Entity:** forge_util_majority_voter

**Generics:**
- `REGISTERED : boolean := false` - Register output for pipeline stages (default: combinational)

**Ports:**
```vhdl
-- Clock & Reset (only used if REGISTERED=true)
clk         : in std_logic;
rst_n       : in std_logic;

-- Control (only used if REGISTERED=true)
enable      : in std_logic;

-- Data inputs
input_a     : in std_logic;
input_b     : in std_logic;
input_c     : in std_logic;

-- Output
majority_out : out std_logic
```

### Behavior
- **Combinational mode (REGISTERED=false):**
  - Output responds immediately to input changes
  - majority_out = (A AND B) OR (A AND C) OR (B AND C)
  - Clock, reset, enable ports ignored

- **Registered mode (REGISTERED=true):**
  - **Reset:** majority_out = '0'
  - **Disabled (enable='0'):** majority_out holds previous value
  - **Enabled (enable='1'):** majority_out = majority logic on rising_edge(clk)

- **Truth table:**
  ```
  A B C | Output
  ------+-------
  0 0 0 |   0
  0 0 1 |   0
  0 1 0 |   0
  0 1 1 |   1
  1 0 0 |   0
  1 0 1 |   1
  1 1 0 |   1
  1 1 1 |   1
  ```

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**
1. test_all_combinations - Verify all 8 input combinations in combinational mode
2. test_registered_mode - Verify registered mode operation with clock
3. test_reset - Verify reset clears output in registered mode
4. test_enable_control - Verify enable holds output in registered mode

**Test Values:**

**P1 (Fast):**
- Test all 8 combinations: 000, 001, 010, 011, 100, 101, 110, 111
- Expected outputs:           0,   0,   0,   1,   0,   1,   1,   1
- Test cycles: 15 cycles (8 for combinational, 7 for registered mode)
- REGISTERED configurations: false (combinational), true (registered)

**P2 (Realistic):**
- Random input sequences (100 combinations)
- Toggle enable in registered mode
- Multiple reset events
- Test cycles: 200 cycles
- Verify no glitches in registered mode

---

## Design Notes

**Architecture:** Combinational majority logic with optional output register

**Approach:**
1. **Combinational logic:** majority = (A AND B) OR (A AND C) OR (B AND C)
2. **Registered mode:** Add output flip-flop with enable control
3. **Generic selection:** Use `if REGISTERED generate` for conditional architecture

**Dependencies:**
- Package: `ieee.std_logic_1164.all`

**Constraints:**
- Combinational delay: ~2 LUT delays (AND-OR structure)
- Registered latency: 1 clock cycle
- Resource usage: ~2 LUTs (combinational), +1 FF (registered)

**Key Design Considerations:**
- Use standard SOP (sum-of-products) for majority logic
- Generate statement for optional register avoids unused logic
- Reset should only affect output register, not combinational logic
- Enable only meaningful in registered mode

---

## Agent Instructions

**Agent 1 (VHDL Generator):**
- Generate entity + architecture with REGISTERED generic
- Use sum-of-products for majority logic: (A∧B)∨(A∧C)∨(B∧C)
- Use `if REGISTERED generate` for optional output register
- Follow port order: clk, rst_n, enable, input_a, input_b, input_c, majority_out
- Output to: `workflow/artifacts/vhdl/forge_util_majority_voter.vhd`

**Agent 2 (Test Designer):**
- Design P1 test architecture (4 tests)
- Create test vector for all 8 input combinations
- Verify both REGISTERED=false and REGISTERED=true configurations
- Output test strategy to: `workflow/artifacts/tests/majority_voter_test_strategy.md`

**Agent 3 (Test Runner):**
- Implement P1 tests from strategy
- Test both combinational and registered modes
- Run via CocoTB + GHDL
- Verify <15 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_majority_voter_tests/`

---

## Expected Output Example

For input sequence in combinational mode:

```
Inputs (A,B,C) → Output
    (0,0,0)    →   0
    (0,0,1)    →   0
    (0,1,0)    →   0
    (0,1,1)    →   1  (2 inputs high)
    (1,0,0)    →   0
    (1,0,1)    →   1  (2 inputs high)
    (1,1,0)    →   1  (2 inputs high)
    (1,1,1)    →   1  (3 inputs high)
```

For registered mode (REGISTERED=true):

```
Cycle 0: rst_n=0, output=0 (reset)
Cycle 1: A=0,B=0,C=0, enable=1, output=0
Cycle 2: A=0,B=1,C=1, enable=1, output=0 (previous cycle was 0)
Cycle 3: A=0,B=1,C=1, enable=1, output=1 (2 inputs high registered)
Cycle 4: A=1,B=1,C=1, enable=0, output=1 (enable=0, holds value)
Cycle 5: A=0,B=0,C=0, enable=0, output=1 (still holding)
```

**Use Cases:**
- Triple modular redundancy (TMR) voting
- Fault-tolerant sensor inputs
- Glitch-resistant button debouncing (3 parallel debouncers)
- Error correction in digital communication
- Reliability enhancement in safety-critical systems
