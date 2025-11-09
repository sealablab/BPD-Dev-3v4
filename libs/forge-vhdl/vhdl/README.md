# FORGE VHDL Components

Reusable VHDL packages and components for FORGE-based custom instruments.

## packages/

Core VHDL packages for FORGE development.

**forge_common_pkg.vhd** ⭐
- FORGE control scheme (CR0[31:29] bit positions)
- `combine_forge_ready()` function
- BRAM loader protocol constants (future)

**Serialization Packages** (MCC Control Register communication)
- `forge_serialization_types_pkg.vhd` - Boolean, std_logic_reg types
- `forge_serialization_voltage_pkg.vhd` - Voltage ↔ register conversion
- `forge_serialization_time_pkg.vhd` - Time ↔ clock cycle conversion

**Voltage Domain Packages** (Direct VHDL voltage utilities)
- `forge_voltage_3v3_pkg.vhd` - 0-3.3V unipolar (TTL, GPIO)
- `forge_voltage_5v0_pkg.vhd` - 0-5.0V unipolar (sensors)
- `forge_voltage_5v_bipolar_pkg.vhd` - ±5.0V bipolar (Moku DAC/ADC)

**forge_lut_pkg.vhd**
- Look-up table utilities
- Voltage/index conversion functions

## components/

Reusable VHDL components organized by category.

### debugging/
- `forge_hierarchical_encoder.vhd` ⭐ - HVS encoder for oscilloscope debugging
- `fsm_observer.vhd` - (deprecated wrapper)

### utilities/
- `forge_util_clk_divider.vhd` - Programmable clock divider
- `forge_voltage_threshold_trigger_core.vhd` - Voltage threshold trigger

### loader/
- `forge_bram_loader.vhd` - BRAM initialization (future)

## Usage

Import packages based on your needs:
```vhdl
library WORK;
use WORK.forge_common_pkg.ALL;                   -- FORGE control scheme
use WORK.forge_serialization_types_pkg.ALL;      -- Core types
use WORK.forge_serialization_voltage_pkg.ALL;    -- Voltage serialization
use WORK.forge_voltage_5v_bipolar_pkg.ALL;       -- ±5V utilities
```

See individual component headers for detailed documentation.
