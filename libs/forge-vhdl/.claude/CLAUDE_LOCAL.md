# forge-vhdl Local Development Guide

**Version:** 3.2.0 - LOCAL ENVIRONMENT
**Purpose:** Interactive VHDL development with AI-First requirements gathering
**Audience:** Students, engineers using Claude Code CLI locally
**Environment:** Local machine with Claude Code CLI

---

## 🎯 You Are Here: Local Development Mode

**Congratulations!** You've successfully set up forge-vhdl for local development.

This environment is optimized for:
- ✅ Interactive requirements gathering (AI-First workflow - default for students)
- ✅ Manual VHDL editing with AI assistance
- ✅ Progressive testing with clean output logs
- ✅ Git-based version control
- ✅ Full control over output verbosity

---

## ⚙️ CRITICAL: Verify Your Output Settings (Do This First!)

**Why this matters:** VHDL test output can be verbose. Incorrect settings will make logs hard to read.

### Step-by-Step Verification

1. **Open config screen:**
   ```
   /config
   ```

2. **Navigate to "Config" tab** (use tab key to cycle)

3. **Verify these settings:**

   | Setting | Recommended Value | Why |
   |---------|-------------------|-----|
   | Verbose output | `false` | Prevents duplicate/verbose logs |
   | Output style | `default` | Best for test output formatting |
   | Auto-compact | `false` | Preserves VHDL test context |
   | Rewind code | `true` | Helpful for iterative debugging |

4. **Reference screenshot:** `static/Claude-CLI-output-settings.png`

5. **After verifying, close config:** Press `Esc` or navigate away

**✓ Done?** You're ready to start developing!

---

## 🚀 Quick Start: Your First Component

### Default Workflow (Students/Beginners - RECOMMENDED)

**Step 1: Start with a simple request**

Just tell me what you need in plain English:

```
"I need a PWM generator with configurable duty cycle"
```

**Step 2: AI-First Requirements Gathering (2-5 minutes)**

I'll ask you 2-3 **critical questions** only:
- What frequency range? (e.g., 1 kHz - 100 kHz)
- Duty cycle resolution? (e.g., 8-bit = 0-255)
- Any special timing constraints?

I'll use **pattern recognition** to infer:
- Port names and types (from similar components)
- Standard VHDL-2008 coding patterns
- Progressive test strategy (P1/P2/P3)
- Reset behavior and clock requirements

**Step 3: Review proposed specification**

I'll show you a complete spec and ask:
```
Does this specification look correct? Should I proceed with automated workflow?
```

**Step 4: Specification complete → Choose execution environment**

Once your specification is ready in `workflow/specs/pending/`, you have **two options**:

**Option A: Run agents in Claude Web (RECOMMENDED)** 🌐

Benefits:
- ✅ **No token limits** - Agents can run as long as needed
- ✅ **Browser convenience** - No terminal management
- ✅ **Zero GHDL setup** - Auto-installs in cloud
- ✅ **Better for testing** - Agents run tests, debug, iterate autonomously

**How to handoff:**
1. Commit your specification:
   ```bash
   git add workflow/specs/pending/
   git commit -m "spec: Add [component] specification (AI-First workflow)"
   git push
   ```

2. Open your repository in Claude Web:
   - Go to https://claude.ai/
   - Start new chat
   - Attach your repository (Projects → Add)
   - Say: "Read workflow/specs/pending/[component].md and execute the complete 3-agent workflow"

3. Claude Web will:
   - Run Agent 1: forge-vhdl-component-generator
   - Run Agent 2: cocotb-progressive-test-designer
   - Run Agent 3: cocotb-progressive-test-runner (with incremental git commits!)
   - Output all artifacts to workflow/artifacts/

4. Pull changes back locally:
   ```bash
   git pull
   ```

5. Review and integrate (local):
   ```bash
   # Move to production
   mv workflow/artifacts/vhdl/[component].vhd vhdl/components/[category]/
   # Tests already in cocotb_tests/ (ready to use)
   ```

**Option B: Run agents locally (if you prefer)** 💻

- Manually invoke agents from local CLI
- Same 3-agent workflow
- Requires local GHDL installation
- Subject to CLI token limits per message

---

### 💡 Recommended Workflow Split

**Local CLI strengths:**
- ✅ Interactive requirements gathering (fast, controlled)
- ✅ Output settings management
- ✅ Manual VHDL editing
- ✅ Final integration and testing

