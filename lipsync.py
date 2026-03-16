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
        # Merge with video - don't use shortest, use the dubbed audio duration
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-i', dubbed_audio_path,
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-ar', '44100', '-ac', '2',
            final_output_path
        ], capture_output=True, check=True)

        logger.info(f"Video merged successfully! Final dubbed video saved to: {final_output_path}")
        return final_output_path

    except Exception as e:
        logger.error(f"Failed during video assembly. Error: {e}")
        logger.debug(traceback.format_exc())
        raise e
