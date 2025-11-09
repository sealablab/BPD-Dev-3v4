-- ============================================================================
-- FORGE Counter Test DUT with Hierarchical Encoder
-- ============================================================================
-- Purpose: Full FORGE 3-layer architecture validation with hierarchical
--          voltage encoding on OutputD (Phase 2 platform testing)
--
-- Design Innovation: FSM state IS the counter!
--   - 6-bit state machine counts 0→1→2→...→max→overflow→0
--   - Tests full FORGE contract (3 layers + hierarchical encoder)
--   - OutputA = state value (16-bit extended for visualization)
--   - OutputD = hierarchical encoding (state + status, SHIM-driven)
--
-- Architecture: FORGE 3-layer pattern per Handoff 6
--   Layer 3 (MAIN): State counter FSM (MCC-agnostic)
--                   - 3 outputs (OutputA/B/C)
--                   - Exports app_state_vector[5:0] + app_status_vector[7:0]
--   Layer 2 (SHIM): Register mapping + hierarchical encoder
--                   - Unpacks CR0[5:0] → app_reg_max_state
--                   - Instantiates forge_hierarchical_encoder
--                   - Drives OutputD with encoded voltage
--   Layer 1 (TOP):  CustomInstrument interface (this entity)
--                   - 4 outputs (OutputA/B/C from MAIN, OutputD from SHIM)
--
-- Control Registers:
--   CR0[31]   - forge_ready (FORGE control scheme)
--   CR0[30]   - user_enable (FORGE control scheme)
--   CR0[29]   - clk_enable (FORGE control scheme)
--   CR0[5:0]  - max_state (configurable count limit, default 15)
--
-- Status Registers:
--   SR0[5:0]  - current_state (6-bit state value)
--   SR0[6]    - overflow_flag (fault indicator)
--
-- Physical Outputs:
--   OutputA   - Current state as 16-bit value (zero-extended)
--   OutputB   - 0 (unused)
--   OutputC   - 0 (unused)
--   OutputD   - Hierarchical voltage encoding (SHIM-driven)
--               state_vector[5:0]  = current state (0-63)
--               status_vector[7]   = overflow flag (fault indicator)
--               status_vector[6:1] = state copy (redundancy, Handoff 6 pattern)
--               status_vector[0]   = 0 (unused)
--
-- Test Strategy:
--   1. Enable counter → state increments 0→1→2→...→max
--   2. OutputD voltage = state × 200 digital units + status offset
--   3. Overflow sets status[7] → negative voltage (fault detection)
--   4. Oscilloscope captures OutputD, decoder extracts state + fault
--
-- FORGE Control Scheme:
--   global_enable = forge_ready AND user_enable AND clk_enable AND loader_done
--   (loader_done = '1' for this test DUT - no BRAM loading)
--
-- References:
--   - Handoff 6: Hierarchical Voltage Encoding
--   - FORGE_App_Wrapper.vhd: Template for 3-layer architecture
--
-- ============================================================================

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library WORK;
use WORK.forge_common_pkg.ALL;

-- ============================================================================
-- Layer 3: State Counter Main Logic (MCC-agnostic, FORGE-compliant)
-- ============================================================================
-- Per Handoff 6: APP Layer receives 3 inputs, 3 outputs
--                Exports app_state_vector[5:0] + app_status_vector[7:0]
--
-- Design: FSM state IS the counter (6-bit linear encoding 0-63)
--   - Auto-increments every clock cycle when enabled
--   - Wraps to 0 when reaching max_state (sets overflow flag)
--   - OutputA = current state (16-bit zero-extended)
--   - OutputB/C = 0 (unused)
--
-- FORGE Compliance:
--   - 3 physical outputs (OutputA/B/C) - OutputD driven by SHIM
--   - State vector: 6-bit linear encoding (0-31 normal, 32-63 reserved)
--   - Status vector[7] = overflow flag (fault indicator per Handoff 6)
--   - Status vector[6:1] = state copy (redundancy, default pattern)
--   - Status vector[0] = 0 (unused)
-- ============================================================================

entity forge_state_counter_main is
    port (
        -- Clock & Reset
        Clk   : in std_logic;
        Reset : in std_logic;  -- Active-high

        -- FORGE Control
        global_enable     : in std_logic;
        ready_for_updates : out std_logic;

        -- Application Registers (unpacked from CR0)
        app_reg_max_state : in unsigned(5 downto 0);  -- Max state (0-63)

        -- Physical Outputs (3 outputs, per Handoff 6)
        OutputA : out signed(15 downto 0);  -- Current state (16-bit extended)
        OutputB : out signed(15 downto 0);  -- Unused
        OutputC : out signed(15 downto 0);  -- Unused

        -- FORGE-mandated state/status exports (Handoff 6)
        app_state_vector  : out std_logic_vector(5 downto 0);  -- FSM state (6-bit)
        app_status_vector : out std_logic_vector(7 downto 0)   -- App status (8-bit)
    );
end entity forge_state_counter_main;

