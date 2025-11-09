# Agent 2: Test Architecture Design Prompt

**Copy-paste this into Claude Code to design test architecture:**

---

Read the VHDL component at `workflow/artifacts/vhdl/[COMPONENT].vhd` and the specification at `workflow/specs/pending/[YOUR_SPEC].md`, then design a CocoTB progressive test architecture:

**Requirements:**
- Analyze VHDL entity for CocoTB compatibility (check for real/boolean types)
- Design progressive test levels (P1/P2/P3 as specified in spec)
- Calculate expected values that match VHDL arithmetic exactly
- Design test wrapper if needed (CocoTB can't access real/boolean directly)
- Create constants file structure with helper functions

**Test Level Guidelines:**
- **P1:** 2-4 essential tests, <20 line output, <5s runtime (LLM-optimized)
- **P2:** 5-10 comprehensive tests, <50 lines, <30s
- **P3:** 15-25 exhaustive tests, <100 lines, <2min

**Output:**
Save test strategy document to: `workflow/artifacts/tests/test_strategy.md`

**Test Strategy Should Include:**
1. List of tests for each level (P1/P2/P3)
2. Test values (matching spec's test requirements)
3. Expected value calculations (step-by-step)
4. Constants file design (TestValues class, helper functions)
5. Test wrapper design (if real/boolean types present)

---

**Note:** Replace `[COMPONENT]` and `[YOUR_SPEC]` with actual names.

**Example usage:**
```
Read workflow/artifacts/vhdl/forge_util_pwm.vhd and
workflow/specs/pending/pwm_generator.md, then design CocoTB progressive
test architecture as described above.
```
