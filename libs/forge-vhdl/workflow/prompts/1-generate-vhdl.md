# Agent 1: VHDL Generation Prompt

**Copy-paste this into Claude Code to run just VHDL generation:**

---

Read the component specification at `workflow/specs/pending/[YOUR_SPEC].md` and generate VHDL-2008 compliant code:

**Requirements:**
- Generate entity + architecture from spec
- Follow VHDL coding standards:
  - Use `std_logic_vector` for FSM states (NOT enums - Verilog compatibility)
  - Port order: clk, rst_n, enable, data inputs, data outputs, status
  - Active-low reset (`rst_n`)
  - GHDL-compatible patterns (2-cycle waits for registered outputs)
- Include inline documentation (comments)
- Match interface exactly as specified in spec

**Output:**
Save generated VHDL to: `workflow/artifacts/vhdl/[component_name].vhd`

**Verification:**
After generation, verify:
- All ports from spec are present
- Reset behavior matches spec
- Enable/disable logic matches spec
- FSM states use `std_logic_vector` encoding

---

**Note:** Replace `[YOUR_SPEC]` with your actual spec filename.

**Example usage:**
```
Read workflow/specs/pending/pwm_generator.md and generate VHDL-2008
compliant code as described above.
```
