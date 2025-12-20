"""Configuration management for Tomi AI Assistant."""

import os
import json
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Default configuration
DEFAULT_CONFIG = {
    # Wake word detection
    "wake_words": ["hey tomi", "hey tom", "hi tomi", "hi tom", "hello tomi"],
    "wake_timeout": 3,
    "phrase_time_limit": 2,
    "dynamic_energy": True,
    "energy_threshold": 300,
    "pause_threshold": 0.4,
    "non_speaking_duration": 0.3,
    
    # Speech recognition
    "listen_timeout": 10,
    "listen_phrase_limit": 10,
    "ambient_noise_duration": 1,
    
    # Text-to-speech
    "tts_engine": "pyttsx3",  # or "edge-tts" for offline alternative
    "tts_rate": 170,
    "tts_volume": 0.9,
    "tts_voice": None,  # None = default, or specify voice ID
    
    # Ollama settings
    "ollama_model": "llama3",
    "ollama_timeout": 60,
    "ollama_retries": 1,
    "ollama_host": "http://localhost:11434",
    
    # System settings
    "debug_mode": False,
    "debug_wake": False,
    "max_concurrent_requests": 1,
    "auto_start": False,
    
    # Logging
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_max_size_mb": 10,
    "log_backup_count": 5,
}


class Config:
    """Configuration manager for Tomi."""
    
    def __init__(self, config_file=None):
        self.config_file = config_file or BASE_DIR / "config" / "settings.json"
        self.config = DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load configuration from file, merging with defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        else:
            # Create default config file
            self.save()
    
    def save(self):
        """Save current configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value."""
        self.config[key] = value
    
    def __getitem__(self, key):
        """Allow dictionary-style access."""
        return self.config[key]
    
    def __setitem__(self, key, value):
        """Allow dictionary-style setting."""
        self.config[key] = value


# Global config instance
config = Config()
