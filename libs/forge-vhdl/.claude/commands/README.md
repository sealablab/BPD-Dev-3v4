# VHDL-FORGE Slash Commands

Quick reference for custom slash commands in VHDL-FORGE.

---

## Available Commands

### /forge-start

**Purpose:** Interactive session starter for local VHDL development (environment-aware)

**What it does:**
- Detects environment (local vs cloud) and validates GHDL installation
- Guides through output settings configuration (local only)
- Routes to appropriate workflow (Student/Engineer/Examples/Cloud validation)
- Loads context progressively based on workflow selection

**Usage modes:**
```
/forge-start              → Interactive mode selector
/forge-start student      → AI-First workflow (2-5 min, intelligent defaults)
/forge-start engineer     → Engineer workflow (15-30 min, full control)
/forge-start cloud        → Validate cloud-compatible setup from local
```

**When to use:**
- ✅ **First command in new session** (recommended!)
- ✅ Starting a new VHDL component (routes to requirements)
- ✅ Validating environment setup
- ✅ Learning workflow options (interactive browser)
- ✅ Checking cloud compatibility before deployment

**When NOT to use:**
- ❌ Mid-session (environment already validated)
- ❌ Just asking quick questions
- ❌ Working on existing components (use direct workflow)

**Session flow (interactive mode):**
1. **Environment Detection** - GHDL check, local/cloud identification
2. **Output Settings Validation** - Guides through /config setup (local only)
3. **Workflow Selection** - Choose Student/Engineer/Examples/Cloud
4. **Context Loading** - Loads only relevant docs for chosen workflow
5. **Workflow Activation** - Begins requirements gathering or validation

**Student Mode (AI-First):**
- 2-5 critical questions only
- Pattern recognition fills in defaults
- 2-5 minutes → complete specification
- Best for: Learning, prototyping, quick builds

**Engineer Mode (Advanced):**
- Delegates to `/gather-requirements`
- 30-question structured interview
- 15-30 minutes → detailed specification
- Best for: Production components, complex FSMs

**Cloud Validation Mode:**
- Checks GHDL, Python, CocoTB, Git configuration
- Validates directory structure
- Reports compatibility status
- Best for: Pre-deployment verification

**Example session:**
```
🔧 VHDL-FORGE Local | GHDL 5.0.1 | Type /forge-start for interactive setup

User: /forge-start

[Environment detection runs...]
💻 LOCAL ENVIRONMENT DETECTED
✅ GHDL Found: GHDL 5.0.1

[Settings check via interactive UI...]
"Have you verified your Claude Code output settings?"
User: [selects "Yes, settings verified"]

[Workflow selection via interactive UI...]
"Which workflow would you like to use?"
User: [selects "🚀 Student (AI-First)"]

✅ FORGE-START COMPLETE
Workflow: ✅ Student (AI-First) activated

"What component would you like to build?"
User: "A PWM generator for LED dimming"

[AI-First requirements gathering begins - 2-5 questions...]
```

**Output artifacts:**
- Environment status banner
- Settings validation checklist
- Workflow-specific context loaded
- Ready state confirmation

**Next steps after /forge-start:**
- Student mode → AI-First requirements (2-5 questions)
- Engineer mode → `/gather-requirements` (30 questions)
- Examples → Select reference spec → 3-agent workflow
- Cloud validation → Compatibility report → workflow selection

**Integration with session hook:**
On session start, you'll see:
```
🔧 VHDL-FORGE Local | GHDL 5.0.1 | Type /forge-start for interactive setup
```
This lightweight banner reminds you to run `/forge-start` for full setup.

---

### /gather-requirements

**Purpose:** Interactive requirements gathering for VHDL component development

**What it does:**
- Launches structured Q&A session (7 phases, ~15-20 questions)
- Validates answers against VHDL-FORGE standards
- Generates complete specification document
- Outputs to: `workflow/specs/pending/[component_name].md`

**When to use:**
- ✅ Starting a new VHDL component
- ✅ Requirements are unclear or incomplete
- ✅ Want guided, structured requirements capture
- ✅ Learning VHDL-FORGE standards and patterns

**When NOT to use:**
- ❌ Requirements already crystal clear (write spec manually)
- ❌ Enhancing existing component (read existing VHDL first)

**Session structure:**
1. **Component Identification** - Name, category, purpose
2. **Functionality Deep Dive** - Features, modes, constraints
3. **Interface Specification** - Ports, generics, types
4. **Behavior Specification** - Reset, enable, states
5. **Testing Strategy** - P1/P2/P3, test cases, values
6. **Design Guidance** - Architecture, dependencies
7. **Specification Generation** - Creates final document

**Output format:**
```
workflow/specs/pending/[component_name].md
```
- Complete specification following VHDL-FORGE template
- Ready for 4-agent automated workflow
- Includes: requirements, interface, tests, design notes

**Example usage:**
```
/gather-requirements

[Interactive Q&A session begins]
You: "Let's design your VHDL component together. What should we call this component?"
User: "A clock divider"
...
[15-20 questions later]
✅ Specification created: workflow/specs/pending/forge_util_clk_divider.md
```

**Next steps after completion:**
```
Option 1 (Recommended): Run full automated workflow
"Read workflow/specs/pending/[component].md and execute the complete 4-agent workflow"

Option 2: Manual implementation
Use spec as guide and implement by hand

Option 3: Refine spec first
Edit generated spec, then run workflow
```

---

## Future Commands (Planned)

### /validate-spec (Coming Soon)

Check specification completeness and standards compliance.

### /review-artifacts (Coming Soon)

Review generated VHDL and tests before integration.

### /integrate-component (Coming Soon)

Automated move from artifacts/ to main codebase with git commit.

---

## How Slash Commands Work

Slash commands in Claude Code:
1. User types `/command-name` in chat
2. Claude loads `.claude/commands/command-name.md`
3. The markdown file contains a prompt that Claude executes
4. User sees the result of executing that prompt

**Creating new commands:**
1. Create `.claude/commands/your-command.md`
2. Write prompt in markdown format
3. Include YAML frontmatter with description:
   ```yaml
   ---
   description: Short description of what this command does
   ---
   ```
4. Command available as `/your-command`

---

## See Also

- `.claude/agents/` - Specialized agents for VHDL development
- `workflow/` - Workflow guides and examples
- `CLAUDE.md` - VHDL-FORGE standards and testing guide
