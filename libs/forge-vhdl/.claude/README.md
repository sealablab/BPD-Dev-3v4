# AI-Assisted VHDL Development Workflow

This directory contains specialized AI agents for autonomous VHDL component development.

---

## The Four-Agent Workflow

```
┌──────────────────────────────────────────────────────────┐
│  0. forge-new-component                                  │
│     Requirements elicitation & placeholder generation     │
│     Output: .md placeholder files with specifications    │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  1. forge-vhdl-component-generator                       │
│     VHDL-2008 code generation                            │
│     Output: .vhd files (removes .md placeholders)        │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  2. cocotb-progressive-test-designer                     │
│     Test architecture design (P1/P2/P3)                  │
│     Output: Test strategy, expected values, wrappers     │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  3. cocotb-progressive-test-runner                       │
│     Test implementation & execution                       │
│     Output: Working test suite, passing tests            │
└──────────────────────────────────────────────────────────┘
```

---

## Agent Descriptions

### Agent 0: forge-new-component

**Location:** `agents/forge-new-component/agent.md`

**Purpose:** Requirements elicitation and file structure scaffolding

**When to use:**
- Starting a new VHDL component from scratch
- Complex components with unclear requirements
- Need to coordinate multiple agents in parallel

**What it does:**
- Asks clarifying questions about functionality, interfaces, test complexity
- Creates `.md` placeholder files (e.g., `forge_util_pwm.vhd.md`)
- Each placeholder specifies which agent should implement it
- Scaffolds complete file structure before implementation

**Outputs:**
- VHDL placeholders (`vhdl/components/*/*.vhd.md`)
- Test placeholders (`cocotb_tests/components/*/P1_*.py.md`)
- Constants placeholders (`*_constants.py.md`)

---

### Agent 1: forge-vhdl-component-generator

**Location:** `agents/forge-vhdl-component-generator/agent.md`

**Purpose:** VHDL-2008 code generation with GHDL awareness

**When to use:**
- Implementing VHDL from placeholder specifications
- Generating utilities, packages, or components
- Direct implementation (if requirements already clear)

**What it does:**
- Generates synthesis-ready VHDL-2008 code
- Follows coding standards (FSM encoding, port order, reset hierarchy)
- GHDL-compatible patterns (2-cycle waits for registered outputs)
- Zero platform dependencies (Moku/probe agnostic)

**Outputs:**
- VHDL entities and architectures (`.vhd` files)
- Removes placeholder `.md` files after generation

---

### Agent 2: cocotb-progressive-test-designer

**Location:** `agents/cocotb-progressive-test-designer/agent.md`

**Purpose:** Test architecture design for progressive testing (P1/P2/P3)

**When to use:**
- After VHDL component is implemented
- Need test strategy for new component
- Designing test wrappers for forbidden types (real, boolean)

**What it does:**
- Analyzes VHDL entity for CocoTB compatibility
- Designs P1 (2-4 tests, <20 lines), P2 (5-10 tests), P3 (comprehensive)
- Calculates expected values matching VHDL arithmetic
- Designs test wrappers if needed
- Creates constants file structure

**Outputs:**
- Test architecture document
- Test strategy (which tests, what values, what order)
- Expected value calculations
- Constants file design
- Test wrapper VHDL design (if needed)

---

### Agent 3: cocotb-progressive-test-runner

**Location:** `agents/cocotb-progressive-test-runner/agent.md`

**Purpose:** Test implementation and execution with CocoTB + GHDL

**When to use:**
- After test designer has created architecture
- Implementing tests from design specs
- Debugging test failures

**What it does:**
- Implements Python test code from designer's architecture
- Creates constants files with helper functions
- Implements P1/P2/P3 test modules
- Runs tests via CocoTB + GHDL
- Debugs failures (timing, type access, expected values)

**Outputs:**
- Working test suite (`cocotb_tests/components/*/`)
- Constants file (`.py`)
- Test modules (`P1_*_basic.py`, etc.)
- Test orchestrator (`test_*_progressive.py`)
- Test execution results

---

## Usage Patterns

### Pattern 1: New Component (Full Workflow)