**Claude Web strengths:**
- ✅ Long-running agent execution
- ✅ Test debugging and iteration
- ✅ Autonomous problem-solving
- ✅ No environment setup

**Optimal pattern:** Gather requirements locally → Execute agents in cloud → Integrate locally

---

## 📚 Alternative Workflows

### Use Reference Specs (Fast Start - Pattern Matching)

Browse proven patterns in `workflow/specs/reference/`:

| Pattern | Use For | Complexity |
|---------|---------|------------|
| `edge_detector.md` | Signal transitions, event detection | Low |
| `synchronizer.md` | Clock domain crossing (CDC) | Low-Med |
| `pwm_generator.md` | Periodic signals, counter-based logic | Medium |
| `debouncer.md` | FSM-based control, button inputs | Medium |
| `pulse_stretcher.md` | Retriggerable timing, pulse extension | Medium |

**Example:**
```
"Read workflow/specs/reference/edge_detector.md and execute the complete 3-agent workflow"
```

I'll generate VHDL + tests based on the reference pattern.

### Engineer Workflow (Advanced - Full Control)

For novel architectures or learning VHDL standards in depth:

```
"I want to create a new VHDL component. Please read workflow/ENGINEER_REQUIREMENTS.md
and guide me through the requirements process."
```

This triggers a **30-question Q&A** covering:
- Component identification
- Detailed functionality
- Complete interface specification
- Behavior/FSM states
- Testing strategy (P1/P2/P3)
- Design constraints
- Standards validation

Takes 15-30 minutes, produces highly detailed spec.

### Manual Implementation (Skip Agents)

For quick edits or expert developers:

```
"Generate VHDL for a 16-bit up/down counter with overflow flag"
```

I'll write VHDL directly without the agent workflow.

---

## 🧪 Testing Locally

### Running Tests

**Default (P1 - LLM-optimized, <20 line output):**
```bash
uv run python cocotb_tests/run.py <component_name>
```

**P2 (Standard validation):**
```bash
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py <component_name>
```

**With more verbosity (debugging):**
```bash
COCOTB_VERBOSITY=NORMAL uv run python cocotb_tests/run.py <component_name>
```

**List all available tests:**
```bash
uv run python cocotb_tests/run.py --list
```

### Expected Output (P1 Test Example)

```
Running P1 tests for forge_util_clk_divider...

✅ PASS: Reset test
✅ PASS: Divide by 2
✅ PASS: Divide by 4
✅ PASS: Enable control

4/4 tests passed (0.8s)
```

**If output exceeds 20 lines:** Something is wrong with test design. See `docs/PROGRESSIVE_TESTING_GUIDE.md`.

---

## 📖 Component Catalog

### Utilities (forge_util_*)

**forge_util_clk_divider** - vhdl/utilities/forge_util_clk_divider.vhd:1
- Programmable clock divider
- Tests: 3 P1, 4 P2 ✓

### Packages

**forge_lut_pkg** - vhdl/packages/forge_lut_pkg.vhd:1
- Look-up table utilities (voltage/index conversion)
- Tests: 4 P1, 4 P2, 1 P3 ✓

**forge_voltage_5v_bipolar_pkg** - vhdl/packages/forge_voltage_5v_bipolar_pkg.vhd:1
- ±5.0V bipolar voltage domain (Moku DAC/ADC)
- Tests: 4 P1, 2 P2 ✓

**forge_voltage_3v3_pkg** - vhdl/packages/forge_voltage_3v3_pkg.vhd:1
- 0-3.3V unipolar (TTL, GPIO, digital glitch)
- Tests: 4 P1, 2 P2 ✓

**forge_voltage_5v0_pkg** - vhdl/packages/forge_voltage_5v0_pkg.vhd:1
- 0-5.0V unipolar (sensor supply, analog)
- Tests: 4 P1, 2 P2 ✓

### Debugging (forge_debug_*)

**forge_hierarchical_encoder** - vhdl/debugging/forge_hierarchical_encoder.vhd:1
- FSM state + status encoding for oscilloscope (NEW STANDARD)
- Tests: 4 P1 ✓

---

## 🎓 Learning Resources

### For Students/Beginners

**Start here:**
1. Read `llms.txt` (component catalog)
2. Browse `workflow/specs/reference/` (5 gold-standard examples)
3. Try AI-First workflow with a simple component (edge detector, synchronizer)
4. Examine generated VHDL to learn patterns

**Key documents:**
- `docs/VHDL_QUICK_REF.md` - Templates and checklists
- `workflow/AI_FIRST_REQUIREMENTS.md` - Fast requirements gathering
- `docs/PROGRESSIVE_TESTING_GUIDE.md` - How to write P1 tests

