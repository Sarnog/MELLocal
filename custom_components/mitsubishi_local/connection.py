"""Connection handler for Mitsubishi AC units."""
import asyncio
import logging
import socket
from typing import Optional

_LOGGER = logging.getLogger(__name__)

class MelConnection:
    """Handles the connection to a Mitsubishi AC unit."""
    
    def __init__(self, host: str, port: int = 8317, timeout: float = 5.0):
        """Initialize the connection handler."""
        self._host = host
        self._port = port
        self._timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """Establish connection with the AC unit."""
        if self._socket is not None:
            return
            
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self._timeout)
            self._socket.connect((self._host, self._port))
        except Exception as e:
            self._socket = None
            _LOGGER.error("Failed to connect to %s:%d: %s", self._host, self._port, e)
            raise
    
    async def disconnect(self) -> None:
        """Close the connection."""
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception as e:
                _LOGGER.error("Error closing connection: %s", e)
            finally:
                self._socket = None
    
    async def send_command(self, command: bytes) -> bytes:
        """Send a command and receive the response."""
        async with self._lock:
            await self.connect()
            
            try:
                self._socket.send(command)
                response = self._socket.recv(1024)
                
                if not response:
                    raise ConnectionError("No response received")
                    
                return response
            except Exception as e:
                _LOGGER.error("Error sending command: %s", e)
                await self.disconnect()
                raise