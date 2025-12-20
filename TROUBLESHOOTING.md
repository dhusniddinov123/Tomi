# Tomi - Troubleshooting Guide

## 🔴 Issue: "Bad Gateway" Error on Speech Recognition

### Symptoms

```
2025-12-09 23:56:45 - Tomi.Wake - ERROR - Wake word recognition request error: recognition request failed: Bad Gateway
```

### Root Causes

1. **Google Speech API rate limiting** - Too many requests
2. **Temporary network issue** - Internet connectivity problem
3. **Google API outage** - (Rare, but possible)
4. **ISP blocking** - (Very rare)

### Solutions (Try in Order)

**Solution 1: Wait and Retry** (Most Common Fix)

```powershell
# This is temporary - just wait 30-60 seconds and try again
# The system will automatically retry
python main.py
# After 1-2 minutes, say "Hey Tomi"
```

**Solution 2: Increase Error Tolerance**
Edit `config/settings.json`:

```json
{
  "debug_wake": true,
  "wake_timeout": 5
}
```

**Solution 3: Check Network Connection**

```powershell
# Test internet
Test-Connection google.com

# Test Google API endpoint
Invoke-WebRequest https://www.google.com -TimeoutSec 5
```

**Solution 4: Use Offline Speech Recognition (Advanced)**
Install Vosk for offline recognition:

```powershell
pip install vosk pocketsphinx
```

---

## 🔴 Issue: "Ollama returned status code: 500"

### Symptoms

```
2025-12-09 23:56:44 - Tomi.Ollama - ERROR - Ollama returned status code: 500
2025-12-09 23:56:44 - Tomi.Ollama - INFO - Retrying request (attempt 2/2) after 2s
```

### Root Causes

1. **Model is still loading** - First run takes time
2. **Ollama process crashed** - Service not stable
3. **Out of memory** - GPU/RAM insufficient
4. **Model path incorrect** - Can't find model files

### Solutions (Try in Order)

**Solution 1: Wait for Model to Load** (Usually Works)

- When you first run Tomi, Ollama is loading the model
- This can take 30-60 seconds on first run
- The system has retry logic built in - just wait

**Solution 2: Verify Model is Installed**

```powershell
# Check what's installed
ollama list

# Should show: llama3:latest
# If not, pull it:
ollama pull llama3:latest
```

**Solution 3: Restart Ollama Service**

```powershell
# Stop any Ollama processes
Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start fresh
ollama serve
```

**Solution 4: Use a Smaller, Faster Model**

```powershell
# Pull a smaller model
ollama pull phi          # Very fast, 3.3B parameters
ollama pull llama2       # Medium, 7B parameters
```

Edit `config/settings.json`:

```json
{
  "ollama_model": "phi:latest",
  "ollama_timeout": 60
}
```

**Solution 5: Check Memory**

```powershell
# Check RAM available
Get-ComputerInfo | Select-Object CsPhysicalMemoryTotal, OsAvailablePhysicalMemory

# Close unnecessary programs
Get-Process | Where-Object {$_.WorkingSet -gt 500MB} | Sort-Object WorkingSet -Descending
```

---

## 🔴 Issue: Wake Word Not Detecting

### Symptoms

- You say "Hey Tomi" but nothing happens
- No error messages in logs
- Microphone seems to be working

### Root Causes

1. **Audio is too quiet** - Microphone not picking up voice
2. **Background noise too high** - Loud environment
3. **Accent/pronunciation** - Google doesn't understand you
4. **Microphone quality** - Built-in mic too poor

### Solutions (Try in Order)

**Solution 1: Speak Louder & Clearer**

- Say wake word slowly and clearly
- Get closer to microphone (6 inches)
- Reduce background noise

**Solution 2: Try Different Wake Words**
Edit `config/settings.json`:

```json
{
  "wake_words": ["hello assistant", "computer", "okay assistant"]
}
```

**Solution 3: Enable Debug Mode**

```json
{
  "debug_wake": true,
  "log_level": "DEBUG"
}
```

Then check logs:

```powershell
Get-Content "logs\tomi_*.log" -Tail 50
# Look for "Heard:" to see what it's detecting
```

**Solution 4: Check Microphone**

```powershell
# List microphones
python -c "import speech_recognition as sr; mics = sr.Microphone.list_microphone_names(); [print(f'{i}: {m}') for i, m in enumerate(mics)]"

# Set specific microphone in config (advanced)
```

**Solution 5: Adjust Energy Threshold**
Edit `config/settings.json`:

```json
{
  "dynamic_energy": false,
  "energy_threshold": 200
}
```

Lower values = more sensitive, Higher values = less sensitive

---

## 🟡 Issue: Slow AI Responses

### Symptoms

- Takes 20-30+ seconds to get a response
- System seems frozen
- High CPU usage

### Root Causes

1. **Large model running** - llama3 is heavy
2. **GPU not available** - Running on CPU only
3. **Not enough RAM** - System struggling
4. **Timeout too high** - Waiting too long

### Solutions

**Solution 1: Use Smaller Model** (Fastest Fix)

```powershell
ollama pull phi
```

Edit `config/settings.json`:

```json
{
  "ollama_model": "phi:latest",
  "ollama_timeout": 30
}
```

Response times:

- `phi` - 2-5 seconds ⚡ (Fastest)
- `llama2` - 5-15 seconds ✓ (Good)
- `llama3` - 10-30+ seconds (Slowest)

**Solution 2: Enable GPU**

```powershell
# Ollama automatically uses GPU if available
# Check if using GPU:
ollama ps
# Should show GPU allocation

# For NVIDIA:
# - Install CUDA drivers: nvidia.com/cuda
# - Run: nvidia-smi (to verify)
```

