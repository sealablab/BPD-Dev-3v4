# forge-vhdl: Cursor Edition

**AI-powered VHDL development optimized for Cursor's multi-agent orchestration**

**Version:** 3.3.0-multi-tenant  
**Purpose:** Full local workflow with multi-agent orchestration  
**Environment:** Cursor IDE (local development with agent orchestration)

---

## 🎯 START HERE (Cursor Users)

This repository is optimized for **Cursor's multi-agent capabilities**, which enable you to run the complete 3-agent workflow **locally** without any cloud handoff. Unlike the hybrid workflow (local requirements → cloud agents), Cursor can orchestrate all agents in one session.

### Key Advantages Over Hybrid Workflow

✅ **Full local execution** - No git push/pull handoff needed  
✅ **Multi-agent orchestration** - Cursor can coordinate agents in sequence  
✅ **Real-time test execution** - Run tests directly and see results immediately  
✅ **Incremental commits** - Make commits as agents complete their work  
✅ **Better IDE integration** - See file changes, test results, and agent progress in real-time  
✅ **No token limits** - Cursor's agent mode handles long-running workflows  

---

## 🚀 Quick Start (3 Steps)

### 1. Open in Cursor

```bash
cursor .
```

### 2. Run Environment Detection

```bash
uv run python .claude/env_detect.py
```

**Expected:** Local environment detected, GHDL found

### 3. Start Multi-Agent Workflow

**Option A: Using Cursor Composer (Recommended)**

Open Cursor Composer (`Cmd+I` or `Ctrl+I`) and say:

```
I need a PWM generator with 8-bit duty cycle control.
Execute the complete 3-agent workflow:
1. Generate specification using AI-First requirements workflow
2. Agent 1: Generate VHDL entity/architecture
3. Agent 2: Design P1 test architecture
4. Agent 3: Implement and run P1 tests
5. Make incremental commits after each agent completes
```

**Option B: Using Cursor Chat with Agent Orchestration**

In Cursor Chat, say:

```
Read workflow/specs/pending/pwm_generator.md (or create it first using AI-First workflow)
Execute the complete 3-agent VHDL development workflow with incremental commits.
```

**Cursor will:**
1. Orchestrate agents in sequence
2. Generate VHDL → Design tests → Implement & run tests
3. Make commits after each agent completes
4. Show test results in real-time
5. Handle any failures and iterate

---

## 🔄 Cursor Multi-Agent Workflow

### Complete Workflow (No Handoff Needed!)

```
User Request
    ↓
Agent 0: Requirements Gathering (AI-First or Engineer)
    ↓ workflow/specs/pending/[component].md
    ↓ [COMMIT: "spec: Add [component] specification"]
    
Agent 1: forge-vhdl-component-generator
    ↓ workflow/artifacts/vhdl/[component].vhd
    ↓ [COMMIT: "feat: Generate [component] VHDL"]
    
Agent 2: cocotb-progressive-test-designer
    ↓ workflow/artifacts/tests/[component]_test_strategy.md
    ↓ [COMMIT: "test: Design [component] test architecture"]
    
Agent 3: cocotb-progressive-test-runner
    ↓ workflow/artifacts/tests/[component]_tests/
    ↓ Run tests: uv run python cocotb_tests/run.py [component]
    ↓ [COMMIT: "test: Implement and run [component] P1 tests"]
    
Final: Integration
    ↓ Move artifacts to production
    ↓ [COMMIT: "feat: Integrate [component] to codebase"]
```

**All in one Cursor session!** No switching between local/cloud.

---

## 🎯 Cursor-Specific Patterns

### Pattern 1: Full Component Generation (Recommended)

**In Cursor Composer (`Cmd+I`):**

```
I need a [component description]. Use the AI-First requirements workflow to:
1. Generate specification in workflow/specs/pending/
2. Execute the complete 3-agent workflow with incremental commits
3. Run P1 tests and verify <20 lines output
4. Show me the results
```

**Cursor orchestrates:**
- Requirements gathering (2-5 min)
- VHDL generation
- Test design
- Test implementation & execution
- Incremental commits
- Final report

**Time:** 10-15 minutes total (vs 20-30 min with hybrid workflow)

### Pattern 2: Agent-by-Agent Control

**Step 1: Requirements**
```
Use the AI-First requirements workflow to create a spec for [component].
Save to workflow/specs/pending/[component].md
```

