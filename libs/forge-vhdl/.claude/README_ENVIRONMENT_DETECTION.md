# Environment Detection System

**Version:** 1.0
**Purpose:** Document the environment-aware architecture for forge-vhdl
**Audience:** Maintainers and contributors

---

## System Overview

forge-vhdl uses **automatic environment detection** to provide optimized workflows for:
- 💻 **Local Development** (Claude Code CLI)
- 🌐 **Cloud Development** (Claude Code Web, GitHub Codespaces)

---

## Architecture

### Detection Flow

```
User launches Claude
   ↓
.claude/startup.py (automatic)
   ↓
.claude/env_detect.py
   ↓
   ┌──────────────────┬──────────────────┐
   │ Local Detected   │ Cloud Detected   │
   ├──────────────────┼──────────────────┤
   │ Check GHDL       │ Check GHDL       │
   │ installed?       │ installed?       │
   ├──────────────────┼──────────────────┤
   │ Found: Guide to  │ Found: Ready     │
   │ check /config    │ to develop       │
   │                  │                  │
   │ Not found:       │ Not found:       │
   │ Guide to install │ Auto-install     │
   ├──────────────────┼──────────────────┤
   │ Load:            │ Load:            │
   │ CLAUDE_LOCAL.md  │ CLAUDE_CLOUD.md  │
   └──────────────────┴──────────────────┘
```

---

## Components

### 1. Detection Script (`.claude/env_detect.py`)

**Purpose:** Detect runtime environment and GHDL availability

**Functions:**

**`detect_runtime_environment() -> str`**
- Returns `"local"` or `"cloud"`
- Checks for cloud indicators:
  - `CODESPACES` environment variable
  - `GITPOD_WORKSPACE_ID` environment variable
  - `REMOTE_CONTAINERS` environment variable
  - `/.dockerenv` file exists
  - `/workspace` directory + `HOME=/root`
- Defaults to `"local"` (safest for template repos)

**`check_ghdl_installed() -> (bool, str)`**
- Runs `ghdl --version`
- Returns (installed, version_string)
- Timeout after 5 seconds

**`check_claude_cli_config() -> Dict`**
- Placeholder for future programmatic config checks
- Currently returns recommendations (user must verify manually)

**`generate_startup_message() -> str`**
- Creates formatted welcome banner
- Environment-specific guidance
- GHDL status display
- Next steps

**`get_claude_md_variant() -> str`**
- Returns `"local"` or `"cloud"`
- Used to load appropriate CLAUDE.md variant

**Usage:**
```bash
# Manual check
uv run python .claude/env_detect.py

# Programmatic use (from Python)
from env_detect import detect_runtime_environment, check_ghdl_installed

env = detect_runtime_environment()  # "local" or "cloud"
ghdl_found, version = check_ghdl_installed()
```

---

### 2. Startup Script (`.claude/startup.py`)

**Purpose:** Display environment-specific welcome message on Claude startup

**Flow:**
1. Imports `env_detect` module
2. Calls `generate_startup_message()`
3. Displays formatted banner
4. Announces which CLAUDE.md variant will be loaded
5. Exits with code 0 (local) or 1 (cloud)

**Exit Codes:**
- `0` → Local environment detected
- `1` → Cloud environment detected
- `2` → Error (fallback to standard CLAUDE.md)

**Integration:**
Claude Code CLI can execute this on startup to show environment info.

---

### 3. Environment-Specific Guides

**`.claude/CLAUDE_LOCAL.md`** (~700 lines)
- **Target:** Local Claude Code CLI users
- **Emphasizes:**
  - Output settings validation (`/config`)
  - Screenshot reference: `static/Claude-CLI-output-settings.png`
  - Interactive requirements gathering
  - Manual GHDL installation guide (macOS/Linux)
  - Local testing workflow

**`.claude/CLAUDE_CLOUD.md`** (~600 lines)
- **Target:** Cloud users (Claude Web, Codespaces)
- **Emphasizes:**
  - GHDL pre-installed via DevContainer
  - Zero local setup required
  - Streamlined AI-First workflow
  - Browser-based VHDL simulation
  - Auto-install fallback (rare)

**`CLAUDE.md`** (~300 lines)
- **Role:** Router/index for all environments
- **Content:**
  - Environment detection instructions
  - Quick reference tables
  - Navigation to environment guides
  - Troubleshooting
  - Component catalog summary

---

### 4. DevContainer Configuration

**`.devcontainer/devcontainer.json`**

**Base Image:**
```json
"image": "ghdl/ghdl:ubuntu22-llvm-5.0"
```
- Official GHDL Docker image
- GHDL 5.0 with LLVM backend **pre-installed**
- Ubuntu 22.04 base

