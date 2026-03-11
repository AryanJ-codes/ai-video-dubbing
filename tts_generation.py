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
    "hi": "hi-IN-SwaraNeural",   # Hindi female (natural)
    "en": "en-US-JennyNeural",
}

async def _synthesize_segment(text: str, voice: str, output_path: str):
    """Async helper to call edge-tts for a single segment."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_dubbed_audio(segments: list, original_audio_path: str,
                           video_duration_sec: float, progress_callback=None) -> str:
    """
    Generates Hindi TTS for each segment using edge-tts and places them
    on a shared audio timeline matching the original timestamps.
    Returns path to the combined dubbed WAV file.
    """
    voice = VOICE_MAP.get(TARGET_LANGUAGE, "hi-IN-SwaraNeural")
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

        logger.info(f"Generating TTS for segment {i}: '{text[:60]}...' " if len(text) > 60 else f"Generating TTS for segment {i}: '{text}'")

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tmp_path = tmp_file.name

            # Run async edge-tts synthesis
            asyncio.get_event_loop().run_until_complete(
                _synthesize_segment(text, voice, tmp_path)
            )

            # Load the MP3 back as numpy array via librosa
            import librosa
            wav_data, _ = librosa.load(tmp_path, sr=sample_rate, mono=True)
            os.unlink(tmp_path)

            # Place on timeline at the correct start timestamp
            start_sample = int(start_time * sample_rate)
            end_sample = start_sample + len(wav_data)

            if end_sample > total_samples:
                padding = np.zeros(end_sample - total_samples, dtype=np.float32)
                final_audio = np.concatenate((final_audio, padding))
                total_samples = len(final_audio)

            final_audio[start_sample:end_sample] += wav_data.astype(np.float32)

        except Exception as e:
            logger.warning(f"Failed TTS for segment {i}: {e}")
            logger.debug(traceback.format_exc())
            continue

        if progress_callback:
            progress_callback((idx + 1) / len(valid_segments),
                              f"Generated TTS for {idx + 1}/{len(valid_segments)} segments.")

    # Normalize to avoid clipping
    max_val = np.max(np.abs(final_audio))
    if max_val > 0:
        final_audio = final_audio / max_val

    logger.info(f"Saving combined dubbed audio to: {output_audio_path}")
    wavfile.write(output_audio_path, sample_rate, final_audio)
    return output_audio_path
