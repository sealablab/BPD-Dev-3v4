# forge-vhdl: Environment-Aware VHDL Development

**Version:** 3.3.0-multi-tenant
**Purpose:** Auto-detecting VHDL framework with AI-assisted development
**Deployment:** Local CLI or Cloud (auto-configured)

---

## ⚡ CLAUDE: FIRST ACTION REQUIRED

**CRITICAL:** Before doing anything else in this session, you MUST run environment detection to determine the correct workflow path.

**Action:** Execute this command immediately:

```bash
uv run python .claude/env_detect.py
```

**Purpose:**
- Detect runtime environment (Local CLI vs Cloud)
- Verify GHDL installation status
- Route to correct environment-specific guide

**After running detection:**
- 💻 **Local environment** → Read `.claude/CLAUDE_LOCAL.md` for local-specific instructions
- 🌐 **Cloud environment** → Read `.claude/CLAUDE_CLOUD.md` for cloud-specific instructions

**DO NOT** proceed with any VHDL tasks until environment is detected and the appropriate guide is loaded.

---

## 🎯 START HERE (User Guide)

This repository automatically configures itself based on your environment. Read this section first, then jump to your environment-specific guide.

### Environment Detection

Run this command to see your detected environment:

```bash
uv run python .claude/env_detect.py
```

**You'll see one of these:**

**💻 Local Environment (Claude Code CLI)**
```
╔════════════════════════════════════════════════════════════════════╗
║  💻 LOCAL ENVIRONMENT DETECTED                                     ║
║  ✅ GHDL Found: GHDL X.X.X                                         ║
║  Before we start, verify your output settings: /config             ║
╚════════════════════════════════════════════════════════════════════╝
```
→ **Next:** Read [`.claude/CLAUDE_LOCAL.md`](.claude/CLAUDE_LOCAL.md)

**🌐 Cloud Environment (Claude Web / Codespaces)**
```
╔════════════════════════════════════════════════════════════════════╗
║  🌐 CLOUD ENVIRONMENT DETECTED                                     ║
║  ✅ GHDL Found: GHDL X.X.X (pre-installed)                         ║
║  Ready for VHDL development! Using cloud workflow.                 ║
╚════════════════════════════════════════════════════════════════════╝
```
→ **Next:** Read [`.claude/CLAUDE_CLOUD.md`](.claude/CLAUDE_CLOUD.md)

---

## 📖 Environment-Specific Guides

**Choose your guide:**

| Environment | Guide | Key Features |
|-------------|-------|--------------|
| 💻 **Local CLI** | [CLAUDE_LOCAL.md](.claude/CLAUDE_LOCAL.md) | Output settings validation • Interactive requirements • **Cloud handoff for agents** |
| 🌐 **Cloud/Codespaces** | [CLAUDE_CLOUD.md](.claude/CLAUDE_CLOUD.md) | GHDL auto-install • Zero setup • **Agent execution** |

---

## 🔄 Hybrid Workflow (RECOMMENDED for Local Users)

**Best practice:** Use each environment for what it does best!

### Local CLI → Requirements Gathering

**Strengths:**
- ✅ Fast interactive prompts (output settings control)
- ✅ Quick terminal I/O for questions
- ✅ Familiar local git workflow
- ✅ `/forge-start` command for guided workflow

**Use for:**
1. Run `/forge-start` to choose workflow (Student/Engineer)
2. Answer requirements questions (2-5 min or 15-30 min)
3. Review generated specification
4. Commit spec to git

### Claude Web → Agent Execution

**Strengths:**
- ✅ No token limits per message (agents run fully)
- ✅ Zero GHDL setup (auto-installs in cloud)
- ✅ Autonomous debugging and iteration
- ✅ Incremental git commits (audit trail)

