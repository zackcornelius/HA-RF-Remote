"""OOK command factory for the RF Ceiling Fan remote.

Each 24-bit code is encoded using an EV1527-like pulse-width modulation:
  • Sync pulse : 1 T high + 31 T low  (T = 350 μs)
  • '1' bit    : 3 T high + 1 T low
  • '0' bit    : 1 T high + 3 T low

The resulting list of signed integers is passed directly to OOKCommand,
where positive values are carrier-on durations and negative values are
carrier-off durations (in microseconds).
"""

from rf_protocols.commands.ook import OOKCommand

from .const import (
    BIT0_OFF_US,
    BIT0_ON_US,
    BIT1_OFF_US,
    BIT1_ON_US,
    FREQUENCY,
    SYNC_OFF_US,
    SYNC_ON_US,
)

_NUM_BITS = 24


def make_command(code: int) -> OOKCommand:
    """Return an OOKCommand for the given 24-bit RF code."""
    timings: list[int] = [SYNC_ON_US, -SYNC_OFF_US]
    for bit_index in range(_NUM_BITS - 1, -1, -1):
        if (code >> bit_index) & 1:
            timings.extend([BIT1_ON_US, -BIT1_OFF_US])
        else:
            timings.extend([BIT0_ON_US, -BIT0_OFF_US])
    return OOKCommand(frequency=FREQUENCY, timings=timings)
