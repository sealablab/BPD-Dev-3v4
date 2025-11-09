# Python Unit Tests (pytest)

Python unit tests for FORGE Python utilities and tools.

**NOT VHDL SIMULATION TESTS** - See `cocotb_tests/` for VHDL testing.

## Purpose

Test Python code using pytest:
- HVS decoder logic
- FORGE control helpers
- GHDL filter functionality
- Platform backend abstractions

## Test Files

**test_hierarchical_decoder.py**
- Tests HVS decoder arithmetic
- State extraction, status decoding, fault detection
- Edge cases (boundary voltages, negative values)

**test_mcc_utils.py**
- Tests FORGE control bit manipulation
- CR0[31:29] helpers
- Control Register value construction

**test_ghdl_filter.py**
- Tests GHDL output filtering logic
- Filter level behavior (aggressive/normal/minimal)
- Output reduction verification

**test_platform_backend.py**
- Tests platform abstraction interfaces
- Backend switching
- Mock testing without hardware

## Running Tests

```bash
# Run all Python unit tests
pytest python_tests/

# Run specific test file
pytest python_tests/test_hierarchical_decoder.py

# With coverage
pytest python_tests/ --cov=python/
```

## pytest Configuration

See `pyproject.toml` for pytest configuration:
```toml
[tool.pytest.ini_options]
testpaths = ["python_tests"]
```

## Separation of Concerns

- `python_tests/` - Python unit tests (pytest)
- `cocotb_tests/` - VHDL simulation tests (CocoTB)

Clear separation prevents confusion about test runners and test types.
