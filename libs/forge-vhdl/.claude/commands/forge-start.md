---
description: Interactive session starter for local VHDL development with environment validation and workflow routing
---

# 🔧 FORGE-START: Local VHDL Development Session Initializer

**Usage:**
- `/forge-start` → Interactive mode selector
- `/forge-start student` → AI-First workflow (2-5 min, intelligent defaults)
- `/forge-start engineer` → Engineer workflow (15-30 min, full control)
- `/forge-start cloud` → Validate cloud-compatible setup (even from local)

---

## STEP 1: Environment Detection & Validation

**First, run environment detection:**

```bash
uv run python .claude/env_detect.py
```

**Parse the output and:**
1. Confirm GHDL installation status
2. Identify runtime environment (local vs cloud)
3. Show the environment banner to user

---

## STEP 2: Output Settings Check (Local Only)

**If local environment detected, use interactive validation:**

Use the `AskUserQuestion` tool to ask:

**Question:** "Have you verified your Claude Code output settings for optimal VHDL test output?"

**Header:** "Settings"

**Options:**
1. **Label:** "✅ Yes, settings verified"
   **Description:** "I've checked /config and set: verbose=false, output style=default, auto-compact=false"

2. **Label:** "⚙️ No, show me how"
   **Description:** "I need guidance on configuring output settings for VHDL development"

3. **Label:** "❓ What are output settings?"
   **Description:** "I don't know what this means - explain why it matters"

**Handle responses:**

- **"Yes, settings verified"** → Proceed to Step 3
- **"No, show me how"** → Show this guidance:
  ```
  📋 Output Settings Configuration:

  1. Run: /config (in Claude Code CLI)
  2. Navigate to: "Config" tab
  3. Verify these settings:
     • Verbose output: false ← CRITICAL for clean P1 test logs
     • Output style: default ← RECOMMENDED
     • Auto-compact: false ← Prevents VHDL output truncation

  4. Visual reference: static/Claude-CLI-output-settings.png

  Why this matters:
  - P1 tests target <20 lines output (LLM-optimized)
  - Verbose mode adds 10-15 lines of noise per test
  - Auto-compact can hide critical simulation warnings

  ✅ After configuring, re-run: /forge-start
  ```
  **Then STOP** - wait for user to configure and restart.

- **"What are output settings?"** → Explain:
  ```
  🎓 Output Settings Explained:

  Claude Code CLI has global settings that control how tool outputs
  are displayed. For VHDL development, we need:

  1. **Verbose output: false**
     - Default: Shows every tool invocation with metadata
     - Problem: Adds 10-15 lines per GHDL test run
     - Our P1 tests target <20 lines total output
     - Solution: Disable verbose to see only simulation results

  2. **Auto-compact: false**
     - Default: Truncates long outputs (>100 lines)
     - Problem: May hide critical VHDL warnings/errors
     - Solution: Disable to see full GHDL output

  3. **Output style: default**
     - Keeps standard formatting for code/logs

  To configure: /config → Config tab → adjust settings
  Reference: static/Claude-CLI-output-settings.png

  Ready to configure? (Then re-run /forge-start)
  ```
  **Then STOP** - wait for user action.

---

## STEP 3: Mode Selection

**Determine which workflow to activate based on command argument:**

### If `/forge-start student` (or user chose "student" interactively):

```
🚀 AI-FIRST WORKFLOW ACTIVATED (Student Mode)

Perfect for:
- Learning VHDL-FORGE patterns
- Quick prototyping (2-5 minutes)
- Intelligent defaults with minimal questions

What happens next:
1. I'll ask 2-5 critical questions only
2. Pattern recognition fills in the rest
3. Generate complete specification → workflow/specs/pending/
4. Run 3-agent automated workflow:
   - Agent 1: VHDL generation
   - Agent 2: Test design (P1/P2/P3)
   - Agent 3: Test execution & validation

Let's start! What component would you like to build?
(Example: "A PWM generator for LED dimming")
```

