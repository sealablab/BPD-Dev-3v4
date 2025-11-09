# FORGE VHDL Components

Reusable VHDL components for custom instrument development.

## debugging/

**forge_hierarchical_encoder.vhd** ⭐
- Hierarchical Voltage Scheme (HVS) encoder
- Encodes 6-bit state + 8-bit status → single oscilloscope channel
- Pure arithmetic (zero LUTs)
- 200mV state steps + ±50mV status "noise"
- Fault detection via sign flip

**fsm_observer.vhd** (DEPRECATED)
- Legacy wrapper around hierarchical encoder
- Use `forge_hierarchical_encoder.vhd` directly for new designs

## utilities/

**forge_util_clk_divider.vhd**
- Programmable clock divider
- Configurable divisor width
- Use for: Clock generation, FSM timing

**forge_voltage_threshold_trigger_core.vhd**
- Voltage threshold trigger logic
- Configurable threshold and hysteresis

## loader/

**forge_bram_loader.vhd** (Future)
- BRAM initialization from external sources
- LUT loading, configuration data
- Integration with FORGE control scheme

## Usage

Components follow FORGE VHDL coding standards:
- Port order: clk, rst_n, clk_en, enable, data, status
- FSM states: std_logic_vector (not enums, Verilog compatible)
- Universal signal prefixes (ctrl_, cfg_, stat_, dbg_)

See individual component headers for detailed documentation and port descriptions.
