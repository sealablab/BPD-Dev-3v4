# Component: Two-Stage Synchronizer

**Category:** utilities
**Purpose:** Safely synchronize asynchronous signals across clock domains (metastability mitigation)

---

## Requirements

### Functionality
- Two-stage flip-flop synchronizer (industry standard)
- Synchronize single-bit asynchronous signals to destination clock domain
- Mitigate metastability (reduce MTBF to acceptable levels)
- Optional reset synchronization
- Configurable number of stages (default=2, can extend to 3 for ultra-high reliability)

### Interface

**Entity:** forge_util_synchronizer

**Generics:**
- `NUM_STAGES : positive := 2` - Number of synchronization stages (2-4)
- `RESET_VALUE : std_logic := '0'` - Initial/reset value for synchronized output

**Ports:**
```vhdl
-- Destination Clock & Reset
clk         : in std_logic;   -- Destination clock domain
rst_n       : in std_logic;   -- Active-low reset

-- Asynchronous Input
async_in    : in std_logic;   -- Signal from source clock domain

-- Synchronized Output
sync_out    : out std_logic   -- Synchronized to clk domain
```

### Behavior
- **Reset:** `sync_out = RESET_VALUE`, all internal stages cleared
- **Normal operation:** Asynchronous `async_in` passed through NUM_STAGES flip-flops
  - Stage 0 (metastability absorber): May enter metastable state briefly
  - Stage 1+ (stabilizers): Output stable, metastability resolved
- **Latency:** NUM_STAGES clock cycles from `async_in` change to `sync_out` change
- **Metastability:** First stage absorbs metastability, second stage provides stable output

**Critical Design Rules:**
- NO combinational logic between stages
- NO fanout from first stage (only feeds second stage)
- Synthesis attributes to prevent optimization:
  - `ASYNC_REG = "TRUE"` (Xilinx)
  - `syn_preserve = 1` (Synplify)

---

## Testing Requirements

**Test Level:** P1 (4 essential tests)

**Required Tests:**
1. test_reset - Verify sync_out = RESET_VALUE after reset
2. test_sync_0_to_1 - Verify async 0→1 transition synchronizes correctly
3. test_sync_1_to_0 - Verify async 1→0 transition synchronizes correctly
4. test_latency - Verify NUM_STAGES cycle latency

**Test Values:**

**P1 (Fast):**
- NUM_STAGES = 2 (standard)
- Async transitions: 0→1→0→1 (sparse transitions, >5 cycles apart)
- Test cycles: 30 cycles
- Verify 2-cycle latency

**P2 (Realistic):**
- NUM_STAGES = [2, 3, 4] (test configurability)
- Async transitions: Variable spacing (2-10 cycles)
- Test cycles: 100 cycles
- Verify correct latency for each NUM_STAGES configuration

**P3 (Stress - Metastability Testing):**
- NOT FEASIBLE: True metastability testing requires gate-level simulation
- P3 tests focus on configuration variations and boundary cases

---

## Design Notes

**Architecture:** Shift register of flip-flops

**Approach:**
1. Declare internal signal: `signal sync_stages : std_logic_vector(NUM_STAGES-1 downto 0);`
2. On each clock:
   - `sync_stages(0) <= async_in` (first stage captures async input)
   - `sync_stages(i) <= sync_stages(i-1)` for i=1 to NUM_STAGES-1
   - `sync_out <= sync_stages(NUM_STAGES-1)` (final stage output)
3. Add synthesis attributes to prevent optimization

**Dependencies:**
- Package: `ieee.std_logic_1164.all`

**Constraints:**
- Minimum stages: 2 (industry standard for metastability)
- Recommended stages: 2 for most applications, 3 for critical paths
- Latency: NUM_STAGES clock cycles
- Works for slow-to-fast and fast-to-slow clock crossings

**Synthesis Attributes (CRITICAL):**
```vhdl
-- Xilinx
attribute ASYNC_REG : string;
attribute ASYNC_REG of sync_stages : signal is "TRUE";

-- Synplify/Synopsys
attribute syn_preserve : boolean;
attribute syn_preserve of sync_stages : signal is true;
```

**Common Pitfall:**
- ❌ NEVER add combinational logic between stages
- ❌ NEVER fan out from first stage to multiple destinations
- ❌ NEVER use for multi-bit buses (use handshake or gray code instead)

---

## Agent Instructions

**Agent 1 (VHDL Generator):**
- Generate entity + architecture with NUM_STAGES generic
- Implement shift register with proper synthesis attributes
- Follow port order: clk, rst_n, async_in, sync_out
- Add comments explaining metastability mitigation
- Output to: `workflow/artifacts/vhdl/forge_util_synchronizer.vhd`

**Agent 2 (Test Designer):**
- Design P1 test architecture (4 tests)
- Create async input sequences with known timing
- Verify NUM_STAGES cycle latency for each transition
- Output test strategy to: `workflow/artifacts/tests/synchronizer_test_strategy.md`
- **NOTE:** Cannot test true metastability in CocoTB (RTL simulation limitation)

**Agent 3 (Test Runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/forge_util_synchronizer_tests/`

---

## Expected Output Example

For NUM_STAGES=2, async_in: `0→1` at cycle 5:

```
Cycle 0-4: async_in=0, sync_stages="00", sync_out=0
Cycle 5:   async_in=1, sync_stages="00", sync_out=0 (input captured)
Cycle 6:   async_in=1, sync_stages="10", sync_out=0 (stage 0 updated)
Cycle 7:   async_in=1, sync_stages="11", sync_out=1 (stage 1 updated, OUTPUT CHANGES)
```

**Latency:** 2 cycles from async_in change to sync_out change

---

## Use Cases

**Primary Use Cases:**
- Clock domain crossing (CDC) for control signals
- Asynchronous input synchronization (buttons, external signals)
- Reset synchronization across clock domains
- Handshake signal synchronization

**When NOT to Use:**
- ❌ Multi-bit data buses (use gray code + sync, or async FIFO)
- ❌ High-frequency toggle signals (pulse stretcher needed first)
- ❌ Signals requiring immediate response (inherent latency)

---

## References

**Industry Standards:**
- Cummings, "Clock Domain Crossing (CDC) Design & Verification Techniques" (2008)
- Xilinx UG912 - "Vivado Design Suite Properties Reference Guide"
- IEEE 1364.1 - Verilog Register Transfer Level Synthesis

**Recommended Reading:**
- `docs/VHDL_CODING_STANDARDS.md` - Section on clock domain crossing
