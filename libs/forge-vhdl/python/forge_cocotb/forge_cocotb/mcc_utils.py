"""
MCC (Moku Control Computer) Utilities

Utilities for preparing VHDL sources for MCC synthesis and deployment.
These are generically useful for any Moku custom instrument development.

Author: Moku Instrument Forge Team
Date: 2025-11-06
Version: 1.0.0
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def copy_sources_for_mcc(
    sources: List[Path],
    test_name: str,
    output_dir: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None
) -> Path:
    """
    Copy VHDL source files to a directory for MCC synthesis upload.

    Creates a timestamped directory with flat file structure (MCC requirement).
    Automatically excludes test-only files that would conflict with MCC infrastructure.

    Args:
        sources: List of VHDL source file paths
        test_name: Name of the test/module (used for subdirectory name)
        output_dir: Base output directory (defaults to current_dir/mcc/in/)
        exclude_patterns: Additional patterns to exclude (beyond defaults)

    Returns:
        Path to created directory with copied sources

    Example:
        from forge_cocotb.mcc_utils import copy_sources_for_mcc

        # In post-test hook:
        def after_test(config, test_name):
            mcc_dir = copy_sources_for_mcc(
                config.sources,
                test_name,
                output_dir=Path("mcc/in"),
                exclude_patterns=["my_testbench"]
            )
            print(f"✅ MCC sources ready: {mcc_dir}")
    """
    # Default exclude patterns (test-only files)
    default_excludes = [
        'test_stub',      # CustomWrapper test stub (MCC provides real one)
        'tb_wrapper',     # CocoTB test wrappers
        'testbench',      # Generic testbench files
        '_tb',            # Common testbench suffix
    ]

    exclude_patterns = exclude_patterns or []
    all_excludes = default_excludes + exclude_patterns

    # Determine output directory
    if output_dir is None:
        output_dir = Path.cwd() / "mcc" / "in"

    # Create timestamped subdirectory
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    mcc_dir = output_dir / f"{test_name}_{timestamp}"
    mcc_dir.mkdir(parents=True, exist_ok=True)

    # Copy source files (flat structure - MCC requirement)
    copied_files = []
    skipped_files = []

    for src_path in sources:
        if not src_path.exists():
            print(f"⚠️  Warning: Source file not found: {src_path}")
            continue

        # Check if file should be excluded
        if any(pattern in src_path.name.lower() for pattern in all_excludes):
            skipped_files.append(src_path.name)
            continue

        # Copy to flat directory structure
        dest_path = mcc_dir / src_path.name
        shutil.copy2(src_path, dest_path)
        copied_files.append(src_path.name)

    # Create manifest file
    manifest_path = mcc_dir / "manifest.txt"
    with open(manifest_path, 'w') as f:
        f.write(f"# MCC Synthesis Files for {test_name}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total files: {len(copied_files)}\n")
        if skipped_files:
            f.write(f"# Skipped (test-only): {len(skipped_files)}\n")
        f.write("\n")

        f.write("# VHDL Source Files (compilation order):\n")
        for filename in copied_files:
            f.write(f"{filename}\n")

        if skipped_files:
            f.write(f"\n# Test-only files (excluded from MCC):\n")
            for filename in sorted(skipped_files):
                f.write(f"# {filename}\n")

        f.write("\n# Instructions:\n")
        f.write("# 1. Upload all .vhd files to MCC CustomWrapper directory\n")
        f.write("# 2. Ensure files are compiled in order listed above\n")
        f.write("# 3. MCC will provide CustomWrapper entity - do not upload test stubs\n")

    # Print summary
    print(f"\n📁 MCC Sources:")
    print(f"   Directory: {mcc_dir.relative_to(Path.cwd())}")
    print(f"   Copied: {len(copied_files)} files")
    if skipped_files:
        print(f"   Skipped: {len(skipped_files)} test-only files")
    print(f"   Manifest: manifest.txt")

    return mcc_dir


def create_mcc_upload_script(
    mcc_dir: Path,
    platform: str = "Moku:Go",
    ip_address: str = "192.168.73.1"
) -> Path:
    """
    Create a shell script to upload sources to MCC via network.

    Args:
        mcc_dir: Directory containing MCC sources
        platform: Moku platform (e.g., "Moku:Go", "Moku:Lab")
        ip_address: Moku IP address

    Returns:
        Path to created upload script

    Note:
        This is a convenience function. Actual MCC upload protocol
        may vary by platform and firmware version.
    """
    script_path = mcc_dir / "upload_to_mcc.sh"

    with open(script_path, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(f"# MCC Upload Script - {platform}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Target: {ip_address}\n\n")

        f.write("# NOTE: This is a template script.\n")
        f.write("# Actual MCC upload protocol may differ by platform/firmware.\n")
        f.write("# Consult MCC documentation for your specific platform.\n\n")

        f.write("set -e  # Exit on error\n\n")

        f.write(f"MOKU_IP=\"{ip_address}\"\n")
        f.write(f"SOURCE_DIR=\"{mcc_dir}\"\n\n")

        f.write("echo \"🚀 Uploading VHDL sources to MCC...\"\n")
        f.write("echo \"Platform: {}\"\n".format(platform))
        f.write("echo \"IP: $MOKU_IP\"\n")
        f.write("echo \"Sources: $SOURCE_DIR\"\n\n")

        f.write("# TODO: Add actual MCC upload commands here\n")
        f.write("# Examples (adjust for your platform):\n")
        f.write("# scp *.vhd moku@$MOKU_IP:/path/to/custom_wrapper/\n")
        f.write("# curl -X POST http://$MOKU_IP/api/upload ...\n\n")

        f.write("echo \"✅ Upload complete!\"\n")

    # Make script executable
    script_path.chmod(0o755)

    print(f"   Upload script: {script_path.name} (template)")
    return script_path
