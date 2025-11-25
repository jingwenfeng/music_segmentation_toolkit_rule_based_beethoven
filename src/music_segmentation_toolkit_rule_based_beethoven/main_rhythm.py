import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .note_event import NoteEvent


def group_by_onset(events: List[NoteEvent]) -> Dict[float, List[NoteEvent]]:
    """
    Group notes by onset time.
    Key = onset (float), value = list of NoteEvent starting at that time.
    """
    groups: Dict[float, List[NoteEvent]] = defaultdict(list)
    for ev in events:
        groups[ev.onset].append(ev)
    return dict(groups)


def get_soprano_bass(notes: List[NoteEvent]) -> Tuple[NoteEvent, NoteEvent]:
    """
    Return (top_note, bass_note) for a chord/group based on pitch.
    """
    top = max(notes, key=lambda n: n.pitch)
    bass = min(notes, key=lambda n: n.pitch)
    return top, bass


def smoothness(pitches: List[int]) -> float:
    """
    Compute simple 'smoothness' = sum of absolute pitch steps.
    Lower = smoother melodic line.
    """
    if len(pitches) < 2:
        return 0.0
    return sum(abs(pitches[i] - pitches[i - 1]) for i in range(1, len(pitches)))


def detect_primary_voice(groups: Dict[float, List[NoteEvent]]) -> str:
    """
    Decide whether the main line is more likely in the soprano or bass,
    based on which outer voice moves more smoothly.

    Returns "top" or "bass".
    """
    if not groups:
        return "top"

    onsets = sorted(groups.keys())
    top_line: List[int] = []
    bass_line: List[int] = []

    for onset in onsets:
        notes = groups[onset]
        top, bass = get_soprano_bass(notes)
        top_line.append(top.pitch)
        bass_line.append(bass.pitch)

    top_s = smoothness(top_line)
    bass_s = smoothness(bass_line)

    # Choose the smoother line (with some hysteresis).
    if top_s <= bass_s * 0.8:
        return "top"
    if bass_s <= top_s * 0.8:
        return "bass"
    # If similar, classical default: soprano-led.
    return "top"


def metric_strength(onset: float, beats_per_bar: int = 4) -> int:
    """
    Very rough metric strength estimate for simple meters.

    Returns:
        0 = weak, 1 = medium, 2 = strong.
    """
    if beats_per_bar <= 0:
        return 0

    pos = onset % beats_per_bar
    pos = round(pos * 2) / 2.0  # snap to nearest 0.5 beat

    if beats_per_bar == 4:
        if math.isclose(pos, 0.0, abs_tol=1e-3):
            return 2  # beat 1
        if math.isclose(pos, 2.0, abs_tol=1e-3):
            return 1  # beat 3
        return 0
    else:
        # fallback: only beat 1 strong
        if math.isclose(pos, 0.0, abs_tol=1e-3):
            return 2
        return 0


def score_note(
    note: NoteEvent,
    group: List[NoteEvent],
    primary_voice: str,
    prev_main: Optional[NoteEvent],
    beats_per_bar: int = 4,
    ornament_ratio: float = 0.25,
) -> float:
    """
    Assign a score to a note in its group based on fully rule-based heuristics.

    Higher score = more likely to be the 'main rhythm' note.
    """
    top, bass = get_soprano_bass(group)
    score = 0.0

    # 0. Grace notes are decorative.
    if note.is_grace:
        score -= 3.0

    # 1. Primary voice orientation (global).
    if primary_voice == "top" and note is top:
        score += 10.0
    if primary_voice == "bass" and note is bass:
        score += 10.0

    # 2. Outer voice preference.
    if note is top:
        score += 4.0
    if note is bass:
        score += 2.0

    # 3. Staff: prefer right-hand for melody in classical piano.
    if note.staff == "RH":
        score += 2.0

    # 4. Voice number (if known).
    if note.voice == 1:
        score += 2.0

    # 5. Duration + ornament filtering.
    max_dur = max((n.duration for n in group), default=0.0)
    if max_dur > 0 and note.duration < max_dur * ornament_ratio and not (
        note is top or note is bass
    ):
        # Very short inner note relative to others -> likely ornament.
        score -= 2.0
    else:
        # Longer notes are structurally more important.
        if note.duration >= 2.0:
            score += 4.0
        elif note.duration >= 1.0:
            score += 2.0

    # 6. Metric strength.
    score += metric_strength(note.onset, beats_per_bar=beats_per_bar)

    # 7. Melodic continuity with previous main note.
    if prev_main is not None:
        interval = abs(note.pitch - prev_main.pitch)
        if interval == 0:
            score += 4.0
        elif interval <= 2:
            score += 3.0
        elif interval <= 5:
            score += 1.0
        elif interval > 12:
            score -= 2.0

    return score


def select_main_rhythm(
    events: List[NoteEvent],
    beats_per_bar: int = 4,
) -> List[NoteEvent]:
    """
    Main public API: extract a single-note 'main rhythm' line.

    Guarantees:
      * For each onset where there were notes, keeps EXACTLY one note.
      * Never deletes all notes at a given time point.
    """
    if not events:
        return []

    groups = group_by_onset(events)
    onsets = sorted(groups.keys())
    primary_voice = detect_primary_voice(groups)

    result: List[NoteEvent] = []
    prev_main: Optional[NoteEvent] = None

    for onset in onsets:
        group = groups[onset]

        if len(group) == 1:
            chosen = group[0]
        else:
            best_note: Optional[NoteEvent] = None
            best_score = float("-inf")

            for note in group:
                s = score_note(
                    note=note,
                    group=group,
                    primary_voice=primary_voice,
                    prev_main=prev_main,
                    beats_per_bar=beats_per_bar,
                )
                if s > best_score:
                    best_score = s
                    best_note = note

            if best_note is None:
                # Failsafe: choose soprano.
                best_note, _ = get_soprano_bass(group)

            chosen = best_note

        result.append(chosen)
        prev_main = chosen

    return result
