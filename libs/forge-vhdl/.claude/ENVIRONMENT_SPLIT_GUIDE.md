# Environment Split Architecture

**Version:** 3.2.0
**Purpose:** Documentation of LOCAL vs CLOUD environment detection and workflow routing
**Audience:** Maintainers, contributors, advanced users

---

## 🎯 Overview

The forge-vhdl template uses **automatic environment detection** to provide different workflows:

- **🌐 CLOUD:** GitHub Codespaces, Gitpod, Docker containers → GHDL pre-installed, automated agents
- **💻 LOCAL:** Claude Code CLI on user's machine → Interactive requirements, manual testing

**Why this split matters:**
- Cloud users **cannot/will not** install GHDL manually → must be pre-installed via DevContainer
- Local users **may already have** GHDL → can leverage local tooling and manual workflows
- Output verbosity differs between environments (local CLI has configurable output settings)

---

## 🔍 Detection Logic

### Detection Script: `.claude/env_detect.py`

**Function:** `detect_runtime_environment() -> str`

**Returns:**
- `"cloud"` - Running in cloud/containerized environment
- `"local"` - Running on user's local machine (default)

### Cloud Environment Indicators

The script checks for these environment variables/files (any truthy value triggers cloud mode):

```python
cloud_indicators = [
    os.environ.get("CODESPACES"),          # GitHub Codespaces
    os.environ.get("GITPOD_WORKSPACE_ID"), # Gitpod
    os.environ.get("REMOTE_CONTAINERS"),   # VS Code Remote Containers
    Path("/.dockerenv").exists(),          # Docker container
    Path("/workspace").exists() and os.environ.get("HOME") == "/root",  # Codespaces pattern
]
```

**Default:** If no cloud indicators detected → `"local"` (safest for template repos)

---

## 📋 Startup Messages

### Cloud Environment (GHDL Found)

```
╔════════════════════════════════════════════════════════════════════╗
║  🌐 CLOUD ENVIRONMENT DETECTED                                     ║
║  ✅ GHDL Found: GHDL 5.0 (LLVM backend)                            ║
║                                                                    ║
║  Ready for VHDL development! Using cloud workflow.                 ║
╚════════════════════════════════════════════════════════════════════╝

Loading cloud-optimized CLAUDE.md instructions...
```

**Next steps:** User directed to `.claude/CLAUDE_CLOUD.md`

---

### Cloud Environment (GHDL NOT Found)

```
╔════════════════════════════════════════════════════════════════════╗
║  🌐 CLOUD ENVIRONMENT DETECTED                                     ║
║  ⚠️  GHDL NOT FOUND                                                ║
║                                                                    ║
║  I can auto-install GHDL for you. This will take ~2-3 minutes.    ║
║  Command: uv run python scripts/cloud_setup_with_ghdl.py          ║
║                                                                    ║
║  Would you like me to install GHDL now?                           ║
╚════════════════════════════════════════════════════════════════════╝
```

**Expected behavior:** Claude offers to run auto-install script

**Note:** In DevContainer environments, this should NEVER happen (GHDL pre-installed)

---

### Local Environment (GHDL Found)

```
╔════════════════════════════════════════════════════════════════════╗
║  💻 LOCAL ENVIRONMENT DETECTED (Claude Code CLI)                   ║
║  ✅ GHDL Found: GHDL 5.0.1 (4.1.0.r602.g37ad91899) [Dunoon edition] ║
║                                                                    ║
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
║                                                                    ║
║  ✓ Ready for AI-First requirements gathering workflow!            ║
║  ✓ Interactive mode enabled (default for students/beginners)      ║
╚════════════════════════════════════════════════════════════════════╝

Loading local-optimized CLAUDE.md instructions...
```

**Next steps:** User directed to `.claude/CLAUDE_LOCAL.md` and `/config` verification

---

### Local Environment (GHDL NOT Found)

```
╔════════════════════════════════════════════════════════════════════╗
║  💻 LOCAL ENVIRONMENT DETECTED (Claude Code CLI)                   ║
║  ⚠️  GHDL NOT FOUND                                                ║
║                                                                    ║
║  For VHDL simulation, please install GHDL:                         ║
║                                                                    ║
║  macOS:                                                            ║
║    brew install ghdl                                               ║
║                                                                    ║
║  Ubuntu/Debian:                                                    ║
║    sudo apt-get install ghdl ghdl-llvm                             ║
║                                                                    ║
║  After installing GHDL, restart this session.                      ║
║                                                                    ║
║  Note: You can still gather requirements and generate specs        ║
║  without GHDL. Testing requires GHDL installation.                 ║
╚════════════════════════════════════════════════════════════════════╝
```

**Expected behavior:** User manually installs GHDL via package manager

---

## 📚 Documentation Routing

