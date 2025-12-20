"""
Download and setup Vosk offline speech recognition model.

This script handles downloading and extracting the Vosk model
required for offline speech recognition.
"""

import os
import sys
import subprocess
from pathlib import Path
from urllib.request import urlopen
import zipfile

BASE_DIR = Path(__file__).parent


def download_file(url, destination):
    """Download file with progress indicator."""
    print(f"Downloading from: {url}")
    print(f"Saving to: {destination}")
    
    try:
        with urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            with open(destination, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"Progress: {percent:.1f}% ({downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB)")
        
        print(f"✅ Downloaded successfully: {destination}")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


def extract_zip(zip_path, extract_to):
    """Extract zip file."""
    try:
        print(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✅ Extracted to: {extract_to}")
        return True
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False


def setup_vosk():
    """Setup Vosk offline speech recognition."""
    print("\n" + "="*60)
    print("TOMI - OFFLINE SPEECH RECOGNITION SETUP")
    print("="*60)
    
    # Create models directory
    models_dir = BASE_DIR / "models"
    models_dir.mkdir(exist_ok=True)
    
    print(f"\nModels directory: {models_dir}")
    
    # Ask which model to download
    print("\nChoose Vosk model to download:")
    print("1. Small model (40MB, fast, good accuracy) - RECOMMENDED")
    print("2. Large model (1.4GB, slower, better accuracy)")

    # If script invoked with --yes or --auto, default to small model
    auto_mode = False
    if len(sys.argv) > 1 and sys.argv[1] in ("--yes", "--auto"):
        auto_mode = True

    if auto_mode:
        choice = "1"
    else:
        choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        model_file = "vosk-model-small-en-us-0.15"
        zip_file = models_dir / "vosk-model-small.zip"
    elif choice == "2":
        model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
        model_file = "vosk-model-en-us-0.22"
        zip_file = models_dir / "vosk-model.zip"
    else:
        print("Invalid choice. Using small model (default)...")
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        model_file = "vosk-model-small-en-us-0.15"
        zip_file = models_dir / "vosk-model-small.zip"
    
    # Check if model already exists
    model_path = models_dir / "model-en-us"
    if model_path.exists():
        print(f"\n✅ Vosk model already exists at: {model_path}")
        return True
    
    # Download model
    print(f"\n⏳ Downloading model (this may take a few minutes)...")
    if not download_file(model_url, str(zip_file)):
        return False
    
    # Extract model
    print(f"\n⏳ Extracting model...")
    if not extract_zip(str(zip_file), str(models_dir)):
        return False
    
    # Rename to standard name
    print(f"\n⏳ Organizing model...")
    extracted_path = models_dir / model_file
    if extracted_path.exists():
        # Remove old name if exists
        if model_path.exists():
            import shutil
            shutil.rmtree(model_path)
        # Rename to standard name
        extracted_path.rename(model_path)
        print(f"✅ Model renamed to: {model_path}")
    
    # Cleanup zip file
    try:
        os.remove(zip_file)
        print(f"✅ Cleaned up: {zip_file}")
    except:
        pass
    
    print("\n" + "="*60)
    print("✅ VOSK MODEL SETUP COMPLETE!")
    print("="*60)
    print(f"\nModel location: {model_path}")
    print("\nNext steps:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Run Tomi: python main.py")
    print("3. Say 'Hey Tomi'")
    print("\nEnjoy offline speech recognition! 🔒")
    
    return True


def verify_vosk():
    """Verify Vosk is properly installed."""
    print("\nVerifying Vosk installation...")
    
    try:
        import vosk
        import pyaudio
        print("✅ Vosk installed")
        print("✅ PyAudio installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Install with: pip install vosk pocketsphinx pyaudio")
        return False
    
    # Check model
    model_path = BASE_DIR / "models" / "model-en-us"
    if model_path.exists():
        print(f"✅ Vosk model found: {model_path}")
        return True
    else:
        print(f"❌ Vosk model not found: {model_path}")
        print("Run this script to download: python setup_vosk.py")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_vosk()
    else:
        setup_vosk()
