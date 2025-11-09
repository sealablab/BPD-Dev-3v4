# forge-vhdl Cloud Development Guide

**Version:** 3.2.0 - CLOUD ENVIRONMENT
**Purpose:** Streamlined VHDL development in browser-based environments
**Audience:** Students, engineers using Claude Code Web / GitHub Codespaces
**Environment:** Cloud (GHDL auto-installed and validated)

---

## 🌐 You Are Here: Cloud Development Mode

**Welcome to cloud-first VHDL development!** Full simulation in your browser - no local toolchain required.

This environment provides:
- ✅ **GHDL pre-installed and validated** (VHDL-2008 simulation)
- ✅ **CocoTB progressive testing** (P1/P2/P3 levels)
- ✅ **AI-First requirements gathering** (default for students)
- ✅ **Automated 3-agent workflow** (requirements → VHDL → tests)
- ✅ **Zero local setup** (works in browser, Codespaces, containers)

---

## ⚡ Quick Start: Your First Component (30 seconds)

### Step 1: Tell me what you need

```
"I need a PWM generator with configurable duty cycle"
```

### Step 2: AI-First Requirements (2-5 minutes)

I'll ask you 2-3 **critical questions** only:
- What frequency range? (e.g., 1 kHz - 100 kHz)
- Duty cycle resolution? (e.g., 8-bit = 0-255)
- Any special timing constraints?

I'll use **pattern recognition** to infer the rest:
- Port names and types (from similar components)
- Standard VHDL-2008 coding patterns
- Progressive test strategy (P1/P2/P3)
- Reset behavior and clock requirements

### Step 3: Automated Implementation

I'll invoke 3 agents automatically:
1. **forge-vhdl-component-generator** → VHDL code
2. **cocotb-progressive-test-designer** → Test architecture
3. **cocotb-progressive-test-runner** → Working tests

### Step 4: Review Artifacts

VHDL and tests appear in `workflow/artifacts/`:
```
workflow/artifacts/
├── vhdl/forge_util_pwm.vhd
└── tests/test_forge_util_pwm_progressive.py
```

**Ready to use!** Tests already run and passing.

---

## 🎯 GHDL Validation (Pre-Installed)

**GHDL is a hard requirement in cloud environments and is pre-installed via DevContainer.**

### DevContainer Setup (Automatic)

The `.devcontainer/devcontainer.json` configuration:
- Uses official GHDL Docker image: `ghdl/ghdl:ubuntu22-llvm-5.0`
- GHDL 5.0 with LLVM backend **pre-installed**
- Automatically runs validation script on container creation
- Installs LLVM 18 and Python dependencies

**On startup, you'll see:**
```
✅ VHDL Found: GHDL 5.0 (LLVM backend)
✅ VHDL-FORGE 3.0 Ready! Run: uv run python cocotb_tests/run.py --list
```

### Validation Script (Automatic)

The DevContainer automatically runs `scripts/cloud_setup_with_ghdl.py` which:
- Verifies GHDL installation
- Creates LLVM library symlinks (critical for GHDL-LLVM)
- Validates with sample VHDL simulation
- Reports readiness status

**This runs automatically - you don't need to do anything!**

### Troubleshooting (Rare)

**If GHDL is somehow missing (should never happen in DevContainer):**

```bash
uv run python scripts/cloud_setup_with_ghdl.py
```

This takes ~2-3 minutes and reinstalls GHDL + dependencies.

**You will NEVER need to manually install GHDL in cloud environments - DevContainer handles it.**

---

## 📚 Development Workflows

### Workflow 1: AI-First (DEFAULT - Students/Beginners)

**Time:** 2-5 minutes
**Best for:** Students, beginners, clear requirements, pattern-matched components

```
User: "I need a binary counter with overflow detection. Use the AI-First workflow."

Claude: [Asks 2-3 critical questions]
  - Counter width? (e.g., 8-bit, 16-bit)
  - Count direction? (up, down, or both?)
  - Overflow behavior? (wrap, stop, flag?)

Claude: [Proposes complete spec based on patterns]
  Specification:
  - Component: forge_util_counter
  - Ports: clk, rst_n, enable, count_up, overflow, count_out[N-1:0]
  - Tests: 5 P1 tests (reset, count up, overflow, enable control, wrap)

  Does this look correct? [User approves]

Claude: [Invokes 3-agent workflow]
  ✅ VHDL generated
  ✅ Tests designed
  ✅ Tests implemented and passing (5/5 PASS)

Claude: Artifacts ready in workflow/artifacts/
```

**Reference:** `workflow/AI_FIRST_REQUIREMENTS.md`

### Workflow 2: Use Reference Specs (Fast Start)

**Time:** <1 minute
**Best for:** Pattern matching, learning from examples

Browse `workflow/specs/reference/` for proven patterns:

