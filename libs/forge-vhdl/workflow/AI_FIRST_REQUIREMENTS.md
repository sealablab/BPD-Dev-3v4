# AI-First Requirements Workflow

**Fast-track specification generation for experienced users and clear requirements**

---

## Philosophy

**Traditional approach:** Ask user 30 questions → Wait for answers → Build spec incrementally

**AI-First approach:** Pattern match → Infer defaults → Propose complete spec → Refine if needed

**Result:** 2-5 minute spec generation vs. 15-30 minute Q&A session, same quality output

---

## When to Use This Workflow

### ✅ Use AI-First When:
- Component matches existing pattern (edge detection, timing, FSM, counter-based)
- User has clear high-level requirements
- User trusts Claude to infer sensible defaults
- Fast prototyping / iteration desired
- User is experienced with VHDL standards

### ❌ Use Interactive Workflow Instead When:
- First VHDL component ever (learning mode)
- Completely novel architecture (no pattern match)
- User wants full control over every detail
- Educational goal (learn VHDL-FORGE standards step-by-step)
- Requirements are vague or contradictory

**Reference:** `workflow/ENGINEER_REQUIREMENTS.md` for full 30-question approach

---

## 4-Step AI-First Workflow

### Step 1: Pattern Recognition & Inference

**Claude's Internal Process (thinking, not asking):**

**Input:** User's high-level component description

**Claude analyzes:**
1. **Pattern matching:** Which reference spec is most similar?
   - Edge/event detection → `edge_detector.md`
   - Clock domain crossing → `synchronizer.md`
   - Periodic signal output → `pwm_generator.md`
   - Button/switch input → `debouncer.md`
   - Pulse timing/extension → `pulse_stretcher.md`

2. **Component naming:** Apply `forge_<category>_<function>` convention
   - Utilities: Generic reusable (clk_divider, timeout, edge_detector)
   - Debugging: Debug infrastructure (fsm_observer, signal_tap)
   - Loader: Memory/config init (bram_loader, lut_loader)

3. **Architecture inference:** Based on pattern match
   - FSM-based: State machine with std_logic_vector states
   - Counter-based: Accumulator + comparator
   - Combinational: Pure logic, no state
   - Pipelined: Multi-stage with registers

4. **Standard ports:** Apply forge-vhdl conventions
   - Always: `clk : in std_logic`, `rst_n : in std_logic` (active-low)
   - Usually: `enable : in std_logic` (component enable)
   - Optional: `clk_en : in std_logic` (clock enable for power gating)
   - Order: clk, rst_n, clk_en, enable, data inputs, data outputs, status

5. **Generics:** Infer from requirements
   - Timing-based: `CLK_FREQ_HZ : positive`, `DURATION_MS : positive`
   - Data width: `DATA_WIDTH : positive`
   - Configuration: `MODE : string`, `THRESHOLD : natural`

6. **Test plan:** Default to 4-5 P1 tests
   - test_reset (always required)
   - test_basic_operation (core functionality)
   - test_enable_control (if enable port exists)
   - test_edge_cases (1-2 boundary conditions)

7. **Dependencies:** Infer packages needed
   - Counter/arithmetic: `ieee.numeric_std.all`
   - Basic logic: `ieee.std_logic_1164.all`
   - Voltage types: `work.forge_voltage_*_pkg.all`
   - FORGE control: `work.forge_common_pkg.all`

8. **Standards compliance:** Auto-apply VHDL-FORGE rules
   - VHDL-2008 only
   - No enums for FSM states (use std_logic_vector)
   - No records in entity ports (CocoTB limitation)
   - Active-low reset: `rst_n` (not `rst`)
   - Signal prefixes: `ctrl_`, `cfg_`, `stat_`, `dbg_`

**Claude asks ONLY if critical ambiguity exists:**
- Multiple valid patterns (FSM vs. counter-based?)
- Output mode choice (level vs. pulse vs. edge?)
- Retriggerable vs. one-shot behavior?
- Voltage domain selection (3v3, 5v0, 5v_bipolar?)

**Example inference:**

