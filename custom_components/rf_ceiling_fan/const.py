"""Constants for the RF Ceiling Fan integration."""

from typing import Final

from rf_protocols import ModulationType

DOMAIN: Final = "rf_ceiling_fan"

CONF_TRANSMITTER: Final = "transmitter"

FREQUENCY: Final = 433_920_000
MODULATION: Final = ModulationType.OOK

# Frame repeat count — the physical remote transmits each code 3 times;
# repeat_count=5 sends 1 initial frame + 5 repeats (6 total) for reliability.
FRAME_REPEAT_COUNT: Final = 5

# EV1527 OOK timing parameters (microseconds)
# T ≈ 410 μs (measured from Pronto captures: short pulses span 368–421 μs)
_T_US: Final = 410
SYNC_ON_US: Final = _T_US
SYNC_OFF_US: Final = 31 * _T_US   # ~12 710 μs gap after sync pulse
BIT1_ON_US: Final = 3 * _T_US    # ~1 230 μs high for a '1' bit
BIT1_OFF_US: Final = _T_US        # ~410 μs low for a '1' bit
BIT0_ON_US: Final = _T_US         # ~410 μs high for a '0' bit
BIT0_OFF_US: Final = 3 * _T_US   # ~1 230 μs low for a '0' bit

# EV1527 device address — the top 16 bits shared by every code from this remote.
# Each 24-bit code = (DEVICE_ADDRESS << 8) | <8-bit command byte>.
DEVICE_ADDRESS: Final = 0x6DD9

# 24-bit RF codes broken down as (DEVICE_ADDRESS << 8) | command byte:
CODE_LIGHT_POWER: Final = 0x6DD905   # command 0x05
CODE_LIGHT_UP: Final = 0x6DD919      # command 0x19
CODE_LIGHT_DOWN: Final = 0x6DD935    # command 0x35
CODE_CT_COLD: Final = 0x6DD918       # command 0x18
CODE_CT_WARM: Final = 0x6DD937       # command 0x37
CODE_FAN_SPEED_1: Final = 0x6DD933   # command 0x33
CODE_FAN_SPEED_2: Final = 0x6DD91A   # command 0x1A
CODE_FAN_SPEED_3: Final = 0x6DD932   # command 0x32
CODE_FAN_OFF: Final = 0x6DD930       # command 0x30
CODE_TIMER_1H: Final = 0x6DD916      # command 0x16
CODE_TIMER_4H: Final = 0x6DD936      # command 0x36

# Light dimmer: number of discrete brightness steps on the remote
BRIGHTNESS_STEPS: Final = 8

# Color temperature extremes (Kelvin)
COLOR_TEMP_WARM_K: Final = 3000   # warm white (lowest K / warmest)
COLOR_TEMP_COLD_K: Final = 6500   # cool white (highest K / coolest)
COLOR_TEMP_MID_K: Final = (COLOR_TEMP_WARM_K + COLOR_TEMP_COLD_K) // 2

# Fan speed count
FAN_SPEED_COUNT: Final = 3