| Pattern | Use For | Complexity |
|---------|---------|------------|
| `edge_detector.md` | Signal transitions, event detection | Low |
| `synchronizer.md` | Clock domain crossing (CDC) | Low-Med |
| `pwm_generator.md` | Periodic signals, counter-based logic | Medium |
| `debouncer.md` | FSM-based control, button inputs | Medium |
| `pulse_stretcher.md` | Retriggerable timing, pulse extension | Medium |

**Example:**
```
"Read workflow/specs/reference/pwm_generator.md and execute the complete 3-agent workflow"
```

I'll generate VHDL + tests automatically based on the reference pattern.

### Workflow 3: Engineer Workflow (Advanced)

**Time:** 15-30 minutes
**Best for:** Novel architectures, complex systems, learning VHDL standards in depth

```
"I want to create a new VHDL component. Please read workflow/ENGINEER_REQUIREMENTS.md
and guide me through the requirements process."
```

This triggers a **30-question Q&A** covering:
- Component identification (name, category, purpose)
- Detailed functionality description
- Complete interface specification (ports, generics)
- Behavior specification (FSM states, timing, edge cases)
- Testing strategy (P1/P2/P3 test cases)
- Design guidance (architectural patterns)
- Standards compliance (VHDL-2008, no enums, etc.)

Produces highly detailed specification with full control over every aspect.

**Reference:** `workflow/ENGINEER_REQUIREMENTS.md`

---

## 🧪 Testing in Cloud Environments

### Running Tests

**Default (P1 - LLM-optimized, <20 line output):**
```bash
uv run python cocotb_tests/run.py <component_name>
```

**P2 (Standard validation):**
```bash
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py <component_name>
```

**All tests:**
```bash
uv run python cocotb_tests/run.py --all
```

**List available tests:**
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

**Key metric:** P1 output should be **<20 lines** (token-efficient for LLM iteration).

If output exceeds 20 lines, see `docs/PROGRESSIVE_TESTING_GUIDE.md`.

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
- ±5.0V bipolar voltage domain (Moku DAC/ADC - **most common**)
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

**Complete guide:** `docs/VHDL_CODING_STANDARDS.md` (600 lines)

---

## 🎓 Learning Resources

### For Students/Beginners

**Start here:**
1. Read `llms.txt` (component catalog)
2. Browse `workflow/specs/reference/` (5 gold-standard examples)
3. Try AI-First workflow with a simple component:
   ```
   "I need an edge detector. Use the AI-First requirements workflow."
   ```
4. Examine generated VHDL to learn patterns

**Key documents:**
- `workflow/AI_FIRST_REQUIREMENTS.md` - Fast requirements gathering (2-5 min)
- `docs/VHDL_QUICK_REF.md` - Templates and checklists
- `docs/PROGRESSIVE_TESTING_GUIDE.md` - How to write P1 tests

### For Engineers/Advanced Users

**Start here:**
1. Read `CLAUDE.md` (comprehensive design guide, ~5k tokens)
2. Study `docs/VHDL_CODING_STANDARDS.md` (complete style guide)
3. Try Engineer workflow for a novel component
4. Review agent implementation: `.claude/agents/*/agent.md`

**Key documents:**
- `workflow/ENGINEER_REQUIREMENTS.md` - Detailed 30-question Q&A
- `docs/VHDL_CODING_STANDARDS.md` - Complete coding standards
- `docs/COCOTB_TROUBLESHOOTING.md` - Advanced testing patterns

---

## 🐛 Common Issues (Cloud-Specific)

### Issue: GHDL installation fails

**Rare in cloud environments (DevContainer pre-configures GHDL).**

If you see this error:
```
❌ GHDL installation failed
```

**Solution:**
1. Check container OS: `cat /etc/os-release`
2. If not Ubuntu/Debian, manual install required:
   ```bash
   # Alpine Linux (rare)
   apk add ghdl ghdl-llvm

   # Fedora/RHEL (rare)
   dnf install ghdl
   ```
3. Report issue to maintainers (should be pre-installed in DevContainer)

### Issue: Tests pass but output is verbose (>20 lines)

**Cause:** Test design needs refinement for P1 level.

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

## 🎯 Next Steps

1. **Try a simple component:**
   ```
   "I need a binary counter with overflow. Use the AI-First workflow."
   ```

2. **Review generated artifacts** in `workflow/artifacts/`

3. **Run tests:**
   ```bash
   uv run python cocotb_tests/run.py forge_util_counter
   ```

4. **Expect <20 line P1 output** (token-efficient)

5. **Commit your work** to git

**Questions?** Just ask! I'm here to help.

---

**Environment:** Cloud (Claude Code Web / GitHub Codespaces)
**GHDL Status:** ✅ Installed and Validated (hard requirement)
**Recommended Workflow:** AI-First (students) or Engineer (advanced)
**Template Origin:** https://github.com/vmars-20/forge-vhdl-3v3-vmars
**Example Workflow:** Check `claude` branch: `git fetch origin claude && git log origin/claude --oneline`

**Last Updated:** 2025-11-09
**Version:** 3.2.0 (template-ready)
**Maintainer:** Moku Instrument Forge Team
