#!/usr/bin/env python3
"""
VHDL-FORGE Cloud Setup with GHDL
Version: 1.0
Purpose: Automated setup and validation for cloud environments with GHDL support
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, List


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header(msg: str) -> None:
    """Print section header"""
    print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}{msg}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}\n")


def print_success(msg: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")


def print_error(msg: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}❌ {msg}{Colors.NC}")


def print_warning(msg: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")


def print_info(msg: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")


def run_command(cmd: str, check: bool = True, capture: bool = True) -> Tuple[int, str, str]:
    """
    Run shell command and return (exit_code, stdout, stderr)

    Args:
        cmd: Command to run
        check: Raise exception on non-zero exit
        capture: Capture output (False = stream to terminal)
    """
    if capture:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    else:
        result = subprocess.run(cmd, shell=True, check=check)
        return result.returncode, "", ""


def check_ghdl() -> bool:
    """Check if GHDL is installed and get version"""
    print_header("Step 1/6: Checking GHDL Installation")

    try:
        exit_code, stdout, stderr = run_command("ghdl --version", check=False)
        if exit_code == 0:
            version = stdout.split('\n')[0]
            print_success(f"GHDL found: {version}")

            # Check version
            if "GHDL 4" in version or "GHDL 5" in version:
                print_success("GHDL version is sufficient (>= 4.0)")
                return True
            else:
                print_warning(f"GHDL version may be old: {version}")
                print_info("Recommended: GHDL 4.0+")
                return True
        else:
            print_error("GHDL not found")
            return False
    except Exception as e:
        print_error(f"Failed to check GHDL: {e}")
        return False


def install_ghdl() -> bool:
    """Attempt to install GHDL via apt-get (container environment)"""
    print_header("Installing GHDL")

    print_info("Attempting to install GHDL via apt-get...")
    print_info("This requires sudo/root access in container")
    print()

    try:
        # Update package lists
        print("Updating package lists...")
        run_command("apt-get update -qq", check=True, capture=False)
        print()

        # Install GHDL and LLVM 18 runtime
        print("Installing GHDL, LLVM 18, and dependencies...")
        run_command("apt-get install -y -qq ghdl ghdl-llvm llvm-18", check=True, capture=False)
        print()

        # Create LLVM library symlink (Ubuntu doesn't do this automatically)
        print("Creating LLVM library symlink for GHDL...")
        run_command(
            "ln -sf /usr/lib/llvm-18/lib/libLLVM.so.1 /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1",
            check=True,
            capture=False
        )
        print_success("LLVM library symlink created")
        print()

        # Verify installation
        exit_code, stdout, stderr = run_command("ghdl --version", check=False)
        if exit_code == 0:
            version = stdout.split('\n')[0]
            print_success(f"GHDL installed successfully: {version}")
            return True
        else:
            print_error("GHDL installation completed but verification failed")
            return False

    except subprocess.CalledProcessError as e:
        print_error(f"Installation failed: {e}")
        print_info("You may need to run this script with sudo/root privileges")
        print_info("Or use a container image with GHDL pre-installed (ghdl/ghdl:ubuntu22-llvm-5.0)")
        return False


def check_python() -> bool:
    """Check Python version"""
    print_header("Step 2/6: Checking Python")

    version = sys.version.split()[0]
    print_success(f"Python found: {version}")

    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 10:
        print_success(f"Python version is sufficient (>= 3.10)")
        return True
    else:
        print_warning(f"Python version may be too old: {version}")
        print_info("Recommended: Python 3.10+")
        return False


def check_uv() -> bool:
    """Check if uv is installed"""
    print_header("Step 3/6: Checking UV Package Manager")

    try:
        exit_code, stdout, stderr = run_command("uv --version", check=False)
        if exit_code == 0:
            print_success(f"UV found: {stdout.strip()}")
            return True
        else:
            print_error("UV not found")
            return False
    except Exception as e:
        print_error(f"Failed to check UV: {e}")
        return False


def install_uv() -> bool:
    """Install UV package manager"""
    print_info("Installing UV...")
    print()

    try:
        run_command(
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
            check=True,
            capture=False
        )
        print()

        # Verify installation
        exit_code, stdout, stderr = run_command("uv --version", check=False)
        if exit_code == 0:
            print_success(f"UV installed: {stdout.strip()}")
            return True
        else:
            print_error("UV installation failed")
            return False
    except Exception as e:
        print_error(f"UV installation failed: {e}")
        return False


def setup_packages() -> bool:
    """Run uv sync and install editable packages"""
    print_header("Step 4/6: Setting Up Python Packages")

    # Run uv sync
    print_info("Running: uv sync")
    try:
        run_command("uv sync", check=True, capture=False)
        print()
        print_success("Base dependencies installed")
    except subprocess.CalledProcessError:
        print_error("uv sync failed")
        return False

    print()

    # Install editable packages
    print_info("Installing workspace packages in editable mode...")
    try:
        run_command(
            "uv pip install -e python/forge_cocotb -e python/forge_platform -e python/forge_tools",
            check=True,
            capture=False
        )
        print()
        print_success("Workspace packages installed")
        return True
    except subprocess.CalledProcessError:
        print_error("Package installation failed")
        return False


def verify_imports() -> bool:
    """Verify all packages can be imported"""
    print_header("Step 5/6: Verifying Package Imports")

    packages = ["forge_cocotb", "forge_platform", "forge_tools"]
    all_ok = True

    for pkg in packages:
        try:
            exit_code, stdout, stderr = run_command(
                f"uv run python -c 'import {pkg}'",
                check=False
            )
            if exit_code == 0:
                print_success(f"{pkg} imports successfully")
            else:
                print_error(f"{pkg} import failed")
                if stderr:
                    print(f"   Error: {stderr.strip()}")
                all_ok = False
        except Exception as e:
            print_error(f"Failed to test {pkg}: {e}")
            all_ok = False

    return all_ok


def verify_tests() -> bool:
    """Verify test runner works"""
    print_header("Step 6/6: Verifying Test Infrastructure")

    print_info("Testing test discovery...")
    try:
        exit_code, stdout, stderr = run_command(
            "uv run python cocotb_tests/run.py --list",
            check=False
        )
        if exit_code == 0:
            print_success("Test runner working")
            print()

            # Count tests
            test_count = stdout.count("  -")
            print_info(f"Found {test_count} available tests")
            return True
        else:
            print_error("Test runner failed")
            if stderr:
                print(f"Error: {stderr}")
            return False
    except Exception as e:
        print_error(f"Test verification failed: {e}")
        return False


def run_sample_test() -> Tuple[bool, str]:
    """
    Run a sample test to verify GHDL integration
    Returns: (success, message)
    """
    print_header("Running Sample Test (GHDL Validation)")

    test_name = "forge_lut_pkg"
    print_info(f"Running test: {test_name}")
    print_info("This will verify GHDL can simulate VHDL code")
    print()

    try:
        exit_code, stdout, stderr = run_command(
            f"uv run python cocotb_tests/run.py {test_name}",
            check=False,
            capture=True
        )

        # Check for success indicators
        if "PASS" in stdout and exit_code == 0:
            return True, f"Test {test_name} PASSED"
        elif "ghdl" in stderr.lower() and "not found" in stderr.lower():
            return False, "GHDL not found - cannot run simulations"
        elif "Missing source files" in stdout or "Missing source files" in stderr:
            return False, "VHDL source files not found - check test_configs.py paths"
        else:
            # Show first 50 lines of output for debugging
            output = (stdout + stderr)[:2000]
            return False, f"Test failed:\n{output}"

    except Exception as e:
        return False, f"Test execution error: {e}"


def main() -> int:
    """Main setup workflow"""
    print()
    print_header("VHDL-FORGE Cloud Setup with GHDL")
    print()

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists() or not Path("python").exists():
        print_error("This script must be run from the VHDL-FORGE root directory")
        print_info(f"Current directory: {Path.cwd()}")
        return 1

    print_success("Running from VHDL-FORGE root directory")
    print()

    # Step 1: Check/Install GHDL
    ghdl_ok = check_ghdl()
    if not ghdl_ok:
        print()
        print_info("Attempting to install GHDL...")
        if not install_ghdl():
            print()
            print_error("GHDL installation failed - this is BLOCKING")
            print()
            print("Manual installation:")
            print("  Container: Use ghdl/ghdl:ubuntu22-llvm-5.0 image")
            print("  Ubuntu:    sudo apt-get install ghdl ghdl-llvm")
            print("  macOS:     brew install ghdl")
            return 1

    print()

    # Step 2: Check Python
    if not check_python():
        print_error("Python version too old")
        return 1

    print()

    # Step 3: Check/Install UV
    uv_ok = check_uv()
    if not uv_ok:
        print()
        if not install_uv():
            return 1

    print()

    # Step 4: Setup packages
    if not setup_packages():
        return 1

    print()

    # Step 5: Verify imports
    if not verify_imports():
        return 1

    print()

    # Step 6: Verify tests
    if not verify_tests():
        return 1

    print()

    # Run sample test
    test_ok, test_msg = run_sample_test()
    if test_ok:
        print_success(test_msg)
    else:
        print_warning(test_msg)
        print_info("Test framework is ready, but VHDL simulation may have issues")

    print()

    # Final summary
    print_header("Setup Complete!")
    print()
    print_success("VHDL-FORGE cloud environment is ready!")
    print()
    print("Next steps:")
    print()
    print("  1. Verify setup:")
    print("     ./scripts/validate_setup.sh")
    print()
    print("  2. List available tests:")
    print("     uv run python cocotb_tests/run.py --list")
    print()
    print("  3. Run a test:")
    print("     uv run python cocotb_tests/run.py forge_util_clk_divider")
    print()
    print("  4. Start development:")
    print("     Type: /gather-requirements (in Claude Code)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
