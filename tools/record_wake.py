"""Record wake-word samples into `data/positive` and negatives into `data/negative`.

Usage (PowerShell / cmd after activating venv):
    python tools/record_wake.py --positive --count 20 --duration 1
    python tools/record_wake.py --negative --count 50 --duration 2

This script uses `sounddevice` + `soundfile` if available, otherwise falls back to PyAudio.
Recorded audio is saved as 16kHz mono WAV files ready for processing.
"""
import argparse
import os
from pathlib import Path
import time
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import sounddevice as sd
    import soundfile as sf
    SD_AVAILABLE = True
except Exception:
    SD_AVAILABLE = False


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def record_with_sounddevice(path: Path, duration: float, samplerate=16000):
    print(f"Recording to {path} for {duration}s")
    data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    sf.write(str(path), data, samplerate)


def record_loop(out_dir: Path, count: int, duration: float, prefix: str):
    ensure_dir(out_dir)
    for i in range(count):
        filename = out_dir / f"{prefix}_{int(time.time())}_{i}.wav"
        print(f"Prepare to record sample {i+1}/{count}. Press Enter to start...")
        input()
        try:
            if SD_AVAILABLE:
                record_with_sounddevice(filename, duration)
            else:
                raise RuntimeError("sounddevice not available. Install sounddevice+soundfile or PyAudio fallback not implemented.")
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Recording failed: {e}")
        time.sleep(0.3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--positive', action='store_true', help='Record wake-word (positive) samples')
    parser.add_argument('--negative', action='store_true', help='Record negative / background samples')
    parser.add_argument('--count', type=int, default=20)
    parser.add_argument('--duration', type=float, default=1.0)
    parser.add_argument('--out', type=str, default='data')
    args = parser.parse_args()

    out = Path(args.out)
    if args.positive:
        record_loop(out / 'positive', args.count, args.duration, 'pos')
    elif args.negative:
        record_loop(out / 'negative', args.count, args.duration, 'neg')
    else:
        print('Nothing selected. Use --positive or --negative')
