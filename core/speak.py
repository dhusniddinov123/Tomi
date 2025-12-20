"""Text-to-speech module for Tomi AI Assistant.

Handles voice output using pyttsx3.
"""

import threading
import queue
import atexit
import pyttsx3
from core.logger import get_logger
from core.config import config

logger = get_logger("Speak")


class _TTSWorker:
    def __init__(self):
        self._q = queue.Queue()
        self._engine = None
        try:
            self._engine = pyttsx3.init()
            # Apply config
            try:
                rate = config.get("tts_rate", None)
                if rate is not None:
                    self._engine.setProperty("rate", rate)
                vol = config.get("tts_volume", None)
                if vol is not None:
                    self._engine.setProperty("volume", vol)
                voice = config.get("tts_voice", None)
                if voice:
                    try:
                        self._engine.setProperty("voice", voice)
                    except Exception:
                        logger.debug("Requested voice not available: %s", voice)
            except Exception as e:
                logger.debug("TTS engine config apply failed: %s", e)

            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self._engine = None

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="TTSWorker")
        self._thread.start()
        atexit.register(self.stop)

    def _run(self):
        while self._running:
            try:
                item = self._q.get()
                if item is None:
                    break
                text = str(item)
                if not text:
                    self._q.task_done()
                    continue
                try:
                    if self._engine is None:
                        print(f"Tomi: {text}")
                    else:
                        self._engine.say(text)
                        self._engine.runAndWait()
                except Exception as e:
                    logger.error("Error during TTS run: %s", e, exc_info=True)
                finally:
                    self._q.task_done()
            except Exception as e:
                logger.error("TTS worker loop error: %s", e, exc_info=True)

    def speak(self, text):
        if not text:
            return
        try:
            self._q.put(text)
        except Exception as e:
            logger.error("Failed to queue TTS text: %s", e)

    def stop(self):
        self._running = False
        try:
            self._q.put(None)
        except Exception:
            pass


# Single global worker
_tts_worker = _TTSWorker()


def speak(text):
    """Enqueue text for TTS (non-blocking)."""
    logger.info("Speaking: %s", text)
    if _tts_worker is None:
        print(f"Tomi: {text}")
        return
    _tts_worker.speak(text)


def list_voices():
    """List available voices from the engine."""
    if _tts_worker is None or _tts_worker._engine is None:
        return []
    try:
        voices = _tts_worker._engine.getProperty("voices")
        return [(v.id, getattr(v, 'name', '')) for v in voices]
    except Exception as e:
        logger.error("Error listing voices: %s", e)
        return []


def set_voice(voice_id):
    """Set the voice by ID on the TTS engine."""
    if _tts_worker is None or _tts_worker._engine is None:
        return False
    try:
        _tts_worker._engine.setProperty("voice", voice_id)
        logger.info("Voice changed to: %s", voice_id)
        return True
    except Exception as e:
        logger.error("Error setting voice: %s", e)
        return False