### For Engineers/Advanced Users

**Start here:**
1. Read `CLAUDE.md` (comprehensive design guide)
2. Study `docs/VHDL_CODING_STANDARDS.md` (600-line style guide)
3. Try Engineer workflow for a novel component
4. Review `docs/COCOTB_TROUBLESHOOTING.md` for advanced testing

**Key documents:**
- `workflow/ENGINEER_REQUIREMENTS.md` - Detailed 30-question Q&A
- `docs/VHDL_CODING_STANDARDS.md` - Complete style guide
- `.claude/agents/*/agent.md` - Agent implementation details

---

## 🔧 VHDL Coding Standards (Quick Reference)

### Mandatory Rules

**FSM States:** Use `std_logic_vector`, NOT enums (Verilog compatibility)

```vhdl
-- ✅ CORRECT
constant STATE_IDLE   : std_logic_vector(1 downto 0) := "00";
constant STATE_ARMED  : std_logic_vector(1 downto 0) := "01";

-- ❌ FORBIDDEN
type state_t is (IDLE, ARMED);  -- NO!
```

**Port Order:** clk, rst_n, clk_en, enable, data, status

```vhdl
entity forge_util_example is
    port (
        -- 1. Clock & Reset
        clk    : in std_logic;
        rst_n  : in std_logic;  -- Active-low

        -- 2. Control
        clk_en : in std_logic;
        enable : in std_logic;

        -- 3. Data inputs
        data_in : in std_logic_vector(15 downto 0);

        -- 4. Data outputs
        data_out : out std_logic_vector(15 downto 0);

        -- 5. Status
        busy : out std_logic
    );
end entity;
```

**Reset Hierarchy:** rst_n > clk_en > enable

```vhdl
process(clk, rst_n)
begin
    if rst_n = '0' then
        output <= (others => '0');
    elsif rising_edge(clk) then
        if clk_en = '1' then
            if enable = '1' then
                output <= input;
            end if
        end if
    end if
end process;
```

---

## 🐛 Common Issues

### Issue: GHDL not found during tests

**Solution:**
```bash
# macOS
brew install ghdl

# Ubuntu/Debian
sudo apt-get install ghdl ghdl-llvm
```

Then restart Claude session.

### Issue: Tests pass but output is too verbose (>20 lines)

**Solution:**
1. Check `GHDL_FILTER_LEVEL` (should be `aggressive` for P1)
2. Check `TEST_LEVEL` (should be `P1_BASIC` or unset)
3. Review test design: Are you running too many iterations?

See `docs/PROGRESSIVE_TESTING_GUIDE.md` for details.

### Issue: CocoTB can't access VHDL signal

**Error:** `AttributeError: 'HierarchyObject' object has no attribute 'value'`

**Cause:** CocoTB can't access `real`, `boolean`, `time`, custom records.

**Solution:** Use test wrapper with `std_logic_vector` / `signed` / `unsigned` only.

See `docs/COCOTB_TROUBLESHOOTING.md` Section 0.

---

## 📝 Git Workflow (Submodule)

**CRITICAL:** All commits must be made inside the submodule!

```bash
cd libs/forge-vhdl
git checkout <your-feature-branch>

# Make changes
git add .
git commit -m "descriptive message"
git push origin <your-feature-branch>

cd ../..
git add libs/forge-vhdl  # Update parent reference
git commit -m "chore: Update forge-vhdl submodule"
git push origin <your-feature-branch>
```

---

## 🎯 Next Steps

1. **Verify output settings** (see top of this guide)
2. **Try a simple component:**
   ```
   "I need an edge detector. Use the AI-First requirements workflow."
   ```
3. **Review generated artifacts** in `workflow/artifacts/`
4. **Run P1 tests** and ensure <20 line output
5. **Commit your work** to git

**Questions?** Just ask! I'm here to help.

---

**Environment:** Local (Claude Code CLI)
**GHDL Status:** {{ "Installed" if ghdl_found else "Not Installed" }}
**Recommended Workflow:** AI-First (students) or Engineer (advanced)
**Template Origin:** https://github.com/vmars-20/forge-vhdl-3v3-vmars
**Example Workflow:** Check `claude` branch: `git fetch origin claude && git log origin/claude --oneline`

**Last Updated:** 2025-11-09
**Version:** 3.2.0 (template-ready)
**Maintainer:** Moku Instrument Forge Team
