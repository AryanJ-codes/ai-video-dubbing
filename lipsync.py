import os
import subprocess
from config import OUTPUTS_DIR
from utils import logger
import traceback

def run_lipsync(video_path: str, dubbed_audio_path: str) -> str:
    """
    Merges the original video with the new dubbed Hindi audio.
    If dubbed audio is longer than video, speeds up video slightly and slows audio
    to fit without cutting any dialogue.
    """
    logger.info("Merging generated Hindi audio with the original video...")

    filename = os.path.basename(video_path)
    name_without_ext = os.path.splitext(filename)[0]
    final_output_path = os.path.join(OUTPUTS_DIR, f"{name_without_ext}_final.mp4")

    try:
        # Get durations
        try:
            video_dur = subprocess.run(
                f'ffprobe -v error -show_entries format=duration -of default=noprintwrappers=1:nokey=1 "{video_path}"',
                shell=True, capture_output=True, text=True, check=True
            ).stdout.strip()
            video_duration = float(video_dur)
        except:
            video_duration = None
            logger.warning("Could not get video duration")
        
        try:
            audio_dur = subprocess.run(
                f'ffprobe -v error -show_entries format=duration -of default=noprintwrappers=1:nokey=1 "{dubbed_audio_path}"',
                shell=True, capture_output=True, text=True, check=True
            ).stdout.strip()
            audio_duration = float(audio_dur)
        except:
            audio_duration = None
        
        if video_duration and audio_duration:
            logger.info(f"Video: {video_duration:.2f}s, Audio: {audio_duration:.2f}s")
        
        # Always apply speed adjustment to fit audio - no cutting allowed
        if video_duration and audio_duration and audio_duration > video_duration:
            # Speed up video and slow down audio to fit exactly
            scale_factor = audio_duration / video_duration
            
            # Apply speed adjustment (no cap - full dialogue must be preserved)
            video_speed = scale_factor
            audio_speed = 1.0
            
            logger.info(f"Adjusting: video {video_speed:.3f}x faster, audio at normal speed")
            
            # Apply video speed up
            temp_video = video_path.replace('.mp4', '_speed.mp4')
            subprocess.run(
                f'ffmpeg -y -i "{video_path}" -filter:v setpts={1/video_speed}*PTS -c:v libx264 -preset fast -crf 23 "{temp_video}"',
                shell=True, capture_output=True, check=True
            )
            
            # Audio stays at original speed (we speed up video to match audio duration)
            video_path = temp_video
        
        # Check if video is still shorter than audio - extend video if needed
        try:
            final_video_dur = subprocess.run(
                f'ffprobe -v error -show_entries format=duration -of default=noprintwrappers=1:nokey=1 "{video_path}"',
                shell=True, capture_output=True, text=True, check=True
            ).stdout.strip()
            final_audio_dur = subprocess.run(
                f'ffprobe -v error -show_entries format=duration -of default=noprintwrappers=1:nokey=1 "{dubbed_audio_path}"',
                shell=True, capture_output=True, text=True, check=True
            ).stdout.strip()
            
            if float(final_video_dur) < float(final_audio_dur):
                # Extend video by looping last frame
                logger.info(f"Extending video from {final_video_dur}s to {final_audio_dur}s")
                temp_extended = video_path.replace('.mp4', '_extended.mp4')
                subprocess.run(
                    f'ffmpeg -y -i "{video_path}" -f lavfi -i color=c=black:s=640x480:r=1 -filter_complex "[0:v]loop=999:1:0,setpts=N/FRAME_RATE/TB[a]" -map "[a]" -t {final_audio_dur} -c:v libx264 -preset fast -crf 23 "{temp_extended}"',
                    shell=True, capture_output=True, check=True
                )
                video_path = temp_extended
        except Exception as e:
            logger.warning(f"Could not extend video: {e}")
        
        # Merge - NO -shortest flag to ensure full audio is preserved
        # If video is shorter, it will be extended (last frame held)
        subprocess.run(
            f'ffmpeg -y -i "{video_path}" -i "{dubbed_audio_path}" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 "{final_output_path}"',
            shell=True, capture_output=True, check=True
        )
        
        # Cleanup temp files
        for f in [video_path, dubbed_audio_path]:
            if ('_speed' in f or '_extended' in f) and os.path.exists(f):
                os.remove(f)

        logger.info(f"Video merged successfully! Final dubbed video saved to: {final_output_path}")
        return final_output_path

    except Exception as e:
        logger.error(f"Failed during video assembly. Error: {e}")
        logger.debug(traceback.format_exc())
        raise e
