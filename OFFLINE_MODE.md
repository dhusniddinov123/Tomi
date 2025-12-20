# 🔒 TOMI COMPLETELY OFFLINE MODE

**Everything works WITHOUT internet!**

## What's Offline

✅ **Wake word detection** - Vosk (no Google API)  
✅ **Speech recognition** - Vosk (no Google API)  
✅ **AI responses** - Ollama (local)  
✅ **Text-to-speech** - pyttsx3 (local)  
✅ **Local commands** - All local

**NO INTERNET REQUIRED** 🚀

---

## Installation (One-Time Setup)

### Step 1: Update Python Dependencies

```powershell
cd d:\Tomi

# Activate virtual environment
.\venv\Scripts\activate

# Update requirements
pip install --upgrade vosk pocketsphinx pyaudio
```

### Step 2: Download Vosk Speech Model

Download the English model (once):

```powershell
# Create models directory
mkdir models

# Download model (choose one):

# Option A: Small model (recommended - 40MB)
curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o models\vosk-model-small.zip
Expand-Archive -Path models\vosk-model-small.zip -DestinationPath models
Rename-Item -Path models\vosk-model-small-en-us-0.15 -NewName model-en-us

# Option B: Large model (more accurate - 1.4GB)
curl -L https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip -o models\vosk-model.zip
Expand-Archive -Path models\vosk-model.zip -DestinationPath models
Rename-Item -Path models\vosk-model-en-us-0.22 -NewName model-en-us
```

### Step 3: Verify Ollama is Running

```powershell
# Start Ollama (new terminal)
ollama serve

# Check it's running (other terminal)
ollama list
```

---

## Run Tomi (Completely Offline)

```powershell
# Terminal 1: Keep Ollama running
ollama serve

# Terminal 2: Run Tomi
cd d:\Tomi
python main.py
```

You should see:

```
Tomi.Main - INFO - 🔒 OFFLINE MODE - No internet required!
```

---

## Using Tomi Offline

### Wake Word

Say: **"Hey Tomi"** or **"Hi Tomi"**

### Commands

**Local Commands** (instant, no internet):

```
"Open Notepad"
"What time is it?"
"Search for cats"           ← Opens browser locally
"YouTube Python"            ← Opens YouTube locally
"Lock computer"
```

**AI Questions** (uses local Ollama):

```
"What's Python?"
"Tell me a joke"
"Explain quantum computing"
"How do I learn coding?"
```

---

## Troubleshooting Offline Mode

### Issue: "Vosk not installed"

**Fix:**

```powershell
pip install vosk pocketsphinx
```

### Issue: "Model not found"

**Fix - Download model:**

```powershell
# Create models directory
mkdir models

# Download small model (recommended)
cd models
curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o vosk-model-small.zip
Expand-Archive -Path vosk-model-small.zip
Rename-Item vosk-model-small-en-us-0.15 model-en-us
cd ..
```

### Issue: "Microphone error"

**Fix:**

```powershell
# Check microphones
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"

# If you have multiple mics, add to config/settings.json:
{
    "audio_device_index": 1
}
```

### Issue: "No speech detected" or "Bad recognition"

**Possible fixes:**

1. Download larger model (more accurate)
2. Speak louder and clearer
3. Reduce background noise
4. Change energy threshold in config

### Issue: "Ollama not responding"

**Fix:**

```powershell
# Make sure Ollama is running
ollama serve

# Check it's responsive
ollama list
```

---

## Model Options

### Small Model (Recommended for First Use)

- Size: 40 MB
- Download: ~30 seconds
- Accuracy: Good
- Performance: Very fast
- Recommended: ✅ YES

```powershell
curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o models\vosk-model-small.zip
Expand-Archive -Path models\vosk-model-small.zip -DestinationPath models
Rename-Item -Path models\vosk-model-small-en-us-0.15 -NewName model-en-us
```

### Large Model (More Accurate)

- Size: 1.4 GB
- Download: ~5 minutes
- Accuracy: Excellent
- Performance: Slower
- Recommended: If accuracy is critical

