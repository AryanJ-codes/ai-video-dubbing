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
        video_dur = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprintwrappers=1:nokey=1', video_path],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        audio_dur = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprintwrappers=1:nokey=1', dubbed_audio_path],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        video_duration = float(video_dur)
        audio_duration = float(audio_dur)
        
        logger.info(f"Video duration: {video_duration:.2f}s, Audio duration: {audio_duration:.2f}s")
        
        # Calculate speed adjustment if audio is longer
        if audio_duration > video_duration:
            # Scale factor to fit audio without cutting
            # Speed up video by (audio/video) and slow down audio by same factor
            scale_factor = audio_duration / video_duration
            # Cap the adjustment to max 20% to avoid unnatural results
            if scale_factor > 1.2:
                logger.warning(f"Audio is {scale_factor:.2f}x longer than video, capping to 1.2x")
                scale_factor = 1.2
                # Recalculate audio duration to match capped video
                audio_duration = video_duration * scale_factor
            
            video_speed = scale_factor
            audio_speed = 1.0 / scale_factor
            
            logger.info(f"Adjusting: video {video_speed:.3f}x, audio {audio_speed:.3f}x")
            
            # Apply speed adjustments
            temp_video = video_path.replace('.mp4', '_speed.mp4')
            subprocess.run([
                'ffmpeg', '-y', '-i', video_path,
                '-filter:v', f'setpts={1/video_speed}*PTS',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                temp_video
            ], capture_output=True, check=True)
            
            temp_audio = dubbed_audio_path.replace('.wav', '_speed.wav')
            subprocess.run([
                'ffmpeg', '-y', '-i', dubbed_audio_path,
                '-filter:a', f'atempo={audio_speed}',
                '-ar', '44100', '-ac', '2', temp_audio
            ], capture_output=True, check=True)
            
            video_path = temp_video
            dubbed_audio_path = temp_audio
        
        # Merge with adjusted video/audio
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-i', dubbed_audio_path,
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-ar', '44100', '-ac', '2',
            final_output_path
        ], capture_output=True, check=True)
        
        # Cleanup temp files
        for f in [video_path, dubbed_audio_path]:
            if '_speed' in f and os.path.exists(f):
                os.remove(f)

        logger.info(f"Video merged successfully! Final dubbed video saved to: {final_output_path}")
        return final_output_path

    except Exception as e:
        logger.error(f"Failed during video assembly. Error: {e}")
        logger.debug(traceback.format_exc())
        raise e
