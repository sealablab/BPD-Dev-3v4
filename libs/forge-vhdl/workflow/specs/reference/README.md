# Reference Component Specifications

**Purpose:** Gold-standard specifications that define quality and patterns

**Audience:**
- 👥 Human users learning the specification format
- 🤖 AI agents referencing proven patterns
- 📚 Documentation of best practices

---

## What Makes These "Reference Quality"?

Each specification in this directory:

✅ **Complete** - All 7 sections fully documented (requirements, interface, behavior, testing, design notes, agent instructions, examples)

✅ **Proven** - Pattern has been validated through implementation or careful design review

✅ **Clear** - Unambiguous requirements that agents can implement autonomously

✅ **Standards-compliant** - Follows VHDL-FORGE standards (std_logic_vector states, port order, reset hierarchy)

✅ **Test-ready** - P1 tests specified with concrete values and expected behaviors

---

## Available Patterns

### 1. **edge_detector.md** - Simple Utility Pattern
**Complexity:** Low
**Pattern:** Registered comparison logic
**Use when:** Detecting signal transitions, event detection
**Key features:** Single-cycle pulse output, configurable edge types
**Architecture:** Two flip-flops (current + previous state), combinational comparison

**Learn from this:** Clean minimal design, simple control flow

---

### 2. **synchronizer.md** - CDC (Clock Domain Crossing) Pattern
**Complexity:** Low-Medium
**Pattern:** Multi-stage register chain for metastability mitigation
**Use when:** Crossing clock domains, external async signals
**Key features:** Configurable stages (default 2), metastability safe
**Architecture:** Shift register chain (prevents metastability propagation)

**Learn from this:** Safety-critical design, proper CDC handling

---

### 3. **pwm_generator.md** - Counter-Based Pattern
**Complexity:** Medium
**Pattern:** Free-running counter with threshold comparison
**Use when:** Generating periodic signals, DAC control, motor drivers
**Key features:** Configurable frequency/duty cycle, 8-bit resolution
**Architecture:** Period counter + duty threshold comparator

**Learn from this:** Arithmetic-based control, configuration registers

---

### 4. **debouncer.md** - FSM Pattern with Timing
**Complexity:** Medium
**Pattern:** FSM with stability counter
**Use when:** Button inputs, mechanical switch noise filtering
**Key features:** Configurable stable time, counter-based FSM
**Architecture:** 4-state FSM (STABLE_LOW, COUNTING_HIGH, STABLE_HIGH, COUNTING_LOW) + stability counter

**Learn from this:** FSM design (std_logic_vector states), time-based control

---

### 5. **pulse_stretcher.md** - Retriggerable Timing Pattern
**Complexity:** Medium
**Pattern:** Retriggerable one-shot timer
**Use when:** Extending short pulses, timeout generation
**Key features:** Retriggerable, configurable duration, time/cycle modes
**Architecture:** Down-counter with retriggerable load

**Learn from this:** Retriggerable timing, mode selection

---

## How to Use These Specs

### For Human Users (Learning)

1. **First time?** Start with `edge_detector.md` (simplest pattern)
2. **Need an FSM?** Study `debouncer.md` for FSM structure
3. **Counter-based?** Use `pwm_generator.md` or `pulse_stretcher.md`
4. **CDC required?** Follow `synchronizer.md` pattern

**Pattern matching:**
```
Your component needs → Reference spec to study
---------------------   -----------------------
Edge detection       → edge_detector.md
Clock domain cross   → synchronizer.md
Periodic signal      → pwm_generator.md
Button input         → debouncer.md
Pulse extension      → pulse_stretcher.md
```

### For AI Agents (Pattern Reference)

When asked to design a new component:

1. **Identify pattern category** (utility, FSM, counter, CDC)
2. **Read matching reference spec** for architectural guidance
3. **Follow same structure** (sections, port order, test levels)
4. **Adapt pattern** to new requirements while preserving best practices

**Example agent workflow:**
```
User: "Create a timeout detector"
Agent: Reads pulse_stretcher.md (similar timing pattern)
       Adapts: Countdown → up-count, pulse stretch → timeout flag
       Follows: Same port order, test structure, documentation style
```

---

## Specification Structure Template

All reference specs follow this structure:

```markdown
# Component: [Name]
**Category:** [utilities|debugging|loader]
**Purpose:** [One-line description]

## Requirements
### Functionality (3-5 bullet points)
### Interface (Entity, Generics, Ports in VHDL)
### Behavior (Reset, Enabled, Disabled, Edge cases)

## Testing Requirements
**Test Level:** P1/P2/P3
**Required Tests:** (3-5 essential tests listed)
**Test Values:** (P1/P2/P3 value sets)

## Design Notes
**Architecture:** [High-level approach]
**Dependencies:** [Packages, components]
**Constraints:** [Timing, resources, interfaces]

## Agent Instructions
**Agent 1:** VHDL generation instructions
**Agent 2:** Test design instructions
**Agent 3:** Test runner instructions

## Expected Output Example
[Concrete behavior examples with values]
```

---

## Quality Checklist

Before adding a new spec to `reference/`, verify:

- [ ] All 7 sections complete and detailed
- [ ] VHDL interface fully specified (exact port names, types, widths)
- [ ] FSM states use `std_logic_vector` (NOT enums)
- [ ] Reset behavior clearly documented
- [ ] P1 tests specified (3-5 tests, <20 line output goal)
- [ ] Test values provided (concrete numbers, not ranges)
- [ ] Design rationale explained
- [ ] Agent instructions specific and actionable
- [ ] At least one behavioral example with concrete values

---

## Lifecycle

**Reference specs:**
- ✅ Committed to git (permanent)
- ✅ Updated only for quality improvements
- ❌ Never deleted
- ❌ Never used as "work queue"

**Relationship to other spec directories:**
```
reference/  → Read-only pattern library (git tracked)
pending/    → Active work queue (git tracked, user specs)
completed/  → Implementation archive (git tracked, historical)
```

---

## Contributing New Reference Specs

To add a new reference specification:

1. Implement and test the component first (verify pattern works)
2. Write specification following template above
3. Review against quality checklist
4. Add to this README with pattern description
5. Commit to `reference/` directory

**Suggested future patterns:**
- SPI controller (serial protocol pattern)
- UART transmitter (baud rate + FIFO pattern)
- Configurable filter (arithmetic + state machine pattern)
- Watchdog timer (timeout + reset pattern)

---

## See Also

- `workflow/specs/README.md` - Overview of all spec directories
- `workflow/specs/pending/README.md` - Active work queue
- `workflow/README.md` - Complete workflow guide
- `CLAUDE.md` - VHDL coding standards and testing patterns