```
User: "I need a timeout detector that triggers after 100ms of inactivity"

Claude infers:
✓ Pattern: pulse_stretcher.md (timing-based counter pattern)
✓ Architecture: Up-counter (vs pulse_stretcher's down-counter)
✓ Name: forge_util_timeout_detector
✓ Category: utilities
✓ Ports: clk, rst_n, enable, activity_in, timeout_out
✓ Generics: CLK_FREQ_HZ (125MHz), TIMEOUT_MS (100ms)
✓ Behavior: Retriggerable (activity resets counter)
✓ Output: Level (stays high until activity)
✓ P1 tests: reset, timeout, retriggerable, enable
✓ Dependencies: ieee.numeric_std (unsigned counter)

Critical ambiguity: Output mode (level vs pulse)?
→ Ask user, provide default suggestion
```

---

### Step 2: Specification Proposal

**Claude generates complete spec summary** and presents for validation:

**Format:**

```markdown
📋 **Proposed Specification: [component_name]**

**Category:** [utilities|debugging|loader]
**Purpose:** [One-sentence description]
**Pattern:** Adapted from [reference_spec.md] ([key difference])

**Interface:**
- Generics: [count] ([names with defaults])
- Ports: [count] ([names])
  - Inputs: [list]
  - Outputs: [list]

**Behavior:**
- [3-5 bullet points of core behavior]
- Reset: [initial state]
- Enable hierarchy: [rst_n > clk_en > enable]

**P1 Tests ([count] tests, <20 lines):**
1. [test_name] - [scenario]
2. [test_name] - [scenario]
3. [test_name] - [scenario]
4. [test_name] - [scenario]

**Dependencies:**
- Packages: [list]
- Components: [list if any]

**Standards Compliance:**
✓ VHDL-2008
✓ std_logic_vector states (no enums)
✓ Active-low reset
✓ CocoTB-compatible ports

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤔 **Review Questions** (answer only to change defaults):

1. [Critical question 1]? (default: [value])
2. [Critical question 2]? (default: [value])
3. Any additional ports/generics? (default: none)

**If defaults look good, just say "proceed" or "looks good"!**
```

**Example proposal:**

```markdown
📋 **Proposed Specification: forge_util_timeout_detector**

**Category:** utilities
**Purpose:** Detect inactivity timeout and assert signal after configurable duration
**Pattern:** Adapted from pulse_stretcher.md (up-counter vs down-counter)

**Interface:**
- Generics: 2 (CLK_FREQ_HZ=125MHz, TIMEOUT_MS=100ms)
- Ports: 5 (clk, rst_n, enable, activity_in, timeout_out)
  - Inputs: activity_in (signal to monitor)
  - Outputs: timeout_out (asserted after timeout)

**Behavior:**
- Counter increments when activity_in='0' (inactive)
- Counter resets to 0 when activity_in='1' (retriggerable)
- timeout_out='1' when counter >= threshold
- Reset clears counter and timeout_out='0'
- Disabled: timeout_out='0', counter holds

**P1 Tests (4 tests, <20 lines):**
1. test_reset - Verify timeout_out=0 after reset
2. test_timeout - Verify timeout after 100ms inactivity
3. test_retriggerable - Verify activity resets counter
4. test_enable - Verify enable control

**Dependencies:**
- Packages: ieee.numeric_std (unsigned counter)
- Components: none

**Standards Compliance:**
✓ VHDL-2008
✓ std_logic_vector states (no enums)
✓ Active-low reset
✓ CocoTB-compatible ports

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤔 **Review Questions** (answer only to change defaults):

1. Output mode: level or pulse? (default: level - stays high until activity)
2. Timeout behavior: retriggerable or one-shot? (default: retriggerable)
3. Any additional ports/generics? (default: none)

**If defaults look good, just say "proceed" or "looks good"!**
```

---

### Step 3: Refinement (Only If Needed)

**User responses (examples):**

**Scenario 1: Accept defaults**
```
User: "Proceed"
User: "Looks good"
User: "Perfect, generate it"
```
→ Claude generates full spec immediately (skip to Step 4)

**Scenario 2: Tweak defaults**
```
User: "Make it pulse mode"
User: "Change timeout to 500ms default"
User: "Add a reset_counter input port"
```
→ Claude updates spec, regenerates proposal, shows diff

