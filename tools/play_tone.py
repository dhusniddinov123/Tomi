import sounddevice as sd
import numpy as np
import json

print('Default sounddevice settings:')
try:
    print('default.device =', sd.default.device)
    print('default.samplerate =', sd.default.samplerate)
except Exception as e:
    print('Could not read defaults:', e)

print('\nAvailable output-capable devices:')
devs = sd.query_devices()
outs = [d for d in devs if d['max_output_channels']>0]
print(json.dumps(outs, indent=2, ensure_ascii=False))

# Play a 500ms 440Hz tone at approachably low volume
fs = 44100
t = np.linspace(0, 0.5, int(fs*0.5), False)
wave = 0.15 * np.sin(2 * np.pi * 440 * t)
try:
    print('\nPlaying test tone (500ms) on default output...')
    sd.play(wave, fs)
    sd.wait()
    print('Played tone successfully')
except Exception as e:
    print('Failed to play tone:', e)

# Also try a short Windows beep as fallback
try:
    import winsound
    print('\nAttempting winsound.Beep fallback...')
    winsound.Beep(750, 300)
    print('winsound.Beep done')
except Exception as e:
    print('winsound.Beep unavailable:', e)
