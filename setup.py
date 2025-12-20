"""
Setup script for installing Tomi as a Windows service or auto-start.

Run this script to:
1. Create virtual environment
2. Install dependencies
3. Setup auto-start (optional)
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent


def run_command(cmd, description):
    """Run a shell command and print result."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✓ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - FAILED")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def create_venv():
    """Create virtual environment."""
    venv_path = BASE_DIR / "venv"
    
    if venv_path.exists():
        print("\nVirtual environment already exists.")
        return True
    
    return run_command(
        f'python -m venv "{venv_path}"',
        "Creating virtual environment"
    )


def install_dependencies():
    """Install Python dependencies."""
    pip_path = BASE_DIR / "venv" / "Scripts" / "pip.exe"
    req_path = BASE_DIR / "requirements.txt"
    
    if not pip_path.exists():
        print("\nError: Virtual environment not found. Run create_venv first.")
        return False
    
    return run_command(
        f'"{pip_path}" install -r "{req_path}"',
        "Installing dependencies"
    )


def setup_autostart():
    """Setup auto-start on Windows."""
    import winshell
    from win32com.client import Dispatch
    
    startup_folder = winshell.startup()
    shortcut_path = Path(startup_folder) / "Tomi AI Assistant.lnk"
    target_path = BASE_DIR / "start_tomi.bat"
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.TargetPath = str(target_path)
    shortcut.WorkingDirectory = str(BASE_DIR)
    shortcut.IconLocation = str(BASE_DIR / "main.py")
    shortcut.Description = "Tomi AI Assistant"
    shortcut.save()
    
    print(f"\n✓ Auto-start shortcut created: {shortcut_path}")
    return True


def check_ollama():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("\n✓ Ollama is installed")
        print(result.stdout)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("\n✗ Ollama not found")
        print("Please install Ollama from: https://ollama.ai/")
        return False


def main():
    """Main setup process."""
    print("=" * 60)
    print("Tomi AI Assistant - Setup")
    print("=" * 60)
    
    # Step 1: Create virtual environment
    print("\n[1/5] Creating virtual environment...")
    if not create_venv():
        print("\nSetup failed at step 1")
        return
    
    # Step 2: Install dependencies
    print("\n[2/5] Installing dependencies...")
    if not install_dependencies():
        print("\nSetup failed at step 2")
        return
    
    # Step 3: Check Ollama
    print("\n[3/5] Checking Ollama installation...")
    ollama_ok = check_ollama()
    
    # Step 4: Check microphone
    print("\n[4/5] Checking microphone...")
    try:
        import speech_recognition as sr
        mics = sr.Microphone.list_microphone_names()
        print(f"✓ Found {len(mics)} microphone(s)")
        for i, mic in enumerate(mics):
            print(f"  {i}: {mic}")
    except Exception as e:
        print(f"✗ Microphone check failed: {e}")
    
    # Step 5: Optional auto-start
    print("\n[5/5] Setup auto-start (optional)...")
    response = input("Do you want Tomi to start automatically on login? (y/n): ")
    
    if response.lower() == 'y':
        try:
            setup_autostart()
        except ImportError:
            print("\nAuto-start requires: pip install pywin32 winshell")
            print("Run this command in your virtual environment.")
        except Exception as e:
            print(f"\nAuto-start setup failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    
    if ollama_ok:
        print("\n✓ All checks passed!")
        print("\nTo start Tomi:")
        print("  - Double-click: start_tomi.bat")
        print("  - Or run: python main.py")
    else:
        print("\n⚠ Please install Ollama before running Tomi")
        print("  Download from: https://ollama.ai/")
        print("  Then run: ollama pull llama3")
    
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