### Master Router: `CLAUDE.md`

**Purpose:** Main entry point that directs users to environment-specific guides

**Key sections:**
- Environment detection instructions
- Quick start for both environments
- Link to `.claude/CLAUDE_LOCAL.md` OR `.claude/CLAUDE_CLOUD.md`

**Token count:** ~3.5k tokens (moderate, loaded at session start)

---

### Local Guide: `.claude/CLAUDE_LOCAL.md`

**Audience:** Users running Claude Code CLI locally

**Key features:**
- `/config` output settings verification (CRITICAL for local)
- Interactive AI-First requirements workflow (default)
- Manual testing workflow documentation
- Git workflow for submodules
- Local GHDL troubleshooting

**Token count:** ~4k tokens

---

### Cloud Guide: `.claude/CLAUDE_CLOUD.md`

**Audience:** Users in GitHub Codespaces, Gitpod, Claude Code Web

**Key features:**
- DevContainer setup (automatic GHDL install)
- Automated 3-agent workflow emphasis
- Cloud-specific troubleshooting (GHDL auto-install)
- Zero manual setup documentation

**Token count:** ~4k tokens

---

## 🛠️ Workflow Differences

### Cloud Workflow (Automated)

1. **User creates repo from template**
2. **Opens in Codespaces/Gitpod** (DevContainer auto-configures)
3. **GHDL pre-installed** (via DevContainer `postCreateCommand`)
4. **Claude detects cloud environment**
5. **Claude guides to `.claude/CLAUDE_CLOUD.md`**
6. **User requests component** ("I need a PWM generator")
7. **Claude invokes 3-agent workflow automatically** (no manual intervention)
8. **Artifacts ready** (`workflow/artifacts/vhdl/`, `workflow/artifacts/tests/`)

**Key:** Minimal user interaction, automated agent workflow

---

### Local Workflow (Interactive)

1. **User clones repo** (or creates from template)
2. **Installs GHDL manually** (or already has it)
3. **Runs `uv run python .claude/env_detect.py`**
4. **Claude detects local environment**
5. **Claude guides to `.claude/CLAUDE_LOCAL.md`**
6. **User verifies `/config` settings** (output verbosity, auto-compact, etc.)
7. **User requests component** ("I need a PWM generator. Use AI-First workflow.")
8. **Claude asks 2-3 critical questions** (interactive requirements gathering)
9. **Claude proposes specification** (user reviews and approves)
10. **Claude invokes agents** (if user approves) OR **generates manually**
11. **Artifacts ready** (`workflow/artifacts/vhdl/`, `workflow/artifacts/tests/`)
12. **User runs tests manually** (`uv run python cocotb_tests/run.py <component>`)

**Key:** More user control, manual testing, interactive requirements

---

## 🧪 Testing the Split

### Manual Testing (Local)

```bash
# From repo root
uv run python .claude/env_detect.py

# Expected output:
Runtime Environment: local
GHDL Installed: True/False
GHDL Version: <version string>
Recommended workflow: CLAUDE_LOCAL.md
```

---

### Manual Testing (Cloud Simulation)

```bash
# Set cloud environment variable
export CODESPACES=true

# Run detection
uv run python .claude/env_detect.py

# Expected output:
Runtime Environment: cloud
GHDL Installed: True/False
GHDL Version: <version string>
Recommended workflow: CLAUDE_CLOUD.md

# Unset when done
unset CODESPACES
```

---

### Automated Testing (Unit Tests)

**Future enhancement:** Add pytest tests for detection logic

```python
def test_cloud_detection_codespaces():
    os.environ["CODESPACES"] = "true"
    assert detect_runtime_environment() == "cloud"

def test_cloud_detection_gitpod():
    os.environ["GITPOD_WORKSPACE_ID"] = "test-workspace"
    assert detect_runtime_environment() == "cloud"

def test_local_detection_default():
    # Clear all cloud indicators
    assert detect_runtime_environment() == "local"
```

---

## 🔧 GHDL Installation Differences

### Cloud (Automatic via DevContainer)

**File:** `.devcontainer/devcontainer.json`

```json
{
  "image": "ghdl/ghdl:ubuntu22-llvm-5.0",
  "postCreateCommand": "bash .devcontainer/setup.sh"
}
```

**Setup script:** `.devcontainer/setup.sh`
- Installs LLVM 18 (GHDL dependency)
- Creates symlinks for libLLVM-18.so → libLLVM.so.1
- Installs Python dependencies (uv, cocotb)
- Runs validation: `uv run python scripts/cloud_setup_with_ghdl.py`

**Result:** GHDL 5.0 with LLVM backend, fully validated, ready to use

---

### Local (Manual Installation)

**macOS:**
```bash
brew install ghdl
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ghdl ghdl-llvm
```

