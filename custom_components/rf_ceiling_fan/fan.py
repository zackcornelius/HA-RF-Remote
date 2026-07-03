"""Fan platform for the RF Ceiling Fan integration."""

import math
from typing import Any, override

from homeassistant.components.fan import ATTR_PERCENTAGE, FanEntity, FanEntityFeature
from homeassistant.components.radio_frequency import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .commands import make_command
from .const import (
    CODE_FAN_OFF,
    CODE_FAN_SPEED_1,
    CODE_FAN_SPEED_2,
    CODE_FAN_SPEED_3,
    FAN_SPEED_COUNT,
)
from .entity import RFCeilingFanEntity

PARALLEL_UPDATES = 1

_SPEED_RANGE = (1, FAN_SPEED_COUNT)
_SPEED_COMMANDS = {
    1: CODE_FAN_SPEED_1,
    2: CODE_FAN_SPEED_2,
    3: CODE_FAN_SPEED_3,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the RF Ceiling Fan fan platform."""
    async_add_entities([RFCeilingFanFan(config_entry)])


class RFCeilingFanFan(RFCeilingFanEntity, FanEntity, RestoreEntity):
    """RF ceiling fan with three discrete speeds."""

    _attr_name = None
    _attr_speed_count = FAN_SPEED_COUNT
    _attr_supported_features = (
        FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.SET_SPEED
    )

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the fan entity."""
        super().__init__(entry)
        self._attr_unique_id = entry.entry_id
        self._speed: int = 0  # 0 = off, 1-3 = speed level

    @property
    @override
    def is_on(self) -> bool:
        """Return True when the fan is running at any speed."""
        return self._speed > 0

    @property
    @override
    def percentage(self) -> int:
        """Return the current speed as a percentage (0 = off)."""
        if self._speed == 0:
            return 0
        return ranged_value_to_percentage(_SPEED_RANGE, self._speed)

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the last known speed from the saved percentage attribute."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is None:
            return
        last_pct = last.attributes.get(ATTR_PERCENTAGE)
        if isinstance(last_pct, (int, float)) and last_pct > 0:
            self._speed = math.ceil(
                percentage_to_ranged_value(_SPEED_RANGE, last_pct)
            )

    @override
    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the fan on at the requested speed (default: speed 1)."""
        if percentage is None or percentage <= 0:
            speed = 1
        else:
            speed = math.ceil(percentage_to_ranged_value(_SPEED_RANGE, percentage))
        await self._async_set_speed(speed)

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self._async_set_speed(0)

    @override
    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed from a percentage value."""
        if percentage <= 0:
            await self._async_set_speed(0)
            return
        speed = math.ceil(percentage_to_ranged_value(_SPEED_RANGE, percentage))
        await self._async_set_speed(speed)

    async def _async_set_speed(self, speed: int) -> None:
        """Send the appropriate RF command for the requested speed."""
        if speed == 0:
            code = CODE_FAN_OFF
        else:
            code = _SPEED_COMMANDS[speed]
        await async_send_command(
            self.hass, self._transmitter, make_command(code), context=self._context
        )
        self._speed = speed
        self.async_write_ha_state()
