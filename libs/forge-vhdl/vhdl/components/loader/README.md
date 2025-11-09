# Loader Components

BRAM initialization and configuration loading components.

## forge_bram_loader.vhd (Future)

**Status:** Design complete, integration pending.

BRAM loader for initializing FPGA Block RAM from external sources.

**Planned features:**
- Network-accessible BRAM loading via Control Registers
- Sets `loader_done` signal for FORGE control scheme
- Supports LUT loading, coefficient tables, waveform data

**Integration plan:**
1. Adapt existing reference implementation for 16-register MCC interface
2. Wire `loader_done` to FORGE wrapper
3. Update `forge_ready` flag when loading completes

**Register allocation (tentative):**
- CR12: BRAM address
- CR13: BRAM data
- CR14: BRAM control (write enable, bank select)
- CR15: BRAM status (loader_done, error flags)

This component will become Layer 1 in the FORGE 3-layer architecture.
