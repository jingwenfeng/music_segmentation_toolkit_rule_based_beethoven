import argparse
from pathlib import Path

from .csv_io import save_csv
from .main_rhythm import select_main_rhythm
from .midi_io import midi_to_note_events, note_events_to_midi
from .validation import check_events_one_note_per_onset


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract a rule-based 'main rhythm' line from a piano MIDI (Beethoven-style)."
    )
    parser.add_argument("midi_in", help="Path to input MIDI file.")
    parser.add_argument(
        "--csv-out",
        help="Optional path to save the main rhythm line as CSV.",
        default=None,
    )
    parser.add_argument(
        "--midi-out",
        help="Optional path to save the main rhythm line as MIDI.",
        default=None,
    )
    parser.add_argument(
        "--beats-per-bar",
        type=int,
        default=4,
        help="Beats per bar (time signature top number) for metric weighting (default: 4).",
    )

    args = parser.parse_args()

    midi_in = Path(args.midi_in)

    # 1. Load MIDI
    events, tpb = midi_to_note_events(midi_in)

    # 2. Extract main rhythm
    main_line = select_main_rhythm(events, beats_per_bar=args.beats_per_bar)

    # 3. Validate one note per onset (should always be True)
    ok, counts = check_events_one_note_per_onset(main_line)
    if not ok:
        print("WARNING: some onsets have != 1 note in the main line (unexpected).")

    # 4. Decide output paths
    if args.csv_out is not None:
        csv_out = Path(args.csv_out)
    else:
        csv_out = midi_in.with_name(midi_in.stem + "_main_rhythm.csv")

    if args.midi_out is not None:
        midi_out = Path(args.midi_out)
    else:
        midi_out = midi_in.with_name(midi_in.stem + "_main_rhythm.mid")

    # 5. Save CSV + MIDI
    save_csv(main_line, csv_out)
    note_events_to_midi(main_line, midi_out, tpb)

    print(f"Input MIDI: {midi_in}")
    print(f"Main rhythm CSV:  {csv_out}")
    print(f"Main rhythm MIDI: {midi_out}")
