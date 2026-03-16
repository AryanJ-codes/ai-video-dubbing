import os
import subprocess
from config import OUTPUTS_DIR
from utils import logger
import traceback

def run_lipsync(video_path: str, dubbed_audio_path: str) -> str:
    """
    Merges the original video with the new dubbed Hindi audio by replacing
    the audio track using FFmpeg.
    """
    logger.info("Merging generated Hindi audio with the original video...")

    filename = os.path.basename(video_path)
    name_without_ext = os.path.splitext(filename)[0]
    final_output_path = os.path.join(OUTPUTS_DIR, f"{name_without_ext}_final.mp4")

    try:
        # Convert audio to stereo 44100Hz AAC first
        temp_audio = dubbed_audio_path.replace('.wav', '_converted.aac')
        
        subprocess.run([
            'ffmpeg', '-y', '-i', dubbed_audio_path,
            '-ar', '44100', '-ac', '2', '-c:a', 'aac', '-b:a', '192k',
            temp_audio
        ], capture_output=True)

        # Merge with video - use -map to explicitly select video from first input and audio from second
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-i', temp_audio,
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            final_output_path
        ], capture_output=True)
        
        # Cleanup temp
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

        logger.info(f"Video merged successfully! Final dubbed video saved to: {final_output_path}")
        return final_output_path

    except Exception as e:
        logger.error(f"Failed during video assembly. Error: {e}")
        logger.debug(traceback.format_exc())
        raise e
