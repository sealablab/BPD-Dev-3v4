#!/usr/bin/env python3
"""
Claude Startup Script for forge-vhdl
Version: 1.0
Purpose: Display environment-specific welcome message and guide users through initial setup

This script is called automatically when Claude starts in a new forge-vhdl session.
It detects the environment (local CLI vs cloud) and displays appropriate guidance.
"""

import sys
from pathlib import Path

# Add .claude directory to path so we can import env_detect
claude_dir = Path(__file__).parent
sys.path.insert(0, str(claude_dir))

try:
    from env_detect import (
        detect_runtime_environment,
        check_ghdl_installed,
        generate_startup_message,
        get_claude_md_variant
    )

    # Generate and display the startup message
    startup_msg = generate_startup_message()
    print(startup_msg)

    # Determine which CLAUDE.md variant to load
    variant = get_claude_md_variant()

    print(f"\n📖 Loading environment-specific guide: .claude/CLAUDE_{variant.upper()}.md")
    print(f"   (Full guide available at: CLAUDE.md)")

    # Return variant as exit code for programmatic use
    # 0 = local, 1 = cloud
    sys.exit(0 if variant == "local" else 1)

except ImportError as e:
    print(f"⚠️  Warning: Could not import env_detect module: {e}")
    print(f"Falling back to standard CLAUDE.md")
    sys.exit(2)
except Exception as e:
    print(f"⚠️  Warning: Startup script encountered an error: {e}")
    print(f"Continuing with standard CLAUDE.md")
    sys.exit(2)