**Verification:**
```bash
ghdl --version
```

**Result:** User-installed GHDL version (varies by OS/package manager)

---

## 📊 Decision Matrix

| Scenario | Environment | GHDL Status | Claude Action | User Action |
|----------|-------------|-------------|---------------|-------------|
| Codespaces first-time | Cloud | Pre-installed | Load `.claude/CLAUDE_CLOUD.md` | Try first component |
| Gitpod first-time | Cloud | Pre-installed | Load `.claude/CLAUDE_CLOUD.md` | Try first component |
| Docker container | Cloud | Pre-installed | Load `.claude/CLAUDE_CLOUD.md` | Try first component |
| Local CLI + GHDL | Local | Installed | Load `.claude/CLAUDE_LOCAL.md` + guide to `/config` | Verify output settings → try component |
| Local CLI no GHDL | Local | Not installed | Show install instructions | Install GHDL manually → restart session |
| Cloud without DevContainer | Cloud | Not installed | Offer auto-install script | Approve auto-install |

---

## 🐛 Common Issues

### Issue: Detection shows "local" in Codespaces

**Cause:** Cloud environment indicators not set (rare)

**Debug:**
```bash
echo $CODESPACES          # Should be "true"
echo $GITPOD_WORKSPACE_ID # Should be set (Gitpod only)
ls /.dockerenv            # Should exist in Docker
```

**Solution:** Check `.devcontainer/devcontainer.json` configuration

---

### Issue: Detection shows "cloud" on local machine

**Cause:** User has cloud environment variables set (rare)

**Debug:**
```bash
env | grep -E "(CODESPACES|GITPOD|REMOTE_CONTAINERS)"
ls /.dockerenv
```

**Solution:** Unset cloud variables or run outside Docker

---

### Issue: GHDL found in cloud but tests fail

**Cause:** LLVM library symlinks missing (GHDL-LLVM backend issue)

**Solution:**
```bash
uv run python scripts/cloud_setup_with_ghdl.py
```

This recreates symlinks: `/usr/lib/x86_64-linux-gnu/libLLVM-18.so.1 → libLLVM.so.1`

---

## 📝 Maintenance Notes

### When Adding New Cloud Platforms

**Example:** Adding Replit support

1. **Update detection logic** (`.claude/env_detect.py`):
   ```python
   os.environ.get("REPL_SLUG"),  # Replit indicator
   ```

2. **Update documentation** (this file, `README.md`, `CLAUDE.md`)

3. **Test detection** on new platform

4. **Update DevContainer config** (if needed for GHDL auto-install)

---

### When Changing GHDL Version

**Example:** Upgrading from GHDL 5.0 to GHDL 6.0

1. **Update DevContainer image** (`.devcontainer/devcontainer.json`):
   ```json
   "image": "ghdl/ghdl:ubuntu22-llvm-6.0"
   ```

2. **Update LLVM version** (`.devcontainer/setup.sh`):
   ```bash
   apt-get install llvm-19
   ln -s /usr/lib/x86_64-linux-gnu/libLLVM-19.so.1 /usr/lib/x86_64-linux-gnu/libLLVM.so.1
   ```

3. **Test GHDL validation** script

4. **Update documentation** (version numbers in all guides)

---

## 🎯 Best Practices

### For Template Users (Post-Fork)

1. **Always run detection first:** `uv run python .claude/env_detect.py`
2. **Read environment-specific guide** (don't skip this step)
3. **Local users:** Verify `/config` settings before testing
4. **Cloud users:** Trust DevContainer auto-setup (should just work)

---

### For Template Maintainers

1. **Keep detection logic simple** (fewer false positives)
2. **Default to "local"** (safer assumption for unknown environments)
3. **Test both paths** (local and cloud) before releasing
4. **Document cloud indicators** (for adding new platforms)
5. **Keep guides in sync** (LOCAL.md and CLOUD.md should cover same topics, different approaches)

---

## 📈 Future Enhancements

### Potential Improvements

1. **Automated tests for detection logic** (pytest suite)
2. **More granular cloud detection** (distinguish Codespaces vs Gitpod vs Docker)
3. **User preference override** (`.env` file to force local/cloud mode)
4. **Detection caching** (avoid re-running on every session)
5. **Visual detection dashboard** (web UI showing environment status)

---

**Last Updated:** 2025-11-09
**Version:** 3.2.0
**Maintainer:** Moku Instrument Forge Team

**Quick References:**
- Detection Script: `.claude/env_detect.py`
- Master Router: `CLAUDE.md`
- Local Guide: `.claude/CLAUDE_LOCAL.md`
- Cloud Guide: `.claude/CLAUDE_CLOUD.md`
- DevContainer Config: `.devcontainer/devcontainer.json`
