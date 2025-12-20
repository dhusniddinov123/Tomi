import sys, time, json
from vosk import Model, KaldiRecognizer
import sounddevice as sd

MODEL_PATH = "models/model-en-us"
SR = 16000

# optional device index from argv
DEVICE_INDEX = int(sys.argv[1]) if len(sys.argv) > 1 else None

m = Model(MODEL_PATH)
rec = KaldiRecognizer(m, SR)

def callback(indata, frames, time_info, status):
    try:
        # handle different buffer types safely
        data = bytes(indata)
        if rec.AcceptWaveform(data):
            print("FINAL:", json.loads(rec.Result()))
        else:
            print("PARTIAL:", json.loads(rec.PartialResult()))
    except Exception as e:
        print("ERR:", e)

print("Using device:", DEVICE_INDEX)
print("Listening raw Vosk for 30s... speak now")
with sd.RawInputStream(samplerate=SR, blocksize=8000, dtype='int16',
                      channels=1, callback=callback, device=DEVICE_INDEX):
    time.sleep(30)
print("Done")