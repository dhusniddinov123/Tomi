"""Generate mel-spectrogram tensors from prepared audio files.

Saves spectrograms as numpy .npz files with labels. These can be loaded
by the training script.

Requirements: librosa, numpy

Usage:
    python tools/generate_spectrograms.py --input prepared --output features
"""
import argparse
from pathlib import Path
import numpy as np
import librosa


def file_to_mel(path, sr=16000, n_mels=64, n_fft=1024, hop_length=256):
    y, _ = librosa.load(path, sr=sr, mono=True)
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.power_to_db(S, ref=np.max)
    return S_db.astype(np.float32)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='prepared')
    parser.add_argument('--output', type=str, default='features')
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    for label in ('positive', 'negative'):
        folder = inp / label
        if not folder.exists():
            print(f"Skipping missing folder {folder}")
            continue
        for f in folder.glob('*.wav'):
            try:
                mel = file_to_mel(str(f))
                out_file = out / (f.stem + '.npz')
                np.savez_compressed(out_file, mel=mel, label=(1 if label=='positive' else 0))
                print(f"Saved {out_file}")
            except Exception as e:
                print(f"Failed {f}: {e}")
