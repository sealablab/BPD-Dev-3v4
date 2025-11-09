-- Dummy VHDL entity for platform infrastructure tests
--
-- Used when testing Python infrastructure (MokuConfig, YAML parsing, etc.)
-- where no actual VHDL logic is needed.
--
-- This entity does nothing - it exists only to satisfy CocoTB's requirement
-- for a toplevel entity.

library IEEE;
use IEEE.std_logic_1164.all;

entity platform_test_dummy is
    port (
        dummy : in std_logic
    );
end entity;

architecture minimal of platform_test_dummy is
begin
    -- Intentionally empty
end architecture;