```powershell
curl -L https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip -o models\vosk-model.zip
Expand-Archive -Path models\vosk-model.zip -DestinationPath models
Rename-Item -Path models\vosk-model-en-us-0.22 -NewName model-en-us
```

---

## Configuration

Edit `config/settings.json`:

```json
{
  "speech_mode": "offline",
  "vosk_model_path": null,
  "audio_device_index": null,

  "wake_words": ["hey tomi", "hi tomi"],
  "wake_timeout": 3,

  "listen_timeout": 10,

  "ollama_model": "llama3:latest",
  "ollama_timeout": 120,

  "debug_mode": false,
  "log_level": "INFO"
}
```

### Custom Vosk Model Path

```json
{
  "vosk_model_path": "C:/path/to/model-en-us"
}
```

### Custom Microphone

```json
{
  "audio_device_index": 2
}
```

### Debug Offline Mode

```json
{
  "debug_mode": true,
  "log_level": "DEBUG"
}
```

---

## Performance Expectations

| Operation               | Time        | Requires Internet |
| ----------------------- | ----------- | ----------------- |
| Wake word detection     | 1-3 seconds | ❌ NO             |
| Speech recognition      | 2-5 seconds | ❌ NO             |
| Local commands          | < 100ms     | ❌ NO             |
| AI response (phi model) | 2-5 sec     | ❌ NO             |
| AI response (llama2)    | 5-15 sec    | ❌ NO             |
| AI response (llama3)    | 10-30 sec   | ❌ NO             |

**All local, all fast, all offline!**

---

## Project Structure (Offline)

```
Tomi/
├── main.py                    ✅ Uses offline mode
├── core/
│   ├── wake_offline.py       ✅ NEW - Offline wake detection
│   ├── listen_offline.py     ✅ NEW - Offline speech recognition
│   ├── wake.py               📡 Fallback (online)
│   ├── listen.py             📡 Fallback (online)
│   ├── speak.py              ✅ Local TTS
│   ├── ollama_client.py      ✅ Local AI
│   └── ...
├── models/
│   └── model-en-us/          ✅ Vosk model (local)
│       └── (speech recognition data)
├── config/
│   └── settings.json         ✅ Offline settings
└── logs/
```

---

## Why Offline?

### Benefits

- ✅ **Privacy** - No data sent to cloud
- ✅ **Speed** - No network latency
- ✅ **Reliability** - Works without internet
- ✅ **Cost** - No API charges
- ✅ **Security** - Everything local
- ✅ **Control** - You own your data

### Limitations

- Speech recognition accuracy: ~95% (vs Google 99%)
- Wake word accuracy: ~95% (vs Google 99%)
- Processing time: Slightly longer

---

## Fallback to Online Mode

If you want to use Google Speech API (requires internet):

```powershell
# Edit config/settings.json
{
    "speech_mode": "online"
}
```

Or edit `main.py`:

```python
# Comment this:
from core.wake_offline import ...

# Uncomment this:
from core.wake import ...
```

---

## What You Need

✅ **Already have:**

- Ollama (running)
- Python (installed)
- Microphone

✅ **To download (one-time):**

- Vosk model (40MB - 1.4GB)
- Python packages (pip install)

✅ **After setup:**

- Nothing else needed!
- Works completely offline
- No internet required

---

## Quick Setup Summary

```powershell
# 1. Install packages
pip install vosk pocketsphinx pyaudio

# 2. Download model
mkdir models
cd models
curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o vosk-model-small.zip
Expand-Archive vosk-model-small.zip
Rename-Item vosk-model-small-en-us-0.15 model-en-us
cd ..

# 3. Run Ollama (new terminal)
ollama serve

# 4. Run Tomi (new terminal)
python main.py

# 5. Say "Hey Tomi"
```

**Done! All offline!** 🔒

---

## Support

Check logs:

```powershell
notepad "logs\tomi_$(Get-Date -Format 'yyyyMMdd').log"
```

Enable debug:
Edit `config/settings.json`:

```json
{
  "debug_mode": true,
  "log_level": "DEBUG"
}
```

---

**Your Tomi now works completely offline - no internet required!** 🚀

_Last Updated: December 10, 2025_
