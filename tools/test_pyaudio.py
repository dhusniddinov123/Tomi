import pyaudio
import json
import sys

p = pyaudio.PyAudio()
devs = [p.get_device_info_by_index(i) for i in range(p.get_device_count())]
print(json.dumps(devs, indent=2))

# try opening each input-capable device with common rates
rates = [16000, 44100, 48000]
for d in devs:
    if d.get("maxInputChannels", 0) > 0:
        for r in rates:
            try:
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=int(r),
                                input=True, input_device_index=int(d["index"]), frames_per_buffer=4096)
                stream.close()
                print("OK device", d["index"], d["name"], "rate", r)
                break
            except Exception as e:
                pass
p.terminate()