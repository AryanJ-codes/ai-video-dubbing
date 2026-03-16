import os
import asyncio
import tempfile
import numpy as np
import scipy.io.wavfile as wavfile
from config import AUDIO_DIR, TARGET_LANGUAGE
from utils import logger
import traceback

# Map language codes to edge-tts voices
VOICE_MAP = {
    "hi": "hi-IN-MadhurNeural",   # Hindi male (natural)
    "en": "en-US-GuyNeural",
}

async def _synthesize_segment(text: str, voice: str, output_path: str):
    """Async helper to call edge-tts for a single segment."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def _time_stretch(wav: np.ndarray, target_length: int) -> np.ndarray:
    """Stretch or compress audio to match target length using librosa."""
    import librosa
    current_length = len(wav)
    if current_length == target_length:
        return wav
    if current_length > target_length:
        return wav[:target_length]
    # Stretch to target length
    stretched = librosa.resample(wav, orig_sr=len(wav), target_sr=target_length)
    if len(stretched) > target_length:
        stretched = stretched[:target_length]
    elif len(stretched) < target_length:
        padding = np.zeros(target_length - len(stretched))
        stretched = np.concatenate([stretched, padding])
    return stretched


def generate_dubbed_audio(segments: list, original_audio_path: str,
                           video_duration_sec: float, progress_callback=None) -> str:
    """
    Generates Hindi TTS for each segment using edge-tts and places them
    on a shared audio timeline matching the original timestamps.
    Time-stretches each segment to fit exactly within its time window.
    """
    voice = VOICE_MAP.get(TARGET_LANGUAGE, "hi-IN-MadhurNeural")
    logger.info(f"Using edge-tts voice: {voice}")

    sample_rate = 24000
    total_samples = int((video_duration_sec + 2.0) * sample_rate)
    final_audio = np.zeros(total_samples, dtype=np.float32)

    filename = os.path.basename(original_audio_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_audio_path = os.path.join(AUDIO_DIR, f"{name_without_ext}_dubbed.wav")

    valid_segments = [(i, seg) for i, seg in enumerate(segments) if seg.get('text', '').strip()]

    for idx, (i, segment) in enumerate(valid_segments):
        text = segment['text'].strip()
        start_time = segment['start']
        end_time = segment.get('end', start_time + 3.0)
        
        # Calculate target duration (original segment duration)
        target_duration = end_time - start_time
        target_samples = int(target_duration * sample_rate)
        
        logger.info(f"Segment {i}: [{start_time:.2f}s→{end_time:.2f}s] ({target_duration:.2f}s) '{text[:50]}...'")

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tmp_path = tmp_file.name

            asyncio.run(
                _synthesize_segment(text, voice, tmp_path)
            )

            # Load the MP3 back as numpy array via librosa
            import librosa
            wav_data, _ = librosa.load(tmp_path, sr=sample_rate, mono=True)
            os.unlink(tmp_path)
            
            # Time-stretch to fit exactly within the segment duration
            wav_stretched = _time_stretch(wav_data, target_samples)
            
            # Place on timeline at the original timestamp
            start_sample = int(start_time * sample_rate)
            end_sample = start_sample + len(wav_stretched)

            if end_sample > len(final_audio):
                padding = np.zeros(end_sample - len(final_audio), dtype=np.float32)
                final_audio = np.concatenate([final_audio, padding])

            final_audio[start_sample:end_sample] += wav_stretched.astype(np.float32)

        except Exception as e:
            logger.warning(f"Failed TTS for segment {i}: {e}")
            logger.warning(traceback.format_exc())
            continue

        if progress_callback:
            progress_callback((idx + 1) / len(valid_segments),
                              f"Generated TTS for {idx + 1}/{len(valid_segments)} segments")

    # Normalize to avoid clipping
    max_val = np.max(np.abs(final_audio))
    if max_val > 0:
        final_audio = final_audio / max_val * 0.95

    logger.info(f"Saving combined dubbed audio to: {output_audio_path}")
    wavfile.write(output_audio_path, sample_rate, final_audio.astype(np.int16))
    return output_audio_path
