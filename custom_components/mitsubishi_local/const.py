"""Constants for the Mitsubishi Local integration."""
DOMAIN = "mitsubishi_local"

# Default Values
DEFAULT_PORT = 8317

# Communication Constants
PACKET_HEADER = bytes([0xfc, 0x5a])
PACKET_FOOTER = bytes([0xfc, 0x5a])

# Operation Modes
MODE_HEAT = "heat"
MODE_COOL = "cool"
MODE_DRY = "dry"
MODE_FAN_ONLY = "fan_only"
MODE_AUTO = "auto"

# Fan Speeds
FAN_AUTO = "auto"
FAN_LOW = "low"
FAN_MEDIUM = "medium"
FAN_HIGH = "high"