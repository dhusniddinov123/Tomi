"""Prepare audio dataset: resample to 16kHz mono, trim silence, normalize volume.

Requirements: librosa, soundfile, numpy

Usage:
    python tools/prepare_dataset.py --input data --output prepared

This script scans `input/positive` and `input/negative`, converts files and writes to output dirs.
"""
import argparse
from pathlib import Path
import librosa
import soundfile as sf
import numpy as np


def trim_silence(y, top_db=20):
    # Use librosa.effects.trim
    import librosa
    yt, index = librosa.effects.trim(y, top_db=top_db)
    return yt


def normalize_audio(y):
    # Normalize to -3 dBFS
    peak = np.max(np.abs(y))
    if peak == 0:
        return y
    target = 0.707
    y = y * (target / peak)
    return y


def process_file(src: Path, dst: Path, sr=16000):
    y, _ = librosa.load(str(src), sr=sr, mono=True)
    y = trim_silence(y, top_db=20)
    y = normalize_audio(y)
    sf.write(str(dst), y, sr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='data')
    parser.add_argument('--output', type=str, default='prepared')
    parser.add_argument('--sr', type=int, default=16000)
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    for label in ('positive', 'negative'):
        src_dir = inp / label
        dst_dir = out / label
        dst_dir.mkdir(parents=True, exist_ok=True)
        if not src_dir.exists():
            print(f"Source dir missing: {src_dir}")
            continue
        for f in src_dir.glob('*.wav'):
            dst = dst_dir / f.name
            try:
                process_file(f, dst, sr=args.sr)
                print(f"Processed {f} -> {dst}")
            except Exception as e:
                print(f"Failed {f}: {e}")
