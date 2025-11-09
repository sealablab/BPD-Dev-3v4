# VHDL-FORGE Workflow Guide

**Purpose:** Simple workflow for AI-assisted VHDL component development

**Target:** Users with Claude Code (desktop/web) who want to leverage the 4-agent system

---

## Quick Start

### 1. Write Your Spec

Create a markdown file in `specs/pending/`:

```bash
cp specs/examples/pwm_generator.md specs/pending/my_component.md
# Edit specs/pending/my_component.md with your requirements
```

**Or** start from scratch - see `specs/README.md` for template.

**Or** use one of two requirements gathering workflows (recommended):

**DEFAULT: AI-First Workflow (Students/Beginners - 2-5 minutes)**
- For students, beginners, clear requirements, pattern-matched components
- Claude infers defaults, proposes complete spec with 2-3 critical questions
- Fast iteration and prototyping
- See `AI_FIRST_REQUIREMENTS.md`

**ALTERNATIVE: Engineer Workflow (Detailed Control - 15-30 minutes)**
- For engineers, novel architectures, complex systems
- 30 guided questions across 7 phases for full technical control
- Learning VHDL-FORGE standards in depth
- See `ENGINEER_REQUIREMENTS.md`

---

### 2. Run the Workflow

**Option A: Full Workflow (Recommended for First Time)**

Copy prompt from `prompts/full-workflow.md` and paste into Claude Code:

```
Read workflow/specs/pending/my_component.md and run the complete
4-agent workflow to generate VHDL + tests.
```

Claude will:
1. Generate VHDL component
2. Design test architecture
3. Implement CocoTB tests
4. Run P1 tests

**Option B: Individual Agents (For Iteration)**

Use individual prompts from `prompts/`:
- `1-generate-vhdl.md` - Just VHDL generation
- `2-design-tests.md` - Just test architecture design
- `3-run-tests.md` - Just test implementation + execution

---

### 3. Review Artifacts

Generated files appear in `workflow/artifacts/`:

```
workflow/artifacts/
├── vhdl/my_component.vhd           # Review VHDL
├── tests/my_component_tests/       # Review tests
└── logs/my_component_workflow.md   # Workflow log
```

**Important:** Review before moving to main codebase!

---

### 4. Move to Codebase

Once satisfied with generated code:

```bash
# Move VHDL to appropriate location
mv workflow/artifacts/vhdl/my_component.vhd vhdl/components/utilities/

# Move tests to appropriate location
mv workflow/artifacts/tests/my_component_tests cocotb_tests/components/

# Update test configs
# (Agent 3 usually does this, but verify)
```

---

## Workflow Patterns

### Pattern 1: New Component (Interactive)

```
User: "I need a clock divider"
  ↓
Agent 0 (forge-new-component): Asks clarifying questions
  ↓
Agent 0: Creates spec in specs/pending/
  ↓
User: Reviews spec, confirms
  ↓
User: Runs full-workflow prompt
  ↓
Agents 1-3: Generate VHDL + tests
  ↓
User: Reviews artifacts/
  ↓
User: Moves to codebase
```

### Pattern 2: Pre-Written Spec (Batch)

```
User: Writes detailed spec in specs/pending/uart.md
  ↓
User: Runs full-workflow prompt
  ↓
Agents 1-3: Generate VHDL + tests (no interaction needed)
  ↓
User: Reviews artifacts/
  ↓
User: Moves to codebase OR iterates
```

### Pattern 3: Test-Only Workflow

```
User: "Add tests for existing forge_util_pwm"
  ↓
User: Runs prompts/2-design-tests.md + 3-run-tests.md
  ↓
Agents 2-3: Generate tests only
  ↓
User: Reviews artifacts/tests/
  ↓
User: Moves to cocotb_tests/components/
```

---

## Directory Reference