**Then:**
- Load `workflow/AI_FIRST_REQUIREMENTS.md` context
- Begin AI-First requirements gathering (2-5 questions)
- DO NOT use /gather-requirements (that's the Engineer workflow)
- **After spec generation:** Offer cloud handoff (see STEP 5)

---

### If `/forge-start engineer` (or user chose "engineer" interactively):

```
🔧 ENGINEER WORKFLOW ACTIVATED (Advanced Mode)

Perfect for:
- Production-grade components
- Complex state machines
- Full control over every detail
- Learning advanced VHDL patterns

What happens next:
1. Structured 30-question interview (7 phases)
2. Deep dive into functionality, interface, behavior
3. Explicit test strategy (P1/P2/P3 design)
4. Generate detailed specification → workflow/specs/pending/
5. Run 3-agent automated workflow with full visibility

This will take 15-30 minutes for thorough requirements capture.

Ready to begin? I'll launch the interactive requirements gathering session.
```

**Then:**
- Execute: `/gather-requirements` (delegate to existing command)
- DO NOT duplicate the logic - the slash command already handles it
- **After spec generation:** Offer cloud handoff (see STEP 5)

---

### If `/forge-start cloud` (validation mode):

```
🌐 CLOUD VALIDATION MODE

Checking cloud-compatible configuration from local environment...
```

**Run these validation checks:**

1. **GHDL Availability:**
   ```bash
   which ghdl && ghdl --version
   ```
   ✅ Found → Show version
   ❌ Not found → Warn: "Cloud requires GHDL (install: brew install ghdl)"

2. **Python Environment:**
   ```bash
   uv run python --version
   ```
   ✅ Python 3.8+ → OK
   ❌ Older/missing → Error

3. **CocoTB Dependencies:**
   ```bash
   uv pip list | grep cocotb
   ```
   ✅ cocotb installed → Show version
   ❌ Not installed → Info: "Will auto-install on first test run"

4. **Git Configuration:**
   ```bash
   git config user.name && git config user.email
   ```
   ✅ Configured → OK
   ❌ Not configured → Warn: "Set git config for commits"

5. **Output Directory Structure:**
   ```bash
   ls -la workflow/specs/pending/ workflow/artifacts/vhdl/ workflow/artifacts/tests/
   ```
   ✅ All exist → OK
   ❌ Missing → Create them

**Show results:**
```
╔════════════════════════════════════════════════════════════════════╗
║  🌐 CLOUD COMPATIBILITY VALIDATION                                 ║
║                                                                    ║
║  ✅ GHDL: [version]                                                ║
║  ✅ Python: [version]                                              ║
║  ✅ CocoTB: [status]                                               ║
║  ✅ Git: [configured/not configured]                               ║
║  ✅ Directory structure: [OK/created]                              ║
║                                                                    ║
║  Result: [READY FOR CLOUD / ISSUES FOUND]                          ║
╚════════════════════════════════════════════════════════════════════╝
```

**Then ask:**
"Everything looks good! Which workflow would you like to use?"
- 🚀 Student (AI-First)
- 🔧 Engineer (Full control)

---

### If `/forge-start` (no argument - interactive mode):

**Use `AskUserQuestion` tool to ask:**

**Question:** "Which workflow would you like to use for VHDL development?"

**Header:** "Workflow"

**Options:**
1. **Label:** "🚀 Student (AI-First)"
   **Description:** "Fast prototyping with intelligent defaults. 2-5 questions, 2-5 minutes. Perfect for learning."

2. **Label:** "🔧 Engineer (Advanced)"
   **Description:** "Full control with 30-question structured interview. 15-30 minutes. Production-grade specs."

3. **Label:** "📚 Browse Examples"
   **Description:** "Explore 5 gold-standard reference specifications (edge detector, PWM, synchronizer, etc.)"

4. **Label:** "🌐 Validate Cloud Setup"
   **Description:** "Check if local environment is cloud-compatible (GHDL, Python, CocoTB, Git)"

**Handle responses:**
- **"Student (AI-First)"** → Jump to `/forge-start student` flow
- **"Engineer (Advanced)"** → Jump to `/forge-start engineer` flow
- **"Browse Examples"** → Jump to STEP 4 (Reference Gallery)
- **"Validate Cloud Setup"** → Jump to `/forge-start cloud` flow

---

## STEP 4: Reference Gallery (if "Browse Examples" selected)

```
📚 GOLD-STANDARD REFERENCE SPECIFICATIONS

These are proven, production-tested component specs that demonstrate
VHDL-FORGE best practices:

1. **Edge Detector** (workflow/specs/reference/edge_detector.md)
   - Timing-critical design
   - Rising/falling/both edge detection
   - FSM state encoding for debug
   - Best for: Learning safety-critical patterns

2. **PWM Generator** (workflow/specs/reference/pwm_generator.md)
   - Parameter-heavy design
   - Generic-driven configuration
   - Duty cycle control (0-100%)
   - Best for: Learning configurable components

3. **Synchronizer** (workflow/specs/reference/synchronizer.md)
   - Clock domain crossing (CDC)
   - Metastability handling
   - 2-stage flip-flop chain
   - Best for: Learning safety patterns

4. **Debouncer** (workflow/specs/reference/debouncer.md)
   - Counter-based state machine
   - Timing constraints
   - Best for: Learning FSM patterns

5. **Pulse Stretcher** (workflow/specs/reference/pulse_stretcher.md)
   - Timing-based control
   - Programmable duration
   - Best for: Learning timed behavior

Would you like to:
A) Read one of these specs and execute its 3-agent workflow
B) Use one as a template for your own component
C) Return to workflow selection
```

**Use `AskUserQuestion` to let user select a spec or return.**

If they select a spec, say:
```
Great choice! I'll read [spec_name] and execute the complete 3-agent workflow:
1. forge-vhdl-component-generator → VHDL code
2. cocotb-progressive-test-designer → Test architecture
3. cocotb-progressive-test-runner → Execution & validation

This will take 2-5 minutes.
```

**Then execute:**
```
Read workflow/specs/reference/[selected].md and execute the complete 3-agent workflow
```

---

## STEP 5: After Specification Generation - Cloud Handoff (RECOMMENDED)

**When specification is complete** (in `workflow/specs/pending/`), offer cloud handoff:

```
✅ SPECIFICATION COMPLETE: workflow/specs/pending/[component].md

Your specification is ready! Now you have two options for running the 3-agent workflow:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 OPTION A: RUN AGENTS IN CLAUDE WEB (RECOMMENDED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Benefits:
  • No token limits (agents run as long as needed)
  • Browser convenience (no terminal management)
  • Zero GHDL setup (auto-installs in cloud)
  • Better for testing (autonomous debugging/iteration)
  • Incremental git commits (audit trail of agent work)

🚀 Quick Handoff Steps:

1. Commit your specification locally:
   git add workflow/specs/pending/[component].md
   git commit -m "spec: Add [component] (AI-First workflow)"
   git push

2. Open Claude Web (https://claude.ai/)
   • Start new chat
   • Attach this repository (Projects → Add)

3. Say to Claude Web:
   "Read workflow/specs/pending/[component].md and execute the complete
    3-agent workflow"

4. Claude Web will:
   • Run Agent 1: forge-vhdl-component-generator
   • Run Agent 2: cocotb-progressive-test-designer
   • Run Agent 3: cocotb-progressive-test-runner (with git commits!)
   • Output artifacts to workflow/artifacts/

5. Pull changes back locally:
   git pull

6. Review and integrate:
   mv workflow/artifacts/vhdl/[component].vhd vhdl/components/[category]/
   # Tests already in cocotb_tests/ (ready to use!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💻 OPTION B: RUN AGENTS LOCALLY (ALTERNATIVE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Subject to CLI token limits per message
⚠️  Requires local GHDL installation
⚠️  Manual agent invocation

Say "run agents locally" if you prefer this option.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Which option would you like?
```

**Use `AskUserQuestion` to prompt:**

**Question:** "How would you like to run the 3-agent workflow?"

**Header:** "Execution"

**Options:**
1. **Label:** "🌐 Cloud (Claude Web)"
   **Description:** "Recommended. No token limits, zero setup, autonomous debugging. Handoff to browser."

2. **Label:** "💻 Local (CLI)"
   **Description:** "Run agents here in terminal. Requires GHDL, subject to token limits."

**Handle responses:**

### If user chooses "Cloud (Claude Web)":

```
Perfect choice! Here's what to do:

1. First, let's commit your specification:
```

**Then run:**
```bash
git add workflow/specs/pending/[component].md
git commit -m "spec: Add [component] specification (AI-First workflow)"
git push
```

**Then show:**
```
✅ Specification committed and pushed!

2. Now open Claude Web:
   • Go to https://claude.ai/
   • Start a new chat
   • Attach this repository as a Project

3. Copy/paste this message to Claude Web:

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Read workflow/specs/pending/[component].md and
   execute the complete 3-agent workflow.

   Use the "commit often" pattern from Agent 3's definition.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. Claude Web will generate VHDL, design tests, run tests, and commit
   all changes with detailed git messages.

5. When complete, come back here and run:
   git pull

6. Review the artifacts and integrate to your main codebase!

🎉 You're all set! Good luck with your component development!
```

**Then STOP** - workflow handed off to cloud.

### If user chooses "Local (CLI)":

```
Understood. I'll run the 3-agent workflow locally.

⚠️  Note: This may take several messages due to CLI token limits.

Starting 3-agent workflow:
1. forge-vhdl-component-generator
2. cocotb-progressive-test-designer
3. cocotb-progressive-test-runner

Beginning Agent 1...
```

**Then proceed with local agent execution.**

---

## Error Handling

**If GHDL not found:**
```
❌ GHDL NOT DETECTED

VHDL-FORGE requires GHDL for simulation and testing.

Install GHDL:
- macOS: brew install ghdl
- Ubuntu/Debian: sudo apt-get install ghdl ghdl-llvm
- Windows: https://github.com/ghdl/ghdl/releases

After installation, re-run: /forge-start
```

**If wrong environment detected:**
```
⚠️  CLOUD ENVIRONMENT DETECTED

You ran /forge-start which is optimized for local CLI development.

For cloud environments (Codespaces/Claude Web):
- Auto-configuration is already active
- GHDL installed automatically
- No output settings needed

Recommended: Just start building!
"I need a [component]. Use the AI-First workflow."

Or continue with /forge-start anyway? (y/n)
```

---

## Important Notes

1. **Always run env_detect.py first** - don't assume environment
2. **Use AskUserQuestion for all interactive prompts** - leverages Claude Code UI
3. **Load context progressively** - only read docs when workflow is selected
4. **Respect argument overrides** - `/forge-start student` skips mode selection
5. **Screenshot references** - use Read tool to show `static/Claude-CLI-output-settings.png` if needed
6. **Delegate to existing commands** - `/gather-requirements` already works, don't duplicate

---

## Context Loading (Do This AFTER workflow selection)

**For Student (AI-First):**
- Read: `workflow/AI_FIRST_REQUIREMENTS.md`
- Read: `llms.txt` (component catalog for pattern matching)

**For Engineer:**
- Execute: `/gather-requirements` (already has all context)

**For Browse Examples:**
- List: `workflow/specs/reference/*.md` files
- Read selected spec on demand

**For Cloud Validation:**
- No additional context needed (validation only)

---

**Ready to execute! Parse command argument and begin flow.**
