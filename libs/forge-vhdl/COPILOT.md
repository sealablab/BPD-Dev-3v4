# forge-vhdl: GitHub Copilot Edition

**AI-powered VHDL development optimized for GitHub Copilot workflows**

**Version:** 3.3.0-multi-tenant  
**Purpose:** IDE-integrated VHDL development with Copilot assistance  
**Environment:** VS Code, GitHub Codespaces, JetBrains IDEs with Copilot

---

## 🎯 START HERE (Copilot Users)

This repository is optimized for GitHub Copilot's **iterative, IDE-based workflow**. Unlike Claude's autonomous agent approach, Copilot excels at inline suggestions, chat-based assistance, and file-focused development.

### Quick Setup

```bash
# 1. Detect environment
uv run python .claude/env_detect.py

# 2. Install dependencies
uv sync

# 3. Verify GHDL (for local development)
ghdl --version

# 4. Run example test
uv run python cocotb_tests/run.py forge_util_clk_divider
```

**Expected output:** 3 tests pass, <20 lines total output

---

## 🔄 Copilot Workflow vs Claude Workflow

### GitHub Copilot Strengths (This Edition)
✅ **Inline suggestions** while editing VHDL/Python  
✅ **Chat-based** iterative development in IDE  
✅ **File-focused** context (current file + related files)  
✅ **Quick iterations** with immediate feedback  
✅ **IDE integration** (debugging, testing, git)

**Use Copilot for:**
- Writing VHDL entities/architectures with inline completion
- Creating CocoTB tests file-by-file
- Debugging test failures interactively
- Refactoring existing components
- Quick documentation updates

### Claude Strengths (Original Edition)
✅ **Autonomous agents** (3-agent workflow)  
✅ **Multi-file** context and generation  
✅ **Long-running** unattended execution  
✅ **Requirements gathering** via structured interviews

**Use Claude for:**
- Initial requirements gathering (AI-First or Engineer workflows)
- Complete component generation (VHDL + tests simultaneously)
- Batch operations across multiple files
- Complex refactoring with dependency analysis

### Hybrid Workflow (RECOMMENDED)

```
Claude (Web/CLI) → Requirements & Spec Generation
    ↓ workflow/specs/pending/[component].md
    
Copilot (IDE) → Implementation & Testing
    ↓ Iterative VHDL development
    ↓ Test creation and debugging
    ↓ Local validation
    
Git → Commit & Integration
```

---

## 🚀 Quick Start Patterns

### Pattern 1: New Component from Scratch

**Step 1: Chat with Copilot**
```
@workspace I need a PWM generator with 8-bit duty cycle control.
Use the AI-First requirements workflow to generate a spec.
```

**Step 2: Copilot generates spec → Review → Save to `workflow/specs/pending/pwm_generator.md`**

**Step 3: Generate VHDL**
```
@workspace Read workflow/specs/pending/pwm_generator.md
Generate the VHDL entity and architecture following docs/VHDL_CODING_STANDARDS.md
```

**Step 4: Generate tests**
```
@workspace Create P1 CocoTB tests for pwm_generator.
Tests must output <20 lines total. Reference test_forge_util_clk_divider.py as example.
```

**Step 5: Run & iterate**
```bash
uv run python cocotb_tests/run.py pwm_generator
```

**Fix issues with Copilot Chat:**
```
@workspace Test failed with error: [paste error]
Check docs/COCOTB_TROUBLESHOOTING.md and fix the test
```

### Pattern 2: Learn from Reference Components

**Open a reference spec:**
```
workflow/specs/reference/edge_detector.md
workflow/specs/reference/pwm_generator.md
workflow/specs/reference/synchronizer.md
```

**Ask Copilot:**
```
@workspace Explain the edge_detector.md spec structure.
I want to create a similar component for [my use case].
```

**Copilot will guide you through adapting the pattern.**

### Pattern 3: Debugging Test Failures

**Common issue: GHDL warnings flooding output**

```bash
# P1 test output should be <20 lines but getting 287 lines?
uv run python cocotb_tests/run.py my_component
```

