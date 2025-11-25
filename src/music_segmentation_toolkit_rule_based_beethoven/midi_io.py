from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union

from mido import Message, MetaMessage, MidiFile, MidiTrack

from .note_event import NoteEvent

PathLike = Union[str, Path]


def midi_to_note_events(path: PathLike) -> Tuple[List[NoteEvent], int]:
    """
    Load a MIDI file and convert all note on/off pairs into NoteEvent objects.

    Returns:
        (events, ticks_per_beat)
    """
    midi_path = Path(path)
    mid = MidiFile(midi_path)
    tpb = mid.ticks_per_beat

    events: List[NoteEvent] = []

    for track in mid.tracks:
        abs_time_ticks = 0
        # (channel, pitch) -> start_tick
        active_notes: Dict[Tuple[int, int], int] = {}

        for msg in track:
            abs_time_ticks += msg.time

            if msg.is_meta:
                continue

            if msg.type == "note_on" and msg.velocity > 0:
                key = (msg.channel, msg.note)
                active_notes[key] = abs_time_ticks

            elif msg.type in ("note_off", "note_on") and msg.velocity == 0:
                key = (msg.channel, msg.note)
                if key not in active_notes:
                    continue  # unmatched note_off; skip

                start_tick = active_notes.pop(key)
                duration_ticks = abs_time_ticks - start_tick
                if duration_ticks <= 0:
                    duration_ticks = 1

                onset_beats = start_tick / tpb
                duration_beats = duration_ticks / tpb
                pitch = msg.note

                # Simple staff heuristic: high = RH, low = LH
                staff: Union[str, None] = "RH" if pitch >= 60 else "LH"

                events.append(
                    NoteEvent(
                        onset=onset_beats,
                        duration=duration_beats,
                        pitch=pitch,
                        staff=staff,
                        voice=None,
                        is_grace=False,
                        tie_start=False,
                        tie_stop=False,
                        measure=None,
                    )
                )

    events.sort(key=lambda e: e.onset)
    return events, tpb


def note_events_to_midi(
    events: Iterable[NoteEvent],
    path: PathLike,
    ticks_per_beat: int,
    tempo: int = 500_000,  # ~120 bpm
) -> None:
    """
    Convert NoteEvent objects back to a simple single-track MIDI file.
    """
    midi_path = Path(path)
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)

    # Add tempo meta event.
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))

    # Build absolute-tick events: (tick, kind, pitch)
    abs_events: List[Tuple[int, str, int]] = []
    for e in events:
        start_ticks = int(round(e.onset * ticks_per_beat))
        end_ticks = int(round((e.onset + e.duration) * ticks_per_beat))
        if end_ticks <= start_ticks:
            end_ticks = start_ticks + 1

        abs_events.append((start_ticks, "on", e.pitch))
        abs_events.append((end_ticks, "off", e.pitch))

    # Sort by time, then ensure note_off before note_on at same tick.
    abs_events.sort(key=lambda item: (item[0], 0 if item[1] == "off" else 1, item[2]))

    prev_tick = 0
    for tick, kind, pitch in abs_events:
        delta = tick - prev_tick
        prev_tick = tick

        if kind == "on":
            track.append(Message("note_on", note=pitch, velocity=80, time=delta, channel=0))
        else:
            track.append(Message("note_off", note=pitch, velocity=64, time=delta, channel=0))

    mid.save(midi_path)
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union

from mido import Message, MetaMessage, MidiFile, MidiTrack

from .note_event import NoteEvent

PathLike = Union[str, Path]


def midi_to_note_events(path: PathLike) -> Tuple[List[NoteEvent], int]:
    """
    Load a MIDI file and convert all note on/off pairs into NoteEvent objects.

    Returns:
        (events, ticks_per_beat)
    """
    midi_path = Path(path)
    mid = MidiFile(midi_path)
    tpb = mid.ticks_per_beat

    events: List[NoteEvent] = []

    for track in mid.tracks:
        abs_time_ticks = 0
        # (channel, pitch) -> start_tick
        active_notes: Dict[Tuple[int, int], int] = {}

        for msg in track:
            abs_time_ticks += msg.time

            if msg.is_meta:
                continue

            if msg.type == "note_on" and msg.velocity > 0:
                key = (msg.channel, msg.note)
                active_notes[key] = abs_time_ticks

            elif msg.type in ("note_off", "note_on") and msg.velocity == 0:
                key = (msg.channel, msg.note)
                if key not in active_notes:
                    continue  # unmatched note_off; skip

                start_tick = active_notes.pop(key)
                duration_ticks = abs_time_ticks - start_tick
                if duration_ticks <= 0:
                    duration_ticks = 1

                onset_beats = start_tick / tpb
                duration_beats = duration_ticks / tpb
                pitch = msg.note

                # Simple staff heuristic: high = RH, low = LH
                staff: Union[str, None] = "RH" if pitch >= 60 else "LH"

                events.append(
                    NoteEvent(
                        onset=onset_beats,
                        duration=duration_beats,
                        pitch=pitch,
                        staff=staff,
                        voice=None,
                        is_grace=False,
                        tie_start=False,
                        tie_stop=False,
                        measure=None,
                    )
                )

    events.sort(key=lambda e: e.onset)
    return events, tpb


def note_events_to_midi(
    events: Iterable[NoteEvent],
    path: PathLike,
    ticks_per_beat: int,
    tempo: int = 500_000,  # ~120 bpm
) -> None:
    """
    Convert NoteEvent objects back to a simple single-track MIDI file.
    """
    midi_path = Path(path)
    mid = MidiFile(ticks_per_beat=ticks_per_beat)
    track = MidiTrack()
    mid.tracks.append(track)

    # Add tempo meta event.
    track.append(MetaMessage("set_tempo", tempo=tempo, time=0))

    # Build absolute-tick events: (tick, kind, pitch)
    abs_events: List[Tuple[int, str, int]] = []
    for e in events:
        start_ticks = int(round(e.onset * ticks_per_beat))
        end_ticks = int(round((e.onset + e.duration) * ticks_per_beat))
        if end_ticks <= start_ticks:
            end_ticks = start_ticks + 1

        abs_events.append((start_ticks, "on", e.pitch))
        abs_events.append((end_ticks, "off", e.pitch))

    # Sort by time, then ensure note_off before note_on at same tick.
    abs_events.sort(key=lambda item: (item[0], 0 if item[1] == "off" else 1, item[2]))

    prev_tick = 0
    for tick, kind, pitch in abs_events:
        delta = tick - prev_tick
        prev_tick = tick

        if kind == "on":
            track.append(Message("note_on", note=pitch, velocity=80, time=delta, channel=0))
        else:
            track.append(Message("note_off", note=pitch, velocity=64, time=delta, channel=0))

    mid.save(midi_path)
