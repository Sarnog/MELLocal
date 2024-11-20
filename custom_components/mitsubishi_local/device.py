"""Mitsubishi AC device implementation."""
import logging
from typing import Dict, Any, Optional

from .connection import MelConnection
from .protocol import MelCloudProtocol

_LOGGER = logging.getLogger(__name__)

class MitsubishiDevice:
    """Represents a Mitsubishi AC device."""
    
    def __init__(self, host: str, port: int = 8317):
        """Initialize the device."""
        self._connection = MelConnection(host, port)
        self._last_state: Optional[Dict[str, Any]] = None
    
    async def get_state(self) -> Dict[str, Any]:
        """Get the current state of the device."""
        try:
            command = MelCloudProtocol.create_packet(
                MelCloudProtocol.CMD_GET_STATUS,
                bytes([0x00])
            )
            response = await self._connection.send_command(command)
            self._last_state = MelCloudProtocol.parse_status_response(response)
            return self._last_state
        except Exception as e:
            _LOGGER.error("Failed to get device state: %s", e)
            raise
    
    async def set_power(self, power: bool) -> None:
        """Set the power state."""
        command = MelCloudProtocol.create_set_command(power=power)
        await self._connection.send_command(command)
    
    async def set_temperature(self, temperature: float) -> None:
        """Set the target temperature."""
        command = MelCloudProtocol.create_set_command(target_temp=temperature)
        await self._connection.send_command(command)
    
    async def set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        mode_map = {
            "heat": MelCloudProtocol.MODE_HEAT,
            "dry": MelCloudProtocol.MODE_DRY,
            "cool": MelCloudProtocol.MODE_COOL,
            "fan_only": MelCloudProtocol.MODE_FAN,
            "auto": MelCloudProtocol.MODE_AUTO
        }
        mode_value = mode_map.get(mode)
        if mode_value is None:
            raise ValueError(f"Invalid mode: {mode}")
            
        command = MelCloudProtocol.create_set_command(mode=mode_value)
        await self._connection.send_command(command)
    
    async def set_fan_speed(self, speed: int) -> None:
        """Set the fan speed (1-4, where 4 is auto)."""
        if not 1 <= speed <= 4:
            raise ValueError("Fan speed must be between 1 and 4")
            
        command = MelCloudProtocol.create_set_command(fan_speed=speed)
        await self._connection.send_command(command)