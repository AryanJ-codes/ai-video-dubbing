from deep_translator import GoogleTranslator
from utils import logger
from config import SOURCE_LANGUAGE, TARGET_LANGUAGE
import time
import copy

def translate_segments(segments: list, progress_callback=None) -> list:
    """
    Translates the transcribed text segments from source to target language.
    Preserves the start and end timestamps.
    """
    logger.info(f"Translating {len(segments)} segments from {SOURCE_LANGUAGE} to {TARGET_LANGUAGE}...")
    
    translator = GoogleTranslator(source=SOURCE_LANGUAGE, target=TARGET_LANGUAGE)
    
    translated_segments = []
    
    for i, segment in enumerate(segments):
        original_text = segment['text'].strip()
        
        if not original_text:
            translated_text = ""
        else:
            try:
                # deep-translator might fail occasionally, adding simple try-catch block
                translated_text = translator.translate(original_text)
                
                # Small sleep to avoid hitting rate limits too fast (optional depending on API)
                time.sleep(0.3)
                
            except Exception as e:
                logger.warning(f"Translation failed for segment {i}: '{original_text}'. Error: {e}")
                # Fallback to empty or original text
                translated_text = original_text
                
        # Create a new dictionary to avoid modifying the original list implicitly
        new_segment = copy.deepcopy(segment)
        new_segment['text'] = translated_text
        translated_segments.append(new_segment)
        
        # Log progress periodically
        if (i + 1) % 10 == 0:
            logger.info(f"Translated {i + 1}/{len(segments)} segments.")
            
    logger.info("Translation complete.")
    return translated_segments
