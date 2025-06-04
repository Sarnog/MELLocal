import sys
import types
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub out Home Assistant modules used during import
homeassistant = types.ModuleType("homeassistant")
homeassistant.core = types.ModuleType("homeassistant.core")
homeassistant.config_entries = types.ModuleType("homeassistant.config_entries")
sys.modules['homeassistant'] = homeassistant
sys.modules['homeassistant.core'] = homeassistant.core
sys.modules['homeassistant.config_entries'] = homeassistant.config_entries
homeassistant.core.HomeAssistant = type("HomeAssistant", (), {})
homeassistant.config_entries.ConfigEntry = type("ConfigEntry", (), {})

# Create stub Crypto modules so tests run without pycryptodome
crypto = types.ModuleType("Crypto")
cipher_mod = types.ModuleType("Crypto.Cipher")
util_mod = types.ModuleType("Crypto.Util")
padding_mod = types.ModuleType("Crypto.Util.Padding")

class SimpleAES:
    block_size = 16
    MODE_ECB = 1

    def __init__(self, key):
        self.key = key

    @classmethod
    def new(cls, key, mode):
        return cls(key)

    def encrypt(self, data: bytes) -> bytes:
        return bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(data))

    def decrypt(self, data: bytes) -> bytes:
        return bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(data))


def pad(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def unpad(data: bytes, block_size: int) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

cipher_mod.AES = SimpleAES
padding_mod.pad = pad
padding_mod.unpad = unpad

sys.modules['Crypto'] = crypto
sys.modules['Crypto.Cipher'] = cipher_mod
sys.modules['Crypto.Util'] = util_mod
sys.modules['Crypto.Util.Padding'] = padding_mod

from custom_components.mitsubishi_local.mitsubishi_api import MitsubishiAPI


def test_encrypt_decrypt_short_payload():
    api = MitsubishiAPI('localhost', encryption_key='0123456789abcdef')
    payload = b'\x42'
    encrypted = api._encrypt_payload(payload)
    assert encrypted != payload
    decrypted = api._decrypt_payload(encrypted)
    assert decrypted == payload
