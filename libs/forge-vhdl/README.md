# 🚀 forge-vhdl: Multi-Tenant AI-Powered VHDL Development

**Build tested VHDL components in minutes with your choice of AI assistant**

**Version:** 3.3.0-multi-tenant
**Template:** https://github.com/vmars-20/forge-vhdl-3v3-vmars

---

## 🎯 Choose Your AI Assistant

This multi-tenant repository supports three leading AI development environments. Each has unique strengths - choose based on your workflow preferences:

### 🤖 [Claude (Original Edition)](CLAUDE.md)

**Best for:** Autonomous workflows, cloud execution, minimal interaction

**Pros:**
- ✅ Full 3-agent autonomous workflow
- ✅ Environment-aware (auto-detects local/cloud)
- ✅ Hybrid workflow (local requirements → cloud agents)
- ✅ Incremental git commits in sandbox branches
- ✅ No token limits in cloud execution

**Cons:**
- ⚠️ Requires git push/pull for cloud handoff
- ⚠️ Cloud execution may have latency
- ⚠️ Less interactive than IDE-based tools

**Quick Start:** [Read CLAUDE.md](CLAUDE.md#quick-start) for `/forge-start` command

---

### 💻 [GitHub Copilot Edition](COPILOT.md)

**Best for:** IDE-integrated development, iterative coding, immediate feedback

**Pros:**
- ✅ Inline code suggestions while typing
- ✅ Deep VS Code/IDE integration
- ✅ Chat-based iterative development
- ✅ File-focused context awareness
- ✅ Immediate feedback on changes
- ✅ Works great in GitHub Codespaces

**Cons:**
- ⚠️ No multi-agent orchestration
- ⚠️ Limited to file-by-file generation
- ⚠️ Requires manual coordination between steps
- ⚠️ Less autonomous than agent-based tools

**Quick Start:** [Read COPILOT.md](COPILOT.md#quick-start) for `@workspace` commands

---

### 🎨 [Cursor Edition](CURSOR.md)

**Best for:** Full local execution, multi-agent orchestration, best of both worlds

**Pros:**
- ✅ Complete local multi-agent orchestration
- ✅ No cloud handoff needed
- ✅ Composer mode for complex workflows
- ✅ Real-time test execution and debugging
- ✅ IDE integration with agent capabilities
- ✅ Incremental commits without leaving IDE

**Cons:**
- ⚠️ Cursor-specific (requires Cursor IDE)
- ⚠️ May require more local resources
- ⚠️ Learning curve for Composer mode

**Quick Start:** [Read CURSOR.md](CURSOR.md#quick-start) for Composer (`Cmd+I`) workflows

---

## 📚 Documentation Architecture

This repository uses a **hierarchical documentation strategy** optimized for AI token usage:

- **[llms.txt](llms.txt)** - Minimal entry point (~500 tokens)
- **[CONTEXT_MANAGEMENT.md](CONTEXT_MANAGEMENT.md)** - Token optimization strategy (IMPORTANT!)
- **Tool-specific guides** - Detailed workflows for each AI assistant

### Progressive Discovery

Each directory contains a README.md explaining:
- Where you are in the structure
- What should be there
- How it relates to the whole

Start with `llms.txt`, then load documentation as needed following the tiered approach in `CONTEXT_MANAGEMENT.md`.

---

## 🔄 Common Workflows

All three AI assistants support these core workflows:

1. **AI-First Requirements** (2-5 minutes)
   - Quick pattern matching
   - 2-3 critical questions
   - Intelligent defaults

2. **Engineer Requirements** (15-30 minutes)
   - 30-question structured interview
   - Full specification control
   - Detailed documentation

3. **3-Agent Workflow**
   - Agent 1: VHDL generation
   - Agent 2: Test design
   - Agent 3: Test implementation

The implementation details vary by tool - see tool-specific guides for details.

---

## 🧪 Testing Standards

All editions follow the same progressive testing approach:

| Level | Tests | Output | Runtime | Use Case |
|-------|-------|--------|---------|----------|
| **P1** | 2-4 essential | <20 lines | <5 sec | Default - fast iteration |
| **P2** | 5-10 + edges | <50 lines | <30 sec | Standard validation |
| **P3** | 15-25 comprehensive | <100 lines | <2 min | Full coverage |

---

## 🚀 Getting Started

1. **Choose your AI assistant** (see comparison above)
2. **Read the tool-specific guide:**
   - Claude → [CLAUDE.md](CLAUDE.md)
   - Copilot → [COPILOT.md](COPILOT.md)
   - Cursor → [CURSOR.md](CURSOR.md)
3. **Follow the quick start** in your chosen guide
4. **Load documentation progressively** (see [CONTEXT_MANAGEMENT.md](CONTEXT_MANAGEMENT.md))

---

## 🏗️ Project Structure

```
.
├── README.md                    # This file - choose your AI
├── llms.txt                     # Minimal entry point for AI agents
├── CONTEXT_MANAGEMENT.md        # Token optimization strategy
├── CLAUDE.md                    # Claude-specific guide
├── COPILOT.md                   # Copilot-specific guide
├── CURSOR.md                    # Cursor-specific guide
│
├── .claude/                     # Shared agent infrastructure
│   ├── agents/                  # Agent definitions (all tools use)
│   ├── env_detect.py           # Environment detection
│   └── ...
│
├── .github/                     # GitHub-specific
│   └── copilot-instructions.md # Copilot custom instructions
│
├── .vscode/                     # VS Code settings
│   ├── settings.json           # Workspace configuration
│   └── extensions.json         # Recommended extensions
│
├── vhdl/                       # VHDL components
├── cocotb_tests/               # Test suite
├── workflow/                   # Requirements & specs
├── docs/                       # Technical documentation
└── scripts/                    # Utilities
```

---

## 🤝 Hybrid Workflows

You can combine tools for optimal results:

### Claude + Copilot
- Use Claude for requirements and initial generation
- Use Copilot for iterative refinement

### Cursor + Claude
- Use Cursor for local development
- Use Claude Web for long-running cloud tasks

### All Three
- Requirements with Claude's `/forge-start`
- Development with Cursor's orchestration
- Refinement with Copilot's suggestions

---

## 📖 Key Documents

**Start Here:**
- [llms.txt](llms.txt) - Component catalog (minimal)
- [CONTEXT_MANAGEMENT.md](CONTEXT_MANAGEMENT.md) - Token optimization

**Tool Guides:**
- [CLAUDE.md](CLAUDE.md) - Claude workflows
- [COPILOT.md](COPILOT.md) - Copilot workflows
- [CURSOR.md](CURSOR.md) - Cursor workflows

**Technical:**
- [docs/VHDL_CODING_STANDARDS.md](docs/VHDL_CODING_STANDARDS.md) - Style guide
- [docs/PROGRESSIVE_TESTING_GUIDE.md](docs/PROGRESSIVE_TESTING_GUIDE.md) - Testing patterns
- [workflow/specs/reference/](workflow/specs/reference/) - Example specifications

---

## 📄 License & Info

**License:** MIT License - See `LICENSE` file
**Version:** 3.3.0-multi-tenant
**Template:** https://github.com/vmars-20/forge-vhdl-3v3-vmars
**Last Updated:** 2025-01-XX
**Maintainer:** Moku Instrument Forge Team

---

**Choose your tool above and get started! Each path leads to the same destination: tested VHDL components in minutes.**