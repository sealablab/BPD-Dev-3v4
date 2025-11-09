#!/usr/bin/env python3
"""
CocoTB Test Runner for forge-vhdl

Uses shared forge_cocotb infrastructure (dogfooding!).

Usage:
    python run.py forge_util_clk_divider         # Run single test
    python run.py --all                          # Run all tests
    python run.py --category=utilities           # Run category
    python run.py --list                         # List available tests

Author: Moku Instrument Forge Team
Date: 2025-11-06
"""

import sys
from pathlib import Path

# Add forge_cocotb to path (we're testing our own infrastructure!)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import shared runner infrastructure
from forge_cocotb.runner import main as runner_main

# Import local test configs
sys.path.insert(0, str(Path(__file__).parent))
from test_configs import TESTS_CONFIG


if __name__ == "__main__":
    # No post-test hook needed for forge-vhdl (library, not deployed to MCC)
    sys.exit(runner_main(tests_config=TESTS_CONFIG))