**Scenario 3: Major change**
```
User: "Actually I want one-shot mode, not retriggerable"
```
→ Claude adjusts behavior section, updates tests, regenerates

**Scenario 4: Ambiguous request**
```
User: "Make it faster"
```
→ Claude asks clarifying question:
```
"Faster" how?
1. Reduce default TIMEOUT_MS (100ms → 10ms)?
2. Increase default CLK_FREQ_HZ (125MHz → higher)?
3. Reduce counter latency (add pipelining)?
```

**Scenario 5: Standards violation**
```
User: "Use enum for mode selection"
```
→ Claude corrects with explanation:
```
❌ VHDL enums not allowed per CLAUDE.md (Verilog compatibility)
✅ Alternative: Use std_logic mode_select port instead
   - mode_select='0' → pulse mode
   - mode_select='1' → level mode

Should I add mode_select port with std_logic type?
```

**Refinement loop:**
1. User requests change
2. Claude updates spec
3. Claude shows diff (what changed)
4. Claude asks "Ready to proceed, or more changes?"
5. Repeat until user says "proceed"

---

### Step 4: Specification Generation

**Claude generates full 7-section markdown spec:**

**File location:** `workflow/specs/pending/[component_name].md`

**Sections (complete template):**

```markdown
# Component: [Name]

**Category:** [utilities|debugging|loader]
**Purpose:** [One-sentence description]

---

## Requirements

### Functionality
- [5-10 bullet points describing what component does]
- [Include operational modes]
- [Include constraints]

### Interface

**Entity:** [component_name]

**Generics:**
- [GENERIC_NAME] : [type] := [default] -- [purpose]

**Ports:**
```vhdl
-- Clock & Reset
clk         : in std_logic;
rst_n       : in std_logic;

-- Control
enable      : in std_logic;

-- Data inputs
[input_name] : in [type];

-- Data outputs
[output_name] : out [type];

-- Status
[status_name] : out std_logic;
```

### Behavior
- **Reset:** [initial values for all outputs and state]
- **Disabled (enable='0'):** [behavior when disabled]
- **Enabled (enable='1'):** [normal operation]
- **Edge cases:** [boundary conditions, overflow, underflow]

---

## Testing Requirements

**Test Level:** P1 ([count] essential tests)

**Required Tests:**
1. [test_name] - [scenario description]
   - Setup: [initial conditions]
   - Stimulus: [inputs applied]
   - Expected: [output values]
   - Duration: [cycles]

2. [test_name] - [scenario description]
   ...

**Test Values:**

**P1 (Fast):**
- [Generic values for fast testing]
- [Test patterns with small cycle counts]
- [Expected outputs]

**P2 (Realistic):**
- [Production generic values]
- [Comprehensive test patterns]
- [Edge case coverage]

---

## Design Notes

**Architecture:** [High-level approach - FSM, counter-based, combinational, pipelined]

**Approach:**
1. [Step-by-step design approach]
2. [Key algorithms or logic]
3. [State machine transitions if applicable]

**Dependencies:**
- Package: [package names]
- Component: [component names if any]

**Constraints:**
- [Timing constraints]
- [Resource constraints]
- [Interface constraints]

**Key Design Considerations:**
- [Important design decisions]
- [Trade-offs made]
- [Why this approach vs. alternatives]

---

## Agent Instructions

**Agent 1 (forge-vhdl-component-generator):**
- Generate entity + architecture
- [Specific VHDL generation instructions]
- Follow port order: [list]
- Output to: `workflow/artifacts/vhdl/[component_name].vhd`

**Agent 2 (cocotb-progressive-test-designer):**
- Design P1 test architecture ([count] tests)
- [Specific test design instructions]
- Output test strategy to: `workflow/artifacts/tests/[component]_test_strategy.md`

**Agent 3 (cocotb-progressive-test-runner):**
- Implement P1 tests from strategy
- Run via CocoTB + GHDL
- Verify <20 line output (GHDL filter applied)
- Output to: `workflow/artifacts/tests/[component_name]_tests/`

---

## Expected Output Example

[Concrete behavioral example with specific values]

```
Cycle  | input | counter | output | notes
-------|-------|---------|--------|-------
0      | 0     | 0       | 0      | reset
1      | 0     | 1       | 0      | counting
2      | 0     | 2       | 0      | counting
...
100    | 0     | 100     | 1      | timeout!
101    | 1     | 0       | 0      | activity reset
```

**Use Cases:**
- [Primary use case 1]
- [Primary use case 2]
- [Integration example]

---

## References

**Related Components:**
- [Similar component 1]
- [Similar component 2]

**Standards:**
- VHDL Coding: `docs/VHDL_CODING_STANDARDS.md`
- Testing: `docs/PROGRESSIVE_TESTING_GUIDE.md`
- Pattern source: `workflow/specs/reference/[pattern].md`
```