**Solution 3: Close Background Apps**

```powershell
# See what's using RAM/CPU
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
```

---

## 🟡 Issue: Microphone Errors

### Symptoms

```
ERROR: Microphone not accessible
```

### Solutions

**Solution 1: Check Windows Privacy Settings**

1. Settings → Privacy & Security → Microphone
2. Turn ON "App permissions"
3. Make sure Python has access

**Solution 2: Test Microphone**

```powershell
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)}') for i in range(p.get_device_count())]"
```

**Solution 3: Switch Microphone**

```powershell
# If you have multiple mics, try a different one
# Edit config to specify device (advanced)
```

---

## 🟡 Issue: Tomi Says Nothing After Wake Word

### Symptoms

- Wake word detected ✓
- Says "Yes, how can I help you?" ✓
- You speak ✓
- But then... silence. Nothing happens.

### Likely Causes

1. Speech recognition failure - "silence" detected
2. Command not recognized - Trying to use local command
3. AI timeout - Waiting for Ollama response
4. TTS is muted

### Debug Steps

**Step 1: Enable Debug Mode**

```json
{
  "debug_mode": true,
  "debug_wake": true,
  "log_level": "DEBUG"
}
```

**Step 2: Watch Logs**

```powershell
Get-Content "logs\tomi_*.log" -Wait -Tail 30
```

**Step 3: Try Simple Command**
After wake word:

- Say: "open notepad" (should open Notepad)
- Say: "what time is it?" (should speak time)

If local commands work but AI doesn't:

- Ollama might be loading
- Check: `ollama list`

---

## 🟢 Performance Tips

### Make it Faster

1. **Use Fast Model**

   ```powershell
   ollama pull phi
   ```

2. **Close Unnecessary Apps**

   - Chrome, Discord, VS Code, etc. use RAM
   - Close when running Tomi

3. **Enable GPU** (if available)

   - NVIDIA: Install CUDA drivers
   - Check: `ollama ps`

4. **Reduce Wake Timeout**
   ```json
   {
     "wake_timeout": 2,
     "ollama_timeout": 30
   }
   ```

### Expected Times

| Component               | Time       | Notes              |
| ----------------------- | ---------- | ------------------ |
| Wake word detection     | < 1 sec    | Per listen attempt |
| Speech recognition      | 1-3 sec    | After speaking     |
| Local command execution | < 100ms    | Instant            |
| AI with phi             | 2-5 sec    | Fastest model      |
| AI with llama2          | 5-15 sec   | Medium             |
| AI with llama3          | 10-30+ sec | Most capable       |

---

## 🔧 Diagnostic Commands

### Check Everything

```powershell
# 1. Python
python --version

# 2. Dependencies
pip list | grep -E "SpeechRecognition|pyttsx3|requests"

# 3. Microphone
python -c "import speech_recognition as sr; print('OK' if sr.Microphone else 'FAIL')"

# 4. Ollama
ollama list
ollama ps

# 5. Ollama API
curl http://localhost:11434/api/tags

# 6. Logs
Get-Content "logs\tomi_*.log" -Tail 100
```

### View Real-Time Logs

```powershell
# Follow logs as they happen
Get-Content "logs\tomi_*.log" -Wait
```

### Search Logs for Errors

```powershell
# Find all errors today
Select-String -Path "logs\tomi_*.log" -Pattern "ERROR"

# Find warnings
Select-String -Path "logs\tomi_*.log" -Pattern "WARNING"
```

---

## 📞 When to Restart

| Issue             | Action                         |
| ----------------- | ------------------------------ |
| "Bad Gateway"     | Wait 30 seconds, try again     |
| Ollama 500 error  | Wait for model to load         |
| Microphone locked | Restart Python                 |
| High CPU usage    | Restart Ollama: `ollama serve` |
| TTS not working   | Restart Python                 |
| Memory leak       | Restart Ollama and Python      |

---

## ✅ Quick Checklist

Before reporting issues:

- [ ] Python 3.8+ installed
- [ ] `pip install -r requirements.txt` run
- [ ] Ollama installed and running
- [ ] Model pulled: `ollama pull llama3:latest`
- [ ] Microphone permissions enabled
- [ ] Network connection working
- [ ] Checked logs for errors

---

## 📊 What the Fixes Do

### Changes Made to Handle Your Issues

1. **Config Updated**

   - Model: `llama3` → `llama3:latest` (matches your install)
   - Timeout: `60s` → `120s` (give model time to load)
   - Retries: `1` → `2` (auto-retry on failure)

2. **Ollama Client Enhanced**

   - Auto-adds `:latest` tag to model names
   - Handles 500 errors (retries automatically)
   - Better error messages

3. **Wake Word Detection Improved**

   - Treats network errors as "no speech" (continues listening)
   - Doesn't crash on "Bad Gateway"
   - Auto-retries on temporary failures

4. **Warm-up Improved**
   - Non-blocking warm-up (doesn't halt startup)
   - Logs warnings but continues

---

## 🎯 Next Step

1. Delete old logs
2. Restart Ollama: `ollama serve`
3. Run Tomi: `python main.py`
4. Say "Hey Tomi" after 30 seconds
5. If issues continue, share the log output

**Your system will now:**

- ✅ Handle speech API errors gracefully
- ✅ Retry automatically on Ollama 500 errors
- ✅ Use correct model name (llama3:latest)
- ✅ Give model time to respond
- ✅ Continue listening instead of crashing

---

_Last Updated: December 9, 2025_
