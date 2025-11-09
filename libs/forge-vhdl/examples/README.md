# FORGE Examples

Complete, working examples demonstrating FORGE architecture patterns.

## counter/

**The canonical FORGE example** - "Hello World" for FORGE development.

Demonstrates:
- ✅ Complete FORGE 3-layer architecture (Loader placeholder → Shim → Main)
- ✅ CR0[31:29] control scheme (the calling convention)
- ✅ HVS encoding (batteries-included oscilloscope debugging)
- ✅ Register packing/unpacking (CR0 → app_reg_*, app_status_* → SR0)
- ✅ ready_for_updates handshaking
- ✅ Progressive CocoTB testing

**Files:**
- `vhdl/forge_counter_with_encoder.vhd` - Complete VHDL implementation
- `cocotb_tests/` - CocoTB test suite
- `README.md` - "Your First FORGE Instrument" tutorial

**Start here** to learn FORGE patterns, then adapt to your own application.
