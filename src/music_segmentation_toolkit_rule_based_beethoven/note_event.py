from dataclasses import dataclass
from typing import Optional


@dataclass
class NoteEvent:
    """
    Basic symbolic note representation used throughout the library.
    """
    onset: float          # time in beats or seconds
    duration: float       # duration in same units as onset
    pitch: int            # MIDI 0-127
    staff: Optional[str]  # 'RH', 'LH', or None
    voice: Optional[int]  # voice index, or None
    is_grace: bool = False
    tie_start: bool = False
    tie_stop: bool = False
    measure: Optional[int] = None
