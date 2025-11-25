import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union

from .note_event import NoteEvent

PathLike = Union[str, Path]


def check_events_one_note_per_onset(
    events: Iterable[NoteEvent],
) -> Tuple[bool, Dict[float, int]]:
    """
    Check that in a list of NoteEvents, each onset has exactly one note.

    Returns:
        (ok, counts)
        ok    = True if all onsets have count == 1.
        counts = dict onset -> count of notes starting at that onset.
    """
    counts: Dict[float, int] = defaultdict(int)
    for e in events:
        counts[e.onset] += 1

    ok = all(count == 1 for count in counts.values())
    return ok, counts


def check_csv_one_note_per_onset(path: PathLike) -> Tuple[bool, Dict[float, int]]:
    """
    Same check, but reading NoteEvents from a CSV file (by onset field).
    """
    csv_path = Path(path)
    counts: Dict[float, int] = defaultdict(int)

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            onset = float(row["onset"])
            counts[onset] += 1

    ok = all(count == 1 for count in counts.values())
    return ok, counts
