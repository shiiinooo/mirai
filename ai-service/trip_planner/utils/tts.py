"""Text-to-Speech utilities using Eleven Labs API."""

import os
from typing import Optional
from elevenlabs import ElevenLabs


def initialize_elevenlabs():
    """Initialize Eleven Labs client from environment."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
    return ElevenLabs(api_key=api_key)


def generate_audio_from_text(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """
    Generate audio from text using Eleven Labs TTS.
    
    Args:
        text: The text to convert to speech
        voice_id: Eleven Labs voice ID (default is a neutral voice)
        
    Returns:
        Audio bytes in MP3 format
        
    Raises:
        ValueError: If API key is not set
        Exception: If TTS generation fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    try:
        # Initialize client
        client = initialize_elevenlabs()
        
        # Generate audio with optimized settings for short stories
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_monolingual_v1",
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        )
        
        # Read all audio bytes
        audio_bytes = b"".join(audio)
        
        return audio_bytes
        
    except Exception as e:
        raise Exception(f"Failed to generate audio: {str(e)}")

