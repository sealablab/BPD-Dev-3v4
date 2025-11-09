# Context Management Strategy

**Version:** 2.0
**Purpose:** Token optimization and tiered loading for AI agents
**Audience:** AI agents (Claude, Copilot, Cursor) working in this repository

---

## Overview

This repository uses a **three-tier context loading strategy** to optimize token usage while ensuring AI agents have necessary information at the right time.

**Token Budget:** 200k tokens total
- System + tools: ~16k tokens (8%)
- Target for messages: ~100k tokens (50%)
- Reserved buffer: ~84k tokens (42%)

**Problem:** Loading all documentation upfront wastes tokens on information not needed for current task.

**Solution:** Tiered loading - start minimal, drill down as needed.

---

## Three-Tier Loading Strategy

### Tier 1: Always Load First (~500-1000 tokens)

**Purpose:** Quick orientation, navigation to deeper context

**Load these first:**
1. **`llms.txt`** (~500 tokens)
   - Repository structure overview
   - Tool selection (Claude/Copilot/Cursor)
   - Component catalog summary
   - Pointer to this document

2. **Tool-specific guide** (based on environment)
   - CLAUDE.md (if using Claude)
   - COPILOT.md (if using GitHub Copilot)
   - CURSOR.md (if using Cursor)

**What you get:**
- High-level architecture
- Where to find detailed info (pointers to Tier 2)
- Common questions answered immediately
- Decision tree for what to load next

**Example - Starting work:**
```
AI Agent loads:
1. llms.txt → "Multi-tenant repo with Claude/Copilot/Cursor support"
2. CLAUDE.md → "I'm using Claude, here's my workflow"

AI Agent knows:
- Repository structure (vhdl/, cocotb_tests/, workflow/)
- Available components (clock divider, voltage packages)
- Where to find standards (docs/VHDL_CODING_STANDARDS.md)
- How to run tests (uv run python cocotb_tests/run.py)
```

---

### Tier 2: Load When Designing/Integrating (~2000-5000 tokens)

**Purpose:** Deep context for specific domains, workflow details

**Load these when:**
- Starting requirements gathering (need workflow details)
- Designing new VHDL components (need standards)
- Setting up testing (need progressive test patterns)
- Debugging integration issues (need troubleshooting guides)

**Tier 2 Documents:**

1. **Workflow Documents**
   - `workflow/AI_FIRST_REQUIREMENTS.md` - Fast requirements (2-5 min)
   - `workflow/ENGINEER_REQUIREMENTS.md` - Detailed requirements (15-30 min)
   - `workflow/specs/reference/*.md` - Example specifications

2. **Agent Definitions** (when running agents)
   - `.claude/agents/forge-vhdl-component-generator/agent.md`
   - `.claude/agents/cocotb-progressive-test-designer/agent.md`
   - `.claude/agents/cocotb-progressive-test-runner/agent.md`

3. **Standards & Guides**
   - `docs/VHDL_CODING_STANDARDS.md` - VHDL style guide
   - `docs/PROGRESSIVE_TESTING_GUIDE.md` - Test design patterns
   - `docs/COCOTB_TROUBLESHOOTING.md` - Common issues & fixes

4. **Tool-Specific Configuration**
   - `.github/copilot-instructions.md` - Copilot custom instructions
   - `.vscode/settings.json` - VS Code configuration

**What you get:**
- Design rationale (why these standards?)
- Complete workflows (step-by-step guides)
- Common pitfalls and solutions
- Tool-specific optimizations

**Example - Creating new component:**
```
AI Agent already loaded Tier 1.

User: "I want to create a PWM generator"

AI Agent loads Tier 2:
1. workflow/AI_FIRST_REQUIREMENTS.md → "2-3 questions pattern matching"
2. workflow/specs/reference/pwm_generator.md → "Example PWM spec"
3. docs/VHDL_CODING_STANDARDS.md → "FSM encoding, port ordering rules"

AI Agent now has:
- Requirements gathering pattern
- Example to follow
- Standards to enforce
```

---

### Tier 3: Load For Implementation (~10000+ tokens)

**Purpose:** Source code, implementation details, debugging

**Load these when:**
- Actually writing/editing code
- Debugging specific errors
- Understanding implementation internals
- Running tests

**Tier 3 Sources:**

