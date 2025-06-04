"""MELCloud protocol implementation."""
import logging
import struct
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)

class MelCloudProtocol:
    """Implementation of the MELCloud protocol."""
    
    PACKET_HEADER = bytes([0x5a, 0x01, 0x11, 0x01])
    PACKET_FOOTER = bytes([0x0d, 0x0a])
    
    # Command types
    CMD_GET_STATUS = 0x02
    CMD_SET_STATUS = 0x01
    
    # Operation modes
    MODE_HEAT = 1
    MODE_DRY = 2
    MODE_COOL = 3
    MODE_FAN = 7
    MODE_AUTO = 8
    
    @staticmethod
    def create_packet(command: int, payload: bytes) -> bytes:
        """Create a packet with header, command, payload, and footer."""
        length = len(payload) + 2  # +2 for command and length byte
        packet = (
            MelCloudProtocol.PACKET_HEADER +
            bytes([length, command]) +
            payload +
            MelCloudProtocol.PACKET_FOOTER
        )
        return packet
    
    @staticmethod
    def parse_status_response(data: bytes) -> Dict[str, Any]:
        """Parse the status response from the device."""
        if len(data) < 20:
            raise ValueError("Response too short")
            
        try:
            return {
                "power": bool(data[3] & 0x01),
                "mode": MelCloudProtocol._parse_mode(data[4]),
                "target_temp": data[5] / 2.0,
                "current_temp": data[6] / 2.0,
                "fan_speed": data[7],
                "vane_horizontal": data[8],
                "vane_vertical": data[9]
            }
        except Exception as e:
            _LOGGER.error("Error parsing status response: %s", e)
            raise
    
    @staticmethod
    def create_set_command(
        power: Optional[bool] = None,
        mode: Optional[int] = None,
        target_temp: Optional[float] = None,
        fan_speed: Optional[int] = None,
        vane_horizontal: Optional[int] = None,
        vane_vertical: Optional[int] = None
    ) -> bytes:
        """Create a command to set device parameters."""
        payload = bytearray(16)
        
        if power is not None:
            payload[3] = 0x01 if power else 0x00
        if mode is not None:
            payload[4] = mode
        if target_temp is not None:
            payload[5] = int(target_temp * 2)
        if fan_speed is not None:
            payload[7] = fan_speed
        if vane_horizontal is not None:
            payload[8] = vane_horizontal
        if vane_vertical is not None:
            payload[9] = vane_vertical
            
        return MelCloudProtocol.create_packet(
            MelCloudProtocol.CMD_SET_STATUS,
            bytes(payload)
        )
    
    @staticmethod
    def _parse_mode(mode_byte: int) -> str:
        """Convert mode byte to string representation."""
        modes = {
            MelCloudProtocol.MODE_HEAT: "heat",
            MelCloudProtocol.MODE_DRY: "dry",
            MelCloudProtocol.MODE_COOL: "cool",
            MelCloudProtocol.MODE_FAN: "fan_only",
            MelCloudProtocol.MODE_AUTO: "auto"
        }
        return modes.get(mode_byte, "unknown")