**Ask Copilot:**
```
@workspace My P1 test output is too verbose (287 lines instead of <20).
Check scripts/ghdl_output_filter.py and cocotb_tests/run.py
How do I enable aggressive filtering?
```

**Copilot will show you the `GHDL_FILTER_LEVEL` environment variable.**

### Pattern 4: Using Existing Components

**Ask Copilot:**
```
@workspace What voltage conversion components are available?
Show me how to convert a real voltage (e.g., 2.5V) to std_logic_vector
for a ±5V DAC.
```

**Copilot reads `llms.txt` and suggests:**
```vhdl
use work.forge_voltage_5v_bipolar_pkg.all;

signal voltage_real : real := 2.5;
signal voltage_slv  : std_logic_vector(15 downto 0);

voltage_slv <= forge_real_to_signed_5v_bipolar_16b(voltage_real);
```

---

## 📖 Documentation Navigation

**Tier 1 (Start Here):**
- `llms.txt` - Component catalog (~800 tokens)
- `COPILOT.md` (this file) - Copilot-specific guide

**Tier 2 (Load as Needed):**
- `CLAUDE.md` - Original framework guide (Claude-specific features)
- `.github/copilot-instructions.md` - Custom instructions for Copilot
- `workflow/README.md` - Complete workflow guide
- `workflow/specs/reference/` - 5 gold-standard examples

**Tier 3 (Specialized):**
- `docs/VHDL_CODING_STANDARDS.md` - Complete style guide (600 lines)
- `docs/COCOTB_TROUBLESHOOTING.md` - Problem→solution debugging
- `docs/PROGRESSIVE_TESTING_GUIDE.md` - Test design patterns

**Ask Copilot to load docs:**
```
@workspace Read docs/VHDL_CODING_STANDARDS.md
Show me the FSM state encoding rules
```

---

## 🧪 Progressive Testing with Copilot

### Test Levels (Critical Concept)

| Level | Tests | Output | Runtime | Use Case |
|-------|-------|--------|---------|----------|
| **P1** | 2-4 essential | <20 lines | <5 sec | **Default** - Fast iteration |
| **P2** | 5-10 + edges | <50 lines | <30 sec | Standard validation |
| **P3** | 15-25 comprehensive | <100 lines | <2 min | Full coverage |
| **P4** | Unlimited | No limit | No limit | Debug mode |

### Creating P1 Tests with Copilot

**In VS Code, create `cocotb_tests/test_my_component.py`:**

Type this comment and let Copilot autocomplete:

```python
# P1 CocoTB tests for my_component
# Test 1: Reset behavior
# Test 2: Basic operation
# Test 3: Enable control
# Output target: <20 lines total
```

**Copilot will generate:**
```python
import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock

@cocotb.test()
async def test_reset(dut):
    """P1: Verify reset clears outputs"""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    assert dut.output.value == 0
    
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_basic_operation(dut):
    """P1: Basic functionality check"""
    # Copilot completes based on entity ports...
```

### Running Tests

```bash
# P1 (default)
uv run python cocotb_tests/run.py my_component

# P2
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py my_component

# Debug mode (full output)
GHDL_FILTER_LEVEL=none uv run python cocotb_tests/run.py my_component
```

---

## 🎨 VHDL Coding Standards (Quick Reference)

### Mandatory Rules

**1. No Enums for FSM States**
```vhdl
-- ✅ CORRECT (Verilog-compatible)
constant STATE_IDLE  : std_logic_vector(1 downto 0) := "00";
constant STATE_ARMED : std_logic_vector(1 downto 0) := "01";

-- ❌ WRONG (breaks Verilog translation)
type state_t is (IDLE, ARMED);
```

**2. Reset Hierarchy**
```vhdl
-- ✅ CORRECT order
process(clk)
begin
  if rising_edge(clk) then
    if rst_n = '0' then
      -- Reset logic
    elsif clk_en = '1' then
      if enable = '1' then
        -- Normal operation
      end if;
    end if;
  end if;
end process;

-- ❌ WRONG (flat structure)
if rst_n = '0' and enable = '1' then  -- Unsafe!
```

