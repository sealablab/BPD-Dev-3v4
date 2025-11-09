# Pending Component Specifications

**Purpose:** Active work queue for specifications waiting to be implemented

**Status:** Ready for automated agent workflow (Agents 1-3)

---

## What Goes Here?

User-created specifications that are ready to be implemented:

✅ Created via `/gather-requirements` interactive session
✅ Manually written following `workflow/specs/README.md` template
✅ Complete and validated (ready for agents to read)
❌ NOT reference specs (those go in `workflow/specs/reference/`)
❌ NOT implemented components (those go in `workflow/specs/completed/`)

---

## Current Specifications

### ✅ Ready for Implementation (Moved to Reference)

**NOTE:** The original 4 example specs have been promoted to `workflow/specs/reference/` as gold-standard patterns:

1. **edge_detector.md** → NOW IN `reference/` (simple utility pattern)
2. **synchronizer.md** → NOW IN `reference/` (CDC pattern)
3. **debouncer.md** → NOW IN `reference/` (FSM pattern)
4. **pulse_stretcher.md** → NOW IN `reference/` (retriggerable timing pattern)

**These specs remain in pending/ for backward compatibility but should be deleted after confirming reference/ copies.**

---

## How to Add New Specifications

### Method 1: Interactive Gathering (Recommended)

**Start conversational requirements gathering with Claude:**
```
"I want to create a new VHDL component. Please read workflow/INTERACTIVE_REQUIREMENTS.md and guide me through the 7-phase requirements gathering process."
```

This conversational approach:
- Walks through 7-phase Q&A session (30 questions)
- Validates answers against VHDL-FORGE standards
- Generates complete specification
- Saves to `workflow/specs/pending/[component].md`

**Note:** Slash commands like `/gather-requirements` don't work in Claude Code Web. Use conversational approach instead.

### Method 2: Manual Authoring

1. Browse `workflow/specs/reference/` for pattern examples
2. Copy template from `workflow/specs/README.md`
3. Write specification following the structure
4. Save to `workflow/specs/pending/[component].md`

---

## How to Implement Specifications

### Option 1: Full Automated Workflow (Recommended)

**In Claude Code:**
```
Read workflow/specs/pending/[component].md and execute the complete 3-agent workflow:
1. Generate VHDL component (Agent 1: forge-vhdl-component-generator)
2. Design test architecture (Agent 2: cocotb-progressive-test-designer)
3. Implement and run CocoTB tests (Agent 3: cocotb-progressive-test-runner)
```

**Agents run autonomously**, generating files in `workflow/artifacts/`

### Option 2: Manual Implementation

1. Read the specification
2. Implement VHDL manually in `vhdl/components/utilities/`
3. Implement tests manually in `cocotb_tests/components/`
4. Mark spec as completed (move to `workflow/specs/completed/`)

### Option 3: Partial Automation

Use individual agents:
- **Agent 1 only:** Generate VHDL, write tests manually
- **Agents 2-3:** Design and run tests for existing VHDL
- **Agent 0 first:** Refine spec before implementation

## Specification Quality

All specs in this directory include:
- ✅ Complete port lists with types and widths
- ✅ Reset and enable behavior documented
- ✅ Test level and required tests specified
- ✅ Design notes and architectural guidance
- ✅ Agent-specific instructions
- ✅ Example behaviors and use cases

## Creating New Specifications

### Method 1: Use Slash Command (Recommended)

```
/gather-requirements
```

This launches an interactive session that:
- Asks structured questions about your component
- Validates answers against VHDL-FORGE standards
- Generates a complete specification document
- Provides next steps for implementation

### Method 2: Manual Authoring

1. Copy `workflow/specs/examples/pwm_generator.md` as template
2. Fill in all sections (see `workflow/specs/README.md`)
3. Validate with checklist in specs README
4. Save in this directory

## Specification Lifecycle

```
reference/  → Read for patterns (gold-standard library)
     ↓
  (user creates new spec, saves to pending/)
     ↓
pending/    → Active work queue (YOU ARE HERE)
     ↓
  (agents 1-3 generate VHDL + tests → artifacts/)
     ↓
  (user reviews artifacts/, integrates to codebase)
     ↓
completed/  → Archive (implementation done)
```

**Directory purposes:**
- **reference/** - Gold-standard patterns (never deleted, always in git)
- **pending/** - Work queue (user specs awaiting implementation)
- **completed/** - Historical archive (implementation done, moved to codebase)

## Next Steps After Implementation

1. **Review artifacts:**
   ```bash
   ls workflow/artifacts/vhdl/
   ls workflow/artifacts/tests/
   ```

2. **Move to main codebase:**
   ```bash
   mv workflow/artifacts/vhdl/[component].vhd vhdl/components/utilities/
   mv workflow/artifacts/tests/[component]_tests cocotb_tests/components/
   ```

3. **Archive specification:**
   ```bash
   mv workflow/specs/pending/[component].md workflow/specs/completed/
   ```

4. **Commit to git:**
   ```bash
   git add vhdl/components/utilities/[component].vhd
   git add cocotb_tests/components/[component]_tests
   git commit -m "feat: Add [component] with CocoTB tests"
   ```

## See Also

- `workflow/specs/README.md` - Specification writing guide
- `workflow/specs/examples/` - Reference examples
- `.claude/commands/gather-requirements.md` - Interactive spec generator
- `workflow/README.md` - Complete workflow guide
