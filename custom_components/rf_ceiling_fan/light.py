"""Light platform for the RF Ceiling Fan integration.

The remote exposes:
  • A toggle power button (not a direct on/off).
  • Incremental brightness up / down buttons (8 discrete steps assumed).
  • Two colour-temperature presets: cold (≈6500 K) and warm (≈3000 K).

Because the remote only has step-wise brightness, the entity tracks an
internal step level (0 = off, 1–8 = brightness steps) and sends the
required number of up/down presses whenever Home Assistant requests a
specific brightness value.  The assumed_state flag is set, so the UI
shows the last-commanded state rather than waiting for confirmation.
"""

from typing import Any, override

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.components.radio_frequency import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .commands import make_command
from .const import (
    BRIGHTNESS_STEPS,
    CODE_CT_COLD,
    CODE_CT_WARM,
    CODE_LIGHT_DOWN,
    CODE_LIGHT_POWER,
    CODE_LIGHT_UP,
    COLOR_TEMP_COLD_K,
    COLOR_TEMP_MID_K,
    COLOR_TEMP_WARM_K,
)
from .entity import RFCeilingFanEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the RF Ceiling Fan light platform."""
    async_add_entities([RFCeilingFanLight(config_entry)])


class RFCeilingFanLight(RFCeilingFanEntity, LightEntity, RestoreEntity):
    """RF ceiling fan light with step-wise dimming and two colour temperatures."""

    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_min_color_temp_kelvin = COLOR_TEMP_WARM_K
    _attr_max_color_temp_kelvin = COLOR_TEMP_COLD_K
    _attr_translation_key = "light"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the light entity."""
        super().__init__(entry)
        self._attr_unique_id = entry.entry_id
        # Track brightness as a step level (0 = off, 1–BRIGHTNESS_STEPS = on)
        self._level: int = 0
        # Default to warm white; async_added_to_hass will restore the actual
        # value from the previous state when the entity is first loaded.
        self._ct_kelvin: int = COLOR_TEMP_WARM_K

    # ------------------------------------------------------------------
    # State properties
    # ------------------------------------------------------------------

    @property
    @override
    def is_on(self) -> bool:
        """Return True when the light is on."""
        return self._level > 0

    @property
    @override
    def brightness(self) -> int | None:
        """Return current brightness (0-255), or None when off."""
        if self._level == 0:
            return None
        return round(self._level * 255 / BRIGHTNESS_STEPS)

    @property
    @override
    def color_temp_kelvin(self) -> int | None:
        """Return the active colour temperature in Kelvin, or None when off."""
        return self._ct_kelvin if self._level > 0 else None

    # ------------------------------------------------------------------
    # State restoration
    # ------------------------------------------------------------------

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the last known brightness and colour temperature."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is None:
            return
        if last.state == STATE_ON:
            # Restore brightness step
            last_bri = last.attributes.get(ATTR_BRIGHTNESS)
            if isinstance(last_bri, (int, float)) and last_bri > 0:
                self._level = round(last_bri * BRIGHTNESS_STEPS / 255)
                self._level = max(1, min(BRIGHTNESS_STEPS, self._level))
            else:
                self._level = BRIGHTNESS_STEPS  # assume maximum if unknown

            # Restore colour temperature
            last_ct = last.attributes.get(ATTR_COLOR_TEMP_KELVIN)
            if isinstance(last_ct, (int, float)):
                self._ct_kelvin = int(last_ct)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on, optionally setting brightness and/or colour temp."""
        target_brightness: int | None = kwargs.get(ATTR_BRIGHTNESS)
        target_ct_k: int | None = kwargs.get(ATTR_COLOR_TEMP_KELVIN)

        # Power on if currently off
        if self._level == 0:
            await self._async_send(CODE_LIGHT_POWER)
            # Start at maximum brightness (physical default when toggled on)
            self._level = BRIGHTNESS_STEPS

        # Adjust colour temperature if requested
        if target_ct_k is not None:
            await self._async_set_ct(target_ct_k)

        # Adjust brightness if requested
        if target_brightness is not None:
            await self._async_set_brightness(target_brightness)

        self.async_write_ha_state()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off (toggle power)."""
        if self._level > 0:
            await self._async_send(CODE_LIGHT_POWER)
            self._level = 0
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _async_set_brightness(self, brightness: int) -> None:
        """Step the brightness up or down to reach the requested level."""
        target_level = round(brightness * BRIGHTNESS_STEPS / 255)
        target_level = max(1, min(BRIGHTNESS_STEPS, target_level))
        delta = target_level - self._level
        if delta > 0:
            for _ in range(delta):
                await self._async_send(CODE_LIGHT_UP)
        elif delta < 0:
            for _ in range(-delta):
                await self._async_send(CODE_LIGHT_DOWN)
        self._level = target_level

    async def _async_set_ct(self, kelvin: int) -> None:
        """Send the cold or warm colour-temperature command."""
        if kelvin >= COLOR_TEMP_MID_K:
            await self._async_send(CODE_CT_COLD)
            self._ct_kelvin = COLOR_TEMP_COLD_K
        else:
            await self._async_send(CODE_CT_WARM)
            self._ct_kelvin = COLOR_TEMP_WARM_K

    async def _async_send(self, code: int) -> None:
        """Send a single RF command via the configured transmitter."""
        await async_send_command(
            self.hass, self._transmitter, make_command(code), context=self._context
        )