**After generation, Claude shows:**

```
✅ **Specification generated:** workflow/specs/pending/[component_name].md

**Summary:**
- Component: [name]
- Category: [category]
- Interface: [input count] inputs, [output count] outputs, [generic count] generics
- Tests: [P1 count] P1 tests
- Pattern: Based on [reference_spec.md]

**Next steps:**

**Option 1: Review spec manually**
Edit workflow/specs/pending/[component_name].md if needed

**Option 2: Run automated 3-agent workflow**
Say "run workflow" to execute:
1. forge-vhdl-component-generator → VHDL implementation
2. cocotb-progressive-test-designer → Test architecture
3. cocotb-progressive-test-runner → Working tests

**Option 3: Commit spec for later**
Spec saved to pending/ directory, ready when you are

What would you like to do?
```

---

## Pattern Matching Rules

### Pattern Recognition Table

| User Request Keywords | Pattern Match | Reference Spec | Key Adaptations |
|-----------------------|---------------|----------------|-----------------|
| "detect edge", "rising", "falling", "transition" | Simple utility | edge_detector.md | Registered comparison |
| "clock domain", "CDC", "async", "metastability" | CDC pattern | synchronizer.md | Multi-stage register |
| "PWM", "duty cycle", "frequency", "periodic" | Counter-based | pwm_generator.md | Period + threshold |
| "button", "debounce", "switch", "bounce" | FSM + timing | debouncer.md | Stability counter |
| "pulse stretch", "extend", "timeout", "one-shot" | Retriggerable timing | pulse_stretcher.md | Down-counter |
| "timeout detector", "inactivity", "watchdog" | Retriggerable timing | pulse_stretcher.md | Up-counter variant |
| "delay", "pipeline", "stages" | Pipelined | synchronizer.md | Shift register |
| "counter", "accumulator", "rollover" | Counter-based | pwm_generator.md | Simple counter |
| "FSM", "state machine", "modes" | FSM pattern | debouncer.md | std_logic_vector states |
| "observer", "debug", "oscilloscope" | Debug pattern | None (custom) | HVS encoding |

### Architectural Pattern Rules

**When to use FSM pattern:**
- User mentions "states", "modes", or "FSM" explicitly
- Multiple operational modes with transitions
- Complex control flow with decision points
- **Template:** debouncer.md (4-state FSM with counter)

**When to use counter-based pattern:**
- Timing-based behavior (delays, periods, timeouts)
- Arithmetic comparisons (thresholds, limits)
- Periodic signal generation
- **Template:** pwm_generator.md or pulse_stretcher.md

**When to use combinational pattern:**
- Pure logic (no state)
- No timing requirements
- Instant response (no latency)
- **Template:** edge_detector.md (minimal state)

**When to use pipelined pattern:**
- Multi-cycle operations
- High-throughput data path
- Latency acceptable, throughput critical
- **Template:** synchronizer.md (register chain)

---

## Inference Rules (Defaults)

### Naming Conventions

**Component name:**
```
forge_<category>_<function>

category:
  - util (generic utilities)
  - debug (debugging infrastructure)
  - loader (memory/config loaders)

function:
  - Lowercase, underscores
  - Verb or noun (clk_divider, edge_detector, timeout)
```

