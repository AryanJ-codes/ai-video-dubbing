import os
from config import OUTPUTS_DIR
from utils import logger
import traceback

def run_lipsync(video_path: str, dubbed_audio_path: str) -> str:
    """
    Merges the original video with the new dubbed Hindi audio by replacing
    the audio track using FFmpeg — fast and lossless on the video stream.
    """
    logger.info("Merging generated Hindi audio with the original video...")

    filename = os.path.basename(video_path)
    name_without_ext = os.path.splitext(filename)[0]
    final_output_path = os.path.join(OUTPUTS_DIR, f"{name_without_ext}_final.mp4")

    try:
        import ffmpeg

        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(dubbed_audio_path)

        (
            ffmpeg
            .output(input_video.video, input_audio.audio, final_output_path, vcodec='copy', acodec='aac')
            .overwrite_output()
            .run(quiet=True, capture_stdout=True, capture_stderr=True)
        )

        logger.info(f"Video merged successfully! Final dubbed video saved to: {final_output_path}")
        return final_output_path

    except ffmpeg.Error as e:
        logger.error("FFmpeg audio merge failed.")
        logger.error(f"FFmpeg msg: {e.stderr.decode('utf8')}")
        logger.debug(traceback.format_exc())
        raise e
    except Exception as e:
        logger.error(f"Failed during video assembly. Error: {e}")
        logger.debug(traceback.format_exc())
        raise e
