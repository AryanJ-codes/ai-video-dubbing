import os
import subprocess
from config import WAV2LIP_DIR, WAV2LIP_CHECKPOINT, OUTPUTS_DIR
from utils import logger
import traceback

def setup_wav2lip():
    """Clones the Wav2Lip repository if it doesn't exist."""
    if not os.path.exists(WAV2LIP_DIR):
        logger.info("Wav2Lip directory not found. Cloning the repository...")
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/Rudrabha/Wav2Lip.git", str(WAV2LIP_DIR)],
                check=True
            )
            logger.info("Successfully cloned Wav2Lip.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone Wav2Lip repository: {e}")
            raise e
            
    if not os.path.exists(WAV2LIP_CHECKPOINT):
        logger.warning(
            "Wav2Lip checkpoint not found.\n"
            "Please download 'wav2lip_gan.pth' from the official Wav2Lip repository and place it in 'Wav2Lip/checkpoints/'."
        )

def run_lipsync(video_path: str, dubbed_audio_path: str) -> str:
    """
    Merges the original video with the new dubbed Hindi audio.
    Since visual lipsync is extremely slow on CPU, this will simply 
    replace the video's audio track with our synchronized TTS audio timeline.
    """
    logger.info("Merging generated Hindi audio with the original video...")
    
    filename = os.path.basename(video_path)
    name_without_ext = os.path.splitext(filename)[0]
    final_output_path = os.path.join(OUTPUTS_DIR, f"{name_without_ext}_final.mp4")
    
    try:
        import ffmpeg
        
        # Load the original video (for the visual stream)
        input_video = ffmpeg.input(video_path)
        # Load the newly dubbed audio
        input_audio = ffmpeg.input(dubbed_audio_path)
        
        # Combine the video stream from input_video and audio stream from input_audio
        (
            ffmpeg
            .output(input_video.video, input_audio.audio, final_output_path, vcodec='copy', acodec='aac')
            .overwrite_output()
            .run(quiet=True, capture_stdout=True, capture_stderr=True)
        )
        
        logger.info(f"Video merged successfully! Final dubbed video saved to: {final_output_path}")
        return final_output_path
        
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg audio merge failed.")
        logger.error(f"FFmpeg msg: {e.stderr.decode('utf8')}")
        logger.debug(traceback.format_exc())
        raise e
    except Exception as e:
        logger.error(f"Failed during video assembly. Error: {e}")
        logger.debug(traceback.format_exc())
        raise e