**3. Port Ordering**
```vhdl
entity forge_component is
  port (
    -- 1. Clock and reset (always first)
    clk     : in  std_logic;
    rst_n   : in  std_logic;
    
    -- 2. Control signals
    clk_en  : in  std_logic := '1';
    enable  : in  std_logic := '1';
    
    -- 3. Data signals (prefixed)
    data_in  : in  std_logic_vector(7 downto 0);
    data_out : out std_logic_vector(7 downto 0);
    
    -- 4. Status signals (prefixed)
    stat_ready : out std_logic;
    stat_error : out std_logic
  );
end entity;
```

**4. Signal Prefixes**
- `ctrl_*` - Control signals
- `cfg_*` - Configuration signals
- `stat_*` - Status signals
- `dbg_*` - Debug signals

**Ask Copilot to enforce standards:**
```
@workspace Review my_component.vhd
Check compliance with docs/VHDL_CODING_STANDARDS.md
Flag any violations
```

---

## 🔧 Copilot-Specific Tips

### Inline Completion Best Practices

**Trigger strong suggestions with comments:**
```vhdl
-- Clock divider with programmable ratio, 8-bit counter, enable control
entity forge_util_my_divider is
  -- Copilot will autocomplete generics/ports based on comment
```

**Use descriptive signal names:**
```vhdl
signal counter_value_8bit : unsigned(7 downto 0);  -- Copilot knows range
signal pwm_duty_cycle_percent : unsigned(6 downto 0);  -- Copilot infers 0-99
```

### Chat Prompts for VHDL

**Generate entity from description:**
```
@workspace Create a VHDL entity for a debouncer:
- Input: raw_button (std_logic)
- Output: button_stable (std_logic)
- Generic: DEBOUNCE_TIME (time := 20 ms)
- Follow docs/VHDL_CODING_STANDARDS.md
```

**Create architecture from entity:**
```
@workspace Generate architecture for forge_util_debouncer entity.
Use a counter-based approach with configurable timeout.
```

**Add test cases:**
```
@workspace Create 3 P1 CocoTB tests for debouncer:
1. Reset behavior
2. Debounce short glitches (<20ms)
3. Pass stable signals (>20ms)
Output must be <20 lines total
```

### Workspace Context Commands

```
@workspace /explain              # Explain selected code
@workspace /doc                  # Generate documentation
@workspace /fix                  # Fix syntax/logic errors
@workspace /tests                # Generate test cases
@workspace #file:llms.txt        # Reference specific file
```

---

## 🛠️ Common Workflows

### Workflow 1: Add Component to Existing System

**Current:** You have a working clock divider  
**Goal:** Add PWM generator that uses divided clock

**Step 1: Check existing components**
```
@workspace What components are in vhdl/components/utilities/?
```

**Step 2: Create spec**
```
@workspace Generate spec for PWM generator that uses forge_util_clk_divider.
Reference workflow/specs/reference/pwm_generator.md structure.
```

**Step 3: Generate VHDL (Copilot suggests)**
```vhdl
-- Copilot auto-suggests entity with clock divider instantiation
entity forge_util_pwm_generator is
  port (
    clk     : in  std_logic;
    rst_n   : in  std_logic;
    clk_en  : in  std_logic := '1';
    -- Copilot completes...
  );
end entity;
```

**Step 4: Instantiate in testbench**
```python
# Copilot suggests CocoTB instantiation
dut.u_clk_div  # Access divider
dut.u_pwm_gen  # Access PWM generator
```

### Workflow 2: Debug Failing Test

**Error message:**
```
AttributeError: 'HierarchyObject' object has no attribute 'value'
```

**Ask Copilot:**
```
@workspace Error in test_my_component.py line 42:
AttributeError: 'HierarchyObject' object has no attribute 'value'
Read docs/COCOTB_TROUBLESHOOTING.md Section 0 and suggest fix
```

**Copilot responds:**
```
The error occurs because VHDL `real` types can't be accessed directly in CocoTB.
Solution: Create a test wrapper that converts real to std_logic_vector.

See docs/COCOTB_TROUBLESHOOTING.md for complete pattern.
```

