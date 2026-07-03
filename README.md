# HA-RF-Remote

Custom Home Assistant integration for a 433 MHz RF ceiling fan, built on the
[`radio_frequency`](https://developers.home-assistant.io/docs/core/entity/radio-frequency/)
entity platform introduced in Home Assistant 2026.5.

## What it does

The integration exposes five entity types for a 433 MHz ceiling fan remote:

| Entity | Features |
|--------|----------|
| **Fan** (`fan.rf_ceiling_fan`) | On / Off, three discrete speeds |
| **Light** (`light.rf_ceiling_fan`) | On / Off, 8-step dimmer, two colour temperatures (warm 3000 K / cold 6500 K) |
| **Button** – Timer 1 h | Activates the remote's 1-hour auto-off timer |
| **Button** – Timer 4 h | Activates the remote's 4-hour auto-off timer |
| **Button** – Send scan command *(diagnostic)* | Transmits the EV1527 code for the byte selected in the number entity below |
| **Number** – Scan command byte *(diagnostic, 0–255)* | Sets which command byte is sent when the scan button is pressed |

## RF protocol

All codes use the **EV1527** OOK protocol at 433.92 MHz with T ≈ 410 µs:

* **Sync pulse**: 1 T high + 31 T low
* **'1' bit**: 3 T high + 1 T low
* **'0' bit**: 1 T high + 3 T low

Each 24-bit code is structured as:

```
[ 16-bit device address 0x6DD9 ][ 8-bit command byte ]
```

### Known command bytes

| Action | Command byte | Full 24-bit code |
|--------|:------------:|-----------------|
| Light power (toggle) | `0x05` | `0x6DD905` |
| Light up | `0x19` | `0x6DD919` |
| Light down | `0x35` | `0x6DD935` |
| Colour temp cold | `0x18` | `0x6DD918` |
| Colour temp warm | `0x37` | `0x6DD937` |
| Fan speed 1 | `0x33` | `0x6DD933` |
| Fan speed 2 | `0x1A` | `0x6DD91A` |
| Fan speed 3 | `0x32` | `0x6DD932` |
| Fan off | `0x30` | `0x6DD930` |
| Timer 1 h | `0x16` | `0x6DD916` |
| Timer 4 h | `0x36` | `0x6DD936` |

### Scanning for unknown commands

To discover what other command bytes (0x00–0xFF) do on the physical device:

1. In Home Assistant, set the **Scan command byte** number entity to the byte you want to try (e.g. `0x20` = 32).
2. Press the **Send scan command** button.
3. Observe the physical fan/light for any response.

Both entities appear under the **Diagnostic** category in the device page and are hidden by default in the main dashboard.

## Requirements

* Home Assistant 2026.5 or later
* A compatible 433 MHz RF transmitter (e.g. Broadlink RM Pro, ESPHome CC1101)
  set up through the `radio_frequency` platform
* Python package `rf-protocols >= 4.0.0` (installed automatically by HA)

## Installation (HACS / manual)

1. Copy the `custom_components/rf_ceiling_fan/` folder into your HA
   `custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for
   **RF Ceiling Fan**.
4. Select the 433 MHz transmitter entity to use and click **Submit**.

## Notes

* The light power button is a **toggle** on the physical remote.  The
  integration keeps track of the assumed on/off state across restarts.
* Brightness is controlled with incremental up/down commands (8 steps).
  When HA requests a specific brightness level the integration sends the
  required number of up/down presses from the current tracked level.
* Colour temperature snaps to either warm (3000 K) or cold (6500 K),
  whichever is closer to the requested value.