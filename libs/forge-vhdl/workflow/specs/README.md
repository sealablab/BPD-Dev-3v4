# Component Specification Guide

**Purpose:** Write specifications that agents can read and implement

**Target:** Component specs in markdown format

---

## Directory Structure (3-Tier System)

```
workflow/specs/
├── reference/     # Gold-standard pattern library (5 specs, read-only)
├── pending/       # Active work queue (user specs awaiting implementation)
├── completed/     # Implementation archive (specs for completed components)
└── README.md      # This file
```

**Quick navigation:**
- **Browse patterns?** → `reference/README.md` (edge detector, synchronizer, PWM, debouncer, pulse stretcher)
- **Create new spec?** → `pending/README.md` (interactive gathering or manual authoring)
- **Archive completed work?** → `completed/README.md` (move specs after implementation)

---

## Spec Template

Save as `specs/pending/your_component.md`:

```markdown
# Component: [Name]

**Category:** [utilities|debugging|loader]
**Purpose:** [One-line description]

---

## Requirements

### Functionality
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

### Interface

**Entity:** [component_name]

**Generics (if any):**
- `GENERIC_NAME : type := default` - Description

**Ports:**
```vhdl
-- Clock & Reset
clk   : in std_logic;
rst_n : in std_logic;

-- Control
enable : in std_logic;

-- Data
data_in  : in std_logic_vector(15 downto 0);
data_out : out std_logic_vector(15 downto 0);

-- Status
busy : out std_logic;
```

### Behavior
- **Reset:** [What happens on reset]
- **Enabled:** [What happens when enabled]
- **Disabled:** [What happens when disabled]
- **Edge cases:** [Boundary conditions, special cases]

---

## Testing Requirements

**Test Level:** [P1|P2|P3]
- P1: 2-4 essential tests (<20 line output, <5s)
- P2: 5-10 comprehensive tests (<50 lines, <30s)
- P3: 15-25 exhaustive tests (<100 lines, <2min)

**Required Tests:**
1. test_reset - Verify reset behavior
2. test_[core_function] - Essential functionality
3. test_[edge_case] - Boundary conditions

**Test Values:**
- P1: Small, fast values (cycles=20)
- P2: Realistic values
- P3: Stress testing values

---

## Design Notes

**Architecture:** [High-level design approach]
- [Design decision 1]
- [Design decision 2]

**Dependencies:**
- Package: [package name] - [why needed]
- Component: [component name] - [why needed]

**Constraints:**
- [Timing constraint]
- [Resource constraint]
- [Interface constraint]

---

## Agent Instructions

**Agent 1 (VHDL Generator):**
- Generate entity + architecture
- Follow VHDL-2008 standards
- Use std_logic_vector for FSM states (not enums)
- Output to: `workflow/artifacts/vhdl/[component_name].vhd`

**Agent 2 (Test Designer):**
- Design [P1|P2|P3] test architecture
- Calculate expected values (match VHDL arithmetic)
- Design test wrapper if real/boolean types used
- Output test strategy to: `workflow/artifacts/tests/test_strategy.md`

**Agent 3 (Test Runner):**
- Implement tests from Agent 2's strategy
- Run P1 tests via CocoTB + GHDL
- Debug failures (timing, types, expected values)
- Output to: `workflow/artifacts/tests/[component_name]_tests/`

---

## Example Values

For this component, use these test values:

**P1 (Fast):**
- [Value set 1]

**P2 (Realistic):**
- [Value set 2]

**P3 (Stress):**
- [Value set 3]
```

---

## Specification Lifecycle

```
reference/  → Browse for patterns (gold-standard examples)
     ↓
  (user creates new spec based on pattern)
     ↓
pending/    → Active work queue (spec ready for implementation)
     ↓
  (agents 1-3: generate VHDL + tests → workflow/artifacts/)
     ↓
  (user reviews artifacts/, integrates to main codebase)
     ↓
completed/  → Archive (historical record)
```

**Directory purposes:**
- **reference/** - Never deleted, always in git, quality benchmarks
- **pending/** - Transient work queue, gets cleared as implemented
- **completed/** - Historical archive, shows what was built

---

## Real Examples

See `reference/` directory for 5 gold-standard specifications:
- `reference/edge_detector.md` - Simple utility pattern
- `reference/synchronizer.md` - CDC pattern
- `reference/pwm_generator.md` - Counter-based pattern
- `reference/debouncer.md` - FSM pattern
- `reference/pulse_stretcher.md` - Retriggerable timing pattern

---

## Tips

### Good Specs
- ✅ Specific port names and widths
- ✅ Clear reset/enable behavior
- ✅ Test complexity level specified
- ✅ Example test values provided
- ✅ Design constraints documented

### Bad Specs
- ❌ Vague interfaces ("some inputs and outputs")
- ❌ No test requirements
- ❌ Missing reset behavior
- ❌ Ambiguous functionality

### Common Patterns

**Clocked Component:**
```vhdl
-- Always include
clk   : in std_logic;
rst_n : in std_logic;  -- Active-low reset

-- Often include
enable : in std_logic;
```

**FSM Component:**
```vhdl
-- CRITICAL: Use std_logic_vector, NOT enums!
constant STATE_IDLE : std_logic_vector(1 downto 0) := "00";
constant STATE_BUSY : std_logic_vector(1 downto 0) := "01";

signal state : std_logic_vector(1 downto 0);
```

**Package Testing:**
- Package functions need test wrappers (CocoTB can't test packages directly)
- Specify wrapper design in spec

---

## Validation Checklist

Before running agents, verify your spec has:

- [ ] Clear component name
- [ ] Category specified (utilities/debugging/loader)
- [ ] Complete port list with types
- [ ] Reset behavior documented
- [ ] Test level specified (P1/P2/P3)
- [ ] At least 3 required tests listed
- [ ] Design notes (architecture approach)

---

## Next Steps

1. Write spec in `specs/pending/`
2. Validate with checklist above
3. Run workflow (see `workflow/README.md`)
4. Review artifacts
5. Move to codebase
