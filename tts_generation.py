import os
import numpy as np
import scipy.io.wavfile as wavfile
from TTS.api import TTS
from config import TTS_MODEL_NAME, AUDIO_DIR, TEMP_DIR, TARGET_LANGUAGE
from utils import logger
import traceback

def generate_dubbed_audio(segments: list, original_audio_path: str, video_duration_sec: float, progress_callback=None) -> str:
    """
    Generates translated speech for each segment and places them on a timeline.
    Returns the path to the combined dubbed audio track.
    """
    logger.info(f"Initializing TTS model '{TTS_MODEL_NAME}'")
    
    # We use XTTS v2 which can clone the voice from the original audio.
    # Check if GPU is available
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"TTS running on device: {device}")
    
    try:
        tts = TTS(TTS_MODEL_NAME).to(device)
    except Exception as e:
        logger.error(f"Failed to load TTS model. Error: {e}")
        raise e
        
    # The output sample rate depends on the TTS model. XTTS v2 is 24000 Hz.
    sample_rate = 24000 
    total_samples = int((video_duration_sec + 2.0) * sample_rate)
    final_audio = np.zeros(total_samples, dtype=np.float32)
    
    filename = os.path.basename(original_audio_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_audio_path = os.path.join(AUDIO_DIR, f"{name_without_ext}_dubbed.wav")
    
    for i, segment in enumerate(segments):
        text = segment['text'].strip()
        start_time = segment['start']
        
        if not text:
            continue
            
        logger.info(f"Generating TTS for segment {i}: '{text}'")
        
        try:
            # XTTS v2 requires a speaker wav for voice cloning and the target language
            # We use the original full audio as the reference speaker sample
            # (In a very long video, a shorter sample < 10s is recommended, but API handles truncating)
            wav_data = tts.tts(text=text, speaker_wav=original_audio_path, language=TARGET_LANGUAGE)
            
            # Place audio at the correct start time timestamp
            start_sample = int(start_time * sample_rate)
            end_sample = start_sample + len(wav_data)
            
            # Ensure we don't exceed the allocated final_audio length
            if end_sample > total_samples:
                # Extend the canvas if necessary
                padding = np.zeros(end_sample - total_samples, dtype=np.float32)
                final_audio = np.concatenate((final_audio, padding))
                total_samples = len(final_audio)
                
            # Add to canvas
            # Overlap simply adds the float values.
            final_audio[start_sample:end_sample] += np.array(wav_data, dtype=np.float32)
            
        except Exception as e:
            logger.warning(f"Failed to generate TTS for segment {i}: {e}")
            logger.debug(traceback.format_exc())
            continue
            
        if progress_callback:
            progress_callback((i + 1) / len(segments), f"Generated TTS for {i + 1}/{len(segments)} segments.")
            
    # Normalize to prevent clipping if overlaps occurred
    max_val = np.max(np.abs(final_audio))
    if max_val > 0:
        final_audio = final_audio / max_val
        
    # Write to WAV
    logger.info(f"Saving combined dubbed audio to: {output_audio_path}")
    wavfile.write(output_audio_path, sample_rate, final_audio)
    
    return output_audio_path
