import os
import subprocess
import ffmpeg
from config import AUDIO_DIR
from utils import logger
import traceback

def extract_audio(video_path: str) -> str:
    """
    Extracts the audio track from the given video file and saves it as a WAV file.
    Returns the absolute path to the extracted audio file.
    """
    logger.info(f"Extracting audio from video: {video_path}")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    filename = os.path.basename(video_path)
    name_without_ext = os.path.splitext(filename)[0]
    audio_output_path = os.path.join(AUDIO_DIR, f"{name_without_ext}.wav")
    
    try:
        # Run FFmpeg to extract audio as a 16kHz mono WAV file which is ideal for Whisper and TTS
        (
            ffmpeg
            .input(video_path)
            .output(audio_output_path, ac=1, ar='16000', format='wav')
            .overwrite_output()
            .run(quiet=True, capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Audio extracted successfully to: {audio_output_path}")
        return audio_output_path
        
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg failed to extract audio.")
        # Print the stderr for more detailed ffmpeg debugging
        logger.error(f"FFmpeg msg: {e.stderr.decode('utf8')}")
        logger.debug(traceback.format_exc())
        raise e
    except Exception as e:
        logger.error(f"Failed to extract audio. Error: {e}")
        logger.debug(traceback.format_exc())
        raise e
