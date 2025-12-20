"""Offline speech recognition module using Vosk.

Works completely offline - no internet required.
Recognizes user commands after wake word detection.
"""

import json
import pyaudio

try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

from core.logger import get_logger
from core.config import config

logger = get_logger("Listen")

# Vosk recognizer (lazy loaded)
_recognizer = None
_model = None


def _load_model():
    """Load Vosk model for speech recognition."""
    global _model, _recognizer
    
    if not VOSK_AVAILABLE:
        return False
    
    try:
        import os
        from pathlib import Path
        
        # Find model path
        model_path = config.get("vosk_model_path", None)
        
        if not model_path:
            possible_paths = [
                Path.home() / ".cache" / "vosk" / "model-en-us",
                Path.home() / "vosk-models" / "model-en-us",
                Path("models") / "model-en-us",
                Path("vosk-models") / "model-en-us",
            ]
            
            for path in possible_paths:
                if path.exists():
                    model_path = str(path)
                    break
        
        if not model_path or not os.path.exists(model_path):
            model_path = "model-en-us"
        
        _model = vosk.Model(model_path)
        _recognizer = vosk.KaldiRecognizer(_model, 16000)
        
        logger.info("Vosk model loaded for offline listening")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load Vosk model: {e}")
        return False


def listen():
    """
    Listen for user command after wake word (offline mode).
    
    Returns:
        dict: Status dictionary with keys:
            - status: "success", "silence", or "error"
            - text: Recognized text (if status is "success")
            - error: Error message (if status is "error")
    """
    if not VOSK_AVAILABLE:
        return {
            "status": "error",
            "error": "Vosk not installed"
        }
    
    # Load model on first use
    if _recognizer is None:
        if not _load_model():
            return {
                "status": "error",
                "error": "Could not load speech model"
            }
    
    try:
        p = pyaudio.PyAudio()
        
        # Audio device
        device_index = config.get("audio_device_index", None)
        
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=4096
        )
        
        stream.start_stream()
        logger.info("Listening for command (offline)...")
        
        # Listen for user command with timeout
        listen_timeout = config.get("listen_timeout", 10)
        frames_to_process = int(16000 / 4096 * listen_timeout)  # ~10 seconds
        
        full_result = ""
        
        for _ in range(frames_to_process):
            data = stream.read(4096, exception_on_overflow=False)
            
            if _recognizer.AcceptWaveform(data):
                # Final result
                result = json.loads(_recognizer.Result())
                text = " ".join(result.get("result", [])).strip()
                
                if text:
                    full_result = text
                    logger.info(f"Recognized: {text}")
                    break
            else:
                # Partial result (for feedback)
                partial = json.loads(_recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text and not full_result:
                    full_result = partial_text
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if full_result:
            return {
                "status": "success",
                "text": full_result
            }
        else:
            logger.info("No speech detected (silence)")
            return {
                "status": "silence"
            }
        
    except Exception as e:
        logger.error(f"Error in offline listening: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


def test_microphone():
    """Test if microphone is accessible."""
    # Guard: ensure Vosk + PyAudio are installed before trying to open a stream
    if not VOSK_AVAILABLE:
        logger.error("Microphone test unavailable: Vosk not installed")
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

        logger.info("Microphone test successful")
        return True
    except Exception as e:
        logger.error(f"Microphone test failed: {e}")
        return False


def is_offline_mode():
    """Check if we're using offline speech recognition."""
    return VOSK_AVAILABLE
