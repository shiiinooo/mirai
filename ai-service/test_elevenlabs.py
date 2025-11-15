"""
Simple test script for Eleven Labs TTS integration.

Usage:
    python test_elevenlabs.py
"""

import os
from dotenv import load_dotenv
from trip_planner.utils.tts import generate_audio_from_text

# Load environment variables
load_dotenv()

def test_elevenlabs_tts():
    """Test Eleven Labs text-to-speech conversion."""
    
    # Check if API key is set
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment variables")
        print("   Please set it in your .env file or environment")
        return False
    
    print("✅ ELEVENLABS_API_KEY found")
    print("\n🎤 Testing Eleven Labs TTS...")
    
    # Test text (a short story similar to what we generate)
    test_text = "Welcome to the Eiffel Tower, one of the most iconic landmarks in the world. As you stand beneath its magnificent iron lattice, you'll feel the pulse of Paris around you. This architectural marvel offers breathtaking views and a glimpse into the city's rich history."
    
    print(f"📝 Test text: {test_text[:100]}...")
    print(f"📏 Text length: {len(test_text)} characters")
    
    try:
        # Generate audio
        print("\n🔄 Generating audio...")
        audio_bytes = generate_audio_from_text(test_text)
        
        # Save to file
        output_file = "test_audio_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        file_size = len(audio_bytes)
        print(f"✅ Audio generated successfully!")
        print(f"📦 File saved: {output_file}")
        print(f"📊 File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        
        # Estimate duration (rough estimate: ~150 words per minute, ~2 bytes per character)
        estimated_duration = len(test_text.split()) / 150 * 60
        print(f"⏱️  Estimated duration: ~{estimated_duration:.1f} seconds")
        
        print("\n🎉 Test completed successfully!")
        print(f"   You can play the audio file: {output_file}")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Eleven Labs TTS Integration Test")
    print("=" * 60)
    print()
    
    success = test_elevenlabs_tts()
    
    print()
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Test failed - check errors above")
    print("=" * 60)