**Port names:**
```
Inputs:
  - [signal]_in (data_in, pulse_in, voltage_in)
  - [function] (divisor, threshold, enable)

Outputs:
  - [signal]_out (data_out, pulse_out, voltage_out)
  - [status] (busy, ready, timeout, fault)

Control:
  - enable (component enable)
  - clk_en (clock enable)
  - rst_n (active-low reset, ALWAYS)
```

**Generic names:**
```
UPPERCASE_WITH_UNDERSCORES

Common:
  - CLK_FREQ_HZ : positive := 125_000_000
  - DATA_WIDTH : positive := 16
  - TIMEOUT_MS : positive := 100
  - MAX_COUNT : natural := 1000
```

### Default Generics

**For timing-based components:**
```vhdl
CLK_FREQ_HZ : positive := 125_000_000  -- Moku standard clock
DURATION_MS : positive := [inferred from user]
```

**For data-width components:**
```vhdl
DATA_WIDTH : positive := 16  -- Standard Moku DAC/ADC width
```

**For mode selection:**
```vhdl
MODE : string := "default_mode"  -- Avoid if possible, use std_logic instead
-- Better: mode_select : in std_logic (compile-time generic vs runtime port)
```

### Default Test Plan

**P1 tests (always include):**
1. `test_reset` - Verify all outputs = 0 after reset
2. `test_basic_[function]` - Core functionality with nominal values
3. `test_enable_control` - Verify enable starts/stops operation (if enable port)
4. `test_[edge_case]` - One boundary condition (max value, overflow, etc.)

**P1 test values:**
- Duration: 20-50 cycles (fast for LLM iteration)
- Data values: Small (10, 100, not 10000)
- Patterns: Simple (0→1→0, not complex sequences)

**P2 tests (if requested):**
- 5-10 additional tests
- Realistic values
- Edge cases, stress testing
- 100-500 cycles

### Default Dependencies

**Always include:**
```vhdl
library ieee;
use ieee.std_logic_1164.all;
```

**If arithmetic/counters:**
```vhdl
use ieee.numeric_std.all;  -- For unsigned, signed
```

**If voltage types:**
```vhdl
use work.forge_voltage_3v3_pkg.all;  -- 0-3.3V (TTL, GPIO)
use work.forge_voltage_5v0_pkg.all;  -- 0-5.0V (sensors)
use work.forge_voltage_5v_bipolar_pkg.all;  -- ±5V (Moku DAC/ADC)
```

**If FORGE integration:**
```vhdl
use work.forge_common_pkg.all;  -- FORGE_READY control
```

**If HVS debug:**
```vhdl
use work.forge_hierarchical_encoder_pkg.all;  -- Oscilloscope debug
```

---

## Critical Questions (When to Ask)

### Always Ask If:

1. **Multiple valid patterns exist**
   ```
   User: "I need a timer"

   Ambiguity: Timer could be:
   - One-shot (pulse_stretcher pattern)
   - Free-running (pwm_generator pattern)
   - Stopwatch (counter pattern)

   Ask: "What type of timer?
   1. One-shot (triggers once, stops)
   2. Free-running (periodic, continuous)
   3. Stopwatch (counts up, user-controlled)
   ```

2. **Output mode unclear**
   ```
   Ambiguity: Output could be level or pulse

   Ask: "Output mode:
   1. Level (stays high until condition clears)
   2. Pulse (1-cycle pulse on event)
   3. Edge (rising/falling/both)

   Default: [suggest based on pattern]"
   ```

3. **Retriggerable vs. one-shot**
   ```
   Ambiguity: For timing components

   Ask: "Behavior when triggered during active period:
   1. Retriggerable (extend/restart timer)
   2. One-shot (ignore until complete)

   Default: retriggerable (more flexible)"
   ```

4. **Voltage domain selection**
   ```
   User: "Convert voltage to digital"

   Ask: "Which voltage range?
   1. 0-3.3V (TTL, GPIO) → forge_voltage_3v3_pkg
   2. 0-5.0V (sensors) → forge_voltage_5v0_pkg
   3. ±5.0V (Moku DAC/ADC) → forge_voltage_5v_bipolar_pkg

   Most common: ±5V (Moku platform)"
   ```

### Never Ask If:

