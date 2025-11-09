# Interactive Requirements Gathering Guide

**Human-readable version of the requirements gathering workflow for conversational use in any Claude interface.**

This guide replaces the `/gather-requirements` slash command (which doesn't work in Claude Code Web) with a structured conversational approach.

---

## Purpose

Ensure complete, validated component specifications before automated agent workflows. This prevents:
- ❌ Incomplete VHDL implementations
- ❌ Missing test cases
- ❌ Standards violations
- ❌ Agent failures due to ambiguous requirements

---

## 7-Phase Requirements Interview

### Phase 1: Component Identification

**Goal:** Establish component name, category, and high-level purpose

**Questions to Ask:**

1. **Component Name**
   ```
   What should we name this component?

   Format: forge_<category>_<function>
   Examples:
   - forge_util_clk_divider (utilities)
   - forge_debug_fsm_observer (debugging)
   - forge_loader_bram (loader)

   Suggested name: [based on user description]
   ```

2. **Category Selection**
   ```
   Which category does this belong to?

   - utilities: Generic reusable components (clk_divider, edge_detector, synchronizer, debouncer)
   - debugging: Debug infrastructure (fsm_observer, signal_tap, probe_mux)
   - loader: Memory/config initialization (bram_loader, lut_loader, config_loader)

   Your choice: ?
   ```

3. **One-Sentence Description**
   ```
   Describe the component in one sentence.

   Format: "Verb + object + purpose"
   Good: "Divides input clock by programmable factor with enable control"
   Bad: "A clock thing" (too vague)

   Your description: ?
   ```

**Deliverable:** Component identity established

---

### Phase 2: Functionality Deep Dive

**Goal:** Understand detailed behavior, constraints, and operational modes

**Questions to Ask:**

4. **Detailed Functionality**
   ```
   Describe how this component works internally.

   Consider:
   - What algorithm or logic does it implement?
   - Is it combinational or sequential?
   - Does it have internal state?
   - How does it transform inputs to outputs?

   Details: ?
   ```

5. **Problem Statement**
   ```
   What problem does this solve?

   Why is this component needed?
   What would happen without it?
   What alternatives exist (and why aren't they sufficient)?

   Problem: ?
   ```

6. **Timing Constraints**
   ```
   Are there timing requirements?

   - Max propagation delay?
   - Must respond within N clock cycles?
   - Setup/hold time requirements?
   - Clock frequency limitations?
   - Latency requirements?

   Constraints: ?
   ```

7. **Operational Modes**
   ```
   Does this component have different modes or states?

   Examples:
   - IDLE / ACTIVE / PAUSED
   - RESET / ARMED / TRIGGERED
   - NORMAL / DEBUG / CALIBRATION

   If FSM-based, list high-level states:
   States: ?
   ```

**Deliverable:** Complete functional description with constraints

---

### Phase 3: Interface Specification

**Goal:** Define all ports, generics, and types with exact specifications

**Questions to Ask:**

8. **Standard Ports (Always Ask First)**
   ```
   Which standard ports are needed?

   □ clk : in std_logic (clock input)
   □ rst_n : in std_logic (active-low reset)
   □ clk_en : in std_logic (clock enable, optional)
   □ enable : in std_logic (component enable, optional)

   Selected: ?
   ```

9. **Input Ports**
   ```
   What data input ports are needed?

   For EACH input port, specify:
   - Name: [descriptive, lowercase, underscores]
   - Type: std_logic | std_logic_vector | signed | unsigned
   - Width: [if vector/signed/unsigned, e.g., "7 downto 0"]
   - Purpose: [what does this input control/provide?]

   Example:
   - Name: divisor
   - Type: unsigned
   - Width: 15 downto 0
   - Purpose: Clock division factor (divide by divisor+1)

   List all inputs: ?
   ```

10. **Output Ports**
    ```
    What output ports are needed?

    For EACH output port, specify:
    - Name: [descriptive, lowercase, underscores]
    - Type: std_logic | std_logic_vector | signed | unsigned
    - Width: [if vector]
    - Purpose: [what does this output provide?]
    - Registered? [clocked output or combinational?]

    List all outputs: ?
    ```

11. **Generics/Parameters**
    ```
    What compile-time parameters are needed?

    For EACH generic, specify:
    - Name: [UPPERCASE, underscores]
    - Type: integer | natural | positive | std_logic | boolean
    - Default: [value if not specified by user]
    - Purpose: [why is this configurable?]

    Common generics:
    - CLK_FREQ_HZ : natural (clock frequency for timing calculations)
    - DATA_WIDTH : positive (bus width)
    - MAX_COUNT : natural (counter limit)

    List all generics: ?
    ```

**Deliverable:** Complete interface specification ready for VHDL entity

---

### Phase 4: Behavior Specification

**Goal:** Define internal logic, state machines, timing, and edge cases

**Questions to Ask:**

12. **State Machine (if applicable)**
    ```
    If component has internal states, define them:

    For EACH state:
    - Name: STATE_IDLE, STATE_ARMED, etc.
    - Encoding: "00", "01", "10", "11" (as std_logic_vector)
    - Description: What happens in this state?
    - Entry condition: How do we enter this state?
    - Exit condition: How do we leave this state?

    ⚠️ CRITICAL: Use std_logic_vector encoding, NOT VHDL enums
    Reason: Verilog compatibility (VHDL enums don't translate)

    States: ?
    ```

13. **State Transitions**
    ```
    What triggers state changes?

    For FSM-based components:
    - Draw state diagram (text format)
    - List transition conditions
    - Specify transition priorities (if multiple conditions possible)

    Example:
    IDLE → ARMED: when arm_trigger = '1'
    ARMED → FIRING: when input_level > threshold
    FIRING → IDLE: when counter = timeout

    Transitions: ?
    ```

14. **Combinational Logic**
    ```
    For non-FSM components, describe logic flow:

    - What calculations are performed?
    - What comparisons/conditions?
    - Pipeline stages (if any)?
    - Dependency chain?

    Logic: ?
    ```

15. **Edge Cases & Boundaries**
    ```
    What happens at edge cases?

    Consider:
    - Input = 0 (if applicable)
    - Input = maximum value
    - Overflow/underflow conditions
    - Simultaneous events (e.g., reset + trigger)
    - Invalid inputs (how handled?)

    Edge cases: ?
    ```

16. **Reset Behavior**
    ```
    What happens when rst_n = '0'?

    Specify initial values for:
    - All output ports: [values]
    - All internal signals: [values]
    - FSM state: [which state?]
    - Counters/registers: [reset values]

    Reset behavior: ?
    ```

17. **Enable Hierarchy**
    ```
    If multiple enable signals exist, what's the hierarchy?

    Standard hierarchy (from CLAUDE.md):
    rst_n > clk_en > enable

    Logic: output changes only if ALL enables active AND not in reset

    Confirm hierarchy: ?
    ```

**Deliverable:** Complete behavioral specification ready for VHDL architecture

---

### Phase 5: Testing Strategy

**Goal:** Define test cases, expected values, and validation criteria

**Questions to Ask:**

18. **P1 Essential Tests (3-5 tests)**
    ```
    What are the ESSENTIAL tests? (must pass for basic functionality)

    For EACH P1 test:
    - Test name: [descriptive]
    - Scenario: [what are we testing?]
    - Setup: [initial conditions]
    - Stimulus: [inputs applied]
    - Expected output: [exact values or ranges]
    - Duration: [simulation cycles, <50 for P1]

    Example:
    - Test: "Reset behavior"
    - Scenario: Component returns to known state on reset
    - Setup: Component in arbitrary state
    - Stimulus: Assert rst_n = '0' for 5 cycles
    - Expected: All outputs = '0', state = IDLE
    - Duration: 10 cycles

    P1 tests (3-5 only): ?
    ```

19. **P2 Comprehensive Tests (5-10 tests)**
    ```
    What additional tests validate edge cases? (for P2 level)

    Consider:
    - Boundary conditions
    - Stress testing (max values, rapid changes)
    - Error injection (invalid inputs)
    - State coverage (visit all FSM states)

    P2 tests: ?
    ```

20. **Expected Signal Values**
    ```
    For key tests, what are exact expected signal values?

    Example waveform expectations:
    Cycle  | clk | rst_n | input | output | state
    -------|-----|-------|-------|--------|-------
    0      | 0   | 0     | X     | 0      | IDLE
    1      | 1   | 0     | X     | 0      | IDLE
    2      | 0   | 1     | 5     | 0      | ARMED
    3      | 1   | 1     | 5     | 10     | ARMED

    Waveforms: ?
    ```

21. **Success Criteria**
    ```
    How do we know the component works correctly?

    - Functional: All outputs match expected values?
    - Timing: Meets timing constraints?
    - Resource: Uses reasonable LUTs/FFs?
    - Edge cases: Handles all boundary conditions?

    Criteria: ?
    ```

**Deliverable:** Complete test plan ready for CocoTB implementation

---

### Phase 6: Design Guidance

**Goal:** Architectural patterns, standards compliance, integration requirements

**Questions to Ask:**

22. **Architectural Pattern**
    ```
    What design pattern should this follow?

    Common patterns:
    - Moore FSM (outputs = f(state only))
    - Mealy FSM (outputs = f(state, inputs))
    - Pipelined (multi-stage with registers)
    - Combinational (pure logic, no state)
    - Counter-based (accumulator + comparator)

    Pattern: ?
    ```

23. **FORGE Integration**
    ```
    Does this component integrate with FORGE control scheme?

    If yes:
    - Use forge_common_pkg for FORGE_READY signal
    - Enable hierarchy: FORGE_READY AND user_enable AND clk_enable
    - See vhdl/packages/forge_common_pkg.vhd

    If no:
    - Standalone component, no FORGE dependencies

    FORGE integration: [YES/NO]
    ```

24. **HVS Encoding (Oscilloscope Debugging)**
    ```
    Should this component export state to oscilloscope via HVS?

    If yes (debugging components, FSMs with visible states):
    - Use forge_hierarchical_encoder
    - Export state_vector[5:0] and status_vector[7:0]
    - See vhdl/components/debugging/forge_hierarchical_encoder.vhd

    If no:
    - No debug output needed

    HVS encoding: [YES/NO]
    ```

25. **Voltage Domain**
    ```
    Does this component work with voltage values?

    If yes, which domain:
    - forge_voltage_3v3_pkg (0-3.3V, TTL/GPIO)
    - forge_voltage_5v0_pkg (0-5.0V, sensors)
    - forge_voltage_5v_bipolar_pkg (±5.0V, Moku DAC/ADC)

    Use case: Converting voltage thresholds to digital values

    Voltage package: [3v3 | 5v0 | 5v_bipolar | none]
    ```

26. **Dependencies**
    ```
    What other forge-vhdl components does this depend on?

    Common dependencies:
    - forge_common_pkg (FORGE control)
    - forge_util_clk_divider (clock generation)
    - forge_hierarchical_encoder (HVS debug)
    - forge_lut_pkg (look-up tables)

    List dependencies: ?
    ```

27. **Standards Compliance**
    ```
    Confirm adherence to VHDL-FORGE standards:

    □ VHDL-2008 only (no VHDL-93)
    □ No enums for FSM states (use std_logic_vector)
    □ No records in entity ports (CocoTB limitation)
    □ Port order: clk, rst_n, clk_en, enable, data, status
    □ Signal prefixes: ctrl_, cfg_, stat_, dbg_
    □ Active-low reset: rst_n (not rst)

    All confirmed: [YES/NO]
    If NO, which standards need adjustment: ?
    ```

**Deliverable:** Design constraints and integration requirements

---

### Phase 7: Specification Generation

**Goal:** Create complete markdown specification file

**Process:**

28. **Generate Specification File**
    ```
    Create: workflow/specs/pending/[component_name].md

    Template: workflow/specs/examples/pwm_generator.md

    Required sections (in order):

    # Component Name

    ## Metadata
    - Category: [utilities|debugging|loader]
    - Version: 1.0.0
    - Author: [Generated via interactive requirements]
    - Date: [YYYY-MM-DD]

    ## Overview
    [One-sentence + detailed description from Phase 2]

    ## Requirements
    ### Functional Requirements
    [From Phase 2: functionality, problem, modes]

    ### Timing Requirements
    [From Phase 2: constraints]

    ### Standards Compliance
    [From Phase 6: VHDL-2008, no enums, etc.]

    ## Interface
    ### Entity Declaration
    ```vhdl
    entity [component_name] is
        generic (
            [From Phase 3: generics]
        );
        port (
            [From Phase 3: ports in standard order]
        );
    end entity;
    ```

    ### Port Descriptions
    [Table with: Name | Direction | Type | Width | Purpose]

    ### Generic Descriptions
    [Table with: Name | Type | Default | Purpose]

    ## Behavior
    ### State Machine (if applicable)
    [From Phase 4: states, transitions, encodings]

    ### Logic Description
    [From Phase 4: combinational logic, calculations]

    ### Reset Behavior
    [From Phase 4: initial values]

    ### Edge Cases
    [From Phase 4: boundary conditions]

    ## Testing
    ### P1 Tests (Essential)
    [From Phase 5: 3-5 tests with scenarios and expected values]

    ### P2 Tests (Comprehensive)
    [From Phase 5: additional edge case tests]

    ### Success Criteria
    [From Phase 5: validation criteria]

    ## Design Notes
    ### Architectural Pattern
    [From Phase 6: Moore FSM, pipelined, etc.]

    ### Dependencies
    [From Phase 6: required packages/components]

    ### Integration
    [From Phase 6: FORGE, HVS, voltage domains]

    ## Implementation Notes
    - Agent: forge-vhdl-component-generator
    - Target: vhdl/components/[category]/[component_name].vhd
    - Test: cocotb_tests/components/test_[component_name]_progressive.py

    ## References
    - VHDL Standards: CLAUDE.md
    - Testing Guide: docs/COCOTB_TROUBLESHOOTING.md
    - Example: [similar component from vhdl/components/]
    ```

29. **Show Summary to User**
    ```
    Specification Summary:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Component:   [name]
    Category:    [category]
    Purpose:     [one-sentence]

    Interface:
    - Inputs:    [count] ([names])
    - Outputs:   [count] ([names])
    - Generics:  [count] ([names])

    Behavior:
    - Type:      [FSM | Combinational | Counter-based]
    - States:    [count if FSM]
    - Timing:    [latency if known]

    Testing:
    - P1 tests:  [count] essential tests
    - P2 tests:  [count] comprehensive tests

    Dependencies:
    - Packages:  [list]
    - Components: [list if any]

    Ready for automated workflow (3 agents):
    1. forge-vhdl-component-generator → VHDL
    2. cocotb-progressive-test-designer → Test arch
    3. cocotb-progressive-test-runner → Working tests
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Does this look correct?
    [WAIT FOR USER APPROVAL]
    ```

30. **Save and Commit**
    ```
    If user approves:

    git add workflow/specs/pending/[component_name].md
    git commit -m "spec: Add [component_name] specification

    Interactive requirements gathering completed.
    Ready for automated agent workflow.

    Component: [name]
    Category: [category]
    Tests: [P1 count] P1, [P2 count] P2

    🤖 Generated via interactive requirements gathering"

    git push origin main
    ```

**Deliverable:** Complete, validated specification committed to repository

---

## Validation Checklist

Before proceeding to agent workflow, verify:

### Completeness
- [ ] All 7 phases completed
- [ ] No "TODO" or "TBD" placeholders in spec
- [ ] All port names, types, widths defined
- [ ] At least 3 P1 tests specified
- [ ] Reset behavior documented

### Standards Compliance
- [ ] Component name follows `forge_<category>_<function>` pattern
- [ ] No VHDL enums mentioned (only std_logic_vector for states)
- [ ] Port order: clk, rst_n, clk_en, enable, data, status
- [ ] Active-low reset named `rst_n`
- [ ] VHDL-2008 compatibility confirmed

### Testability
- [ ] Test scenarios are specific (not vague)
- [ ] Expected values are concrete (not "should work")
- [ ] P1 tests are <50 cycles each
- [ ] Success criteria are measurable

### Clarity
- [ ] No ambiguous requirements ("fast", "efficient", "good")
- [ ] Edge cases explicitly handled
- [ ] Assumptions documented
- [ ] Dependencies listed

If all boxes checked ✅ → **PROCEED TO AGENT WORKFLOW**

If any boxes unchecked ❌ → **RETURN TO RELEVANT PHASE**

---

## Example: Complete Requirements Session

See `workflow/specs/examples/requirements_session_transcript.md` for full example of conversational requirements gathering for a PWM generator component.

---

## Troubleshooting

**Q: User says "I don't know" to many questions**
A: Provide examples, suggest defaults, explain why the question matters

**Q: User provides vague requirements ("make it fast")**
A: Ask quantitative follow-ups ("How fast? Latency in cycles? Frequency limit?")

**Q: User wants to skip requirements gathering**
A: Explain that incomplete specs lead to agent failures and rework

**Q: Requirements change mid-interview**
A: Perfectly fine! Update earlier answers, regenerate spec

**Q: Specification is very long (>500 lines)**
A: That's OK! Better too much detail than too little. Agents will extract what they need.

---

**Last Updated:** 2025-11-09
**Version:** 1.0.0
**Replaces:** /gather-requirements slash command (not available in Claude Code Web)
