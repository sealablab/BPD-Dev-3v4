#!/usr/bin/env python3
"""
VHDL-FORGE Session Start Hook
Lightweight banner + /forge-start announcement for local CLI sessions

Output: Single-line banner with /forge-start suggestion
"""

import subprocess
import sys
import os

def check_ghdl():
    """Quick GHDL availability check"""
    try:
        result = subprocess.run(
            ["ghdl", "--version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            # Extract version (first line usually contains it)
            version = result.stdout.split('\n')[0].strip()
            return True, version
        return False, None
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False, None

def detect_environment():
    """Detect local vs cloud"""
    # Check for Codespaces environment variable
    if os.getenv('CODESPACES') == 'true':
        return 'cloud'

    # Check for common cloud indicators
    cloud_indicators = [
        'GITPOD_WORKSPACE_ID',
        'REPLIT_DEPLOYMENT',
        'GITHUB_CODESPACE_TOKEN'
    ]

    for indicator in cloud_indicators:
        if os.getenv(indicator):
            return 'cloud'

    # Default to local
    return 'local'

def main():
    """Output lightweight session start banner"""

    env = detect_environment()
    ghdl_ok, ghdl_version = check_ghdl()

    if env == 'local':
        # Local CLI environment - show banner
        if ghdl_ok:
            # Extract short version (e.g., "5.0.1" from full version string)
            short_ver = ghdl_version.split()[1] if len(ghdl_version.split()) > 1 else "installed"

            print(f"🔧 VHDL-FORGE Local | GHDL {short_ver} | Type /forge-start for interactive setup")
        else:
            print("⚠️  VHDL-FORGE Local | GHDL not found | Install: brew install ghdl")
    else:
        # Cloud environment - minimal message
        print("🌐 VHDL-FORGE Cloud | Auto-configured | Start building!")

    # Exit with success (don't block session)
    sys.exit(0)

if __name__ == "__main__":
    main()