**Step 2: Agent 1 (VHDL Generation)**
```
Read workflow/specs/pending/[component].md
Act as Agent 1 (forge-vhdl-component-generator):
- Read .claude/agents/forge-vhdl-component-generator/agent.md
- Generate VHDL entity/architecture
- Save to workflow/artifacts/vhdl/[component].vhd
- Commit: "feat: Generate [component] VHDL"
```

**Step 3: Agent 2 (Test Design)**
```
Read workflow/artifacts/vhdl/[component].vhd
Act as Agent 2 (cocotb-progressive-test-designer):
- Read .claude/agents/cocotb-progressive-test-designer/agent.md
- Design P1 test architecture
- Save to workflow/artifacts/tests/[component]_test_strategy.md
- Commit: "test: Design [component] test architecture"
```

**Step 4: Agent 3 (Test Implementation)**
```
Read workflow/artifacts/tests/[component]_test_strategy.md
Act as Agent 3 (cocotb-progressive-test-runner):
- Read .claude/agents/cocotb-progressive-test-runner/agent.md
- Implement P1 tests
- Run: uv run python cocotb_tests/run.py [component]
- Verify <20 lines output
- Commit: "test: Implement and run [component] P1 tests"
```

### Pattern 3: Using Existing Specs

**If you already have a spec:**

```
Read workflow/specs/pending/[component].md
Execute the complete 3-agent workflow:
1. Generate VHDL
2. Design tests
3. Implement and run tests
4. Make incremental commits
```

**Or use reference specs:**

```
Read workflow/specs/reference/pwm_generator.md
Execute the complete 3-agent workflow to generate a working implementation.
```

---

## 🛠️ Cursor Agent Orchestration

### Agent Definitions

Cursor can load agent definitions from:
- `.claude/agents/forge-vhdl-component-generator/agent.md` - VHDL generation
- `.claude/agents/cocotb-progressive-test-designer/agent.md` - Test design
- `.claude/agents/cocotb-progressive-test-runner/agent.md` - Test execution

### Orchestration Pattern

**In Cursor Composer, you can say:**

```
Execute the 3-agent workflow for [component]:
1. Load Agent 1 definition from .claude/agents/forge-vhdl-component-generator/agent.md
2. Generate VHDL from workflow/specs/pending/[component].md
3. Load Agent 2 definition from .claude/agents/cocotb-progressive-test-designer/agent.md
4. Design tests from the generated VHDL
5. Load Agent 3 definition from .claude/agents/cocotb-progressive-test-runner/agent.md
6. Implement and run tests
7. Make commits after each agent completes
```

### Terminal Command Execution

Cursor can run terminal commands directly:

```
After Agent 3 completes, run:
uv run python cocotb_tests/run.py [component]

Verify output is <20 lines. If not, debug with Agent 3.
```

**Cursor will:**
- Execute the command
- Show output in terminal
- Parse results
- Continue workflow based on results

---

## 📋 Requirements Workflows

### AI-First Requirements (Fast - 2-5 min)

**In Cursor Chat:**

```
I need a [component description]. Use the AI-First requirements workflow.
Read workflow/AI_FIRST_REQUIREMENTS.md and gather requirements.
```

**Cursor will:**
- Pattern match to reference specs
- Ask 2-3 critical questions only
- Generate complete specification
- Save to `workflow/specs/pending/[component].md`

### Engineer Requirements (Detailed - 15-30 min)

**In Cursor Chat:**

```
I want to create a new VHDL component. 
Read workflow/ENGINEER_REQUIREMENTS.md and guide me through the requirements process.
```

**Cursor will:**
- Ask 30 questions across 7 phases
- Provide educational guidance
- Generate detailed specification
- Save to `workflow/specs/pending/[component].md`

---

## 🧪 Testing with Cursor

### Real-Time Test Execution

**After Agent 3 generates tests, Cursor can run them immediately:**

```
Run P1 tests for [component]:
uv run python cocotb_tests/run.py [component]

If output >20 lines, debug with Agent 3 to fix filtering.
```

**Cursor will:**
- Execute test command
- Show results in terminal
- Parse pass/fail counts
- Check output line count
- Iterate if needed

### Progressive Test Levels

