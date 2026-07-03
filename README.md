# HA-RF-Remote

Custom Home Assistant integration for a 433 MHz RF ceiling fan, built on the
[`radio_frequency`](https://developers.home-assistant.io/docs/core/entity/radio-frequency/)
entity platform introduced in Home Assistant 2026.5.

## What it does

The integration exposes two entities for a 433 MHz ceiling fan remote:

| Entity | Features |
|--------|----------|
| **Fan** (`fan.rf_ceiling_fan`) | On / Off, three discrete speeds |
| **Light** (`light.rf_ceiling_fan`) | On / Off, 8-step dimmer, two colour temperatures (warm 3000 K / cold 6500 K) |

## RF commands

All codes are 24-bit, encoded with EV1527-like OOK pulse-width modulation at
433.92 MHz (T = 350 µs).

| Action | 24-bit code |
|--------|-------------|
| Light power (toggle) | `0110 1101 1101 1001 0000 0101` |
| Fan speed 1 | `0110 1101 1101 1001 0011 0011` |
| Fan speed 2 | `0110 1101 1101 1001 0001 1010` |
| Fan speed 3 | `0110 1101 1101 1001 0011 0010` |
| Fan off | `0110 1101 1101 1001 0011 0000` |
| Light up | `0110 1101 1101 1001 0001 1001` |
| Light down | `0110 1101 1101 1001 0011 0101` |
| Timer 1 h | `0110 1101 1101 1001 0001 0110` |
| Timer 4 h | `0110 1101 1101 1001 0011 0110` |
| Colour temp cold | `0110 1101 1101 1001 0001 1000` |
| Colour temp warm | `0110 1101 1101 1001 0011 0111` |

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