1. **Standards-compliant default exists**
   - Reset polarity: Always active-low `rst_n`
   - Port order: Always clk, rst_n, clk_en, enable, data, status
   - State encoding: Always std_logic_vector (never enums)

2. **Pattern provides clear answer**
   - Edge detector: Obviously needs edge type configuration
   - Synchronizer: Obviously needs 2+ stages
   - PWM: Obviously needs frequency + duty cycle

3. **User already specified**
   - If user says "100ms timeout", don't ask for duration
   - If user says "rising edge", don't ask for edge type

---

## Example: Complete AI-First Session

**User input:**
```
I need a watchdog timer that resets the system if software doesn't ping it within 500ms
```

**Step 1: Claude's inference (internal thinking):**
```
Pattern match: pulse_stretcher.md (retriggerable timing)
Adaptation: Up-counter, system reset output

Name: forge_util_watchdog
Category: utilities
Ports: clk, rst_n, enable, watchdog_ping, system_reset_n
Generics: CLK_FREQ_HZ (125MHz), TIMEOUT_MS (500ms)
Behavior: Counter increments, ping resets, timeout → system_reset_n='0'
Tests: reset, timeout, ping_resets_counter, enable

Critical ambiguity: Output polarity (active-high reset or active-low?)
→ Suggest active-low (matches rst_n convention)
```

**Step 2: Proposal:**
```markdown
📋 **Proposed Specification: forge_util_watchdog**

**Category:** utilities
**Purpose:** Watchdog timer with configurable timeout and system reset output
**Pattern:** Adapted from pulse_stretcher.md (up-counter with active-low reset output)

**Interface:**
- Generics: 2 (CLK_FREQ_HZ=125MHz, TIMEOUT_MS=500ms)
- Ports: 5 (clk, rst_n, enable, watchdog_ping, system_reset_n)
  - Inputs: watchdog_ping (software heartbeat)
  - Outputs: system_reset_n (active-low system reset)

**Behavior:**
- Counter increments when watchdog_ping='0' (no pings)
- Counter resets to 0 when watchdog_ping='1' (ping received)
- system_reset_n='0' when counter >= timeout (triggers reset)
- system_reset_n='1' normally (no reset)
- Reset clears counter, system_reset_n='1'

**P1 Tests (4 tests, <20 lines):**
1. test_reset - Verify system_reset_n='1' after reset
2. test_timeout - Verify system_reset_n='0' after 500ms without ping
3. test_ping_resets - Verify ping resets counter
4. test_enable - Verify enable control

**Dependencies:**
- Packages: ieee.numeric_std (unsigned counter)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤔 **Review Questions** (answer only to change defaults):

1. Reset output polarity: active-low (system_reset_n='0' triggers reset) or active-high? (default: active-low, matches rst_n convention)
2. Ping mechanism: level-sensitive (watchdog_ping='1' resets) or edge-sensitive (0→1 transition)? (default: level-sensitive)
3. Any additional features (reset counter readback, timeout warning, etc.)? (default: none)

**If defaults look good, just say "proceed"!**
```

**Step 3: User refinement:**
```
User: "Add a timeout_warning output that goes high at 80% of timeout"

Claude: Updates spec, adds port:
  timeout_warning : out std_logic  -- High when counter > (0.8 * timeout)

Updated proposal shown, user says "proceed"
```

**Step 4: Generation:**
```
✅ Specification generated: workflow/specs/pending/forge_util_watchdog.md

Ready for automated 3-agent workflow?
Say "run workflow" to execute.
```

---

## Validation Checklist

Before generating final spec, Claude internally validates:

### Completeness
- [ ] Component name follows `forge_<category>_<function>` pattern
- [ ] All ports have: name, direction, type, width (if vector), purpose
- [ ] All generics have: name, type, default, purpose
- [ ] Reset behavior specified for all outputs
- [ ] At least 3 P1 tests defined with scenarios
- [ ] Dependencies listed (packages, components)

### Standards Compliance
- [ ] VHDL-2008 (no VHDL-93 constructs)
- [ ] No enums for FSM states (std_logic_vector only)
- [ ] No records in entity ports (CocoTB limitation)
- [ ] Active-low reset named `rst_n`
- [ ] Port order: clk, rst_n, clk_en, enable, data, status
- [ ] Signal prefixes used: ctrl_, cfg_, stat_, dbg_

