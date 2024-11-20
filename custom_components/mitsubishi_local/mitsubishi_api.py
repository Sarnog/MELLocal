"""API for communicating with Mitsubishi AC units locally."""
import asyncio
import logging
import socket
from typing import Dict, Any
from Crypto.Cipher import AES
from .const import (
    DEFAULT_PORT,
    PACKET_HEADER,
    PACKET_FOOTER,
)

_LOGGER = logging.getLogger(__name__)

class MitsubishiAPI:
    """API for communicating with Mitsubishi AC units."""

    def __init__(self, host: str, port: int = DEFAULT_PORT, encryption_key: str = None):
        """Initialize the API."""
        self._host = host
        self._port = port
        self._encryption_key = encryption_key.encode() if encryption_key else None
        self._socket = None

    async def connect(self) -> None:
        """Establish connection with the AC unit."""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self._host, self._port))
            self._socket.settimeout(5.0)
        except Exception as e:
            _LOGGER.error("Failed to connect: %s", e)
            raise

    def _encrypt_payload(self, payload: bytes) -> bytes:
        """Encrypt the payload using AES."""
        if not self._encryption_key:
            return payload
        
        cipher = AES.new(self._encryption_key, AES.MODE_ECB)
        return cipher.encrypt(payload)

    def _decrypt_payload(self, payload: bytes) -> bytes:
        """Decrypt the payload using AES."""
        if not self._encryption_key:
            return payload
        
        cipher = AES.new(self._encryption_key, AES.MODE_ECB)
        return cipher.decrypt(payload)

    async def send_command(self, command: bytes) -> bytes:
        """Send command to the AC unit and receive response."""
        if not self._socket:
            await self.connect()

        try:
            packet = PACKET_HEADER + self._encrypt_payload(command) + PACKET_FOOTER
            self._socket.send(packet)
            response = self._socket.recv(1024)
            return self._decrypt_payload(response[2:-2])
        except Exception as e:
            _LOGGER.error("Failed to send command: %s", e)
            raise

    async def get_state(self) -> Dict[str, Any]:
        """Get the current state of the AC unit."""
        response = await self.send_command(bytes([0x42]))  # Status request command
        return self._parse_status_response(response)

    async def set_temperature(self, temperature: float) -> None:
        """Set the target temperature."""
        temp_command = bytes([0x41, int(temperature * 2)])  # Temperature command
        await self.send_command(temp_command)

    async def set_mode(self, mode: str) -> None:
        """Set the operation mode."""
        mode_map = {
            "heat": 0x01,
            "cool": 0x02,
            "dry": 0x03,
            "fan_only": 0x04,
            "auto": 0x05
        }
        mode_command = bytes([0x43, mode_map.get(mode, 0x05)])  # Mode command
        await self.send_command(mode_command)

    def _parse_status_response(self, response: bytes) -> Dict[str, Any]:
        """Parse the status response from the AC unit."""
        # This is a simplified parser - actual implementation would need to match
        # the specific protocol of your AC unit
        return {
            "current_temperature": response[0] / 2,
            "target_temperature": response[1] / 2,
            "mode": self._get_mode_from_response(response[2]),
            "fan_mode": self._get_fan_mode_from_response(response[3])
        }

    def _get_mode_from_response(self, mode_byte: int) -> str:
        """Convert mode byte to string representation."""
        mode_map = {
            0x01: "heat",
            0x02: "cool",
            0x03: "dry",
            0x04: "fan_only",
            0x05: "auto"
        }
        return mode_map.get(mode_byte, "auto")

    def _get_fan_mode_from_response(self, fan_byte: int) -> str:
        """Convert fan mode byte to string representation."""
        fan_map = {
            0x01: "low",
            0x02: "medium",
            0x03: "high",
            0x04: "auto"
        }
        return fan_map.get(fan_byte, "auto")