**Automatic Setup:**
```json
"postCreateCommand": "apt-get update && apt-get install -y llvm-18 && curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH=\"$HOME/.cargo/bin:$PATH\" && uv run python scripts/cloud_setup_with_ghdl.py"
```

**On container creation:**
1. Install LLVM 18 (required for GHDL-LLVM)
2. Install `uv` (Python package manager)
3. Run `cloud_setup_with_ghdl.py` (validation)

**Validation Script:**
```json
"updateContentCommand": "uv run python scripts/cloud_setup_with_ghdl.py"
```
- Re-validates GHDL on content updates

**Result:**
- ✅ GHDL always present in cloud environments
- ✅ Auto-validated on every container creation
- ✅ Ready for VHDL development immediately

---

## Cloud Environment Detection

### Indicators Checked

**Environment Variables:**
- `CODESPACES` → GitHub Codespaces
- `GITPOD_WORKSPACE_ID` → Gitpod
- `REMOTE_CONTAINERS` → VS Code Remote Containers

**File System:**
- `/.dockerenv` → Docker container
- `/workspace` + `HOME=/root` → Common Codespaces pattern

### Why Default to Local?

**Reason:** Template repositories start as local clones.

**Scenario:**
1. User forks template on GitHub
2. User clones to local machine
3. User runs `uv sync` (no container yet)
4. User launches Claude locally

If we defaulted to cloud, local users would see incorrect guidance.

**Safety:** Better to assume local (user can verify) than assume cloud (might not have GHDL).

---

## GHDL Installation

### Cloud (Automatic)

**Method:** DevContainer base image
- Official `ghdl/ghdl:ubuntu22-llvm-5.0` image
- GHDL pre-compiled and ready
- Validation script runs on creation

**Fallback:** `scripts/cloud_setup_with_ghdl.py`
- Rare case: GHDL missing or broken
- Reinstalls GHDL + LLVM 18
- Creates library symlinks
- Validates with sample simulation

**Result:** GHDL is a **hard requirement** and always present.

### Local (Manual Guidance)

**Method:** User installs via package manager

**macOS:**
```bash
brew install ghdl
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ghdl ghdl-llvm
```

**After install:**
```bash
# Restart Claude session
exit
claude
```

Claude will re-detect and confirm GHDL is available.

**Why not auto-install locally?**
- Requires `sudo` (security concern)
- Different package managers (brew, apt, dnf, pacman, etc.)
- User may want specific GHDL version/backend
- Better to guide user through their preferred method

---

## Output Settings Validation (Local Only)

### Why This Matters

**Problem:** VHDL test output can be verbose (hundreds of lines)

**forge-vhdl goal:** <20 line P1 test output (LLM-optimized)

**Claude CLI default:** Verbose mode can defeat this optimization

**Solution:** Guide users to check `/config` settings

### Recommended Settings

| Setting | Value | Why |
|---------|-------|-----|
| Verbose output | `false` | Prevents duplicate/verbose logs |
| Output style | `default` | Best for test output formatting |
| Auto-compact | `false` | Preserves VHDL test context |
| Rewind code | `true` | Helpful for iterative debugging |

### How We Guide Users

**Startup banner (local only):**
```
╔════════════════════════════════════════════════════════════════════╗
║  Before we start, please verify your output settings:             ║
║                                                                    ║
║  1. Run: /config                                                   ║
║  2. Navigate to "Config" tab                                       ║
║  3. Check these settings:                                          ║
║     • Verbose output: false (RECOMMENDED for clean logs)           ║
║     • Output style: default (RECOMMENDED)                          ║
║     • Auto-compact: false (RECOMMENDED for VHDL test output)       ║
║                                                                    ║
║  Reference screenshot: static/Claude-CLI-output-settings.png       ║
╚════════════════════════════════════════════════════════════════════╝
```

**CLAUDE_LOCAL.md:**
- Dedicated section with step-by-step instructions
- Screenshot reference
- Explanation of why each setting matters

**Cloud environments:**
- No output settings to check (browser-based)
- Banner omits this section

---

## User Workflows

### S0-S3: Template Onboarding

**S0: Fork Template Repository (GitHub)**
- User clicks "Use this template"
- Creates new repository

**S1: Clone Repository Locally**
```bash
git clone https://github.com/[user]/my-vhdl-project
cd my-vhdl-project
```

**S2: Bootstrap Python Environment**
```bash
uv sync
```
- No GHDL required yet
- Installs CocoTB, Python dependencies

**S3: Launch Claude and Detect Environment**
```bash
claude
```

**Claude automatically:**
1. Runs `env_detect.py`
2. Displays welcome banner
3. Loads appropriate guide (CLAUDE_LOCAL.md or CLAUDE_CLOUD.md)
4. Guides through next steps

