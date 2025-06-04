diff --git a/custom_components/mitsubishi_local/connection.py b/custom_components/mitsubishi_local/connection.py
index a412b7af2956c9a7f00d6987ffa60aede955474b..93ea9e95bff8b387390315ab981ccb6e5aa09257 100644
    b/custom_components/mitsubishi_local/connection.py
@@ -1,60 +1,67 @@
 """Connection handler for Mitsubishi AC units."""
 import asyncio
 import logging
-import socket
 from typing import Optional
 
 _LOGGER = logging.getLogger(__name__)
 
 class MelConnection:
     """Handles the connection to a Mitsubishi AC unit."""
     
     def __init__(self, host: str, port: int = 8317, timeout: float = 5.0):
         """Initialize the connection handler."""
         self._host = host
         self._port = port
         self._timeout = timeout
         self._reader: Optional[asyncio.StreamReader] = None
         self._writer: Optional[asyncio.StreamWriter] = None
         self._lock = asyncio.Lock()
     
     async def connect(self) -> None:
         """Establish connection with the AC unit."""
         if self._writer is not None:
             return            
 
         try:
             self._reader, self._writer = await asyncio.wait_for(
                 asyncio.open_connection(self._host, self._port),
                 timeout=self._timeout,
             )
         except Exception as e:
             self._reader = None
             self._writer = None
             _LOGGER.error("Failed to connect to %s:%d: %s", self._host, self._port, e)
             raise
     
     async def disconnect(self) -> None:
         """Close the connection."""
         if self._writer is not None:
             try:
                 self._writer.close()
                 await self._writer.wait_closed()
             except Exception as e:
                 _LOGGER.error("Error closing connection: %s", e)
             finally:
                 self._reader = None
                 self._writer = None
     
     async def send_command(self, command: bytes) -> bytes:
         """Send a command and receive the response."""
         async with self._lock:
             await self.connect()            
 
             try:
               
                 assert self._writer is not None and self._reader is not None
                 self._writer.write(command)
                 await self._writer.drain()
                 response = await asyncio.wait_for(self._reader.read(1024), self._timeout)
 
                 if not response:
                     raise ConnectionError("No response received")                    
 
                 return response
             except Exception as e:
                 _LOGGER.error("Error sending command: %s", e)
                 await self.disconnect()
                 raise
 
