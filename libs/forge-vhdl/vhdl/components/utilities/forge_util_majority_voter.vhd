--------------------------------------------------------------------------------
-- Component: forge_util_majority_voter
-- Category: utilities
-- Purpose: 3-input majority logic voter for fault-tolerant digital systems
--
-- Description:
--   Implements 3-input majority voting logic where output is high when 2 or
--   more inputs are high. Supports both combinational and registered modes
--   for pipeline integration.
--
-- Truth Table:
--   A B C | Output
--   ------+-------
--   0 0 0 |   0
--   0 0 1 |   0
--   0 1 0 |   0
--   0 1 1 |   1
--   1 0 0 |   0
--   1 0 1 |   1
--   1 1 0 |   1
--   1 1 1 |   1
--
-- Architecture: Combinational SOP (sum-of-products) with optional output register
--   majority = (A AND B) OR (A AND C) OR (B AND C)
--
-- Use Cases:
--   - Triple modular redundancy (TMR) voting
--   - Fault-tolerant sensor inputs
--   - Glitch-resistant button debouncing
--   - Error correction in digital communication
--
-- Version: 1.0
-- Generated: 2025-11-09
--------------------------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;

entity forge_util_majority_voter is
    generic (
        REGISTERED : boolean := false  -- Register output for pipeline stages
    );
    port (
        -- Clock & Reset (only used if REGISTERED=true)
        clk         : in  std_logic;
        rst_n       : in  std_logic;

        -- Control (only used if REGISTERED=true)
        enable      : in  std_logic;

        -- Data inputs
        input_a     : in  std_logic;
        input_b     : in  std_logic;
        input_c     : in  std_logic;

        -- Output
        majority_out : out std_logic
    );
end entity forge_util_majority_voter;

architecture rtl of forge_util_majority_voter is

    -- Internal signals
    signal majority_logic : std_logic;

begin

    -------------------------------------------------------------------------------
    -- Combinational Majority Logic
    --
    -- Implements: (A AND B) OR (A AND C) OR (B AND C)
    --
    -- This is the minimal sum-of-products form for 3-input majority voting.
    -- Output is high when 2 or more inputs are high.
    -------------------------------------------------------------------------------
    majority_logic <= (input_a and input_b) or
                      (input_a and input_c) or
                      (input_b and input_c);

    -------------------------------------------------------------------------------
    -- Output Mode Selection
    --
    -- REGISTERED=false: Direct combinational path (zero latency)
    -- REGISTERED=true:  Registered output with enable control (1 cycle latency)
    -------------------------------------------------------------------------------

    -- Combinational mode: Direct output
    GEN_COMBINATIONAL: if not REGISTERED generate
        majority_out <= majority_logic;
    end generate GEN_COMBINATIONAL;

    -- Registered mode: Clocked output with enable
    GEN_REGISTERED: if REGISTERED generate
        process(clk, rst_n)
        begin
            if rst_n = '0' then
                majority_out <= '0';
            elsif rising_edge(clk) then
                if enable = '1' then
                    majority_out <= majority_logic;
                end if;
                -- If enable='0', output holds previous value
            end if;
        end process;
    end generate GEN_REGISTERED;

end architecture rtl;
