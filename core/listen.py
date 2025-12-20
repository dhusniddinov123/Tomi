"""Speech recognition module for Tomi AI Assistant.

Handles listening to user commands after wake word detection.
"""

import speech_recognition as sr
from core.logger import get_logger
from core.config import config

logger = get_logger("Listen")

# Initialize recognizer and microphone
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Load configuration
LISTEN_TIMEOUT = config.get("listen_timeout", 10)
PHRASE_TIME_LIMIT = config.get("listen_phrase_limit", 10)
AMBIENT_DURATION = config.get("ambient_noise_duration", 1)


def listen():
    """
    Listen for user command after wake word detection.
    
    Returns:
        dict: Status dictionary with keys:
            - status: "success", "silence", or "error"
            - text: Recognized text (if status is "success")
            - error: Error message (if status is "error")
    """
    try:
        with mic as source:
            logger.info("Listening for command...")
            recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_DURATION)
            
            try:
                audio = recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )
            except sr.WaitTimeoutError:
                logger.info("Listen timeout - no speech detected")
                return {"status": "silence"}

        # Recognize speech
        try:
            text = recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return {"status": "success", "text": text}
            
        except sr.UnknownValueError:
            logger.info("No speech detected or unintelligible")
            return {"status": "silence"}
            
        except sr.RequestError as e:
            logger.error(f"Recognition request error: {e}")
            return {"status": "error", "error": str(e)}
            
    except Exception as e:
        logger.error(f"Unexpected error in listen: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


def test_microphone():
    """Test if microphone is accessible."""
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info("Microphone test successful")
        return True
    except Exception as e:
        logger.error(f"Microphone test failed: {e}")
        return False
