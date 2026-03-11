import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "videos"
AUDIO_DIR = BASE_DIR / "audio"
OUTPUTS_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"


# Model configurations
WHISPER_MODEL = "tiny" # Can be 'tiny', 'base', 'small', 'medium', 'large'
TARGET_LANGUAGE = "hi"
SOURCE_LANGUAGE = "en"

# Helper to ensure directories exist
def setup_directories():
    for directory in [VIDEOS_DIR, AUDIO_DIR, OUTPUTS_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
