#!/usr/bin/env python3
"""
CocoTB Test Runner - Shared Infrastructure

Provides unified test running infrastructure for all CocoTB tests in the workspace.
Supports progressive testing (P1/P2/P3) with GHDL output filtering and extensible hooks.

Usage:
    # In project-specific run.py:
    from forge_cocotb.runner import main as runner_main
    from test_configs import TESTS_CONFIG

    if __name__ == "__main__":
        sys.exit(runner_main(tests_config=TESTS_CONFIG))

Author: Moku Instrument Forge Team
Date: 2025-11-06
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Callable, Dict
import os
import threading

# Import from forge_cocotb package
from .ghdl_filter import GHDLOutputFilter, FilterLevel

# CocoTB imports
try:
    from cocotb_tools.runner import get_runner
except ImportError:
    print("❌ CocotB tools not found! Install with: uv sync")
    sys.exit(1)


class FilteredOutput:
    """
    Context manager that captures and filters stdout/stderr at OS level.

    This is BULLETPROOF - it redirects file descriptors 1 and 2 (stdout/stderr)
    through pipes, so even C code (like GHDL) can't bypass it.
    """
    def __init__(self, filter_level: FilterLevel = FilterLevel.NORMAL):
        self.filter = GHDLOutputFilter(level=filter_level)
        self.original_stdout = None
        self.original_stderr = None
        self.pipe_read = None
        self.pipe_write = None
        self.reader_thread = None
        self.stop_reading = False

    def __enter__(self):
        """Start capturing and filtering output"""
        # Save original file descriptors
        self.original_stdout = os.dup(1)  # Save stdout
        self.original_stderr = os.dup(2)  # Save stderr

        # Create pipe for capturing output
        self.pipe_read, self.pipe_write = os.pipe()

        # Redirect stdout and stderr to pipe write end
        os.dup2(self.pipe_write, 1)  # Redirect stdout to pipe
        os.dup2(self.pipe_write, 2)  # Redirect stderr to pipe

        # Start reader thread to filter and display output
        self.stop_reading = False
        self.reader_thread = threading.Thread(target=self._read_and_filter)
        self.reader_thread.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original output and clean up"""
        try:
            # Flush before restoring
            sys.stdout.flush()
            sys.stderr.flush()

            # Restore original stdout/stderr
            os.dup2(self.original_stdout, 1)
            os.dup2(self.original_stderr, 2)

            # Close pipe write end (signals EOF to reader)
            os.close(self.pipe_write)

            # Wait for reader thread to finish
            if self.reader_thread and self.reader_thread.is_alive():
                self.reader_thread.join(timeout=2.0)

            # Close remaining file descriptors
            if self.original_stdout:
                os.close(self.original_stdout)
            if self.original_stderr:
                os.close(self.original_stderr)
            # Note: pipe_read is closed by fdopen in the thread
        except Exception as e:
            print(f"Warning: cleanup error: {e}", file=sys.stderr)

        return False  # Don't suppress exceptions

    def _read_and_filter(self):
        """Read from pipe and filter output in real-time"""
        pipe_file = None
        try:
            # Wrap pipe_read in a file object
            pipe_file = os.fdopen(self.pipe_read, 'r', buffering=1)
            for line in pipe_file:
                # Filter and print to original stdout
                if not self.filter.should_filter(line.rstrip('\n')):
                    os.write(self.original_stdout, line.encode())
                else:
                    self.filter.stats.filtered_lines += 1
                self.filter.stats.total_lines += 1
        except (OSError, ValueError):
            # Pipe closed or invalid - normal shutdown
            pass
        except Exception as e:
            # Log unexpected errors to original stdout
            try:
                os.write(self.original_stdout, f"\n[Filter error: {e}]\n".encode())
            except:
                pass
        finally:
            if pipe_file:
                try:
                    pipe_file.close()
                except:
                    pass


