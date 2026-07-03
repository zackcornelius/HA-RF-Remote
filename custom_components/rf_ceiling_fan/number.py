"""Number platform for the RF Ceiling Fan integration.

Exposes one diagnostic number entity:
  • Scan command byte (0–255) — selects which EV1527 command byte is sent
    when the "Send scan command" button entity is pressed.  This allows
    systematic discovery of undocumented remote commands without adding a
    separate button for every possible code.
"""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .entity import RFCeilingFanEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the RF Ceiling Fan number platform."""
    async_add_entities([RFCeilingFanScanCommandNumber(config_entry)])


class RFCeilingFanScanCommandNumber(RFCeilingFanEntity, NumberEntity, RestoreEntity):
    """Number entity representing the command byte used for raw scanning.

    The value is persisted across restarts so that the user can return to
    a partially-explored command space without losing their place.
    """

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0.0
    _attr_native_max_value = 255.0
    _attr_native_step = 1.0
    _attr_translation_key = "scan_command"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the number entity."""
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_scan_command"
        self._attr_native_value = 0.0
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        """Restore the last known scan command byte."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state not in (
            None,
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            try:
                value = float(last.state)
                self._attr_native_value = max(0.0, min(255.0, value))
            except (ValueError, TypeError):
                pass
        self.hass.data.setdefault(DOMAIN, {}).setdefault(self._entry_id, {})[
            "scan_command"
        ] = int(self._attr_native_value)

    async def async_set_native_value(self, value: float) -> None:
        """Update the scan command byte and sync to shared state."""
        self._attr_native_value = value
        self.hass.data.setdefault(DOMAIN, {}).setdefault(self._entry_id, {})[
            "scan_command"
        ] = int(value)
        self.async_write_ha_state()
