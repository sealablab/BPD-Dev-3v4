# forge_tools - FORGE Utilities and Decoders

Standalone tools for FORGE development and debugging.

## hierarchical_decoder.py

**Hierarchical Voltage Scheme (HVS) decoder** - Extract state + status from oscilloscope voltage.

Decodes 14-bit payload (6-bit state + 8-bit status) from single voltage channel.

**Functions:**
- `decode_hierarchical_voltage(voltage)` - Decode raw voltage value
- `decode_oscilloscope_voltage(voltage_array)` - Decode oscilloscope capture

**Returns:**
```python
{
    'state': int,           # 0-31 (6-bit state)
    'status': int,          # 0-255 (8-bit status)
    'fault': bool,          # True if status[7] = 1 (negative voltage)
    'voltage': float        # Original voltage
}
```

**Example:**
```python
from forge_tools.hierarchical_decoder import decode_hierarchical_voltage

result = decode_hierarchical_voltage(0.414)
# result = {'state': 2, 'status': 0x12, 'fault': False, 'voltage': 0.414}

result = decode_hierarchical_voltage(-0.414)
# result = {'state': 2, 'status': 0x92, 'fault': True, 'voltage': -0.414}
```

**Architecture:**
- State: 200mV steps (major state transitions)
- Status[6:0]: 0-100mV offset (fine-grained detail, 0.78mV per step)
- Status[7]: Fault indicator (sign flip)

See `docs/HVS_ENCODING.md` for complete HVS specification.

## Future Tools

- Register value converters (voltage ↔ digital)
- Bitstream analysis utilities
- MCC API helpers