### Local Development (Post-Setup)

1. **Verify output settings** (`/config`)
2. **Try first component:**
   ```
   "I need a PWM generator. Use the AI-First workflow."
   ```
3. **Review specification** (workflow/specs/pending/)
4. **Approve automated workflow** (Agents 1-3)
5. **Review artifacts** (workflow/artifacts/)
6. **Run tests** (ensure <20 line P1 output)
7. **Commit to git**

### Cloud Development (Post-Setup)

1. **Confirm GHDL validated** (automatic)
2. **Try first component:**
   ```
   "I need a PWM generator. Use the AI-First workflow."
   ```
3. **Review specification** (workflow/specs/pending/)
4. **Approve automated workflow** (Agents 1-3)
5. **Review artifacts** (workflow/artifacts/)
6. **Run tests** (ensure <20 line P1 output)
7. **Commit to git**

**Difference:** No output settings to check in cloud!

---

## File Locations

**Detection System:**
- `.claude/env_detect.py` - Core detection logic
- `.claude/startup.py` - Welcome banner display

**Environment Guides:**
- `CLAUDE.md` - Router/index (~300 lines)
- `.claude/CLAUDE_LOCAL.md` - Local workflow (~700 lines)
- `.claude/CLAUDE_CLOUD.md` - Cloud workflow (~600 lines)

**DevContainer:**
- `.devcontainer/devcontainer.json` - Cloud environment config

**Documentation:**
- `docs/ONBOARDING.md` - S0-S3 walkthrough
- `.claude/README_ENVIRONMENT_DETECTION.md` - This file

**Reference:**
- `static/Claude-CLI-output-settings.png` - Screenshot for local users

---

## Testing

### Manual Environment Detection Test

```bash
# From repository root
uv run python .claude/env_detect.py
```

**Expected output (local):**
```
Runtime Environment: local
GHDL Installed: True
GHDL Version: GHDL 5.0.1 (gcc backend)

Recommended workflow: CLAUDE_LOCAL.md

╔════════════════════════════════════════════════════════════════════╗
║  💻 LOCAL ENVIRONMENT DETECTED (Claude Code CLI)                   ║
║  ✅ GHDL Found: GHDL 5.0.1                                         ║
║  ...                                                               ║
╚════════════════════════════════════════════════════════════════════╝
```

**Expected output (cloud/DevContainer):**
```
Runtime Environment: cloud
GHDL Installed: True
GHDL Version: GHDL 5.0 (LLVM backend)

Recommended workflow: CLAUDE_CLOUD.md

╔════════════════════════════════════════════════════════════════════╗
║  🌐 CLOUD ENVIRONMENT DETECTED                                     ║
║  ✅ GHDL Found: GHDL 5.0 (LLVM backend)                            ║
║  ...                                                               ║
╚════════════════════════════════════════════════════════════════════╝
```

### Integration Test (DevContainer)

**GitHub Codespaces:**
1. Go to repository on GitHub
2. Click "Code" → "Create codespace"
3. Wait for container creation (~1-2 min)
4. Verify GHDL validation message appears
5. Launch Claude
6. Verify cloud workflow loads

**VS Code Remote Containers:**
1. Open repository in VS Code
2. Click "Reopen in Container"
3. Wait for container creation
4. Verify GHDL validation message
5. Launch Claude
6. Verify cloud workflow loads

---

## Future Enhancements

### Programmatic Config Reading

**Current:** User manually checks `/config`

**Future:** `check_claude_cli_config()` could:
- Read Claude CLI config file (if API available)
- Programmatically verify settings
- Auto-suggest changes

**Blocker:** Need Claude CLI config file format/API

### CI/CD Integration

**Test both environments:**
- Local: Run tests on macOS, Linux with GHDL installed
- Cloud: Run tests in DevContainer
- Verify environment detection works correctly

### Metrics Collection

**Track:**
- % users in local vs cloud
- GHDL installation success rate
- Output settings verification rate (local)

---

## Summary

**Key Innovation:**
Automatic environment detection with zero manual configuration.

**User Experience:**
1. Fork template
2. Clone locally
3. Run `uv sync`
4. Launch Claude
5. **Everything auto-configured!**

**Maintainability:**
- Single detection script (`env_detect.py`)
- Environment-specific guides (CLAUDE_LOCAL/CLOUD.md)
- DevContainer guarantees cloud setup
- Clear separation of concerns

**Result:**
Students and engineers can start VHDL development in minutes, not hours!

---

**Last Updated:** 2025-11-09
**Version:** 1.0
**Maintainer:** Moku Instrument Forge Team
