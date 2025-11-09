# Cloud Validation Test V2 - Complete Workflow

**Purpose:** Comprehensive validation of cloud-first VHDL development experience

**Status:** V2 - Improved after successful V1 run

---

## Copy This Entire Prompt Into Fresh Claude Code Web Session

```markdown
Hi Claude! I'm testing the forge-vhdl-3v1-claude repository's cloud-first experience.

This repository claims to provide "Full VHDL simulation in your browser" with one-command setup.

Let's validate the complete developer experience from scratch:

---

## Phase 1: First Impressions (Documentation Review)

Please read and evaluate:

1. **README.md** - Main entry point
   - Does it immediately convey "cloud-first"?
   - Is the Quick Start clear and actionable?
   - Would a new user know what to do first?

2. **QUICKSTART_CLOUD.md** - Step-by-step guide
   - Are the steps clear and complete?
   - Is the expected output well-defined?
   - Would this guide a beginner successfully?

3. **llms.txt** - Quick reference
   - Is cloud setup prominently featured?
   - Is the one-command setup easy to find?
   - Is the value proposition clear?

**Report:**
- On a scale of 1-10, how clear is the cloud-first message?
- What's confusing or could be improved?
- What works really well?

---

## Phase 2: Environment Setup (The Critical Test)

Run the one-command setup:

```bash
uv run python scripts/cloud_setup_with_ghdl.py
```

**Observe and report:**
- Did it start without errors?
- What's being installed? (GHDL, Python packages, etc.)
- How long did it take?
- Were there any warnings or errors?
- Did it complete with "Setup Complete!" message?

**Expected:** ~2-3 minutes, auto-installs GHDL, runs sample test

---

## Phase 3: Basic Validation (Can We Run Tests?)

Execute these commands and report results:

```bash
# List all available tests
uv run python cocotb_tests/run.py --list

# Count how many tests are available
uv run python cocotb_tests/run.py --list | grep -c "  -"

# Run a simple component test
uv run python cocotb_tests/run.py forge_util_clk_divider

# Run a package test
uv run python cocotb_tests/run.py forge_lut_pkg
```

**Report for each test:**
- Did it pass? (look for "PASS" in output)
- How many lines of output? (should be <20 for P1 tests)
- Were there any errors?
- Did GHDL actually simulate VHDL? (look for "ghdl" in output)

---

## Phase 4: Developer Workflow (AI-Assisted Development)

Try the AI-assisted workflow:

```bash
# Check if slash command exists
cat .claude/commands/gather-requirements.md

# Try to understand the agent workflow
ls .claude/agents/

# Read the agent overview
cat .claude/agents/README.md
```

**Then attempt:**
- Type: `/gather-requirements`
- See if the agent loads
- Ask me: "What does the requirements gathering workflow do?"

**Report:**
- Are the AI agents accessible?
- Is the workflow clear?
- Would you feel confident using this for VHDL development?

---

## Phase 5: Code Exploration (Understanding the Codebase)

Explore the VHDL components:

```bash
# List VHDL components
find vhdl/components -name "*.vhd" | head -10

# Look at a simple component
cat vhdl/components/utilities/forge_util_clk_divider.vhd

# Check the test for that component
ls cocotb_tests/components/forge_util_clk_divider_tests/

# Read the component constants
cat cocotb_tests/components/forge_util_clk_divider_tests/forge_util_clk_divider_constants.py
```

**Report:**
- Is the code structure clear?
- Are the VHDL components well-documented?
- Do the tests make sense?
- Could you add a new component following these patterns?

---

## Phase 6: Advanced Testing (Progressive Test Levels)

Try different test levels:

```bash
# P1 (Basic, fast, LLM-optimized)
uv run python cocotb_tests/run.py forge_util_clk_divider

# P2 (Intermediate, comprehensive)
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py forge_util_clk_divider

# Compare output lengths
```

**Report:**
- How much more output does P2 produce vs P1?
- Is the progressive testing concept clear?
- Would this be useful for iterative development?

---

## Phase 7: Example Walkthrough (Counter Example)

Follow the counter example:

```bash
# Navigate to example
cd examples/counter

# Read the README
cat README.md

# Look at the main VHDL file
ls vhdl/

# Check what tests exist
ls -la cocotb_tests/
```

**Report:**
- Does the example demonstrate the FORGE patterns?
- Is it clear how to adapt it for your own use?
- What's the learning curve like?

---

## Final Summary

Please provide a comprehensive report:

### ✅ What Worked Perfectly
- List everything that exceeded expectations
- What made the cloud-first experience great?

### ⚠️ What Worked But Could Be Improved
- Small friction points
- Unclear documentation
- Minor bugs or warnings

### ❌ What Failed or Blocked Progress
- Hard blockers
- Major confusion points
- Missing critical information

### 💡 Recommendations for V3
- Specific improvements to documentation
- Workflow enhancements
- Better onboarding steps

### 🎯 Overall Assessment
- Would you recommend this to a colleague learning VHDL?
- Is the "cloud-first" promise delivered?
- Rate the experience: 1-10

---

Thank you! This comprehensive test will help validate the complete developer journey.
```

---

## Test Administrator Notes

### Success Criteria (V2 - More Stringent)

**Documentation (Phase 1):**
- [ ] Cloud-first message is immediately obvious
- [ ] README.md Quick Start is actionable in <30 seconds
- [ ] QUICKSTART_CLOUD.md exists and is comprehensive
- [ ] First-time user wouldn't be confused about next steps

**Setup (Phase 2):**
- [ ] One-command setup works without manual intervention
- [ ] GHDL installs successfully in cloud environment
- [ ] Setup completes in <5 minutes
- [ ] Sample test runs and passes
- [ ] No blocking errors or warnings

**Testing (Phase 3):**
- [ ] Test runner works (`--list` shows tests)
- [ ] At least 3 different tests can run
- [ ] At least 50% of tests pass
- [ ] Test output is clean (<20 lines for P1)
- [ ] GHDL simulation actually executes

**AI Workflow (Phase 4):**
- [ ] `/gather-requirements` slash command exists
- [ ] Agent documentation is accessible
- [ ] Workflow is explained clearly
- [ ] User understands how to use agents

**Code Structure (Phase 5):**
- [ ] VHDL components are well-organized
- [ ] Tests follow clear patterns
- [ ] Documentation exists in code
- [ ] New user could add a component

**Advanced Features (Phase 6):**
- [ ] Progressive testing works (P1 vs P2)
- [ ] Output reduction is evident
- [ ] Concept is clear and valuable

**Examples (Phase 7):**
- [ ] Counter example is complete
- [ ] README explains the pattern
- [ ] User can understand how to adapt it

**Overall Experience:**
- [ ] Setup time: <5 minutes
- [ ] Success rate: >50% of tests pass
- [ ] Documentation clarity: 8+/10
- [ ] Would recommend: Yes

### Known Acceptable Issues

From V1 testing, these are acceptable:
- Some tests may fail (50% baseline is OK)
- Minor warnings during setup (non-blocking)
- `uv.lock` updates after setup

### Failure Modes to Watch For

Red flags that require immediate fixes:
- Setup script crashes or hangs
- GHDL installation fails completely
- Test runner doesn't work at all
- Documentation is confusing about cloud vs local
- No clear entry point for new users

---

## Iteration Strategy

If issues found:
1. Categorize: Blocker / Major / Minor
2. Fix blockers immediately
3. Batch minors for next iteration
4. Document majors for future work

---

**Version:** 2.0
**Previous:** V1 succeeded, minor improvements needed
**Focus:** Complete developer journey validation
**Next:** V3 will focus on specific pain points from V2
