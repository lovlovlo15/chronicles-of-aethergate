# Sounds for Chronicles of Aether Gate

This folder contains sound effects used by the game. The SoundManager looks here first.

- Preferred filenames (one per event):
  - `menu.(wav|ogg)` – UI/menu blip
  - `pickup.(wav|ogg)` – item pickup
  - `attack.(wav|ogg)` – player attack
  - `heal.(wav|ogg)` – healing
  - `victory.(wav|ogg)` – win fanfare
  - `defeat.(wav|ogg)` – defeat sting

If no files are present, the game will generate simple tone WAVs here on first use, so you’ll always have something audible without external downloads.

## Adding your own sounds
Use short, small files (WAV/OGG). Creative Commons Zero (CC0) sounds are recommended.

- Place your files here with the exact names above.
- Format: 16-bit PCM WAV or OGG (mono recommended).
- Keep durations short (50–1000 ms) for snappy UX.

### Background music
- Place your music as `background.mp3` in this folder. This track will loop while the game runs.
- Make sure you have the right to use the track and include attribution if required (e.g., CC BY 4.0).

## Suggested sources (CC0 / permissive)
- https://freesound.org (filter by License: Creative Commons 0)
- https://pixabay.com/sound-effects/
- https://mixkit.co/free-sound-effects/

Note: Don’t commit proprietary or non-redistributable assets unless you have rights to do so.
