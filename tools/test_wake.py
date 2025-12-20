"""Quick tester for wake-word detection.

Runs the online (`core.wake`) and offline (`core.wake_offline`) detectors
in a loop and prints results so you can say wake phrases and see which
detector (if any) picked them up.

Usage: Activate your venv and run:
    python tools/test_wake.py
"""
import time
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.logger import get_logger
logger = get_logger("WakeTest")

try:
    import core.wake as wake_online
except Exception as e:
    wake_online = None
    logger.warning(f"Online wake module unavailable: {e}")

try:
    import core.wake_offline as wake_offline
except Exception as e:
    wake_offline = None
    logger.warning(f"Offline wake module unavailable: {e}")

print("Starting wake-word test. Say your wake phrases clearly now.")
print("Press Ctrl+C to stop.")

def test_loop(duration=30):
    start = time.time()
    while time.time() - start < duration:
        # Online detector (non-blocking short listen)
        if wake_online:
            try:
                ok = wake_online.listen_for_wake_word()
                if ok:
                    print(f"[ONLINE] Wake detected at {time.strftime('%X')}")
            except Exception as e:
                print(f"[ONLINE] error: {e}")

        # Offline detector
        if wake_offline:
            try:
                ok = wake_offline.listen_for_wake_word()
                if ok:
                    print(f"[OFFLINE] Wake detected at {time.strftime('%X')}")
            except Exception as e:
                print(f"[OFFLINE] error: {e}")

        # brief pause to avoid tight loop
        time.sleep(0.1)

if __name__ == '__main__':
    try:
        test_loop(30)
    except KeyboardInterrupt:
        print("Stopped by user")