### Testability
- [ ] P1 tests are <50 cycles each
- [ ] Test values are concrete (not "TBD" or ranges)
- [ ] Expected outputs are measurable (not "should work")
- [ ] Success criteria are clear (pass/fail conditions)

### Clarity
- [ ] No ambiguous requirements ("fast", "efficient", "good")
- [ ] Edge cases explicitly handled
- [ ] Assumptions documented
- [ ] Architecture choice justified

**If any validation fails:** Claude asks clarifying question before generating

---

## Integration with Existing Workflows

### Relationship to Interactive Workflow

**AI-First is NOT a replacement**, it's a **complement**:

```
workflow/
├── ENGINEER_REQUIREMENTS.md      # 30-question full guidance (engineer mode)
├── AI_FIRST_REQUIREMENTS.md      # This file (fast mode)
└── README.md                      # Explains when to use each

User scenarios:
1. First time user → Interactive (educational)
2. Experienced user, clear req → AI-First (fast)
3. Novel architecture → Interactive (guidance needed)
4. Pattern-matched component → AI-First (inference works)
```

### Handoff to Agent Workflow

**After spec generation, identical path:**

```
Spec ready in workflow/specs/pending/[component].md
  ↓
User: "run workflow" or manual agent invocation
  ↓
Agent 1: forge-vhdl-component-generator
  → workflow/artifacts/vhdl/[component].vhd
  ↓
Agent 2: cocotb-progressive-test-designer
  → workflow/artifacts/tests/[component]_test_strategy.md
  ↓
Agent 3: cocotb-progressive-test-runner
  → workflow/artifacts/tests/[component]_tests/
  ↓
User reviews artifacts, integrates to main codebase
```

**No difference in agent behavior** - same input format (markdown spec)

---

## Quick Reference

### User Invocation

**Start AI-First workflow:**
```
"I need a [component description]. Use the AI-First requirements workflow to generate a spec."
```

**Examples:**
```
"I need a timeout detector. Use AI-First workflow."
"I need a button debouncer. Use AI-First workflow."
"Create an edge detector using AI-First approach."
"Generate spec for a watchdog timer (AI-First)."
```

### Claude's Response Pattern

1. **Analyze:** (internal thinking, not shown to user)
2. **Propose:** Show complete spec summary + 2-3 critical questions
3. **Refine:** Iterate on user feedback
4. **Generate:** Write full markdown spec
5. **Handoff:** Offer to run 3-agent workflow

### Time Estimates

| Workflow | User time | Total time | Spec quality |
|----------|-----------|------------|--------------|
| Interactive (30Q) | 15-30 min | 20-40 min | 100% complete |
| AI-First (2-3Q) | 2-5 min | 5-10 min | 95%+ complete |

---

## Troubleshooting

**Q: Spec has incorrect assumptions**
**A:** Provide corrections, Claude will regenerate proposal with updates

**Q: Multiple components in one request**
**A:** Claude creates separate specs for each, or asks which to do first

**Q: Novel architecture (no pattern match)**
**A:** Claude suggests falling back to Interactive workflow for guidance

**Q: User says "I don't know" to critical question**
**A:** Claude provides examples, suggests most common default, explains trade-offs

**Q: Spec too simple (under-specified)**
**A:** Claude asks "Should I add [missing feature]?" based on pattern completeness

**Q: Spec too complex (over-engineered)**
**A:** User says "simpler", Claude removes optional features, focuses on core

---

## See Also

- **`workflow/ENGINEER_REQUIREMENTS.md`** - Full 30-question guided approach
- **`workflow/specs/reference/`** - 5 gold-standard pattern specs
- **`workflow/specs/reference/README.md`** - Pattern matching guide
- **`CLAUDE.md`** - VHDL-FORGE coding standards and testing patterns
- **`docs/VHDL_CODING_STANDARDS.md`** - Complete VHDL style guide

---

**Last Updated:** 2025-11-09
**Version:** 1.0.0
**Complements:** ENGINEER_REQUIREMENTS.md (full guided approach for engineers)
