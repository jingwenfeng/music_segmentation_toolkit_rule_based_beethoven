"""
music_segmentation_toolkit_rule_based_beethoven

Rule-based main rhythm extraction for classical piano MIDI
(Beethoven-focused heuristics).
"""

from .note_event import NoteEvent
from .main_rhythm import (
    group_by_onset,
    get_soprano_bass,
    select_main_rhythm,
    detect_primary_voice,
)
from .midi_io import midi_to_note_events, note_events_to_midi
from .csv_io import save_csv, load_csv
from .validation import check_events_one_note_per_onset, check_csv_one_note_per_onset

__all__ = [
    "NoteEvent",
    "group_by_onset",
    "get_soprano_bass",
    "select_main_rhythm",
    "detect_primary_voice",
    "midi_to_note_events",
    "note_events_to_midi",
    "save_csv",
    "load_csv",
    "check_events_one_note_per_onset",
    "check_csv_one_note_per_onset",
]

__version__ = "0.1.0"