**P1 (Default):**
```
Run P1 tests: uv run python cocotb_tests/run.py [component]
Expected: <20 lines, <5 sec, 2-4 tests
```

**P2:**
```
Run P2 tests: TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py [component]
Expected: <50 lines, <30 sec, 5-10 tests
```

**P3:**
```
Run P3 tests: TEST_LEVEL=P3_COMPREHENSIVE uv run python cocotb_tests/run.py [component]
Expected: <100 lines, <2 min, 15-25 tests
```

---

## 🔄 Incremental Commits

### Commit Strategy

**Cursor can make commits after each agent completes:**

```
After Agent 1 completes:
git add workflow/artifacts/vhdl/[component].vhd
git commit -m "feat: Generate [component] VHDL"

After Agent 2 completes:
git add workflow/artifacts/tests/[component]_test_strategy.md
git commit -m "test: Design [component] test architecture"

After Agent 3 completes:
git add workflow/artifacts/tests/[component]_tests/
git commit -m "test: Implement and run [component] P1 tests"
```

**In Cursor Composer, you can say:**

```
After each agent completes, make an incremental commit with a descriptive message.
```

### Integration Commit

**After reviewing artifacts:**

```
Move artifacts to production:
- mv workflow/artifacts/vhdl/[component].vhd vhdl/components/[category]/
- Tests already in cocotb_tests/

Commit: "feat: Integrate [component] to codebase"
```

---

## 📚 Documentation Navigation

**Tier 1 (Quick Reference):**
- `llms.txt` - Component catalog (~800 tokens)
- `CURSOR.md` (this file) - Cursor-specific guide

**Tier 2 (Agent Definitions):**
- `.claude/agents/forge-vhdl-component-generator/agent.md` - VHDL generation
- `.claude/agents/cocotb-progressive-test-designer/agent.md` - Test design
- `.claude/agents/cocotb-progressive-test-runner/agent.md` - Test execution

**Tier 3 (Standards & Guides):**
- `CLAUDE.md` - Original framework guide (testing standards, architecture)
- `docs/VHDL_CODING_STANDARDS.md` - Complete style guide (600 lines)
- `docs/COCOTB_TROUBLESHOOTING.md` - Problem→solution debugging
- `workflow/AI_FIRST_REQUIREMENTS.md` - Fast requirements (2-5 min)
- `workflow/ENGINEER_REQUIREMENTS.md` - Detailed requirements (15-30 min)

**Reference Specs:**
- `workflow/specs/reference/` - 5 gold-standard examples

---

## 🎓 Example: Complete Workflow

### User Request

```
I need a timeout detector that triggers after 100ms of inactivity.
Execute the complete 3-agent workflow with incremental commits.
```

### Cursor's Execution

**Step 1: Requirements (AI-First)**
- Pattern match: `pulse_stretcher.md` (retriggerable timing)
- Ask: Output mode (level vs pulse)? Default: level
- Generate: `workflow/specs/pending/forge_util_timeout_detector.md`
- Commit: `"spec: Add forge_util_timeout_detector specification"`

**Step 2: Agent 1 (VHDL Generation)**
- Read spec + agent definition
- Generate: `workflow/artifacts/vhdl/forge_util_timeout_detector.vhd`
- Commit: `"feat: Generate forge_util_timeout_detector VHDL"`

**Step 3: Agent 2 (Test Design)**
- Analyze VHDL component
- Design: 4 P1 tests (reset, timeout, retriggerable, enable)
- Generate: `workflow/artifacts/tests/forge_util_timeout_detector_test_strategy.md`
- Commit: `"test: Design forge_util_timeout_detector test architecture"`

**Step 4: Agent 3 (Test Implementation)**
- Implement P1 tests
- Run: `uv run python cocotb_tests/run.py forge_util_timeout_detector`
- Output: 3 tests pass, 12 lines total ✅
- Commit: `"test: Implement and run forge_util_timeout_detector P1 tests"`

**Step 5: Integration**
- Review artifacts
- Move VHDL to `vhdl/components/utilities/`
- Commit: `"feat: Integrate forge_util_timeout_detector to codebase"`

**Total Time:** ~12 minutes (all local, no handoff)

---

## 🔧 Cursor-Specific Tips

### Using Composer Mode

**Composer (`Cmd+I`) is best for:**
- Multi-step workflows
- Agent orchestration
- Long-running tasks
- Incremental commits

