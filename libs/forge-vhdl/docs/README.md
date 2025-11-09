# Documentation Directory

**Where you are:** `/docs/`
**Purpose:** Technical standards, guides, and troubleshooting

## What Should Be Here

This directory contains comprehensive technical documentation:

```
docs/
├── VHDL_CODING_STANDARDS.md      # Complete style guide (600+ lines)
├── VHDL_QUICK_REF.md             # Templates and checklists
├── PROGRESSIVE_TESTING_GUIDE.md  # P1/P2/P3 test patterns
├── COCOTB_TROUBLESHOOTING.md     # Problem→solution guide
└── README.md                      # This file
```

## Key Documents

### VHDL_CODING_STANDARDS.md
**Purpose:** Mandatory VHDL coding rules for all components

**Key Rules:**
- No enums for FSM states (use constants)
- Strict port ordering (clk, rst_n, clk_en, enable, data, status)
- Reset hierarchy (proper nesting)
- Signal prefixes (ctrl_, cfg_, stat_, dbg_)

**When to load:** Before writing any VHDL code

### PROGRESSIVE_TESTING_GUIDE.md
**Purpose:** Design patterns for P1/P2/P3 test levels

**Contents:**
- Test level definitions
- Output filtering strategies
- Test organization patterns
- Coverage guidelines

**When to load:** When designing or debugging tests

### COCOTB_TROUBLESHOOTING.md
**Purpose:** Common CocoTB issues and solutions

**Sections:**
- Section 0: Type access issues ('HierarchyObject' errors)
- GHDL output filtering
- Test discovery problems
- Signal access patterns

**When to load:** When tests fail or behave unexpectedly

### VHDL_QUICK_REF.md
**Purpose:** Quick templates and checklists

**Contents:**
- Entity/architecture templates
- FSM patterns
- Test templates
- Review checklists

**When to load:** Quick syntax reference during coding

## Navigation

- **Up:** Go to repository root
- **Standards:** Start with VHDL_CODING_STANDARDS.md
- **Testing:** See PROGRESSIVE_TESTING_GUIDE.md
- **Examples:** See `/workflow/specs/reference/` for implementations

## AI Agent Notes

**Loading Strategy (from CONTEXT_MANAGEMENT.md):**
- These are Tier 2 documents (~2-5k tokens each)
- Load only when actively needed
- Don't load all at once (wastes tokens)
- Prefer loading specific sections vs entire files

**Common Patterns:**
1. User asks about FSM encoding → Load VHDL_CODING_STANDARDS.md
2. User has test output issues → Load PROGRESSIVE_TESTING_GUIDE.md
3. User gets CocoTB error → Load COCOTB_TROUBLESHOOTING.md
4. User needs template → Load VHDL_QUICK_REF.md

## Quick Reference

### FSM State Encoding (No Enums!)
```vhdl
constant STATE_IDLE  : std_logic_vector(1 downto 0) := "00";
constant STATE_ARMED : std_logic_vector(1 downto 0) := "01";
```

### Port Ordering
```vhdl
clk → rst_n → clk_en → enable → data_in → data_out → status
```

### Test Levels
- P1: 2-4 tests, <20 lines output
- P2: 5-10 tests, <50 lines output
- P3: 15-25 tests, <100 lines output

### Common Issue
```
Error: 'HierarchyObject' object has no attribute 'value'
Solution: VHDL real/boolean types need wrapper
```