```
User: "I need a PWM generator"
  ↓
Agent 0: forge-new-component
  - Asks: Frequency range? Duty cycle resolution? Interfaces?
  - Creates: forge_util_pwm.vhd.md, P1_forge_util_pwm_basic.py.md, etc.
  ↓
Agent 1: forge-vhdl-component-generator
  - Reads: forge_util_pwm.vhd.md
  - Creates: forge_util_pwm.vhd (removes .md)
  ↓
Agent 2: cocotb-progressive-test-designer
  - Reads: forge_util_pwm.vhd
  - Designs: Test architecture, expected values
  ↓
Agent 3: cocotb-progressive-test-runner
  - Reads: Test architecture
  - Creates: Working test suite
  - Runs: Tests and reports results
```

### Pattern 2: Direct Implementation (Clear Requirements)

```
User: "Generate 16-bit up/down counter with overflow"
  ↓
Agent 1: forge-vhdl-component-generator (skip agent 0)
  - Creates: forge_util_counter.vhd directly
  ↓
Agent 2: cocotb-progressive-test-designer
  - Designs: Test architecture
  ↓
Agent 3: cocotb-progressive-test-runner
  - Implements and runs tests
```

### Pattern 3: Test Only (VHDL Already Exists)

```
User: "Add tests for existing forge_util_clk_divider"
  ↓
Agent 2: cocotb-progressive-test-designer (skip agents 0-1)
  - Reads: existing VHDL
  - Designs: Test architecture
  ↓
Agent 3: cocotb-progressive-test-runner
  - Implements and runs tests
```

---

## Key Principles

**1. Agent Specialization**
- Each agent has a specific role (plan, implement VHDL, design tests, run tests)
- Clear handoff protocols between agents
- Each agent knows its predecessor and successor

**2. Placeholder-Driven Development**
- Agent 0 creates `.md` placeholders with detailed specs
- Downstream agents read placeholders, implement, and remove `.md` extension
- Placeholders enable parallel agent execution

**3. Progressive Testing (P1/P2/P3)**
- P1: 2-4 tests, <20 line output, <5s runtime (LLM-optimized)
- P2: 5-10 tests, <50 lines, <30s (standard validation)
- P3: 10-25 tests, <100 lines, <2min (comprehensive)
- 98% output reduction via GHDL filtering

**4. GHDL Awareness**
- All agents know critical GHDL gotchas
- 2-cycle waits for registered outputs
- CocoTB type constraints (no real, boolean, natural at ports)
- Test wrappers for forbidden types

**5. Standalone Focus**
- No monorepo dependencies
- No platform-specific knowledge (Moku, probes)
- Reusable VHDL components and test infrastructure

---

## Quick Start

**For new components:**
```
1. Start with agent 0 (forge-new-component)
2. Let it ask clarifying questions
3. Review generated placeholders
4. Invoke subsequent agents sequentially or in parallel
```

**For clear requirements:**
```
1. Skip to agent 1 (forge-vhdl-component-generator)
2. Provide detailed spec directly
3. Continue to agents 2-3 for testing
```

**For testing existing VHDL:**
```
1. Skip to agent 2 (cocotb-progressive-test-designer)
2. Point to existing .vhd file
3. Continue to agent 3 for test implementation
```

---

## Agent Coordination

**Sequential Execution (Recommended for Complex Components):**
```
Agent 0 → Agent 1 → Agent 2 → Agent 3
(Each completes before next starts)
```

**Parallel Execution (For Independent Tasks):**
```
Agent 0 creates placeholders
  ↓
Agent 1 (VHDL) ║ Agent 2 (Test Design)
(Run in parallel) ║ (Run in parallel)
  ↓              ↓
      Agent 3 (Test Runner)
    (Waits for both)
```

**Manual Implementation:**
- Placeholders can be implemented by hand
- Remove `.md` extension when done
- Agents provide specifications, user provides implementation

---

## Documentation Hierarchy

**Tier 1 (Quick Start):**
- This README.md - Workflow overview
- Individual agent README.md files - Agent summaries

**Tier 2 (Complete Reference):**
- Agent `agent.md` files - Full prompts with examples
- `CLAUDE.md` - Testing standards, architecture patterns

**Tier 3 (Implementation Details):**
- `docs/VHDL_CODING_STANDARDS.md` - Coding rules
- `docs/COCOTB_TROUBLESHOOTING.md` - Debugging guide
- Source code and examples

---

**Last Updated:** 2025-11-09
**Version:** 3.2.0
**Agent Count:** 4 (forge-new-component, forge-vhdl-component-generator, cocotb-progressive-test-designer, cocotb-progressive-test-runner)
**Status:** ✅ Production-ready, template-ready
**Template Origin:** https://github.com/vmars-20/forge-vhdl-3v3-vmars
**Example Workflow:** See `claude` branch for complete execution example
