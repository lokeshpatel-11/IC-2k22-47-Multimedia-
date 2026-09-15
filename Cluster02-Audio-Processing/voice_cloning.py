import os
import shutil

try:
    from gradio_client import Client, handle_file
except ImportError:
    print("Error: 'gradio_client' is not installed.")
    print("Please install it by running: pip install gradio_client")
    exit(1)

def clone_voice(text, speaker_audio_path, output_audio_path, language="en"):
    """
    Clone a voice from an input audio file and generate speech for the given text.
    Uses the free MyShell OpenVoice API via HuggingFace Spaces.
    """
    if not os.path.exists(speaker_audio_path):
        print(f"\nError: Input audio file not found at '{speaker_audio_path}'")
        print("Please check the path and try again.")
        return

    if not os.path.isfile(speaker_audio_path):
        print(f"\nError: Provided path '{speaker_audio_path}' is not a file.")
        return

    try:
        print("\nConnecting to OpenVoice AI Model...")
        print("This is completely free and requires no heavy downloads.")
        
        # Connect to the HuggingFace space for OpenVoice
        client = Client("myshell-ai/OpenVoice")

        print("\nModel connected successfully.")
        print(f"Generating audio for text: '{text}'")
        print(f"Cloning voice from: '{speaker_audio_path}'")
        print("Processing... Please wait a few seconds.")
        
        # Call the API endpoint
        result = client.predict(
            text,
            "default", # style
            handle_file(speaker_audio_path),
            True,
            fn_index=1
        )
        
        # The API returns a tuple: (info_text, generated_audio_path, reference_audio_path)
        generated_audio_temp_path = result[1]
        
        if not generated_audio_temp_path:
            print("\nError: The model did not return any audio.")
            return
            
        # Copy the generated audio from temp directory to the user's desired output path
        shutil.copy2(generated_audio_temp_path, output_audio_path)
        
        print(f"\nSuccess! Cloned audio saved to: {output_audio_path}")

    except Exception as error:
        print(f"\nError while cloning voice: {error}")
        print("\nNote: Make sure you have an active internet connection.")

def main():
    print("=" * 40)
    print("AI VOICE CLONING TOOL (FAST & FREE)")
    print("=" * 40)

    # Example configuration (Change these paths as needed)
    
    # 1. Path to your sample voice (Provide an existing mp3/wav/ogg file)
    speaker_audio_path = "/Users/sachinyaduwanshi/Desktop/mm_lab/Cluster02-Audio-Processing/audio.ogg" 
    
    # 2. Where to save the final cloned audio
    output_audio_path = "/Users/sachinyaduwanshi/Desktop/mm_lab/cloned_output.wav" 
    
    # 3. Text to speak
    text = "Hello, this is a test of voice cloning using OpenVoice! It works instantly without heavy downloads."

    # Remove quotes if user copies a path with quotes
    speaker_audio_path = speaker_audio_path.strip('"').strip("'")
    output_audio_path = output_audio_path.strip('"').strip("'")

    clone_voice(text, speaker_audio_path, output_audio_path)


if __name__ == "__main__":
    main()
