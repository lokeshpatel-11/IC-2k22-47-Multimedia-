import os
import requests
import time

def clone_and_generate(api_key, text, audio_sample_path, output_path):
    """
    Step 1: Create a voice clone using ElevenLabs API
    Step 2: Generate speech from text using the cloned voice
    """
    
    headers = {
        "xi-api-key": api_key
    }
    
    print("\n[1/3] Uploading your voice sample to ElevenLabs for cloning...")
    
    # 1. Add Voice API Endpoint
    add_voice_url = "https://api.elevenlabs.io/v1/voices/add"
    
    # Prepare form data
    data = {
        "name": f"Clone_{int(time.time())}",
        "description": "Voice clone for Multimedia Lab"
    }
    
    with open(audio_sample_path, 'rb') as f:
        files = {
            'files': (os.path.basename(audio_sample_path), f, 'audio/ogg')
        }
        
        response = requests.post(add_voice_url, headers=headers, data=data, files=files)
        
    if response.status_code != 200:
        print("\nError cloning voice. Make sure you have a paid ElevenLabs account (Instant Voice Cloning is not available on free tier).")
        print(f"Details: {response.text}")
        return
        
    voice_id = response.json().get("voice_id")
    print(f"Success! Voice ID generated: {voice_id}")
    
    print("\n[2/3] Sending text to ElevenLabs Text-to-Speech API...")
    
    # 2. Text to Speech API Endpoint
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    tts_headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    tts_data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    tts_response = requests.post(tts_url, headers=tts_headers, json=tts_data)
    
    if tts_response.status_code != 200:
        print(f"\nError generating speech: {tts_response.text}")
        return
        
    print(f"\n[3/3] Saving generated audio to {output_path}...")
    
    # 3. Save the audio file
    with open(output_path, 'wb') as f:
        f.write(tts_response.content)
        
    print(f"\nTask Completed! The cloned audio is ready at: {output_path}")


def main():
    print("=" * 50)
    print("ELEVENLABS VOICE CLONING (CLOUD API)")
    print("=" * 50)
    
    # Get API Key
    api_key = input("Enter your ElevenLabs API Key: ").strip()
    if not api_key:
        print("API Key is required! Exiting...")
        return
        
    # Get Text to Speak
    text = input("\nEnter the text you want your cloned voice to speak:\n> ").strip()
    if not text:
        print("Text is required! Exiting...")
        return

    # Fixed Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_voice = os.path.join(script_dir, "sample_voice.ogg")
    output_audio = os.path.join(script_dir, "cloned_speech_output.mp3")
    
    if not os.path.exists(sample_voice):
        print(f"\nError: Could not find the sample voice file at {sample_voice}")
        print("Please place an audio file named 'sample_voice.ogg' in the same folder.")
        return
        
    clone_and_generate(api_key, text, sample_voice, output_audio)

if __name__ == "__main__":
    main()
