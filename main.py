"""
Tomi - Personal AI Desktop Assistant (OFFLINE MODE)

A voice-activated AI assistant using OFFLINE speech recognition, wake word detection,
text-to-speech, and local LLM (Ollama) for intelligent responses.

Features:
- ✅ NO INTERNET REQUIRED
- ✅ Offline wake word detection (Vosk)
- ✅ Offline speech recognition (Vosk)
- ✅ Text-to-speech via pyttsx3 (local)
- ✅ Local AI via Ollama (local)
- ✅ Local command execution (open apps, search web, etc.)
- ✅ Comprehensive logging
- ✅ Error recovery and retry logic
"""

import sys
import signal
import threading
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import get_logger
from core.config import config
from core.speak import speak
from core.ollama_client import ollama_client
from modules.commands import command_handler

# Prefer offline modules only when their runtime dependencies are present.
# Import the offline module packages (they set a flag indicating availability),
# then bind the functions we need only if offline mode is usable. Otherwise
# fall back to the online implementations.
use_offline = False
try:
    import core.wake_offline as wake_offline
    import core.listen_offline as listen_offline

    if getattr(wake_offline, "is_offline_mode", lambda: False)():
        listen_for_wake_word = wake_offline.listen_for_wake_word
        test_wake_mic = wake_offline.test_microphone
        listen = listen_offline.listen
        test_listen_mic = listen_offline.test_microphone
        use_offline = True
    else:
        raise ImportError("offline modules present but not usable")

except Exception as e:
    logger_init = get_logger("Main")
    logger_init.warning(f"Offline mode not available ({e}), falling back to online speech recognition")
    from core.wake import listen_for_wake_word, test_microphone as test_wake_mic
    from core.listen import listen, test_microphone as test_listen_mic
    use_offline = False

logger = get_logger("Main")

# Display mode on startup
if use_offline:
    logger.info("🔒 OFFLINE MODE - No internet required!")
else:
    logger.warning("📡 ONLINE MODE - Requires internet connection")

# Thread synchronization
ai_lock = threading.Lock()
tts_active = threading.Event()
shutdown_event = threading.Event()


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Shutdown signal received. Cleaning up...")
    shutdown_event.set()
    speak("Goodbye!")
    sys.exit(0)


def check_prerequisites():
    """
    Check if all prerequisites are met before starting.
    
    Returns:
        bool: True if all checks pass, False otherwise
    """
    logger.info("Running prerequisite checks...")
    
    # Check microphone
    logger.info("Testing microphone...")
    if not test_wake_mic():
        logger.error("Microphone test failed")
        speak("Error: Microphone not accessible. Please check your audio devices.")
        return False
    
    # Check Ollama
    logger.info("Checking Ollama availability...")
    if not ollama_client.is_available():
        logger.warning("Ollama service not available")
        speak("Warning: AI service is not running. Some features may not work.")
        # Don't fail - allow running without AI for local commands
    else:
        logger.info("Ollama is available")
        models = ollama_client.list_models()
        if models:
            logger.info(f"Available models: {', '.join(models)}")
        
        if config.get("ollama_model") not in models and models:
            logger.warning(f"Configured model '{config.get('ollama_model')}' not found")
    
    return True


def warm_up_model():
    """Warm up the Ollama model in background."""
    try:
        logger.info("Warming up AI model...")
        ollama_client.warm_up()
    except Exception as e:
        logger.warning(f"Model warm-up failed (non-fatal): {e}")
        # Don't fail - just log warning


def handle_user_query(query):
    """
    Handle user query with AI or local commands.
    
    Args:
        query (str): User's command/question
    """
    # Prevent overlapping AI responses
    if not ai_lock.acquire(blocking=False):
        tts_active.set()
        try:
            speak("I'm still thinking, please wait a moment.")
        finally:
            tts_active.clear()
        return

    try:
        # First, check if this is a local command
        is_local, response = command_handler.execute(query)
        
        if is_local:
            # Local command handled
            tts_active.set()
            try:
                speak(response)
            finally:
                tts_active.clear()
            return
        
        # Not a local command - use AI
        tts_active.set()
        try:
            speak("Thinking...")
        finally:
            tts_active.clear()

        # Get AI response
        logger.info(f"Sending query to AI: {query}")
        response = ollama_client.generate(query)
        
        # Speak the response
        tts_active.set()
        try:
            speak(response)
        finally:
            tts_active.clear()
            
    except Exception as e:
        logger.error(f"Error handling query: {e}", exc_info=True)
        tts_active.set()
        try:
            speak("Sorry, I encountered an error processing your request.")
        finally:
            tts_active.clear()
    finally:
        ai_lock.release()


def main_loop():
    """Main assistant loop - listens for wake word and handles commands."""
    logger.info("Entering main loop...")
    
    while not shutdown_event.is_set():
        try:
            # If TTS is active, don't listen (avoid feedback loop)
            if tts_active.is_set():
                time.sleep(0.05)
                continue

            # Listen for wake word
            if listen_for_wake_word():
                logger.info("Wake word detected, awaiting command...")
                
                tts_active.set()
                try:
                    speak("Yes, how can I help you?")
                finally:
                    tts_active.clear()
                
                # Listen for user command
                result = listen()
                
                if result["status"] == "silence":
                    # User didn't speak - continue listening
                    logger.info("No command received (silence)")
                    continue
                
                if result["status"] == "error":
                    # Error occurred
                    logger.error(f"Listen error: {result.get('error', 'Unknown')}")
                    tts_active.set()
                    try:
                        speak("Sorry, I couldn't hear you right now.")
                    finally:
                        tts_active.clear()
                    continue
                
                # Got user input
                user_input = result.get("text", "").strip()
                if not user_input:
                    continue
                
                logger.info(f"User command: {user_input}")
                
                # Handle in background thread
                handler_thread = threading.Thread(
                    target=handle_user_query,
                    args=(user_input,),
                    daemon=True
                )
                handler_thread.start()
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            shutdown_event.set()
            break
        
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(1)  # Brief pause before retrying


def main():
    """Main entry point."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("Tomi AI Assistant Starting...")
    logger.info("=" * 60)
    
    # Run prerequisite checks
    if not check_prerequisites():
        logger.error("Prerequisite checks failed. Exiting.")
        return 1
    
    # Start greeting
    speak("Hello, I am Tomi. I'm ready.")
    logger.info("Tomi is ready!")
    
    # Warm up model in background
    warmup_thread = threading.Thread(target=warm_up_model, daemon=True)
    warmup_thread.start()
    
    # Start main loop
    try:
        main_loop()
    except Exception as e:
        logger.critical(f"Fatal error in main: {e}", exc_info=True)
        speak("A critical error occurred. Shutting down.")
        return 1
    
    logger.info("Tomi shutting down...")
    return 0


if __name__ == "__main__":
    sys.exit(main())

