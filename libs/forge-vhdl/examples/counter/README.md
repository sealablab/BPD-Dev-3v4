# FORGE Counter Example - Your First FORGE Instrument

**Status:** Placeholder - Full tutorial to be written

This example demonstrates the complete FORGE 3-layer architecture using a simple counter that doubles as an FSM state machine.

## What This Example Teaches

### FORGE Control Scheme (CR0[31:29])
The 4-condition enable pattern:
```
global_enable = forge_ready AND user_enable AND clk_enable AND loader_done
```

### HVS Encoding (Batteries Included)
Every FORGE instrument exports:
- `app_state_vector[5:0]` - FSM state (0-31)
- `app_status_vector[7:0]` - Application status (bit 7 = fault)

The SHIM layer automatically encodes these to OutputD for oscilloscope debugging.

### 3-Layer Architecture
- **Layer 3 (Main):** Counter FSM logic (MCC-agnostic)
- **Layer 2 (Shim):** Register mapping + FORGE control + HVS encoder
- **Layer 1 (Wrapper):** MCC CustomInstrument interface

## Files

**vhdl/forge_counter_with_encoder.vhd**
- Complete 3-layer implementation
- Counter state doubles as FSM state (clever resource reuse)
- Includes hierarchical encoder for OutputD

**cocotb_tests/**
- P1 tests: FORGE control sequence, basic operation, overflow
- Validates complete control flow

## Adapting to Your Application

1. Replace Layer 3 (forge_counter_main) with your FSM logic
2. Export your `app_state_vector[5:0]` and `app_status_vector[7:0]`
3. Keep Layer 2 (shim) pattern - it handles FORGE control + HVS encoding
4. Define your control registers in CR0-CR15

You get oscilloscope debugging for free through HVS encoding!

## Next Steps

See `docs/GETTING_STARTED.md` for detailed tutorial.