architecture rtl of forge_state_counter_main is
    -- State counter (6-bit, linear encoding 0-63)
    signal state : unsigned(5 downto 0);
    signal overflow_flag : std_logic;

begin
    -- State counter FSM process
    process(Clk, Reset)
    begin
        if Reset = '1' then
            -- Reset to state 0
            state             <= (others => '0');
            overflow_flag     <= '0';
            ready_for_updates <= '1';  -- Safe to update at reset

        elsif rising_edge(Clk) then
            -- Default: clear overflow flag (pulse)
            overflow_flag <= '0';

            if global_enable = '0' then
                -- Disabled: hold at state 0, ready for updates
                state             <= (others => '0');
                ready_for_updates <= '1';
            else
                -- Enabled: increment state counter
                ready_for_updates <= '0';  -- Lock configuration during counting

                if state >= app_reg_max_state then
                    -- Overflow: wrap to 0, set fault flag
                    state         <= (others => '0');
                    overflow_flag <= '1';
                else
                    -- Normal increment
                    state <= state + 1;
                end if;
            end if;
        end if;
    end process;

    -- Physical Outputs (3 outputs per Handoff 6)
    OutputA <= resize(signed(state), 16);  -- State as 16-bit signed (zero-extended)
    OutputB <= (others => '0');            -- Unused
    OutputC <= (others => '0');            -- Unused

    -- FORGE-mandated state/status exports (Handoff 6)
    app_state_vector <= std_logic_vector(state);  -- 6-bit state (linear encoding)

    -- Status vector per Handoff 6 default pattern:
    --   Bit 7:   overflow_flag (fault indicator)
    --   Bits 6:1: state copy (redundancy)
    --   Bit 0:   '0' (unused)
    app_status_vector <= overflow_flag & std_logic_vector(state) & '0';

end architecture rtl;

-- ============================================================================
-- Layer 2: FORGE Shim (Register Mapping + Hierarchical Encoder)
-- ============================================================================
-- Per Handoff 6: SHIM instantiates forge_hierarchical_encoder
--                Receives app_state_vector + app_status_vector from MAIN
--                Drives OutputD with encoded voltage
--
-- Responsibilities:
--   1. Extract FORGE control scheme (CR0[31:29])
--   2. Unpack Control Registers → app_reg_* signals (typed)
--   3. Synchronize register updates with ready_for_updates handshaking
--   4. Pack app_state/status → Status Registers (future network readable)
--   5. Instantiate forge_hierarchical_encoder for OutputD
--
-- Register Mapping:
--   CR0[31:29] - FORGE control scheme (extracted by TOP wrapper)
--   CR0[5:0]   - app_reg_max_state (configurable count limit)
--   SR0[5:0]   - current state (from app_state_vector)
--   SR0[6]     - overflow flag (from app_status_vector[7])
-- ============================================================================

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library WORK;
use WORK.forge_common_pkg.ALL;

entity forge_state_counter_shim is
    port (
        -- Clock & Reset
        clk   : in std_logic;
        rst_n : in std_logic;  -- Active-low

        -- FORGE Control
        global_enable : in std_logic;

        -- Update Handshaking
        ready_for_updates : out std_logic;

        -- Control Registers (from MCC interface)
        Control0 : in std_logic_vector(31 downto 0);

        -- Status Registers (to MCC interface)
        Status0 : out std_logic_vector(31 downto 0);

        -- Physical Inputs (3 inputs per Handoff 6)
        InputA : in signed(15 downto 0);
        InputB : in signed(15 downto 0);
        InputC : in signed(15 downto 0);

        -- Physical Outputs (4 outputs: 3 from MAIN, 1 from encoder)
        OutputA : out signed(15 downto 0);  -- From MAIN
        OutputB : out signed(15 downto 0);  -- From MAIN
        OutputC : out signed(15 downto 0);  -- From MAIN
        OutputD : out signed(15 downto 0)   -- From hierarchical encoder
    );
end entity forge_state_counter_shim;

architecture rtl of forge_state_counter_shim is
    -- Application register signals
    signal app_reg_max_state : unsigned(5 downto 0);

    -- State/status signals from MAIN (Layer 3)
    signal app_state_vector  : std_logic_vector(5 downto 0);
    signal app_status_vector : std_logic_vector(7 downto 0);

    -- Physical outputs from MAIN
    signal main_output_a : signed(15 downto 0);
    signal main_output_b : signed(15 downto 0);
    signal main_output_c : signed(15 downto 0);

    -- Handshaking
    signal main_ready_for_updates : std_logic;

    -- Active-high reset (main logic uses active-high)
    signal reset : std_logic;

