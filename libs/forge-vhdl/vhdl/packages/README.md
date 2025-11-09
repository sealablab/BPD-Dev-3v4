# FORGE VHDL Packages

Core packages for FORGE architecture and register communication.

## FORGE Control Scheme

**forge_common_pkg.vhd** ⭐
- CR0[31:29] bit position constants (`FORGE_READY_BIT`, `USER_ENABLE_BIT`, `CLK_ENABLE_BIT`)
- `combine_forge_ready()` function - Computes global_enable from 4 conditions
- BRAM loader protocol (future)

## Register Serialization (MCC Communication)

**forge_serialization_types_pkg.vhd**
- `std_logic_reg` type - Semantic correctness for register bits
- Boolean ↔ std_logic conversion (`bool_to_sl`, `sl_to_bool`)

**forge_serialization_voltage_pkg.vhd**
- Voltage ↔ register bit conversion
- Available ranges: ±0.5V, ±5V, ±20V, ±25V (16-bit/8-bit, signed/unsigned)
- Most common: `voltage_*_5v_bipolar_s16` (Moku DAC/ADC)

**forge_serialization_time_pkg.vhd**
- Time duration ↔ clock cycle conversion
- Clock-frequency aware: `ns_to_cycles()`, `us_to_cycles()`, `ms_to_cycles()`, `s_to_cycles()`

## Voltage Domain Utilities (Direct VHDL)

**forge_voltage_3v3_pkg.vhd**
- 0-3.3V unipolar domain
- Use for: TTL, GPIO, digital glitch, 3.3V probe interfaces

**forge_voltage_5v0_pkg.vhd**
- 0-5.0V unipolar domain
- Use for: Sensor supply, 0-5V DAC outputs

**forge_voltage_5v_bipolar_pkg.vhd**
- ±5.0V bipolar domain
- Use for: Moku DAC/ADC, AC signals, most analog work
- **Default choice** for analog applications

## Other Utilities

**forge_lut_pkg.vhd**
- Look-up table utilities
- Voltage/index conversion
- LUT constants

## Design Philosophy

**Explicit package selection enforces voltage domain boundaries.**

Function-based type safety (Verilog-compatible, no records/physical types).
