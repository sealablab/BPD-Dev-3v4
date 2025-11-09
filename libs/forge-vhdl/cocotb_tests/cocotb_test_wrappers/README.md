# CocoTB Test Wrappers

VHDL wrappers for testing packages and functions that cannot be tested directly by CocoTB.

## Why Wrappers?

CocoTB cannot directly test:
- VHDL packages (only entities can be top-level in simulation)
- Package functions/constants (not accessible as signals)
- Types like `real`, `boolean`, `time` (CocoTB type constraints)

## Wrapper Pattern

Test wrappers expose package functions as entity ports:

```vhdl
entity forge_lut_pkg_tb_wrapper is
    port (
        clk : in std_logic;
        -- Expose package constants as signals
        test_constant : out std_logic_vector(15 downto 0);

        -- Expose package functions via signals
        sel_test : in std_logic;
        input_value : in signed(15 downto 0);
        output_value : out signed(15 downto 0)
    );
end entity;

architecture tb of forge_lut_pkg_tb_wrapper is
begin
    test_constant <= PACKAGE_CONSTANT;

    process(clk)
    begin
        if rising_edge(clk) then
            if sel_test = '1' then
                output_value <= package_function(input_value);
            end if;
        end if;
    end process;
end architecture;
```

## Available Wrappers

- `forge_lut_pkg_tb_wrapper.vhd` - LUT package testing
- `forge_voltage_3v3_pkg_tb_wrapper.vhd` - 3.3V voltage package
- `forge_voltage_5v0_pkg_tb_wrapper.vhd` - 5.0V voltage package
- `forge_voltage_5v_bipolar_pkg_tb_wrapper.vhd` - ±5V voltage package

## Type Conversion

Wrappers handle type conversions between VHDL `real`/`boolean` and CocoTB-accessible types:
- `real` → `signed(15 downto 0)` (scaled digital values)
- `boolean` → `std_logic` (0/1)

See `docs/COCOTB_TROUBLESHOOTING.md` Section 0 for complete type constraint guide.
