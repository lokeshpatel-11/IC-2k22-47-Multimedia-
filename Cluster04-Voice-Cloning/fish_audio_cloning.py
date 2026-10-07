import os
import requests
from dotenv import load_dotenv


def main():

    print("=" * 60)
    print("FISH AUDIO - FREE S2.1 PRO TTS")
    print("=" * 60)

    # Load .env
    load_dotenv()

    api_key = os.getenv("FISH_API_KEY")

    if not api_key:
        print("\n❌ FISH_API_KEY not found.")
        print("Create .env file:")
        print("FISH_API_KEY=your_api_key")
        return

    # Get text
    text = input("\nEnter the text you want the AI to speak:\n> ").strip()

    if not text:
        print("❌ Text is required.")
        return

    # Optional reference voice
    reference_id = input(
        "\nEnter Voice Reference ID "
        "(press Enter for normal AI voice):\n> "
    ).strip()

    # API
    url = "https://api.fish.audio/v1/tts"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",

        # IMPORTANT
        "model": "s2.1-pro-free"
    }

    body = {
        "text": text,
        "format": "mp3"
    }

    # Add cloned voice if provided
    if reference_id:
        body["reference_id"] = reference_id

    try:

        print("\n[Processing] Sending request...")
        print("Model: s2.1-pro-free")

        response = requests.post(
            url,
            headers=headers,
            json=body
        )

        # Error handling
        if not response.ok:

            print("\n❌ API Error")
            print("Status:", response.status_code)
            print("Message:", response.text)

            return

        # Save audio
        output_file = "fish_audio_output.mp3"

        with open(output_file, "wb") as f:
            f.write(response.content)

        print("\n✅ SUCCESS!")
        print("Audio saved as:")
        print(output_file)

    except Exception as e:

        print("\n❌ Error:")
        print(e)


if __name__ == "__main__":
    main()