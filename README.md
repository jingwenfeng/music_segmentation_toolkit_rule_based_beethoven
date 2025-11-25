# music_segmentation_toolkit_rule_based_beethoven

Rule-based tools for analyzing piano MIDI in a **Beethoven / Classical** style.

The toolkit focuses on:

- extracting a **single-note “main rhythm” line** from dense piano textures
  (one note per time point, like a clear melody line),
- working directly with **MIDI**, **CSV**, and **simple Python objects**.

No AI / GPT / machine learning is used – everything is **fully rule-based and deterministic**, so you can see and modify every decision.

## 1. Project layout

This project uses the modern **src/** layout:

music_segmentation_toolkit_rule_based_beethoven/
├─ pyproject.toml
├─ README.md
├─ src/
│  └─ music_segmentation_toolkit_rule_based_beethoven/
│     ├─ __init__.py
│     ├─ note_event.py
│     ├─ main_rhythm.py
│     ├─ midi_io.py
│     ├─ csv_io.py
│     ├─ validation.py
│     ├─ cli.py
│     └─ example.ipynb


The main package lives inside:

src/music_segmentation_toolkit_rule_based_beethoven/

so after installation you import it like:

import music_segmentation_toolkit_rule_based_beethoven

## 2. Installation

Clone and install in editable mode:

pip install -e .

## 3. Quickstart

Example usage:

from music_segmentation_toolkit_rule_based_beethoven import (
    midi_to_note_events,
    select_main_rhythm,
    save_csv,
    note_events_to_midi,
)

events, tpb = midi_to_note_events("TEST/sonate-no-8-pathetique-3rd-movement.mid")
main_line = select_main_rhythm(events, beats_per_bar=2)
save_csv(main_line, "TEST/pathetique_main_rhythm.csv")
note_events_to_midi(main_line, "TEST/pathetique_main_rhythm.mid", tpb)

## 4. Core concepts

### NoteEvent

A dataclass describing a single note in the performance.

## 5. API overview

Includes midi_io, csv_io, main_rhythm, validation, cli.

## 6. Rules Explained 

------------------------------------------------------------
RULE 1 — GROUP NOTES BY THEIR ONSET TIME
------------------------------------------------------------

Purpose:

Identify which notes begin at the exact same moment.

Explanation:

If multiple notes share the same start time (same onset value), they belong to the same “time slice.” This is equivalent to a vertical harmonic moment in a score.

Example:

Time = 2.0 beats

Notes = [60, 64, 67]

These are all part of the same chord or simultaneous gesture.

------------------------------------------------------------
RULE 2 — IDENTIFY SOPRANO AND BASS (OUTER VOICES)
------------------------------------------------------------

Purpose:

Classical music assigns special importance to the highest and lowest notes at any moment.

Soprano = highest pitch in the slice.

Bass = lowest pitch in the slice.

Reason:

In Classical/Beethoven style:

The soprano is the most likely location of the melody.

The bass carries foundational harmonic motion or rhythmic drive.

Inner voices rarely contain the main idea.

------------------------------------------------------------
RULE 3 — DETERMINE WHETHER THE MAIN LINE IS SOPRANO-LED OR BASS-LED
------------------------------------------------------------

Purpose:

Different Beethoven passages are led by different voices.

Method:

Track the soprano over time → measure its smoothness (sum of pitch intervals).

Track the bass over time → measure its smoothness.

Whichever line moves with smaller average jumps is considered the globally “leading” line (the expected main voice).

If soprano is smoother → soprano-led.

If bass is smoother → bass-led.

------------------------------------------------------------
RULE 4 — SCORE EVERY NOTE ACCORDING TO CLASSICAL LOGIC
------------------------------------------------------------

This is the core. Each note in a time slice is given a numerical score. The note with the highest score becomes the main rhythm note for that moment.

Below are all scoring factors, written in plain English:

4A. Outer Voice Priority

- If soprano: add large bonus.
- If bass: add moderate bonus.

Inner voices have no special priority.

4B. Staff / Hand Logic

- If note is in right hand (RH): add bonus.

Rationale: Classical piano melody is usually in the right hand.

4C. Duration Importance

- Long notes → add score.
- Very short notes → subtract score.

Rationale: Long tones represent structural melody; short ones are often ornamental.

4D. Metric Strength

- Notes on strong beats get added score.

Examples:

Beat 1 in 4/4 = strongest.

Beat 3 in 4/4 = medium.

Weak beats = no bonus.

4E. Melodic Continuity

- If note matches previous main pitch → large bonus.
- If within 1–2 semitones → medium bonus.
- If within 3–5 semitones → small bonus.
- If huge leap (>12 semitones) → penalty.

This mimics how real melodies move: stepwise or small intervals.

4F. Ornament Suppression

If a note is extremely short compared to others in the same time slice, and it is not soprano or bass, subtract bonus.

Prevents selecting decorative inner notes.

4G. Voice Number Priority

If voice == 1 (from notation or score import), add bonus.
Voice 1 typically denotes primary line.

------------------------------------------------------------
RULE 5 — SELECT HIGHEST-SCORING NOTE PER TIME SLICE
------------------------------------------------------------

After scoring, the note with the highest score is selected for that onset.

This guarantees:

- One note per time.
- A coherent melodic line.
- Classical-like behavior.

------------------------------------------------------------
RULE 6 — GUARANTEE EXACTLY ONE NOTE PER ONSET
------------------------------------------------------------

Regardless of how many notes appear at a time (2, 5, 12…), exactly ONE must be chosen.

This ensures:

- Rhythm is preserved.
- Output is usable for segmentation.
- No time slice is lost.

------------------------------------------------------------
RESULT OF ALL RULES COMBINED
------------------------------------------------------------

The output is a clear Beethoven-style melodic skeleton:

- Smooth melodic motion.
- Priority to outer voices.
- Rhythmically meaningful.
- Ornament-free.
- Beat-structured.
- Classical phrase logic preserved.

This main line can then be used for:

- Sentence segmentation
- Thematic/motivic analysis
- Structural reduction
- Machine-readable melodic shape