class TestRunner:
    """CocoTB test runner using Python API with extensible hooks"""

    def __init__(
        self,
        verbose: bool = False,
        filter_output: bool = True,
        post_test_hook: Optional[Callable] = None,
        tests_dir: Optional[Path] = None
    ):
        """
        Initialize test runner.

        Args:
            verbose: Enable verbose output (DEBUG log level)
            filter_output: Enable GHDL output filtering
            post_test_hook: Optional callback(config, test_name) called after test passes
            tests_dir: Test directory (defaults to current directory)
        """
        self.verbose = verbose
        self.filter_output = filter_output
        self.post_test_hook = post_test_hook
        self.tests_dir = tests_dir or Path.cwd()

    def run_test(self, test_name: str, tests_config: Dict) -> bool:
        """
        Run a single test.

        Args:
            test_name: Name of test to run
            tests_config: Dictionary of test configurations

        Returns:
            True if test passed, False otherwise.
        """
        if test_name not in tests_config:
            print(f"❌ Test '{test_name}' not found!")
            print(f"Available tests: {', '.join(tests_config.keys())}")
            return False

        config = tests_config[test_name]

        print("=" * 70)
        print(f"Running test: {test_name}")
        print(f"Category: {config.category}")
        print(f"Toplevel: {config.toplevel}")
        print(f"Test module: {config.test_module}")
        print("=" * 70)

        # Validate source files exist
        missing_sources = [str(src) for src in config.sources if not src.exists()]
        if missing_sources:
            print(f"❌ Missing source files:")
            for src in missing_sources:
                print(f"  - {src}")
            return False

        # Create GHDL runner
        runner = get_runner("ghdl")

        # Set working directory to tests/
        os.chdir(self.tests_dir)

        # Build configuration
        build_args = config.ghdl_args.copy()

        # Add simulation arguments (empty for now - keeping it simple!)
        # TODO: Add back GHDL optimization flags once basic testing works:
        #   --ieee-asserts=disable-at-0  (suppress initialization warnings)
        #   --assert-level=error         (only stop on errors)
        #   --stop-time=10ms             (timeout for runaway sims)
        sim_args = []

        # Set CocotB environment variables
        os.environ["COCOTB_REDUCED_LOG_FMT"] = "1"
        os.environ["COCOTB_LOG_LEVEL"] = "DEBUG" if self.verbose else "INFO"

        # Determine filter level
        filter_level_str = os.environ.get("GHDL_FILTER_LEVEL", "normal").lower()
        if filter_level_str == "aggressive":
            filter_level = FilterLevel.AGGRESSIVE
        elif filter_level_str == "normal":
            filter_level = FilterLevel.NORMAL
        elif filter_level_str == "minimal":
            filter_level = FilterLevel.MINIMAL
        elif filter_level_str == "none":
            filter_level = FilterLevel.NONE
        else:
            filter_level = FilterLevel.NORMAL

        try:
            # Build HDL (unfiltered - we want to see build errors)
            print("\n📦 Building HDL sources...")
            runner.build(
                sources=[str(src) for src in config.sources],
                hdl_toplevel=config.toplevel,
                always=True,
                build_args=build_args,
            )

            # Run tests with BULLETPROOF output filtering
            print("\n🧪 Running CocotB tests...")

            if self.filter_output and filter_level != FilterLevel.NONE:
                # BULLETPROOF: Capture at OS level - even GHDL can't bypass this!
                with FilteredOutput(filter_level=filter_level) as filtered:
                    runner.test(
                        hdl_toplevel=config.toplevel,
                        test_module=config.test_module,
                        test_args=sim_args,
                    )
                # Print filter summary
                if filtered.filter.stats.filtered_lines > 0:
                    print(f"\n[Filtered {filtered.filter.stats.filtered_lines} lines " +
                          f"({filtered.filter.stats.filtered_lines}/{filtered.filter.stats.total_lines} = " +
                          f"{100*filtered.filter.stats.filtered_lines/filtered.filter.stats.total_lines:.1f}% reduction)]")
            else:
                # No filtering - direct output
                runner.test(
                    hdl_toplevel=config.toplevel,
                    test_module=config.test_module,
                    test_args=sim_args,
                )

            # Call post-test hook if provided
            if self.post_test_hook:
                self.post_test_hook(config, test_name)

            print("\n" + "=" * 70)
            print(f"✅ Test '{test_name}' PASSED")
            print("=" * 70)
            return True

        except Exception as e:
            print("\n" + "=" * 70)
            print(f"❌ Test '{test_name}' FAILED")
            print(f"Error: {e}")
            print("=" * 70)
            return False

    def run_all_tests(self, tests_config: Dict) -> Dict[str, bool]:
        """
        Run all configured tests.

        Args:
            tests_config: Dictionary of test configurations

        Returns:
            Dict of {test_name: passed}
        """
        results = {}
        test_names = list(tests_config.keys())

        print(f"\n🚀 Running {len(test_names)} tests...\n")

        for i, test_name in enumerate(test_names, 1):
            print(f"\n[{i}/{len(test_names)}] {test_name}")
            results[test_name] = self.run_test(test_name, tests_config)

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for v in results.values() if v)
        failed = len(results) - passed

        for test_name, passed_flag in results.items():
            status = "✅ PASS" if passed_flag else "❌ FAIL"
            print(f"{status}: {test_name}")

        print("=" * 70)
        print(f"Results: {passed} passed, {failed} failed, {len(results)} total")
        print("=" * 70)

        return results

    def run_category(self, category: str, tests_config: Dict) -> Dict[str, bool]:
        """
        Run all tests in a category.

        Args:
            category: Category name
            tests_config: Dictionary of test configurations

        Returns:
            Dict of {test_name: passed}
        """
        # Filter tests by category
        tests = {name: cfg for name, cfg in tests_config.items() if cfg.category == category}

        if not tests:
            available = set(cfg.category for cfg in tests_config.values())
            print(f"❌ Category '{category}' not found!")
            print(f"Available categories: {', '.join(sorted(available))}")
            return {}

        print(f"\n🚀 Running {len(tests)} tests in category '{category}'...\n")

        results = {}
        for i, test_name in enumerate(sorted(tests.keys()), 1):
            print(f"\n[{i}/{len(tests)}] {test_name}")
            results[test_name] = self.run_test(test_name, tests_config)

        # Summary
        passed = sum(1 for v in results.values() if v)
        failed = len(results) - passed

        print("\n" + "=" * 70)
        print(f"Category '{category}': {passed} passed, {failed} failed")
        print("=" * 70)

        return results

    def list_tests(self, tests_config: Dict):
        """List all available tests"""
        print("Available CocoTB Tests")
        print("=" * 70)

        # Group by category
        by_category = {}
        for name, config in tests_config.items():
            category = config.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((name, config))

        for category in sorted(by_category.keys()):
            tests = by_category[category]
            print(f"\n{category.upper()} ({len(tests)} tests):")
            for test_name, config in sorted(tests):
                print(f"  - {test_name:30s} ({config.test_module})")

        print("\n" + "=" * 70)
        print(f"Total: {len(tests_config)} tests")
        print("=" * 70)


