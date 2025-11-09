-- ============================================================================
-- FORGE Counter Test DUT
-- ============================================================================
-- Purpose: Simple FORGE-compliant counter for platform testing validation
--
-- Architecture: FORGE 3-layer pattern (simplified for test DUT)
--   Layer 2: FORGE shim (extracts CR0[31:29], unpacks control registers)
--   Layer 3: Counter main logic
--
-- Control Registers:
--   CR0[31]   - forge_ready (set by loader/test)
--   CR0[30]   - user_enable (user control)
--   CR0[29]   - clk_enable (clock gating)
--   CR0[15:0] - counter_max (configurable count limit)
--
-- Status Registers:
--   SR0[31:0] - counter_value (current count)
--   SR1[0]    - counter_overflow (flag when count wraps)
--
-- FORGE Control Scheme:
--   global_enable = forge_ready AND user_enable AND clk_enable AND loader_done
--   (loader_done = '1' for this test DUT - no BRAM loading)
--
-- ============================================================================

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library WORK;
use WORK.forge_common_pkg.ALL;

-- ============================================================================
-- Layer 3: Counter Main Logic (MCC-agnostic)
-- ============================================================================

entity forge_counter_main is
    port (
        -- Clock & Reset
        Clk   : in std_logic;
        Reset : in std_logic;  -- Active-high

        -- FORGE Control
        global_enable     : in std_logic;
        ready_for_updates : out std_logic;

        -- Application Registers (unpacked from CR0)
        app_reg_counter_max : in unsigned(15 downto 0);

        -- Status Outputs (packed to SR0, SR1)
        app_status_counter_value : out unsigned(31 downto 0);
        app_status_overflow      : out std_logic
    );
end entity forge_counter_main;

architecture rtl of forge_counter_main is
    -- FSM states (std_logic_vector for Verilog compatibility)
    constant STATE_IDLE    : std_logic_vector(1 downto 0) := "00";
    constant STATE_RUNNING : std_logic_vector(1 downto 0) := "01";

    signal state   : std_logic_vector(1 downto 0);
    signal counter : unsigned(31 downto 0);
    signal overflow_flag : std_logic;

begin
    -- Main FSM process
    process(Clk, Reset)
    begin
        if Reset = '1' then
            -- Reset state
            counter       <= (others => '0');
            state         <= STATE_IDLE;
            overflow_flag <= '0';
            ready_for_updates <= '0';

        elsif rising_edge(Clk) then
            -- Default: clear overflow flag (pulse)
            overflow_flag <= '0';

            case state is
                when STATE_IDLE =>
                    -- Safe to update configuration
                    ready_for_updates <= '1';
                    counter           <= (others => '0');

                    if global_enable = '1' then
                        -- Lock configuration, start counting
                        ready_for_updates <= '0';
                        state             <= STATE_RUNNING;
                    end if;

                when STATE_RUNNING =>
                    -- Configuration locked during operation
                    ready_for_updates <= '0';

                    if global_enable = '0' then
                        -- Disabled, return to IDLE
                        state   <= STATE_IDLE;
                        counter <= (others => '0');
                    else
                        -- Increment counter
                        if counter >= app_reg_counter_max then
                            -- Overflow: wrap to 0
                            counter       <= (others => '0');
                            overflow_flag <= '1';
                        else
                            counter <= counter + 1;
                        end if;
                    end if;

                when others =>
                    -- Safety fallback
                    state <= STATE_IDLE;
            end case;
        end if;
    end process;

    -- Status outputs
    app_status_counter_value <= counter;
    app_status_overflow      <= overflow_flag;

end architecture rtl;

-- ============================================================================
-- Layer 2: FORGE Shim (Extracts CR0[31:29], unpacks Control Registers)
-- ============================================================================

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library WORK;
use WORK.forge_common_pkg.ALL;

entity forge_counter_shim is
    port (
        -- Clock & Reset
        clk   : in std_logic;
        rst_n : in std_logic;  -- Active-low

        -- Control Registers (from MCC interface)
        Control0 : in std_logic_vector(31 downto 0);

        -- Status Registers (to MCC interface)
        Status0 : out std_logic_vector(31 downto 0);
        Status1 : out std_logic_vector(31 downto 0)
    );
end entity forge_counter_shim;

architecture rtl of forge_counter_shim is
    -- FORGE control scheme signals
    signal forge_ready  : std_logic;
    signal user_enable  : std_logic;
    signal clk_enable   : std_logic;
    signal loader_done  : std_logic;
    signal global_enable : std_logic;

    -- Application register signals
    signal app_reg_counter_max : unsigned(15 downto 0);

    -- Status signals from main
    signal app_status_counter_value : unsigned(31 downto 0);
    signal app_status_overflow      : std_logic;

    -- Handshaking
    signal ready_for_updates : std_logic;

    -- Active-high reset (main logic uses active-high)
    signal reset : std_logic;

begin
    -- Convert reset polarity
    reset <= not rst_n;

    -- Extract FORGE control scheme from CR0[31:29]
    forge_ready <= Control0(FORGE_READY_BIT);    -- CR0[31]
    user_enable <= Control0(USER_ENABLE_BIT);    -- CR0[30]
    clk_enable  <= Control0(CLK_ENABLE_BIT);     -- CR0[29]

    -- Hardcode loader_done = '1' (no BRAM loading in this test DUT)
    loader_done <= '1';

    -- Compute global_enable using forge_common_pkg function
    global_enable <= combine_forge_ready(
        forge_ready => forge_ready,
        user_enable => user_enable,
        clk_enable  => clk_enable,
        loader_done => loader_done
    );

    -- Unpack Control Registers → app_reg_* signals
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            app_reg_counter_max <= (others => '0');
        elsif rising_edge(clk) then
            if ready_for_updates = '1' then
                -- Main logic says it's safe to update registers
                app_reg_counter_max <= unsigned(Control0(15 downto 0));
            end if;
            -- else: Hold current values (main logic busy)
        end if;
    end process;

    -- Pack app_status_* signals → Status Registers
    Status0 <= std_logic_vector(app_status_counter_value);  -- SR0[31:0]
    Status1 <= (0 => app_status_overflow, others => '0');   -- SR1[0]

    -- Instantiate Layer 3: Counter Main Logic
    U_MAIN: entity work.forge_counter_main
        port map (
            Clk   => clk,
            Reset => reset,

            global_enable     => global_enable,
            ready_for_updates => ready_for_updates,

            app_reg_counter_max      => app_reg_counter_max,

            app_status_counter_value => app_status_counter_value,
            app_status_overflow      => app_status_overflow
        );

end architecture rtl;

-- ============================================================================
-- Top-Level Wrapper (for CocoTB testing)
-- ============================================================================
-- This wrapper provides a convenient interface for CocoTB tests.
-- In production, this would be replaced by CustomWrapper (MCC interface).
-- ============================================================================

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity forge_counter is
    port (
        -- Clock & Reset
        clk   : in std_logic;
        rst_n : in std_logic;

        -- Control Registers
        Control0 : in std_logic_vector(31 downto 0);

        -- Status Registers
        Status0 : out std_logic_vector(31 downto 0);
        Status1 : out std_logic_vector(31 downto 0)
    );
end entity forge_counter;

architecture rtl of forge_counter is
begin
    -- Instantiate FORGE shim (Layer 2)
    U_SHIM: entity work.forge_counter_shim
        port map (
            clk      => clk,
            rst_n    => rst_n,
            Control0 => Control0,
            Status0  => Status0,
            Status1  => Status1
        );

end architecture rtl;
