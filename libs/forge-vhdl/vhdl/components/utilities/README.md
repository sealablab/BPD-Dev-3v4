# Utility Components

General-purpose VHDL utilities for custom instrument development.

## forge_util_clk_divider.vhd

Programmable clock divider with enable control.

**Generics:**
- `MAX_DIV` - Maximum divisor bit width

**Ports:**
- `divisor` - Division ratio (0 = clock pass-through, N = divide by N+1)
- `clk_out` - Divided clock output

**Use cases:**
- Clock generation for slower logic
- FSM timing control
- Pulse width generation

## forge_voltage_threshold_trigger_core.vhd

Voltage threshold trigger with configurable hysteresis.

**Use cases:**
- Voltage monitoring
- Threshold detection
- Analog signal conditioning

See individual component headers for detailed port descriptions and usage examples.
