#!/usr/bin/env python3
"""
Environment Detection for forge-vhdl
Version: 1.0
Purpose: Detect runtime environment (local CLI vs cloud) and GHDL availability

This script is called by Claude at startup to determine:
1. Is this running locally (Claude CLI) or in cloud (Claude Web/Codespaces)?
2. Is GHDL installed?
3. What workflow should we guide the user through?
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Dict


def detect_runtime_environment() -> str:
    """
    Detect if we're running in Claude CLI (local) or Claude Web (cloud)

    Returns:
        "local" - Running in Claude Code CLI on user's machine
        "cloud" - Running in Claude Web, Codespaces, or containerized environment
    """
    # Check for cloud environment indicators
    cloud_indicators = [
        os.environ.get("CODESPACES"),  # GitHub Codespaces
        os.environ.get("GITPOD_WORKSPACE_ID"),  # Gitpod
        os.environ.get("REMOTE_CONTAINERS"),  # VS Code Remote Containers
        Path("/.dockerenv").exists(),  # Docker container
        Path("/workspace").exists() and os.environ.get("HOME") == "/root",  # Codespaces pattern
    ]

    if any(cloud_indicators):
        return "cloud"

    # Default to local (safest assumption for new template repos)
    return "local"


def check_ghdl_installed() -> Tuple[bool, str]:
    """
    Check if GHDL is available in PATH

    Returns:
        (is_installed, version_string)
    """
    try:
        result = subprocess.run(
            ["ghdl", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            return True, version
        else:
            return False, ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, ""


def check_claude_cli_config() -> Dict[str, bool]:
    """
    Check Claude Code CLI configuration for recommended settings

    Returns:
        Dictionary with config checks (for local environments only)
    """
    # These are recommendations for the user to manually verify
    # We can't programmatically read Claude CLI config (it's internal)
    return {
        "verbose_output": None,  # User should check: false (recommended)
        "output_style": None,  # User should check: default (recommended)
        "auto_compact": None,  # User should check: false (better for logs)
    }


def generate_startup_message() -> str:
    """
    Generate environment-specific startup message for Claude to display

    Returns:
        Formatted message string
    """
    runtime = detect_runtime_environment()
    ghdl_installed, ghdl_version = check_ghdl_installed()

    if runtime == "cloud":
        if ghdl_installed:
            return f"""
╔════════════════════════════════════════════════════════════════════╗
║  🌐 CLOUD ENVIRONMENT DETECTED                                     ║
║  ✅ GHDL Found: {ghdl_version:<50} ║
║                                                                    ║
║  Ready for VHDL development! Using cloud workflow.                 ║
╚════════════════════════════════════════════════════════════════════╝

Loading cloud-optimized CLAUDE.md instructions...
"""
        else:
            return f"""
╔════════════════════════════════════════════════════════════════════╗
║  🌐 CLOUD ENVIRONMENT DETECTED                                     ║
║  ⚠️  GHDL NOT FOUND                                                ║
║                                                                    ║
║  I can auto-install GHDL for you. This will take ~2-3 minutes.    ║
║  Command: uv run python scripts/cloud_setup_with_ghdl.py          ║
║                                                                    ║
║  Would you like me to install GHDL now?                           ║
╚════════════════════════════════════════════════════════════════════╝
"""

    else:  # local
        if ghdl_installed:
            return f"""
╔════════════════════════════════════════════════════════════════════╗
║  💻 LOCAL ENVIRONMENT DETECTED (Claude Code CLI)                   ║
║  ✅ GHDL Found: {ghdl_version:<50} ║
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
"""
        else:
            return f"""
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
"""


def get_claude_md_variant() -> str:
    """
    Determine which CLAUDE.md variant to load

    Returns:
        "cloud" or "local" - which workflow to activate
    """
    runtime = detect_runtime_environment()
    return runtime


if __name__ == "__main__":
    # When run directly, print environment info for debugging
    runtime = detect_runtime_environment()
    ghdl_installed, ghdl_version = check_ghdl_installed()

    print(f"Runtime Environment: {runtime}")
    print(f"GHDL Installed: {ghdl_installed}")
    if ghdl_installed:
        print(f"GHDL Version: {ghdl_version}")
    print(f"\nRecommended workflow: CLAUDE_{runtime.upper()}.md")
    print(f"\n{generate_startup_message()}")