**Example:**
```
Execute the 3-agent workflow for [component] with incremental commits.
After each agent, show me the results before proceeding.
```

### Using Chat Mode

**Chat is best for:**
- Quick questions
- Single-agent tasks
- Debugging
- Learning patterns

**Example:**
```
What components are available? Check llms.txt
How do I use forge_voltage_5v_bipolar_pkg? Show me an example.
```

### Terminal Integration

**Cursor can execute commands and parse results:**

```
Run tests and check output:
uv run python cocotb_tests/run.py [component] | wc -l

If >20, debug with Agent 3 to fix filtering.
```

---

## 🆚 Comparison: Cursor vs Hybrid Workflow

| Feature | Cursor (This Edition) | Hybrid (Local → Cloud) |
|--------|---------------------|------------------------|
| **Requirements** | ✅ Local (Cursor Chat) | ✅ Local (Claude CLI) |
| **Agent Execution** | ✅ Local (Cursor Composer) | ⚠️ Cloud (Claude Web) |
| **Test Execution** | ✅ Real-time (local) | ⚠️ Cloud (requires pull) |
| **Commits** | ✅ Incremental (local) | ⚠️ Cloud (auto-merge) |
| **IDE Integration** | ✅ Full (file changes, terminal) | ⚠️ Limited (web UI) |
| **Token Limits** | ✅ None (agent mode) | ⚠️ None (cloud) |
| **Handoff Overhead** | ✅ None | ⚠️ Git push/pull |
| **Total Time** | ✅ 10-15 min | ⚠️ 20-30 min |

**Winner:** Cursor for local development, Hybrid for cloud-only environments

---

## 🐛 Troubleshooting

### Agent Not Loading Definition

**Issue:** Cursor doesn't load agent definition  
**Solution:** Explicitly reference the file:

```
Read .claude/agents/forge-vhdl-component-generator/agent.md
Act as Agent 1 and generate VHDL from [spec].
```

### Test Execution Fails

**Issue:** Tests fail or output too verbose  
**Solution:** Ask Agent 3 to debug:

```
Agent 3: Test execution failed with [error].
Read docs/COCOTB_TROUBLESHOOTING.md and fix the issue.
```

### Commit Not Made

**Issue:** Cursor doesn't make incremental commits  
**Solution:** Explicitly request:

```
After Agent 1 completes, make a commit:
git add workflow/artifacts/vhdl/[component].vhd
git commit -m "feat: Generate [component] VHDL"
```

---

## 📖 Additional Resources

**Agent Definitions:**
- `.claude/agents/forge-vhdl-component-generator/agent.md`
- `.claude/agents/cocotb-progressive-test-designer/agent.md`
- `.claude/agents/cocotb-progressive-test-runner/agent.md`

**Workflow Guides:**
- `workflow/AI_FIRST_REQUIREMENTS.md` - Fast requirements (2-5 min)
- `workflow/ENGINEER_REQUIREMENTS.md` - Detailed requirements (15-30 min)
- `workflow/README.md` - Complete workflow guide

**Standards:**
- `docs/VHDL_CODING_STANDARDS.md` - Complete style guide
- `docs/COCOTB_TROUBLESHOOTING.md` - Debugging guide
- `CLAUDE.md` - Testing standards and architecture patterns

**Reference Specs:**
- `workflow/specs/reference/` - 5 gold-standard examples

---

## ⚡ Quick Commands Reference

```bash
# Environment detection
uv run python .claude/env_detect.py

# Run P1 tests (default)
uv run python cocotb_tests/run.py <component>

# Run P2 tests
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py <component>

# List all tests
uv run python cocotb_tests/run.py --list

# Run all tests
uv run python cocotb_tests/run.py --all
```

---

**Version:** 3.3.0-multi-tenant  
**Last Updated:** 2025-01-XX  
**Template:** https://github.com/vmars-20/forge-vhdl-3v3-vmars  
**Maintainer:** Moku Instrument Forge Team

**Quick Links:**
- [Component Catalog](llms.txt)
- [Agent Definitions](.claude/agents/)
- [Reference Specs](workflow/specs/reference/)
- [VHDL Standards](docs/VHDL_CODING_STANDARDS.md)
- [Claude Edition](CLAUDE.md) (for cloud workflows)
- [Copilot Edition](COPILOT.md) (for IDE-integrated development)

