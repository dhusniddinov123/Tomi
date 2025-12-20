# Tomi AI Desktop Assistant

A personal AI desktop assistant using voice recognition, wake word detection, text-to-speech, and local LLM generation via Ollama.

## Features

✨ **Core Features**

- 🎤 Continuous background listening with wake word detection
- 🗣️ Natural speech recognition via Google Speech API
- 🔊 Text-to-speech responses using pyttsx3
- 🤖 Local AI responses via Ollama (llama3)
- 💻 Local command execution (open apps, web searches, etc.)
- 📝 Comprehensive logging system
- 🔄 Automatic error recovery and retry logic
- 🧵 Multi-threaded architecture for responsive performance

## Wake Words

Say any of these to activate Tomi:

- "Hey Tomi"
- "Hi Tomi"
- "Hello Tomi"

## Prerequisites

### Required Software

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **Ollama** - [Download Ollama](https://ollama.ai/)
3. **Working microphone** - Built-in or external

### Install Ollama Model

After installing Ollama, pull the default model:

```bash
ollama pull llama3
```

## Installation

### 1. Clone or Download

```bash
cd d:\
git clone <your-repo> Tomi
cd Tomi
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Ollama is Running

```bash
ollama list
```

## Usage

### Basic Usage

```bash
python main.py
```

### First Run

1. Tomi will test your microphone
2. Tomi will verify Ollama connection
3. You'll hear: "Hello, I am Tomi. I'm ready."
4. Say "Hey Tomi" to activate
5. Ask your question or give a command

### Example Interactions

**AI Conversations:**

- "Hey Tomi" → "Yes, how can I help you?"
- "What's the weather like today?" → [AI response]
- "Tell me a joke" → [AI response]

**Local Commands:**

- "Open Notepad" → Opens Notepad
- "Open Calculator" → Opens Calculator
- "Search for Python tutorials" → Opens Google search
- "YouTube Python programming" → Opens YouTube search
- "What time is it?" → Speaks current time
- "What's today's date?" → Speaks current date

## Configuration

Edit `config/settings.json` to customize:

```json
{
  "wake_words": ["hey tomi", "hi tomi"],
  "tts_rate": 170,
  "ollama_model": "llama3",
  "ollama_timeout": 60,
  "debug_mode": false
}
```

### Available Settings

| Setting          | Description              | Default                   |
| ---------------- | ------------------------ | ------------------------- |
| `wake_words`     | List of wake phrases     | `["hey tomi", "hi tomi"]` |
| `tts_rate`       | Speech speed (words/min) | `170`                     |
| `tts_volume`     | Volume (0.0-1.0)         | `0.9`                     |
| `ollama_model`   | Ollama model name        | `"llama3"`                |
| `ollama_timeout` | AI timeout (seconds)     | `60`                      |
| `debug_mode`     | Enable debug logging     | `false`                   |

## Project Structure

```
Tomi/
├── main.py                 # Main entry point
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── wake.py            # Wake word detection
│   ├── listen.py          # Speech recognition
│   ├── speak.py           # Text-to-speech
│   ├── ollama_client.py   # Ollama API client
│   ├── config.py          # Configuration management
│   └── logger.py          # Logging system
├── modules/               # Extended functionality
│   ├── __init__.py
│   └── commands.py        # Local command handlers
├── logs/                  # Log files
├── config/               # Configuration files
│   └── settings.json
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Logging

Logs are stored in `logs/tomi_YYYYMMDD.log`

- Automatic log rotation (10MB per file)
- Keeps 5 backup files
- Debug info for troubleshooting

View logs:

```bash
cat logs/tomi_20231209.log
```

## Troubleshooting

### Microphone Not Working

```bash
# Test microphone access
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### Ollama Not Responding

```bash
# Check if Ollama is running
ollama list

# Start Ollama service (if needed)
ollama serve
```

### Wake Word Not Detecting

- Speak clearly and closer to microphone
- Reduce background noise
- Try different wake words
- Enable debug mode: set `"debug_wake": true` in config

### Slow AI Responses

- Use a smaller model: `ollama pull llama2`
- Increase timeout in config
- Check GPU/CPU usage

## Advanced Usage

### Environment Variables

Override config with environment variables:

```bash
$env:TOMI_WAKE_TIMEOUT = "5"
$env:TOMI_OLLAMA_MODEL = "llama2"
python main.py
```

### Custom Voice

List available voices:

```python
from core.speak import list_voices
print(list_voices())
```

Set voice in config:

```json
{
  "tts_voice": "HKEY_LOCAL_MACHINE\\SOFTWARE\\..."
}
```

## Making it a Desktop App

### 1. Auto-Start on Windows

#### Method A: Startup Folder

1. Create shortcut to `main.py`
2. Press `Win + R`, type `shell:startup`
3. Copy shortcut to Startup folder

#### Method B: Task Scheduler

```powershell
# Run as admin
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "d:\Tomi\main.py"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Tomi Assistant" -Description "Personal AI Assistant"
```

### 2. Package as Executable (PyInstaller)

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name Tomi main.py

# Executable will be in dist/Tomi.exe
```

### 3. System Tray Icon (Optional)

Install pystray:

```bash
pip install pystray pillow
```

See `modules/tray_icon.py` (to be implemented) for system tray integration.

### 4. Windows Service (Advanced)

Use NSSM (Non-Sucking Service Manager):

```bash
# Download NSSM from nssm.cc
nssm install TomiAssistant "d:\Tomi\venv\Scripts\python.exe" "d:\Tomi\main.py"
nssm start TomiAssistant
```

## Performance Tips

1. **Use GPU acceleration** - Ollama automatically uses GPU if available
2. **Smaller models** - Use `llama2` or `phi` for faster responses
3. **SSD storage** - Store Ollama models on SSD
4. **Close background apps** - Free up RAM and CPU

## Security Considerations

⚠️ **Important:**

- Shutdown/restart commands are **disabled by default** for safety
- Enable them in `modules/commands.py` if needed
- Consider adding password protection for sensitive commands
- Review all voice commands before executing

## Contributing

Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

MIT License - See LICENSE file

## Support

For issues:

1. Check logs in `logs/` folder
2. Enable debug mode in config
3. Review troubleshooting section
4. Open GitHub issue with logs

## Roadmap

Future features:

- [ ] System tray icon
- [ ] GUI settings panel
- [ ] Plugin system for custom commands
- [ ] Multi-language support
- [ ] Voice training for better wake word accuracy
- [ ] Cloud sync for conversation history
- [ ] Mobile app integration

---

**Made with ❤️ for productivity**
