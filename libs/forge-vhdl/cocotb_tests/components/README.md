# Component Unit Tests

CocoTB tests for individual VHDL components in isolation.

## Structure

Each component has its own subdirectory:
```
<component_name>/
├── __init__.py
├── constants.py                    # Shared constants, test values, HDL config
├── P1_basic.py                     # Essential tests (3-5 tests, <20 lines)
├── P2_intermediate.py (optional)   # Edge cases (10-15 tests)
└── P3_comprehensive.py (optional)  # Full coverage (20-30 tests)
```

## Available Component Tests

**forge_util_clk_divider/**
- Clock divider functionality
- Divisor configuration
- Edge cases (divide-by-0, overflow)

**forge_hierarchical_encoder/**
- HVS encoding validation
- State progression, status offset, fault detection
- Arithmetic verification (pure arithmetic, zero LUTs)

**forge_lut_pkg/**
- Look-up table utilities
- Voltage/index conversion
- Package function testing (requires test wrapper)

## Running Component Tests

```bash
# Run P1 tests for a component
uv run python cocotb_tests/run.py forge_util_clk_divider

# Run P2 tests
TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py forge_util_clk_divider
```

## Adding New Component Tests

See `docs/COCOTB_GUIDE.md` for step-by-step instructions on adding tests for new components.
