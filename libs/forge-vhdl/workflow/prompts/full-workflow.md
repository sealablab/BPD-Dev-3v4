# Full 4-Agent Workflow Prompt

**Copy-paste this into Claude Code to run the complete workflow:**

---

Read the component specification at `workflow/specs/pending/[YOUR_SPEC].md` and execute the complete 4-agent VHDL development workflow:

**Agent 1: VHDL Generation**
- Read the spec and generate VHDL-2008 compliant entity + architecture
- Follow VHDL coding standards (std_logic_vector for FSM states, port order)
- Use GHDL-compatible patterns (2-cycle waits for registered outputs)
- Save output to: `workflow/artifacts/vhdl/[component_name].vhd`

**Agent 2: Test Architecture Design**
- Analyze the generated VHDL component
- Design progressive test architecture (P1/P2/P3 as specified in spec)
- Calculate expected values (match VHDL arithmetic exactly)
- Design test wrapper if real/boolean types present
- Create constants file structure
- Save test strategy to: `workflow/artifacts/tests/test_strategy.md`

**Agent 3: Test Implementation & Execution**
- Read Agent 2's test strategy
- Implement CocoTB test suite following progressive testing pattern
- Create constants file (`[component]_constants.py`)
- Create P1 test module (`P1_[component]_basic.py`)
- Create test orchestrator (`test_[component]_progressive.py`)
- Save to: `workflow/artifacts/tests/[component]_tests/`
- Run P1 tests via CocoTB + GHDL
- Report results (should be <20 lines output)

**Final Report:**
After all agents complete, provide:
1. Summary of generated files
2. P1 test results (pass/fail counts)
3. Any issues encountered
4. Recommended next steps (move to codebase, run P2 tests, etc.)

---

**Note:** Replace `[YOUR_SPEC]` with your actual spec filename.

**Example usage:**
```
Read workflow/specs/pending/pwm_generator.md and execute the complete
4-agent VHDL development workflow as described above.
```
