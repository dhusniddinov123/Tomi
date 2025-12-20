"""Offline wake-word detector using Vosk.

Works completely offline without internet.
No dependency on Google Speech API.
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    import vosk
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

import sounddevice as sd

from core.logger import get_logger
from core.config import config

# Add cooldown globals near top
WAKE_COOLDOWN = config.get("wake_cooldown", 1.5)
_last_wake_ts = 0.0

logger = get_logger("Wake")

# debug flag from config
debug_wake = config.get("debug_wake", False)

# Initialize Vosk model
_model = None
_recognizer = None


def _load_model():
    """Load Vosk model from disk."""
    global _model, _recognizer
    
    if not VOSK_AVAILABLE:
        logger.error("Vosk not installed - install with: pip install vosk pocketsphinx")
        return False
    
    try:
        # Model path - can be customized in config
        model_path = config.get("vosk_model_path", None)
        
        if not model_path:
            # Try to find model in common locations
            possible_paths = [
                Path.home() / ".cache" / "vosk" / "model-en-us",
                Path.home() / "vosk-models" / "model-en-us",
                Path("models") / "model-en-us",
                Path("vosk-models") / "model-en-us",
            ]
            
            for path in possible_paths:
                if path.exists():
                    model_path = str(path)
                    logger.info(f"Found Vosk model at: {model_path}")
                    break
        
        if not model_path or not os.path.exists(model_path):
            logger.warning("Vosk model not found.")
            # Attempt to run the setup script once to fetch the model non-interactively
            setup_script = Path(__file__).resolve().parents[1] / 'setup_vosk.py'
            if setup_script.exists():
                logger.info("Attempting to download Vosk model via setup_vosk.py (non-interactive)...")
                try:
                    import subprocess
                    # Use --yes to default to small model
                    subprocess.run([sys.executable, str(setup_script), '--yes'], check=True)
                except Exception as e:
                    logger.warning(f"Automated model download failed: {e}")

            # After attempting download, look for the standard model location
            model_path = Path('models') / 'model-en-us'
            if not model_path.exists():
                logger.warning("Vosk model still not found after automated download attempt.")
                return False
        
        _model = vosk.Model(str(model_path))
        _recognizer = vosk.KaldiRecognizer(_model, 16000)
        _recognizer.SetWords(config.get("wake_words", ["hey tomi", "hi tomi"]))
        
        logger.info("Vosk model loaded successfully (OFFLINE MODE)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load Vosk model: {e}")
        return False


def listen_for_wake_word():
    """
    Listen for wake word using offline Vosk recognition.
    
    Returns:
        bool: True if wake word detected, False otherwise
    """
    global _last_wake_ts
    if not VOSK_AVAILABLE:
        logger.error("Vosk not available - cannot detect wake words offline")
        return False
    
    # Load model on first use
    if _model is None:
        if not _load_model():
            return False
    
    p = None
    stream = None
    use_sounddevice = False
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_index = config.get("audio_device_index", None)
        rate = int(config.get("vosk_sample_rate", 16000))
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                frames_per_buffer=4096,
                input_device_index=device_index,
            )
            logger.debug("Using PyAudio input (device=%s rate=%s)", device_index, rate)
        except OSError as e:
            logger.warning("PyAudio open failed (device=%s, rate=%s): %s", device_index, rate, e)
            # fall back to sounddevice
            use_sounddevice = True
    except Exception as e:
        logger.debug("PyAudio not usable, will use sounddevice: %s", e)
        use_sounddevice = True

    if use_sounddevice:
        # use sounddevice RawInputStream (matches debug_vosk)
        device_index = config.get("audio_device_index", None)
        rate = int(config.get("vosk_sample_rate", 16000))
        try:
            logger.info("Falling back to sounddevice input (device=%s rate=%s)", device_index, rate)
            with sd.RawInputStream(samplerate=rate, blocksize=4096, dtype='int16',
                                   channels=1, device=device_index) as sdstream:
                while True:
                    data, _ = sdstream.read(4096)
                    try:
                        b = bytes(data)
                    except Exception:
                        b = data.tobytes() if hasattr(data, "tobytes") else bytes(data)
                    if _recognizer.AcceptWaveform(b):
                        result = json.loads(_recognizer.Result())

                        # Normalize Vosk output into a single string
                        words = result.get("result", [])
                        if isinstance(words, list):
                            parts = []
                            for item in words:
                                if isinstance(item, dict):
                                    w = item.get('word') or item.get('text') or ''
                                else:
                                    w = str(item)
                                w = w.strip()
                                if w:
                                    parts.append(w)
                            recognized = " ".join(parts).lower()
                        else:
                            recognized = (result.get('text') or str(words)).lower()

                        try:
                            if debug_wake:
                                logger.debug("Wake recognizer heard: %s", recognized)

                            # Check for wake words
                            wake_words = config.get("wake_words", ["hey tomi", "hi tomi"]) or []
                            for w in wake_words:
                                if w and w.lower() in recognized:
                                    now = time.time()
                                    if now - _last_wake_ts < WAKE_COOLDOWN:
                                        logger.debug("Wake ignored due to cooldown (%.2fs left)", WAKE_COOLDOWN - (now - _last_wake_ts))
                                        return False
                                    _last_wake_ts = now
                                    logger.info("Wake word detected (offline): %s", w)
                                    # sd.RawInputStream context will close automatically
                                    return True
                        except Exception as e:
                            logger.error("Error processing Vosk result: %s", e, exc_info=True)
        except Exception as e:
            logger.error("Sounddevice input failed: %s", e, exc_info=True)
            return False
    else:
        # existing PyAudio read loop (unchanged)
        try:
            while True:
                data = stream.read(4096, exception_on_overflow=False)

                if _recognizer.AcceptWaveform(data):
                    result = json.loads(_recognizer.Result())
                    # Vosk 'result' is usually a list of dicts with 'word' keys; the full text may also be
                    # available under result.get('text'). Normalize both cases into a string.
                    text = result.get("result", [])

                    try:
                        if isinstance(text, list):
                            parts = []
                            for item in text:
                                if isinstance(item, dict):
                                    w = item.get('word') or item.get('text') or ''
                                else:
                                    w = str(item)
                                w = w.strip()
                                if w:
                                    parts.append(w)
                            recognized = " ".join(parts).lower()
                        else:
                            # Fallback to top-level text field or string conversion
                            recognized = (result.get('text') or str(text)).lower()

                        if debug_wake:
                            logger.debug(f"Wake recognizer heard: {recognized}")

                        # Check for wake words
                        wake_words = config.get("wake_words", ["hey tomi", "hi tomi"]) or []
                        for w in wake_words:
                            if w and w.lower() in recognized:
                                now = time.time()
                                if now - _last_wake_ts < WAKE_COOLDOWN:
                                    logger.debug("Wake ignored due to cooldown (%.2fs left)", WAKE_COOLDOWN - (now - _last_wake_ts))
                                    return False
                                _last_wake_ts = now
                                logger.info("Wake word detected (offline): %s", w)
                                stream.stop_stream()
                                stream.close()
                                p.terminate()
                                return True
                    except Exception as e:
                        logger.error(f"Error processing Vosk result: {e}", exc_info=True)
        finally:
            try:
                stream.stop_stream(); stream.close()
            except Exception:
                pass
            try:
                p.terminate()
            except Exception:
                pass
        
        return False


def test_microphone():
    """Test if microphone is accessible."""
    # Guard: if Vosk/PyAudio are not available, return a clear failure
    if not VOSK_AVAILABLE:
        logger.error("Microphone test unavailable: Vosk or PyAudio not installed")
        return False

    try:
        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4096
        )

        stream.start_stream()
        stream.stop_stream()
        stream.close()
        p.terminate()

        logger.info("Microphone test successful (OFFLINE MODE)")
        return True
    except Exception as e:
        logger.error(f"Microphone test failed: {e}")
        return False


def is_offline_mode():
    """Check if we're using offline speech recognition."""
    return VOSK_AVAILABLE