def main(
    tests_config: Dict,
    post_test_hook: Optional[Callable] = None,
    tests_dir: Optional[Path] = None
) -> int:
    """
    Main entry point for test runner.

    Args:
        tests_config: Dictionary of test configurations (from test_configs.py)
        post_test_hook: Optional callback(config, test_name) called after test passes
        tests_dir: Test directory (defaults to caller's directory)

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    parser = argparse.ArgumentParser(
        description="CocoTB Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py <test_name>                 # Run single test
  python run.py --all                       # Run all tests
  python run.py --category=<category>       # Run category
  python run.py --list                      # List tests
  python run.py <test_name> --verbose       # Verbose output
        """,
    )

    parser.add_argument(
        "test_name",
        nargs="?",
        help="Name of test to run",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Run all tests in category",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available tests",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (DEBUG log level)",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Disable GHDL output filtering (show all warnings)",
    )
    parser.add_argument(
        "--filter-level",
        type=str,
        choices=["aggressive", "normal", "minimal", "none"],
        default=None,
        help="Set GHDL output filter level (default: normal)",
    )

    args = parser.parse_args()

    # Set filter level if specified
    if args.filter_level:
        os.environ["GHDL_FILTER_LEVEL"] = args.filter_level
    elif args.no_filter:
        os.environ["GHDL_FILTER_LEVEL"] = "none"

    # Determine tests directory (caller's directory if not specified)
    if tests_dir is None:
        # Get caller's directory (the script that imported us)
        frame = sys._getframe(1)
        caller_file = frame.f_code.co_filename
        tests_dir = Path(caller_file).parent

    # Create runner
    runner = TestRunner(
        verbose=args.verbose,
        filter_output=not args.no_filter,
        post_test_hook=post_test_hook,
        tests_dir=tests_dir
    )

    # Handle commands
    if args.list:
        runner.list_tests(tests_config)
        return 0

    elif args.all:
        results = runner.run_all_tests(tests_config)
        # Exit with non-zero if any tests failed
        return 0 if all(results.values()) else 1

    elif args.category:
        results = runner.run_category(args.category, tests_config)
        return 0 if all(results.values()) else 1

    elif args.test_name:
        success = runner.run_test(args.test_name, tests_config)
        return 0 if success else 1

    else:
        parser.print_help()
        return 1
