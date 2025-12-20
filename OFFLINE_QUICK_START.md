# ⚡ OFFLINE TOMI - QUICK START (5 MINUTES)

**Everything works offline - no internet needed!**

---

## Step 1: Install Packages (2 minutes)

```powershell
cd d:\Tomi

# Activate virtual environment (if not already)
.\venv\Scripts\activate

# Install/update packages
pip install -r requirements.txt
```

---

## Step 2: Download Speech Model (2 minutes)

**Option A: Automatic (Recommended)**

```powershell
python setup_vosk.py
# Follow prompts, choose option 1 (small model - 40MB)
```

**Option B: Manual**

```powershell
mkdir models
cd models

# Download small model (recommended - 40MB)
curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o vosk-model-small.zip
Expand-Archive vosk-model-small.zip
Rename-Item vosk-model-small-en-us-0.15 model-en-us

cd ..
```

---

## Step 3: Start Ollama (1 minute)

**New PowerShell terminal:**

```powershell
ollama serve
```

Keep this running!

---

## Step 4: Run Tomi (1 minute)

**New PowerShell terminal:**

```powershell
cd d:\Tomi
python main.py
```

You should see:

```
🔒 OFFLINE MODE - No internet required!
Tomi: Hello, I am Tomi. I'm ready.
```

---

## Step 5: Try It!

After a few seconds:

**Say:** "Hey Tomi"

**You hear:** "Yes, how can I help you?"

**Say:** "What time is it?"

**Tomi responds:** "It's 12:30 PM"

---

## That's It! 🎉

Your Tomi now works **100% offline**!

---

## Common Commands

### After Waking Up ("Hey Tomi"):

**AI Questions:**

- "Tell me a joke"
- "What's Python?"
- "Explain AI"

**Local Commands:**

- "What time is it?"
- "Open Notepad"
- "Search for cats"
- "Lock computer"

---

## If Something Doesn't Work

### "Vosk not found" or "Module not installed"

```powershell
pip install vosk pocketsphinx pyaudio
```

### "Model not found"

```powershell
python setup_vosk.py
```

### "Microphone error"

Check Windows Privacy Settings:

- Settings → Privacy & Security → Microphone
- Turn ON microphone access

### "Nothing happens"

Check logs:

```powershell
notepad "logs\tomi_$(Get-Date -Format 'yyyyMMdd').log"
```

---

## Files You Need

✅ Already there:

- `main.py` - Main program (updated for offline)
- `core/wake_offline.py` - Offline wake detection
- `core/listen_offline.py` - Offline speech recognition
- `core/speak.py` - Local text-to-speech
- `core/ollama_client.py` - Local AI

✅ To download (one-time):

- Vosk model (40MB - 1.4GB)

---

## What's Different from Before?

| Feature            | Before        | Now               |
| ------------------ | ------------- | ----------------- |
| Wake word          | Google API ☁️ | Vosk (offline) ✅ |
| Speech recognition | Google API ☁️ | Vosk (offline) ✅ |
| AI responses       | Ollama ✅     | Ollama ✅         |
| TTS                | pyttsx3 ✅    | pyttsx3 ✅        |
| Internet required  | YES ⚠️        | NO ✅             |

---

## Performance

| Operation           | Time     |
| ------------------- | -------- |
| Wake word detection | 1-3 sec  |
| Speech recognition  | 2-5 sec  |
| Local commands      | Instant  |
| AI response         | 5-30 sec |

**All local, all fast!**

---

## Next Steps

1. ✅ Done with setup? Enjoy!
2. 📖 More details? Read `OFFLINE_MODE.md`
3. 🆘 Having issues? Check `TROUBLESHOOTING.md`
4. 🎯 Want to customize? Edit `config/settings.json`

---

## You're Ready! 🚀

Say **"Hey Tomi"** and start using your offline AI assistant!

No internet required. Complete privacy. Always available. 🔒

---

_OFFLINE MODE - December 10, 2025_