### Workflow 3: Refactor to Use Voltage Package

**Before (manual conversion):**
```vhdl
signal voltage_real : real;
signal voltage_int  : integer;
voltage_int <= integer(voltage_real * 32767.0 / 5.0);
```

**Ask Copilot:**
```
@workspace Refactor this manual voltage conversion to use
forge_voltage_5v_bipolar_pkg functions
```

**After (Copilot suggests):**
```vhdl
use work.forge_voltage_5v_bipolar_pkg.all;

signal voltage_real : real;
signal voltage_slv  : std_logic_vector(15 downto 0);

voltage_slv <= forge_real_to_signed_5v_bipolar_16b(voltage_real);
```

---

## 📦 Component Catalog (Quick Reference)

**Most Used Components:**

1. **forge_util_clk_divider** - Programmable clock divider (P1 tests ✓)
2. **forge_voltage_5v_bipolar_pkg** - ±5V conversions for Moku DAC/ADC (P1 tests ✓)
3. **forge_lut_pkg** - Look-up table utilities (P1 tests ✓)
4. **forge_common_pkg** - FORGE_READY handshaking (P1 tests ✓)

**Ask Copilot:**
```
@workspace Show me all available components in llms.txt
```

**Or read directly:**
```bash
cat llms.txt
```

---

## 🔄 Copilot ↔ Claude Integration

### Use Copilot When:
- ✅ Editing single files (VHDL or Python)
- ✅ Debugging test failures interactively
- ✅ Refactoring existing code
- ✅ Quick iterations with immediate feedback
- ✅ Learning patterns from examples

### Use Claude When:
- ✅ Generating requirements specs (AI-First workflow: 2-5 min)
- ✅ Multi-file generation (VHDL + tests + docs simultaneously)
- ✅ Running autonomous 3-agent workflow
- ✅ Large refactoring across many files
- ✅ Initial project setup and scaffolding

### Handoff Pattern

**Copilot → Claude:**
```bash
# 1. Commit your Copilot work
git add vhdl/components/utilities/my_component.vhd
git commit -m "feat: Add initial my_component entity"

# 2. Create spec for Claude agents
cat > workflow/specs/pending/my_component.md << EOF
# my_component Specification
[Paste spec]
EOF

# 3. Switch to Claude (Web or CLI)
# "Read workflow/specs/pending/my_component.md and execute 3-agent workflow"
```

**Claude → Copilot:**
```bash
# 1. Pull Claude's autonomous work
git pull  # Merges Claude's sandbox branch

# 2. Review in IDE with Copilot assistance
code workflow/artifacts/vhdl/my_component.vhd

# 3. Ask Copilot to review
# "@workspace Review workflow/artifacts/vhdl/my_component.vhd
#  Check VHDL coding standards compliance"

# 4. Integrate to production
mv workflow/artifacts/vhdl/my_component.vhd vhdl/components/utilities/
```

---

## 🐛 Troubleshooting with Copilot

### Quick Diagnostics

**Ask Copilot:**
```
@workspace Run diagnostics:
1. Check GHDL installation: ghdl --version
2. List available tests: uv run python cocotb_tests/run.py --list
3. Run environment detection: uv run python .claude/env_detect.py
```

### Common Issues

**Issue: "GHDL not found"**
```
@workspace How do I install GHDL on macOS/Linux?
```

**Issue: "Test output too verbose"**
```
@workspace My P1 tests output 287 lines instead of <20.
Check scripts/ghdl_output_filter.py for filtering configuration.
```

**Issue: "CocoTB can't access signal"**
```
@workspace Error: 'HierarchyObject' object has no attribute 'value'
Read docs/COCOTB_TROUBLESHOOTING.md Section 0
```

---

## 📚 Additional Resources

**Environment-Specific Guides:**
- `.claude/CLAUDE_LOCAL.md` - Local development (if using Claude CLI)
- `.claude/CLAUDE_CLOUD.md` - Cloud development (if using Claude Web)