begin
    -- Convert reset polarity
    reset <= not rst_n;

    -- Unpack Control Registers → app_reg_* signals
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            app_reg_max_state <= to_unsigned(15, 6);  -- Default: count to 15
        elsif rising_edge(clk) then
            if main_ready_for_updates = '1' then
                -- Main logic says it's safe to update registers
                app_reg_max_state <= unsigned(Control0(5 downto 0));
            end if;
            -- else: Hold current values (main logic busy)
        end if;
    end process;

    -- Pack state/status → Status Registers
    Status0 <= (31 downto 7 => '0') & app_status_vector(7) & app_state_vector;

    -- Handshaking passthrough
    ready_for_updates <= main_ready_for_updates;

    -- Physical outputs: Pass through from MAIN (OutputA/B/C)
    OutputA <= main_output_a;
    OutputB <= main_output_b;
    OutputC <= main_output_c;

    -- Instantiate Layer 3: State Counter Main Logic
    U_MAIN: entity work.forge_state_counter_main
        port map (
            Clk   => clk,
            Reset => reset,

            global_enable     => global_enable,
            ready_for_updates => main_ready_for_updates,

            app_reg_max_state => app_reg_max_state,

            OutputA => main_output_a,
            OutputB => main_output_b,
            OutputC => main_output_c,

            app_state_vector  => app_state_vector,
            app_status_vector => app_status_vector
        );

    -- Instantiate Hierarchical Encoder (drives OutputD)
    U_ENCODER: entity work.forge_hierarchical_encoder
        generic map (
            DIGITAL_UNITS_PER_STATE  => 200,      -- 200 digital units per state
            DIGITAL_UNITS_PER_STATUS => 0.78125   -- 100/128 digital units per status LSB
        )
        port map (
            clk           => clk,
            reset         => reset,  -- Active-high reset

            state_vector  => app_state_vector,   -- 6-bit state from MAIN
            status_vector => app_status_vector,  -- 8-bit status from MAIN

            voltage_out   => OutputD             -- Encoded voltage output
        );

end architecture rtl;

-- ============================================================================
-- Layer 1: Top-Level Wrapper (CustomInstrument Interface)
-- ============================================================================
-- Per Handoff 6: TOP wrapper provides standard MCC CustomInstrument interface
--                Extracts FORGE control scheme (CR0[31:29])
--                Passes through all 4 outputs (OutputA/B/C from SHIM, OutputD from SHIM encoder)
--
-- Simplified for test DUT (no InputA/B/C/D, only Control0 and Status0)
-- ============================================================================

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library WORK;
use WORK.forge_common_pkg.ALL;

entity forge_counter_with_encoder is
    port (
        -- Clock & Reset
        clk   : in std_logic;
        rst_n : in std_logic;

        -- Control Registers (simplified: only CR0 for test DUT)
        Control0 : in std_logic_vector(31 downto 0);

        -- Status Registers (simplified: only SR0 for test DUT)
        Status0 : out std_logic_vector(31 downto 0);

        -- Physical Outputs (4 outputs per MCC CustomInstrument interface)
        OutputA : out signed(15 downto 0);  -- From MAIN (state value)
        OutputB : out signed(15 downto 0);  -- From MAIN (unused)
        OutputC : out signed(15 downto 0);  -- From MAIN (unused)
        OutputD : out signed(15 downto 0)   -- From SHIM encoder (hierarchical encoding)
    );
end entity forge_counter_with_encoder;

architecture rtl of forge_counter_with_encoder is
    -- FORGE control scheme signals
    signal forge_ready   : std_logic;
    signal user_enable   : std_logic;
    signal clk_enable    : std_logic;
    signal loader_done   : std_logic;
    signal global_enable : std_logic;

    -- Handshaking
    signal ready_for_updates : std_logic;

    -- Dummy inputs (not used by state counter)
    signal dummy_input_a : signed(15 downto 0);
    signal dummy_input_b : signed(15 downto 0);
    signal dummy_input_c : signed(15 downto 0);

begin
    -- Extract FORGE control scheme from CR0[31:29]
    forge_ready <= Control0(FORGE_READY_BIT);  -- CR0[31]
    user_enable <= Control0(USER_ENABLE_BIT);  -- CR0[30]
    clk_enable  <= Control0(CLK_ENABLE_BIT);   -- CR0[29]

    -- Hardcode loader_done = '1' (no BRAM loading in this test DUT)
    loader_done <= '1';

    -- Compute global_enable using forge_common_pkg function
    global_enable <= combine_forge_ready(
        forge_ready => forge_ready,
        user_enable => user_enable,
        clk_enable  => clk_enable,
        loader_done => loader_done
    );

    -- Dummy inputs (state counter doesn't use physical inputs)
    dummy_input_a <= (others => '0');
    dummy_input_b <= (others => '0');
    dummy_input_c <= (others => '0');

    -- Instantiate Layer 2: FORGE Shim
    U_SHIM: entity work.forge_state_counter_shim
        port map (
            clk   => clk,
            rst_n => rst_n,

            global_enable     => global_enable,
            ready_for_updates => ready_for_updates,

            Control0 => Control0,
            Status0  => Status0,

            InputA => dummy_input_a,
            InputB => dummy_input_b,
            InputC => dummy_input_c,

            OutputA => OutputA,
            OutputB => OutputB,
            OutputC => OutputC,
            OutputD => OutputD  -- Hierarchical encoder output from SHIM
        );

end architecture rtl;
