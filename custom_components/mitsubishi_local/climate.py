"""Climate platform for Mitsubishi Local integration."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_AUTO,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_FAN_MODE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    TEMP_CELSIUS,
)

from .const import DOMAIN
from .device import MitsubishiDevice

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

HVAC_MODES = [
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_AUTO,
]

FAN_MODES = ["Low", "Medium", "High", "Auto"]

class MitsubishiClimate(ClimateEntity):
    """Representation of a Mitsubishi AC Unit."""

    def __init__(self, device: MitsubishiDevice, name: str):
        """Initialize the climate device."""
        self._device = device
        self._name = name
        self._state: Optional[Dict[str, Any]] = None

    @property
    def name(self) -> str:
        """Return the display name of this entity."""
        return self._name

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def precision(self) -> float:
        """Return the precision of the system."""
        return PRECISION_HALVES

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        if self._state:
            return self._state.get("current_temp")
        return None

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature we try to reach."""
        if self._state:
            return self._state.get("target_temp")
        return None

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return HVAC_MODES

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation mode."""
        if not self._state or not self._state.get("power"):
            return HVAC_MODE_OFF
        return self._state.get("mode", HVAC_MODE_OFF)

    @property
    def fan_modes(self) -> List[str]:
        """Return the list of available fan modes."""
        return FAN_MODES

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting."""
        if self._state:
            fan_speed = self._state.get("fan_speed")
            if fan_speed is not None and 1 <= fan_speed <= 4:
                return FAN_MODES[fan_speed - 1]
        return None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self._device.set_temperature(temp)
            await self.async_update()

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_OFF:
            await self._device.set_power(False)
        else:
            if self.hvac_mode == HVAC_MODE_OFF:
                await self._device.set_power(True)
            await self._device.set_mode(hvac_mode)
        await self.async_update()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        try:
            fan_speed = FAN_MODES.index(fan_mode) + 1
            await self._device.set_fan_speed(fan_speed)
            await self.async_update()
        except ValueError:
            _LOGGER.error("Invalid fan mode: %s", fan_mode)

    async def async_update(self) -> None:
        """Retrieve latest state."""
        try:
            self._state = await self._device.get_state()
        except Exception as e:
            _LOGGER.error("Failed to update device state: %s", e)
