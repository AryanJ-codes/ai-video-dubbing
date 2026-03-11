import os
import yt_dlp
from config import VIDEOS_DIR
from utils import logger
import traceback

def download_youtube_video(url: str) -> str:
    """
    Downloads a YouTube video as an MP4 file into the videos directory.
    Returns the absolute path to the downloaded video file.
    """
    logger.info(f"Preparing to download video from: {url}")
    
    # We set a specific output template to save in our VIDEOS_DIR
    output_template = os.path.join(VIDEOS_DIR, "%(id)s.%(ext)s")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': True,
        # 'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_id = info_dict.get("id", None)
            video_ext = info_dict.get("ext", "mp4")
            
            if not video_id:
                raise ValueError("Could not extract video ID from the URL.")
                
            video_path = os.path.join(VIDEOS_DIR, f"{video_id}.{video_ext}")
            
            # Since yt-dlp might merge to webm or mkv instead of mp4 occasionally, 
            # let's try to locate the file that was actually created.
            if not os.path.exists(video_path):
                # Search for any file with that video_id prefix
                for f in os.listdir(VIDEOS_DIR):
                    if f.startswith(video_id):
                        video_path = os.path.join(VIDEOS_DIR, f)
                        break
                        
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Download seemed to finish, but file not found at {video_path}")
                
            logger.info(f"Video successfully downloaded to: {video_path}")
            return video_path
            
    except Exception as e:
        logger.error(f"Failed to download video from {url}. Error: {e}")
        logger.debug(traceback.format_exc())
        raise
