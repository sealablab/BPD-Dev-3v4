# Digital Scaling Philosophy for FORGE Components

**Core Principle:** Strict separation between digital encoding (FPGA) and analog scaling (platform)

---

## Executive Summary

All FORGE components operate in the **digital domain**, outputting platform-agnostic digital codes (signed 16-bit). The platform hardware (DAC/ADC) handles the analog domain conversion based on configuration.

**Key Insight:** Components output digital units, NOT voltages. Platform determines voltage mapping.

---

## The Separation Principle

### What FORGE Components Do (Digital Domain)

- Output: `signed(15 downto 0)` digital codes
- Range: -32768 to +32767 (two's complement)
- Units: Digital units (platform-agnostic)
- Example: 200 digital units per state

### What Platform Does (Analog Domain)

- Maps digital codes to physical voltages
- Configures DAC/ADC ranges (±5V, ±10V, etc.)
- Handles calibration and scaling
- Example: ±32768 digital → ±5V analog (platform-specific)

---

## Implementation Examples

### 1. Hierarchical Encoder (forge_hierarchical_encoder)

**Location:** `vhdl/components/debugging/forge_hierarchical_encoder.vhd`

**Digital Output Formula:**
```
Base = state × 200 (digital units)
Offset = status[6:0] × 0.78125 (digital units)
Sign = status[7] ? -1 : +1
Output = (Base + Offset) × Sign
```

**Platform Interpretation (NOT in VHDL):**
- Moku Go (±5V): 200 digital units ≈ 30.5 mV
- Hypothetical ±10V platform: 200 digital units ≈ 61 mV
- Same VHDL, different voltages!

### 2. Voltage Packages (Conversion Utilities)

**Location:** `vhdl/packages/forge_voltage_*_pkg.vhd`

**Purpose:** Provide conversion utilities between digital codes and voltage representations for:
- Testing and simulation
- Documentation and debugging
- Platform-specific interpretation

**NOT:** Hardcoded voltage definitions in components!

**Available Packages:**
- `forge_voltage_3v3_pkg` - 0-3.3V domain conversions
- `forge_voltage_5v0_pkg` - 0-5.0V domain conversions
- `forge_voltage_5v_bipolar_pkg` - ±5.0V domain conversions (most common)

**Key Functions:**
```vhdl
-- Convert voltage to digital (for testing)
function to_digital(voltage : real) return signed;

-- Convert digital to voltage (for interpretation)
function from_digital(digital : signed(15 downto 0)) return real;
```

---

## Design Benefits

### 1. Platform Agnosticism
- Same VHDL works on Go/Lab/Pro/Delta
- No recompilation for different DAC ranges
- Future platforms supported automatically

### 2. Clean Architecture
- Digital domain (FPGA) isolated from analog domain (platform)
- No voltage constants in component logic
- Platform configuration external to VHDL

### 3. Testability
- Components tested with digital values
- Platform-independent test cases
- Voltage interpretation in test harness only

---

## Common Misconceptions

### ❌ "Components output voltages"
**Reality:** Components output digital codes. Platform converts to voltage.

### ❌ "Need different VHDL for different platforms"
**Reality:** Same VHDL everywhere. Platform configures DAC range.

### ❌ "Voltage packages define component behavior"
**Reality:** Voltage packages are utilities for conversion/testing, not component logic.

---

## Best Practices

### DO ✅
- Output `signed(15 downto 0)` digital codes
- Document digital scaling factors (e.g., "200 units per state")
- Use voltage packages for testing/simulation only
- Let platform handle analog configuration

### DON'T ❌
- Hardcode voltage constants in components
- Assume specific DAC/ADC ranges
- Mix digital and analog concepts in logic
- Tie components to specific platforms

---

## References

### Design Documentation
- Detailed rationale: `Obsidian/Project/Review/HIERARCHICAL_ENCODER_DIGITAL_SCALING.md`
- Hierarchical encoder: `vhdl/components/debugging/forge_hierarchical_encoder.vhd`

### Voltage Utilities
- Conversion packages: `vhdl/packages/forge_voltage_*_pkg.vhd`
- Not for component logic, only for testing/interpretation

### Platform Specifications
- See monorepo: `libs/moku-models/` for platform DAC/ADC specifications
- Platform determines digital → voltage mapping

---

**Philosophy:** Write once in digital domain, deploy anywhere with platform-specific analog configuration.