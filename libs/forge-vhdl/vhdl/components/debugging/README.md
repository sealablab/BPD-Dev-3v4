# Debugging Components

VHDL components for FPGA debugging and observability.

## forge_hierarchical_encoder.vhd ⭐

**Hierarchical Voltage Scheme (HVS) encoder** - Encodes FSM state + status onto oscilloscope channel.

**Inputs:**
- `app_state_vector[5:0]` - FSM state (0-31)
- `app_status_vector[7:0]` - Application status (bit 7 = fault indicator)

**Output:**
- `debug_voltage` (signed 16-bit) - Encoded voltage for DAC output

**Encoding:**
- State: 200mV steps (human-readable on oscilloscope)
- Status[6:0]: ±50mV "noise" around base voltage (machine-decodable)
- Status[7]: Fault → voltage sign flip (unmistakable error indication)

**Architecture:** Pure arithmetic, zero LUTs.

**Use case:** Every FORGE instrument should include HVS encoding on OutputD for oscilloscope debugging.

See `docs/HVS_ENCODING.md` for complete specification.

## fsm_observer.vhd (DEPRECATED)

Legacy compatibility wrapper around `forge_hierarchical_encoder.vhd`.

**Migration:** Use `forge_hierarchical_encoder.vhd` directly for new designs.