**Use for:**
1. Open Claude Web (https://claude.ai/code/)
2. Select repository from dropdown + choose cloud environment
3. Say: "Read workflow/specs/pending/[component].md and execute 3-agent workflow"
4. Agents run autonomously in sandbox branch (`claude/xxxxyyyy`):
   - Agent 1: Generate VHDL
   - Agent 2: Design tests
   - Agent 3: Implement & run tests (with incremental commits!)
5. Pull results back locally (auto-merges sandbox work to main)

### Local CLI → Integration

**Strengths:**
- ✅ Review generated artifacts
- ✅ Run tests locally
- ✅ Integrate to production codebase
- ✅ Commit final work

**Complete pattern:**
```bash
# Local: Generate spec
/forge-start → Answer questions → Spec created

# Local: Commit & push spec
git add workflow/specs/pending/
git commit -m "spec: Add [component]"
git push

# Cloud: Run agents (in Claude Web browser)
# Navigate to https://claude.ai/code/
# Select your repository + cloud environment (see static/Claude-WEB-ui-new-session.png)
# Say: "Read workflow/specs/pending/[component].md and execute 3-agent workflow"
# Agents work in sandbox branch (claude/xxxxyyyy) with incremental commits

# Local: Pull & integrate
git pull  # Auto-merges sandbox branch work to main
mv workflow/artifacts/vhdl/[component].vhd vhdl/components/[category]/
# Tests already in cocotb_tests/
```

**Why this works:**
- **Local CLI** = Interactive gathering (fast, controlled)
- **Claude Web** = Long-running agents (unlimited, autonomous, sandbox branch isolation)
- **Local CLI** = Final review (familiar tooling)

**Note:** Claude Web always starts from `main` branch (no branch selection in UI). It creates a temporary sandbox branch (`claude/xxxxyyyy`) that automatically merges back when you pull.

---

## ⚡ Quick Start (30 seconds)

**1. Detect environment:**
```bash
uv run python .claude/env_detect.py
```

**2. Read environment-specific guide (link above)**

**3. Try your first component:**
```
"I need a PWM generator. Use the AI-First requirements workflow."
```

Claude will gather requirements (2-3 questions), generate specification, create VHDL + tests automatically.

---

## 🧭 Project Overview

**forge-vhdl** = Cloud-first VHDL framework for Moku custom instruments

**Key Innovation:**
98% test output reduction (287 lines → 8 lines) via GHDL filtering + progressive test levels (P1/P2/P3)

**Two Workflows:**
- **AI-First** (students/beginners): 2-5 min, pattern-matched, intelligent defaults
- **Engineer** (advanced): 15-30 min, 30-question Q&A, full control

**Testing Standard:**
P1 tests must output <20 lines (LLM-optimized for fast iteration)

---

## 📚 Documentation Architecture

**Tier 1: Quick Reference**
- `llms.txt` - Component catalog (~800 tokens)

**Tier 2: Environment Guides** (Start here!)
- **CLAUDE_LOCAL.md** - Local development (output config, interactive workflow)
- **CLAUDE_CLOUD.md** - Cloud development (GHDL auto-install, streamlined)
- **CLAUDE.md (this file)** - Router/index for all environments

**Tier 3: Detailed References** (load as needed)
- `docs/VHDL_CODING_STANDARDS.md` - Complete style guide (600 lines)
- `docs/PROGRESSIVE_TESTING_GUIDE.md` - Test design patterns
- `docs/COCOTB_TROUBLESHOOTING.md` - Problem→solution debugging
- `workflow/specs/reference/` - 5 gold-standard component specifications

---

## 🎓 Common Patterns

### Requirements Gathering

**AI-First (DEFAULT for students):**
```
"I need a [component]. Use the AI-First requirements workflow."
```
- 2-3 critical questions only
- Pattern recognition fills in the rest
- 2-5 minutes → complete specification

**Engineer (for advanced control):**
```
"Read workflow/ENGINEER_REQUIREMENTS.md and guide me through requirements."
```
- 30-question structured interview
- 7 phases (identification → functionality → interface → behavior → testing → design → generation)
- 15-30 minutes → detailed specification

**Reference Specs (learn from examples):**
```
"Read workflow/specs/reference/edge_detector.md and execute the 3-agent workflow"
```
- 5 proven patterns: edge_detector, synchronizer, pwm_generator, debouncer, pulse_stretcher
- Gold-standard examples for learning

### Development Workflow

```
Requirements Gathering (AI-First or Engineer)
   ↓ workflow/specs/pending/[component].md
Agent 1: forge-vhdl-component-generator
   ↓ VHDL entity/architecture
Agent 2: cocotb-progressive-test-designer
   ↓ Test architecture + strategy
Agent 3: cocotb-progressive-test-runner
   ↓ Working tests, execution results
```

---

## 🔧 VHDL Standards (Quick Reference)

**Mandatory Rules:**

| Rule | Correct ✅ | Wrong ❌ |
|------|-----------|----------|
| **FSM States** | `constant STATE_IDLE : std_logic_vector(1 downto 0) := "00";` | `type state_t is (IDLE, ARMED);` ← NO ENUMS! |
| **Port Order** | clk, rst_n, clk_en, enable, data, status | Random order |
| **Reset Hierarchy** | `if rst_n = '0' then ... elsif clk_en = '1' then ... elsif enable = '1'` | Flat structure |
| **Signal Prefixes** | `ctrl_`, `cfg_`, `stat_`, `dbg_` | No prefixes |

**Why?**
- Verilog compatibility (enums don't translate)
- Synthesis predictability (explicit encoding)
- Safety (reset hierarchy prevents unsafe states)

**Full guide:** `docs/VHDL_CODING_STANDARDS.md`

---

## 🧪 Testing Standards (Quick Reference)

**Progressive Test Levels:**

| Level | Tests | Output | Runtime | When to use |
|-------|-------|--------|---------|-------------|
| **P1** | 2-4 essential | <20 lines | <5 sec | **Default** (LLM-optimized) |
| **P2** | 5-10 with edges | <50 lines | <30 sec | Standard validation |
| **P3** | 15-25 comprehensive | <100 lines | <2 min | Full coverage |
| **P4** | Unlimited | No limit | No limit | Debug mode |

**Golden Rule:** If P1 output > 20 lines, you're doing it wrong!

**Running tests:**
```bash
# P1 (default)
uv run python cocotb_tests/run.py <component>

# P2
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py <component>
```

**Full guide:** `docs/PROGRESSIVE_TESTING_GUIDE.md`

---

## 📦 Component Catalog (Summary)

**Utilities** (`vhdl/utilities/`)
- `forge_util_clk_divider` - Programmable clock divider (P1/P2 tests ✓)

**Voltage Packages** (`vhdl/packages/`)
- `forge_voltage_3v3_pkg` - 0-3.3V (TTL, GPIO) (P1/P2 tests ✓)
- `forge_voltage_5v0_pkg` - 0-5.0V (sensor supply) (P1/P2 tests ✓)
- `forge_voltage_5v_bipolar_pkg` - ±5.0V (Moku DAC/ADC - **most common**) (P1/P2 tests ✓)

**LUT Utilities** (`vhdl/packages/`)
- `forge_lut_pkg` - Voltage/index conversion (P1/P2/P3 tests ✓)

**Debugging** (`vhdl/debugging/`)
- `forge_hierarchical_encoder` - FSM state encoding for oscilloscope (P1 tests ✓)

**Full catalog:** `llms.txt`

---

## 🐛 Troubleshooting

**Environment detection issues:**
```bash
uv run python .claude/env_detect.py
```

**GHDL not found (local):**
```bash
# macOS
brew install ghdl

# Ubuntu/Debian
sudo apt-get install ghdl ghdl-llvm
```

**GHDL not found (cloud):**
```bash
# Auto-install (cloud only)
uv run python scripts/cloud_setup_with_ghdl.py
```

**Test output too verbose:**
- Check `GHDL_FILTER_LEVEL=aggressive` (default for P1)
- Check `TEST_LEVEL=P1_BASIC` (or unset)
- See `docs/PROGRESSIVE_TESTING_GUIDE.md`

**CocoTB can't access signal:**
- Error: `'HierarchyObject' object has no attribute 'value'`
- Cause: Using `real`, `boolean`, `time`, or custom records in entity ports
- Solution: Use test wrapper with `std_logic_vector` / `signed` / `unsigned`
- See `docs/COCOTB_TROUBLESHOOTING.md` Section 0

---

## 🎯 Next Steps

1. **Detect your environment:** `uv run python .claude/env_detect.py`
2. **Read your environment guide:**
   - Local → `.claude/CLAUDE_LOCAL.md`
   - Cloud → `.claude/CLAUDE_CLOUD.md`
3. **Try a component:** "I need a PWM generator. Use the AI-First workflow."
4. **Review artifacts:** `workflow/artifacts/vhdl/` and `workflow/artifacts/tests/`
5. **Run tests:** Ensure P1 output <20 lines
6. **Commit to git**

---

## 📁 Documentation Index

**Environment Guides** (primary references)
- `.claude/CLAUDE_LOCAL.md` - Local development guide
- `.claude/CLAUDE_CLOUD.md` - Cloud development guide

**Workflow Guides**
- `workflow/AI_FIRST_REQUIREMENTS.md` - Fast requirements (2-5 min)
- `workflow/ENGINEER_REQUIREMENTS.md` - Detailed requirements (15-30 min)
- `workflow/specs/reference/` - 5 gold-standard examples

**Technical References**
- `docs/VHDL_CODING_STANDARDS.md` - Complete style guide (600 lines)
- `docs/VHDL_QUICK_REF.md` - Templates and checklists
- `docs/PROGRESSIVE_TESTING_GUIDE.md` - Test design patterns
- `docs/COCOTB_TROUBLESHOOTING.md` - Debugging guide

**Agent Definitions**
- `.claude/agents/forge-vhdl-component-generator/agent.md`
- `.claude/agents/cocotb-progressive-test-designer/agent.md`
- `.claude/agents/cocotb-progressive-test-runner/agent.md`

---

**Last Updated:** 2025-11-09
**Version:** 3.3.0-multi-tenant (environment-aware, slim router, template-ready)
**Original Template:** https://github.com/vmars-20/forge-vhdl-3v3-vmars
**Maintainer:** Moku Instrument Forge Team

**Quick links:**
- [Local Development Guide](.claude/CLAUDE_LOCAL.md)
- [Cloud Development Guide](.claude/CLAUDE_CLOUD.md)
- [Component Catalog](llms.txt)
- [Reference Specifications](workflow/specs/reference/)
- [Example Workflow](../../tree/claude) - Complete 3-agent execution on `claude` branch

**Post-Template Checklist:**
- Update README.md with your repository URL (lines 47, 51, 500)
- Run environment detection: `uv run python .claude/env_detect.py`
- Read your environment-specific guide (CLAUDE_LOCAL.md or CLAUDE_CLOUD.md)
- Check `claude` branch for workflow example: `git fetch origin claude`