| Directory | Purpose | Gitignored? |
|-----------|---------|-------------|
| `specs/pending/` | User component specs | No (tracked) |
| `specs/examples/` | Reference specs | No (tracked) |
| `prompts/` | Copy-paste agent prompts | No (tracked) |
| `artifacts/` | Generated code (scratch) | **Yes** |
| `artifacts/vhdl/` | Generated VHDL | **Yes** |
| `artifacts/tests/` | Generated tests | **Yes** |
| `artifacts/logs/` | Workflow logs | **Yes** |

**Why gitignore artifacts/?**
- Generated code should be reviewed before committing
- Prevents accidental commits of unreviewed code
- Keeps main codebase clean

---

## Tips

### Spec Writing
- Be specific about interfaces (port names, widths)
- Specify test complexity (P1: 3 tests, P2: 10 tests)
- Include expected behavior (reset, enable, edge cases)

### Agent Coordination
- Let Agent 0 ask questions (interactive requirements)
- Agent 1 reads specs and generates VHDL
- Agent 2 designs tests (before implementation)
- Agent 3 implements and runs tests

### Iteration
- Review artifacts/ after each agent
- Re-run individual agents if needed
- Update spec and re-run full workflow

### Claude Code Web
- Full workflow works great in web UI
- Agents run autonomously (no local setup needed)
- DevContainer provides GHDL + CocoTB environment

---

## Example Session

```
# 1. Start with spec
vim workflow/specs/pending/spi_controller.md
# (Write detailed SPI controller spec)

# 2. Kick off workflow in Claude Code
"Read workflow/specs/pending/spi_controller.md and run the complete
4-agent workflow. Generate VHDL component + CocoTB progressive tests."

# 3. Agents run (5-10 minutes)
# - Agent 1: Generates VHDL
# - Agent 2: Designs test architecture
# - Agent 3: Implements tests, runs P1 tests

# 4. Review outputs
ls workflow/artifacts/vhdl/
ls workflow/artifacts/tests/

# 5. Test manually (optional)
uv run python cocotb_tests/run.py spi_controller

# 6. Move to codebase
mv workflow/artifacts/vhdl/spi_controller.vhd vhdl/components/utilities/
mv workflow/artifacts/tests/spi_controller_tests cocotb_tests/components/
git add vhdl/components/utilities/spi_controller.vhd
git add cocotb_tests/components/spi_controller_tests
git commit -m "feat: Add SPI controller with CocoTB tests"
```

---

## Troubleshooting

**Q: Agents can't find my spec**
- Ensure spec is in `workflow/specs/pending/`
- Use full path in prompt: `workflow/specs/pending/my_component.md`

**Q: Generated code not appearing**
- Check `workflow/artifacts/` directories
- Agents may save to different subdirectories

**Q: Tests fail after generation**
- Review `artifacts/logs/` for errors
- Re-run Agent 3 with fixes
- Check GHDL installation: `ghdl --version`

**Q: Want to restart workflow**
- Delete `artifacts/` contents
- Re-run full workflow prompt

---

## Advanced: Custom Prompts

Create your own prompts in `prompts/`:

```markdown
# prompts/my-custom-workflow.md

Read all specs in workflow/specs/pending/*.md and:
1. Generate VHDL for each component
2. Design P2-level tests (10+ tests each)
3. Run all tests and report results
4. Generate integration test for all components
```

Then reference it: `"Follow workflow/prompts/my-custom-workflow.md"`

---

## See Also

- `AI_FIRST_REQUIREMENTS.md` - **DEFAULT** rapid requirements workflow (2-5 min, students/beginners)
- `ENGINEER_REQUIREMENTS.md` - Detailed requirements workflow (15-30 min, engineers)
- `.claude/README.md` - Agent workflow details
- `CLAUDE.md` - Testing standards, VHDL coding rules
- `SPEC.md` - System setup (GHDL, uv, containers)
- `specs/README.md` - Spec writing guide
- `specs/reference/README.md` - Gold-standard pattern library

## Output Styles (Future Feature)

**Note:** Output style customization is a planned feature for future Claude Code releases. When available, it will enable:
- Collaborative learning mode with explanatory comments
- TODO(human) markers for student contribution points
- Interactive pair-programming experience

Stay tuned for updates in future releases.
