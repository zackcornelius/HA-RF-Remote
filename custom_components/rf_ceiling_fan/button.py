"""Button platform for the RF Ceiling Fan integration.

Exposes button entities:
  • Timer 1 h     — activates the remote's 1-hour auto-off timer.
  • Timer 4 h     — activates the remote's 4-hour auto-off timer.
  • Toggle beep   — toggles the confirmation beep on the fan.
  • Send scan command — sends the EV1527 code whose command byte is set by
    the companion "Scan command byte" number entity.  Useful for discovering
    unknown remote commands when experimenting with the full 0x00–0xFF range.
"""

from homeassistant.components.button import ButtonEntity
from homeassistant.components.radio_frequency import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .commands import make_command
from .const import CODE_TIMER_1H, CODE_TIMER_4H, CODE_TOGGLE_BEEP, DEVICE_ADDRESS, DOMAIN
from .entity import RFCeilingFanEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the RF Ceiling Fan button platform."""
    async_add_entities(
        [
            RFCeilingFanTimer1HButton(config_entry),
            RFCeilingFanTimer4HButton(config_entry),
            RFCeilingFanToggleBeepButton(config_entry),
            RFCeilingFanScanButton(config_entry),
        ]
    )


class _RFCeilingFanFixedCodeButton(RFCeilingFanEntity, ButtonEntity):
    """Base class for a button that sends a fixed RF command code."""

    _code: int

    async def async_press(self) -> None:
        """Send the RF command."""
        await async_send_command(
            self.hass,
            self._transmitter,
            make_command(self._code),
            context=self._context,
        )


class RFCeilingFanTimer1HButton(_RFCeilingFanFixedCodeButton):
    """Button that activates the 1-hour auto-off timer."""

    _code = CODE_TIMER_1H
    _attr_translation_key = "timer_1h"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_timer_1h"


class RFCeilingFanTimer4HButton(_RFCeilingFanFixedCodeButton):
    """Button that activates the 4-hour auto-off timer."""

    _code = CODE_TIMER_4H
    _attr_translation_key = "timer_4h"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_timer_4h"


class RFCeilingFanToggleBeepButton(_RFCeilingFanFixedCodeButton):
    """Button that toggles the confirmation beep on the fan."""

    _code = CODE_TOGGLE_BEEP
    _attr_translation_key = "toggle_beep"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_toggle_beep"


class RFCeilingFanScanButton(RFCeilingFanEntity, ButtonEntity):
    """Button that transmits the command byte currently held in the number entity.

    This is a discovery/diagnostic tool.  Set the "Scan command byte" number
    entity to any value 0–255, then press this button to transmit the
    corresponding EV1527 code: (DEVICE_ADDRESS << 8) | command_byte.
    """

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "send_scan_command"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the scan button."""
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_send_scan_command"
        self._entry_id = entry.entry_id

    async def async_press(self) -> None:
        """Send the selected scan command."""
        command_byte: int = int(
            self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("scan_command", 0)
        )
        code = (DEVICE_ADDRESS << 8) | (command_byte & 0xFF)
        await async_send_command(
            self.hass,
            self._transmitter,
            make_command(code),
            context=self._context,
        )
