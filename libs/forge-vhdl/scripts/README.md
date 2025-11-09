# Scripts

Standalone scripts for FORGE development and debugging.

## ghdl_output_filter.py

Standalone GHDL output filter script (can be used outside CocoTB framework).

**Purpose:** Filter verbose GHDL simulation output for human readability.

**Filter levels:**
- `aggressive` - 90-98% reduction (default for P1 tests)
- `normal` - 80-90% reduction
- `minimal` - 50-70% reduction (duplicate warnings only)
- `none` - Pass-through (debugging filter itself)

**Usage:**
```bash
# Pipe GHDL output through filter
ghdl -r my_testbench | python scripts/ghdl_output_filter.py --level aggressive

# Or set environment variable
export GHDL_FILTER_LEVEL=aggressive
ghdl -r my_testbench | python scripts/ghdl_output_filter.py
```

**Filters:**
- Metavalue warnings (U, X, Z, W, -)
- Null range warnings
- Init warnings
- Internal GHDL messages
- Duplicate warnings

**Preserves:**
- Errors and failures
- Assertions
- Test results (PASS/FAIL)
- First occurrence of each warning type

See `GHDL_FILTER.md` for detailed implementation documentation.

## Future Scripts

- Bitstream packaging utilities
- Register value calculators
- MCC deployment helpers