1. **VHDL Source Files**
   - `vhdl/components/utilities/*.vhd` - Component implementations
   - `vhdl/packages/*.vhd` - Package definitions
   - `vhdl/debugging/*.vhd` - Debug utilities

2. **Test Files**
   - `cocotb_tests/test_*.py` - Test implementations
   - `cocotb_tests/run.py` - Test runner

3. **Generated Artifacts**
   - `workflow/artifacts/vhdl/*.vhd` - Generated VHDL
   - `workflow/artifacts/tests/*.py` - Generated tests
   - `workflow/specs/pending/*.md` - Work in progress specs

**What you get:**
- Actual implementation code
- Test examples
- Line-by-line logic
- Generated outputs to inspect

**Example - Debugging test failure:**
```
AI Agent already loaded Tier 1 & 2.

User: "P1 tests output 287 lines instead of <20"

AI Agent loads Tier 3:
1. cocotb_tests/run.py → "How test filtering works"
2. scripts/ghdl_output_filter.py → "Filter implementation"
3. cocotb_tests/test_forge_util_clk_divider.py → "Example P1 test"

AI Agent can now:
- Trace filtering logic
- Compare working vs failing test
- Identify issue (missing GHDL_FILTER_LEVEL=aggressive)
```

---

## Decision Tree: What to Load When

### Starting a New Task

```
User request arrives
    ↓
Load Tier 1 (always)
    ↓
Is this a quick question? (component lookup, test command, etc.)
    ↓ Yes → Answer from Tier 1
    ↓ No
    ↓
Does this involve requirements/design?
    ↓ Yes → Load Tier 2 (workflows, standards)
    ↓ No
    ↓
Does this involve implementation/debugging?
    ↓ Yes → Load Tier 3 (source code)
```

### Examples by Question Type

**Quick Questions (Tier 1 only):**
- "What components are available?"
  - Answer from llms.txt → "Clock divider, voltage packages, etc."

- "How do I run tests?"
  - Answer from llms.txt → "uv run python cocotb_tests/run.py"

- "Which AI tool should I use?"
  - Answer from README.md → "Claude for autonomous, Copilot for IDE, Cursor for both"

**Design Questions (Tier 1 + 2):**
- "How do I gather requirements?"
  - Tier 1: llms.txt → "AI-First or Engineer workflows"
  - Tier 2: workflow/AI_FIRST_REQUIREMENTS.md → "2-3 questions, pattern matching"

- "What are the VHDL standards?"
  - Tier 1: llms.txt → "See docs/VHDL_CODING_STANDARDS.md"
  - Tier 2: docs/VHDL_CODING_STANDARDS.md → "No enums, port ordering, reset hierarchy"

**Implementation Questions (Tier 1 + 2 + 3):**
- "Generate a PWM controller"
  - Tier 1: llms.txt → "Check workflow/specs/reference/"
  - Tier 2: workflow/specs/reference/pwm_generator.md → "Example specification"
  - Tier 3: vhdl/components/utilities/forge_util_clk_divider.vhd → "Similar implementation"

---

## Token Budget Guidelines

### Conservative Approach (Recommended)

**Always load:**
- Tier 1: ~1k tokens (llms.txt + tool guide)

**Load as needed:**
- Tier 2: Add ~2-5k tokens per document
- Tier 3: Add ~5-10k tokens per source file

**Example budget:**
```
Tier 1: 1k tokens (base)
Tier 2:
  - workflow/AI_FIRST_REQUIREMENTS.md: +2k
  - docs/VHDL_CODING_STANDARDS.md: +3k
Total so far: 6k tokens (3% of budget)

Tier 3 (if needed):
  - vhdl source file: +5k
  - test file: +2k
Total: 13k tokens (6.5% of budget)

Still have 187k tokens available (93.5%)
```

### Aggressive Approach (When Confident)

If you know exactly what's needed:
- Skip Tier 1 navigation, load Tier 2/3 directly
- Useful for follow-up questions in same session

**Example:**
```
User: "Now fix the bit width issue"

AI Agent (already in context):
- Skip Tier 1 (already loaded)
- Skip Tier 2 (already loaded standards)
- Load Tier 3 directly: specific VHDL file

Saves reloading 6k tokens
```

---

## Common Workflows & Token Usage

### Workflow 1: New Component Development

