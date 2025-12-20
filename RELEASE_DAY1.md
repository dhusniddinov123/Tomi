# Tomi — Day 1 Release Notes

Summary:

- Implemented offline speech recognition using Vosk (`core/wake_offline.py`, `core/listen_offline.py`).
- Added a background TTS worker to prevent pyttsx3 run-loop errors (`core/speak.py`).
- Improved PyAudio handling and added `sounddevice` fallback for input device issues.
- Automated Vosk model setup and added `setup_vosk.py` helper.
- Added tools for dataset collection and testing (`tools/*`).
- Tuned `config/settings.json` defaults for Day‑1 testing.

Suggested commit message (already used):

"Day-1: Offline Vosk, TTS worker, audio/device fixes and tuning"

Suggested PR description / comments:

- Implemented offline-first speech stack with Vosk and a robust fallback path for audio I/O.
- Replaced blocking TTS calls with a background worker to avoid runtime errors.
- Added device detection and test utilities to help users select working audio devices.
- Updated `config/settings.json` with recommended defaults for Windows (16000 sample rate for Vosk, energy tuning).

Notes for pushing:

- The repository was initialized locally and committed. To push, ensure network access to GitHub and that your SSH key is added to your GitHub account (or use HTTPS with credentials).

Contact:

- GitHub: dhusniddinov123
- Email: dostonxusniddinov123456@gmail.com
