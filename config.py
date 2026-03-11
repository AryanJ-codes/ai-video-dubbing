import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = BASE_DIR / "videos"
AUDIO_DIR = BASE_DIR / "audio"
OUTPUTS_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"

# WAV2LIP configurations
WAV2LIP_DIR = BASE_DIR / "Wav2Lip"
WAV2LIP_CHECKPOINT = WAV2LIP_DIR / "checkpoints" / "wav2lip_gan.pth"
FACE_DETECTION_CHECKPOINT = WAV2LIP_DIR / "face_detection" / "detection" / "sfd" / "s3fd.pth"

# Model configurations
WHISPER_MODEL = "base" # Can be 'tiny', 'base', 'small', 'medium', 'large'
TTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2" # Good multi-lingual model supporting Hindi
TARGET_LANGUAGE = "hi"
SOURCE_LANGUAGE = "en"

# Helper to ensure directories exist
def setup_directories():
    for directory in [VIDEOS_DIR, AUDIO_DIR, OUTPUTS_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