**Steps:**
1. Load Tier 1 (llms.txt, tool guide) ~1k
2. Load Tier 2 (requirements workflow) ~2k
3. User answers questions (no new loading)
4. Load Tier 2 (VHDL standards) ~3k
5. Generate component (no new loading)
6. Load Tier 3 (test examples) ~2k

**Total:** ~8k tokens (4% budget)

---

### Workflow 2: Quick Component Lookup

**Steps:**
1. Load Tier 1 (llms.txt) ~500 tokens
2. Answer from component list

**Total:** ~500 tokens (0.25% budget)

---

### Workflow 3: Debugging Test Issues

**Steps:**
1. Load Tier 1 (llms.txt, tool guide) ~1k
2. Load Tier 2 (COCOTB_TROUBLESHOOTING.md) ~3k
3. Load Tier 3 (test file, run.py) ~4k

**Total:** ~8k tokens (4% budget)

---

## Anti-Patterns to Avoid

### ❌ Loading Everything Upfront
```
AI Agent: "Let me load all docs, all source, all tests..."
Result: 50k+ tokens wasted, nothing left for conversation
```

**Instead:**
```
AI Agent: "Load llms.txt first. User asked about PWM → load PWM-related docs only."
Result: 3k tokens used, 197k available
```

---

### ❌ Re-loading Same Content
```
User: "What about the clock divider?"
AI Agent: Loads docs/VHDL_CODING_STANDARDS.md (3k tokens)

User: "And the PWM?"
AI Agent: Loads docs/VHDL_CODING_STANDARDS.md again (3k tokens wasted)
```

**Instead:**
```
AI Agent: "Already have VHDL standards in context, reference it directly."
Result: 0 additional tokens
```

---

### ❌ Loading Source Code for Questions
```
User: "What testing levels are available?"
AI Agent: Loads all test files (20k tokens)
```

**Instead:**
```
AI Agent: "Check Tier 1: llms.txt has P1/P2/P3 summary."
Result: 500 tokens vs 20k
```

---

## Best Practices

### 1. Start Minimal
Always load Tier 1 first. Don't assume you need deeper context.

### 2. Load Just-In-Time
Load Tier 2/3 only when needed for current question.

### 3. Reuse Context
If already loaded, reference it. Don't reload.

### 4. Prefer Documentation Over Code
Tier 2 (docs) is more concise than Tier 3 (source code).

### 5. Use Tool-Specific Guides
Each tool (Claude/Copilot/Cursor) has optimized workflows.

---

## Special Cases

### Multi-Tool Questions

**User:** "Should I use Claude or Cursor?"

**Approach:**
1. Load Tier 1 (README.md) → "Comparison table"
2. No need for Tier 2/3

**Total:** ~1k tokens for complete answer

---

### Cross-Tool Workflows

**User:** "Use Claude for requirements then Cursor for implementation"

**Approach:**
1. Load Tier 1 (llms.txt)
2. Load Tier 2 (CLAUDE.md) → "Requirements workflow"
3. Load Tier 2 (CURSOR.md) → "Implementation workflow"

**Total:** ~5k tokens for hybrid workflow

---

## Directory-Level Discovery

Each directory contains README.md for progressive discovery:

```
vhdl/README.md              → "VHDL components live here"
vhdl/components/README.md   → "Organized by category"
vhdl/packages/README.md     → "Voltage and utility packages"
cocotb_tests/README.md      → "Progressive test suite"
workflow/README.md          → "Requirements and specs"
docs/README.md              → "Standards and guides"
```

Load these as you navigate deeper into the structure.

---

## Meta-Strategy: When to Use This Document

**Load CONTEXT_MANAGEMENT.md when:**
- Starting a complex multi-file task
- Unsure what documentation to load
- Optimizing token usage
- Training new AI agents

**Don't load when:**
- Simple single-file questions
- Already know exactly what to load
- Following established workflow

---

## Summary

**Three Tiers:**
1. **Tier 1** (~500-1k tokens) - Always load, quick orientation
2. **Tier 2** (~2-5k tokens) - Load for design/workflow
3. **Tier 3** (~5-10k tokens) - Load for implementation

**Decision Tree:**
- Quick question? → Tier 1 only
- Design/workflow? → Tier 1 + 2
- Implementation? → Tier 1 + 2 + 3

**Best Practice:**
Start minimal, load just-in-time, reuse context, prefer docs over code.

---

**Last Updated:** 2025-01-XX
**Version:** 2.0
**Maintained By:** forge-vhdl team