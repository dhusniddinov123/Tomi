# 🎯 TOMI - QUICK REFERENCE CARD

## 📋 INSTALLATION (First Time Only)

```powershell
# 1. Install dependencies
cd d:\Tomi
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Install Ollama model
ollama pull llama3

# 3. Test run
python main.py
```

---

## 🚀 DAILY USAGE

### Start Tomi

```powershell
# Option 1: Double-click
start_tomi.bat

# Option 2: PowerShell
.\start_tomi.ps1

# Option 3: Direct
python main.py
```

### Wake Words

- "Hey Tomi"
- "Hi Tomi"
- "Hello Tomi"

### Example Commands

**AI Questions:**

- "Hey Tomi" → "What's the weather?"
- "Hey Tomi" → "Tell me a joke"
- "Hey Tomi" → "Explain quantum physics"

**Local Commands:**

- "Open Notepad"
- "Open Calculator"
- "Search for Python tutorials"
- "YouTube machine learning"
- "What time is it?"
- "What's today's date?"

---

## ⚙️ CONFIGURATION

Edit: `config/settings.json`

```json
{
  "wake_words": ["hey tomi"], // Your wake words
  "tts_rate": 170, // Speech speed
  "ollama_model": "llama3", // AI model
  "ollama_timeout": 60, // AI timeout (seconds)
  "debug_mode": false // Enable debug logs
}
```

---

## 🔧 AUTO-START SETUP

### Task Scheduler (Recommended)

```powershell
# Run as Administrator
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "d:\Tomi\main.py" -WorkingDirectory "d:\Tomi"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "Tomi" -Action $action -Trigger $trigger
```

### Startup Folder (Simple)

1. Press `Win + R`
2. Type: `shell:startup`
3. Copy `start_tomi.bat` shortcut there

---

## 📊 MONITORING

### View Logs

```powershell
# Latest log
notepad "logs\tomi_$(Get-Date -Format 'yyyyMMdd').log"

# Live monitoring
Get-Content "logs\tomi_*.log" -Wait -Tail 20
```

### Check Status

- Logs location: `d:\Tomi\logs\`
- Config: `d:\Tomi\config\settings.json`

---

## 🐛 TROUBLESHOOTING

### Microphone Not Working

```powershell
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### Ollama Not Responding

```powershell
# Check Ollama
ollama list
ollama serve  # If not running
```

### Wake Word Not Detecting

1. Speak louder/clearer
2. Reduce background noise
3. Enable debug: `"debug_wake": true` in config

### Slow Responses

```powershell
# Use faster model
ollama pull phi
# Then update config: "ollama_model": "phi"
```

---

## 🛑 STOP TOMI

- Press `Ctrl + C` in terminal
- Or close terminal window
- Tomi will say "Goodbye!"

---

## 📁 PROJECT STRUCTURE

```
Tomi/
├── main.py              ← Main entry point
├── start_tomi.bat      ← Quick start (Windows)
├── requirements.txt    ← Dependencies
├── core/               ← Core modules
│   ├── wake.py        ← Wake word detection
│   ├── listen.py      ← Speech recognition
│   ├── speak.py       ← Text-to-speech
│   └── ollama_client.py ← AI client
├── modules/
│   └── commands.py    ← Local commands
├── config/
│   └── settings.json  ← Your settings
└── logs/              ← Log files
```

---

## 📚 DOCUMENTATION

- **User Guide**: `README.md`
- **Deployment**: `DEPLOYMENT.md`
- **Full Audit**: `AUDIT_REPORT.md`

---

## 🔗 QUICK LINKS

| Task         | Command                           |
| ------------ | --------------------------------- |
| Start Tomi   | `python main.py`                  |
| View logs    | `notepad logs\tomi_*.log`         |
| Edit config  | `notepad config\settings.json`    |
| Install deps | `pip install -r requirements.txt` |
| Check Ollama | `ollama list`                     |
| Pull model   | `ollama pull llama3`              |

---

## 🆘 EMERGENCY FIXES

### Complete Reset

```powershell
# 1. Stop Tomi (Ctrl+C)
# 2. Delete config
Remove-Item config\settings.json
# 3. Restart - will recreate defaults
python main.py
```

### Reinstall Dependencies

```powershell
.\venv\Scripts\activate
pip install --upgrade --force-reinstall -r requirements.txt
```

---

## ✅ HEALTH CHECK

Run before reporting issues:

```powershell
# 1. Python version
python --version

# 2. Microphone
python -c "import speech_recognition as sr; print('OK')"

# 3. Ollama
ollama list

# 4. Tomi test
python main.py
# Say "Hey Tomi" → "What time is it?"
```

---

**🎤 Ready to use? Say "Hey Tomi" and start talking!**

_Keep this card handy for quick reference_
