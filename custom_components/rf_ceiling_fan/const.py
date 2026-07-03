"""Constants for the RF Ceiling Fan integration."""

from typing import Final

from rf_protocols import ModulationType

DOMAIN: Final = "rf_ceiling_fan"

CONF_TRANSMITTER: Final = "transmitter"

FREQUENCY: Final = 433_920_000
MODULATION: Final = ModulationType.OOK

# EV1527-like OOK timing parameters (microseconds)
# T = 350 μs
_T_US: Final = 350
SYNC_ON_US: Final = _T_US
SYNC_OFF_US: Final = 31 * _T_US   # 10 850 μs gap after sync pulse
BIT1_ON_US: Final = 3 * _T_US    # 1 050 μs high for a '1' bit
BIT1_OFF_US: Final = _T_US        # 350 μs low for a '1' bit
BIT0_ON_US: Final = _T_US         # 350 μs high for a '0' bit
BIT0_OFF_US: Final = 3 * _T_US   # 1 050 μs low for a '0' bit

# 24-bit RF codes (verified bit-by-bit from the problem spec)
CODE_LIGHT_POWER: Final = 0x6DD905   # 0110 1101 1101 1001 0000 0101
CODE_FAN_SPEED_1: Final = 0x6DD933   # 0110 1101 1101 1001 0011 0011
CODE_FAN_SPEED_2: Final = 0x6DD91A   # 0110 1101 1101 1001 0001 1010
CODE_FAN_SPEED_3: Final = 0x6DD932   # 0110 1101 1101 1001 0011 0010
CODE_FAN_OFF: Final = 0x6DD930       # 0110 1101 1101 1001 0011 0000
CODE_LIGHT_UP: Final = 0x6DD919      # 0110 1101 1101 1001 0001 1001
CODE_LIGHT_DOWN: Final = 0x6DD935    # 0110 1101 1101 1001 0011 0101
CODE_TIMER_1H: Final = 0x6DD916      # 0110 1101 1101 1001 0001 0110
CODE_TIMER_4H: Final = 0x6DD936      # 0110 1101 1101 1001 0011 0110
CODE_CT_COLD: Final = 0x6DD918       # 0110 1101 1101 1001 0001 1000
CODE_CT_WARM: Final = 0x6DD937       # 0110 1101 1101 1001 0011 0111

# Light dimmer: number of discrete brightness steps on the remote
BRIGHTNESS_STEPS: Final = 8

# Color temperature extremes (Kelvin)
COLOR_TEMP_WARM_K: Final = 3000   # warm white (lowest K / warmest)
COLOR_TEMP_COLD_K: Final = 6500   # cool white (highest K / coolest)
COLOR_TEMP_MID_K: Final = (COLOR_TEMP_WARM_K + COLOR_TEMP_COLD_K) // 2

# Fan speed count
FAN_SPEED_COUNT: Final = 3
