import csv
from pathlib import Path
from typing import List, Optional, Union

from .note_event import NoteEvent

PathLike = Union[str, Path]


def save_csv(events: List[NoteEvent], path: PathLike) -> None:
    """
    Save a list of NoteEvents to CSV.

    Columns:
        onset, duration, pitch, staff, voice, is_grace, tie_start, tie_stop, measure
    """
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "onset",
            "duration",
            "pitch",
            "staff",
            "voice",
            "is_grace",
            "tie_start",
            "tie_stop",
            "measure"
        ])
        for e in events:
            writer.writerow([
                f"{e.onset:.6f}",
                f"{e.duration:.6f}",
                e.pitch,
                e.staff if e.staff is not None else "",
                e.voice if e.voice is not None else "",
                int(e.is_grace),
                int(e.tie_start),
                int(e.tie_stop),
                e.measure if e.measure is not None else "",
            ])


def load_csv(path: PathLike) -> List[NoteEvent]:
    """
    Load NoteEvents from a CSV file produced by save_csv().
    """
    csv_path = Path(path)
    events: List[NoteEvent] = []

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            onset = float(row["onset"])
            duration = float(row["duration"])
            pitch = int(row["pitch"])

            staff = row["staff"] if row["staff"] else None
            voice = int(row["voice"]) if row["voice"] else None

            is_grace = bool(int(row["is_grace"]))
            tie_start = bool(int(row["tie_start"]))
            tie_stop = bool(int(row["tie_stop"]))

            measure = int(row["measure"]) if row["measure"] else None

            events.append(
                NoteEvent(
                    onset=onset,
                    duration=duration,
                    pitch=pitch,
                    staff=staff,
                    voice=voice,
                    is_grace=is_grace,
                    tie_start=tie_start,
                    tie_stop=tie_stop,
                    measure=measure,
                )
            )

    events.sort(key=lambda n: n.onset)
    return events
