# Lab 3 AI Interaction Log - Voice and Speech Prototypes

This file automatically logs all significant interactions between students and WendyTA (GitHub Copilot Chat) during Lab 3.

## How to Use This Log
- **Automatic**: WendyTA appends entries when providing substantial help
- **Timestamped**: Each interaction includes date/time in YYYY-MM-DD HH:MM:SS format
- **Commit Required**: Students must commit this file with their lab submission
- **Attribution**: Reference this log in your Lab 3 README.md under "AI Usage"

## [2025-09-27 22:50:00] - Voice Assistant Setup and Troubleshooting
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Technical Issues Resolved
- **pyttsx3 Voice Configuration**: Fixed "SetVoiceByName failed with unknown return code -1 for voice: gmw/en" error
- **ALSA Audio Warnings**: Explained and addressed numerous ALSA configuration warnings (non-critical)
- **FLAC Installation**: Installed missing FLAC utility needed for speech recognition audio processing
- **TTS Engine Selection**: Modified voice assistant to use espeak directly to avoid voice compatibility issues

### Code Changes
- **Files Modified**: `/home/pi/Interactive-Lab-Hub/Lab 3/ollama/ollama_voice_assistant.py`
- **AI-Generated Code**: Improved error handling for TTS initialization, fallback to espeak
- **Student Modifications**: Student worked through voice assistant setup and testing

### Learning Objectives
- **Audio System Understanding**: Learned about ALSA, JACK, and audio device configuration on Raspberry Pi
- **Error Diagnosis**: Identified difference between critical errors and system warnings
- **Dependency Management**: Understood the need for system utilities like FLAC for audio processing
- **Voice Synthesis**: Explored pyttsx3 vs espeak for text-to-speech functionality

### Next Steps
- Voice assistant should now work properly with speech recognition and synthesis
- Test the complete ollama voice assistant functionality
- Proceed with Lab 3 voice interaction implementation

---

## Log Entries
*Interactions will be automatically appended below with timestamps*

## [2025-09-24 17:19:30] - Environment Setup and SSL Certificate Fix
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Issue Resolved
- **Problem**: SSL certificate verification failed when installing spacy-curated-transformers from piwheels.org
- **Error**: `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired`
- **Files Affected**: Lab 3 virtual environment (.venv), pip configuration

### Technical Solution Applied
1. **System Update**: Updated ca-certificates package via `sudo apt update && sudo apt install -y ca-certificates`
2. **Virtual Environment**: Confirmed proper activation of Lab 3 .venv
3. **Bypass Strategy**: Temporarily disabled piwheels extra-index-url to install problematic package from PyPI directly
4. **Configuration Management**: Used `pip config` to manage index URLs
5. **Complete Installation**: Successfully installed all Lab 3 requirements.txt dependencies

### Learning Outcomes
- **SSL Troubleshooting**: Student learned systematic approach to SSL certificate issues on Raspberry Pi
- **Package Management**: Understanding of pip index URLs, piwheels vs PyPI, and virtual environments
- **Problem-Solving Pattern**: How to isolate problematic packages and find alternative sources

### Commands Used
```bash
# System certificate update
sudo apt update && sudo apt install -y ca-certificates

# Virtual environment activation
cd "/home/pi/Interactive-Lab-Hub/Lab 3" && source .venv/bin/activate

# Pip configuration management
pip config set global.extra-index-url ""  # Disable piwheels temporarily
pip install spacy-curated-transformers==0.3.1  # Install from PyPI
pip config set global.extra-index-url "https://www.piwheels.org/simple"  # Re-enable

# Complete installation
pip install -r requirements.txt
```

### Next Steps
- Student ready to begin Lab 3 voice/speech experiments
- All TTS engines (Piper, KittenTTS) and speech recognition systems (Whisper, Vosk) now available
- Web framework dependencies installed for interactive prototypes

---