**Workflow Guides:**
- `workflow/AI_FIRST_REQUIREMENTS.md` - Fast requirements (2-5 min)
- `workflow/ENGINEER_REQUIREMENTS.md` - Detailed requirements (15-30 min)
- `workflow/specs/reference/` - 5 gold-standard examples

**Technical Docs:**
- `docs/VHDL_CODING_STANDARDS.md` - Complete style guide (600 lines)
- `docs/PROGRESSIVE_TESTING_GUIDE.md` - Test design patterns
- `docs/COCOTB_TROUBLESHOOTING.md` - Problem→solution debugging

---

## ⚡ Quick Commands Reference

```bash
# Environment detection
uv run python .claude/env_detect.py

# Install dependencies
uv sync

# Run P1 tests (default)
uv run python cocotb_tests/run.py <component>

# Run P2 tests
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py <component>

# List all tests
uv run python cocotb_tests/run.py --list

# Run all tests
uv run python cocotb_tests/run.py --all

# View component catalog
cat llms.txt
```

---

## 🎓 Learning Path

**Day 1: Setup & Basics**
1. Run environment detection
2. Run example test: `forge_util_clk_divider`
3. Read one reference spec: `workflow/specs/reference/edge_detector.md`
4. Ask Copilot to explain the spec structure

**Day 2: Create Simple Component**
1. Use AI-First workflow to create a spec (with Copilot's help)
2. Generate VHDL entity (let Copilot autocomplete)
3. Create 2 P1 tests
4. Run and validate

**Day 3: Learn Standards**
1. Ask Copilot to quiz you on FSM encoding rules
2. Review reset hierarchy pattern
3. Explore voltage package usage
4. Refactor Day 2 component to follow all standards

**Day 4: Complex Component**
1. Create component that uses existing utilities
2. Write P1, P2, P3 test levels
3. Optimize test output (<20 lines for P1)
4. Document with Copilot's help

**Day 5: Integration**
1. Integrate component into larger system
2. Use Copilot to check dependencies
3. Run full test suite
4. Commit to production

---

## 🤝 Contributing

When contributing VHDL components:

1. **Follow standards** - Use Copilot to validate:
   ```
   @workspace Check my_component.vhd against docs/VHDL_CODING_STANDARDS.md
   ```

2. **Create P1 tests** - Must output <20 lines:
   ```bash
   uv run python cocotb_tests/run.py my_component | wc -l
   # Must be < 20
   ```

3. **Document** - Use Copilot to generate:
   ```
   @workspace Generate specification doc for my_component
   Follow workflow/specs/reference/edge_detector.md structure
   ```

4. **Test all levels** - P1, P2, P3:
   ```bash
   uv run python cocotb_tests/run.py my_component  # P1
   TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py my_component  # P2
   TEST_LEVEL=P3_COMPREHENSIVE uv run python cocotb_tests/run.py my_component  # P3
   ```

---

## 📞 Getting Help

**Ask Copilot first:**
```
@workspace I'm stuck with [problem]. 
Check relevant docs in docs/ and workflow/ directories.
```

**Still stuck? Check docs:**
- `docs/COCOTB_TROUBLESHOOTING.md` - Most common issues
- `docs/PROGRESSIVE_TESTING_GUIDE.md` - Test design help
- `.github/copilot-instructions.md` - Copilot-specific guidance

**For autonomous workflows, switch to Claude:**
- Open Claude Web: https://claude.ai/code/
- Say: "Read CLAUDE.md and execute 3-agent workflow for [component]"

---

**Version:** 3.3.0-multi-tenant  
**Last Updated:** 2025-11-09  
**Template:** https://github.com/vmars-20/forge-vhdl-3v3-vmars  
**Maintainer:** Moku Instrument Forge Team

**Quick Links:**
- [Component Catalog](llms.txt)
- [VHDL Standards](docs/VHDL_CODING_STANDARDS.md)
- [Reference Specs](workflow/specs/reference/)
- [Troubleshooting](docs/COCOTB_TROUBLESHOOTING.md)
- [Claude Edition](CLAUDE.md) (for autonomous workflows)
