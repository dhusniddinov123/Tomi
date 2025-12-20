"""Wake-word detector for Tomi AI Assistant.

Listens for wake words like "hey tomi", "hi tomi", etc.
Uses Google Speech Recognition with configurable parameters.
"""

import speech_recognition as sr
from core.logger import get_logger
from core.config import config

logger = get_logger("Wake")

# Initialize recognizer and microphone
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Load configuration
WAKE_WORDS = config.get("wake_words", ["hey tomi", "hi tomi", "hi"])
WAKE_TIMEOUT = config.get("wake_timeout", 3)
PHRASE_TIME_LIMIT = config.get("phrase_time_limit", 2)
USE_DYNAMIC_ENERGY = config.get("dynamic_energy", True)
ENERGY_THRESHOLD = config.get("energy_threshold", 300)
PAUSE_THRESHOLD = config.get("pause_threshold", 0.4)
NON_SPEAKING_DURATION = config.get("non_speaking_duration", 0.3)
DEBUG_WAKE = config.get("debug_wake", False)

# Configure recognizer
recognizer.dynamic_energy_threshold = USE_DYNAMIC_ENERGY
if not USE_DYNAMIC_ENERGY:
    recognizer.energy_threshold = ENERGY_THRESHOLD

# Ensure pause_threshold >= non_speaking_duration
if PAUSE_THRESHOLD < NON_SPEAKING_DURATION:
    NON_SPEAKING_DURATION = PAUSE_THRESHOLD

recognizer.pause_threshold = PAUSE_THRESHOLD
recognizer.non_speaking_duration = NON_SPEAKING_DURATION

# Flag for ambient adjustment
_ambient_adjusted = False


def listen_for_wake_word():
    """
    Listen for wake word detection.
    
    Returns:
        bool: True if wake word detected, False otherwise
    """
    global _ambient_adjusted
    
    try:
        with mic as source:
            # Do brief ambient noise adjustment once
            if not _ambient_adjusted:
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    logger.debug("Ambient noise adjustment complete")
                    _ambient_adjusted = True
                except Exception as e:
                    logger.warning(f"Ambient noise adjustment failed: {e}")
                    _ambient_adjusted = True  # Don't retry every time

            # Listen for short phrases
            try:
                audio = recognizer.listen(
                    source,
                    timeout=WAKE_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )
            except sr.WaitTimeoutError:
                # No speech detected - not an error
                return False

        # Recognize speech
        try:
            text = recognizer.recognize_google(audio).lower()
            
            if DEBUG_WAKE:
                logger.debug(f"Heard: {text}")
            
            # Check for wake words
            for word in WAKE_WORDS:
                if word in text:
                    logger.info(f"Wake word detected: '{word}'")
                    return True
            
            return False
            
        except sr.UnknownValueError:
            # Unintelligible or silence
            if DEBUG_WAKE:
                logger.debug("Unintelligible audio or silence")
            return False
            
        except sr.RequestError as e:
            error_msg = str(e).lower()
            # Treat temporary network errors as "no speech" rather than failure
            if 'gateway' in error_msg or 'timeout' in error_msg or '503' in error_msg or 'bad' in error_msg or 'connection' in error_msg:
                if DEBUG_WAKE:
                    logger.warning(f"Temporary speech API issue (will retry): {e}")
                return False  # Continue listening, don't crash
            logger.error(f"Wake word recognition request error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in wake word detection: {e}", exc_info=True)
        return False


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
