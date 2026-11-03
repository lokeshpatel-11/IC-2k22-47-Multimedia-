import os
import time

from pathlib import Path

import requests
from dotenv import load_dotenv

API_URL = "https://api.fish.audio/v1/tts"
MODEL_NAME = "s2.1-pro-free"


def generate_speech(text, api_key, voice_id, output_file):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "model": MODEL_NAME,
    }

    payload = {
        "text": text,
        "format": "mp3",
    }

    # Use a saved voice only when the user provides its ID.
    if voice_id:
        payload["reference_id"] = voice_id

    print("\nGenerating speech. Please wait...")

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )

        if not response.ok:
            print("\nSpeech generation failed.")
            print(f"HTTP status: {response.status_code}")

            try:
                print("Details:", response.json())
            except ValueError:
                print("Details:", response.text[:500])

            return

        if not response.content:
            print("Error: The API returned an empty audio file.")
            return

        destination = Path(output_file).expanduser()

        if destination.suffix.lower() != ".mp3":
            destination = destination.with_suffix(".mp3")

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)

        print("\nSpeech generated successfully!")
        print(f"Saved file: {destination.resolve()}")
        print(f"File size: {destination.stat().st_size:,} bytes")

    except requests.Timeout:
        print("Error: Request timed out. Please try again.")

    except requests.RequestException as error:
        print(f"Network error: {error}")

    except OSError as error:
        print(f"File saving error: {error}")


def main():
    load_dotenv()

    print("=" * 45)
    print("       AI VOICE GENERATION SYSTEM")
    print("=" * 45)

    api_key = os.getenv("FISH_API_KEY")

    if not api_key or api_key == "your_actual_api_key_here":
        print("\nAPI key is missing.")
        print("Add your valid FISH_API_KEY to the .env file.")
        return

    # Validate the menu choice.
    while True:
        print("\nSelect a voice option:")
        print("1. Standard model voice")
        print("2. Existing saved voice")

        choice = input("Enter choice (1 or 2): ").strip()

        if choice in ("1", "2"):
            break

        print("Invalid input! Enter only 1 or 2.")

    voice_id = ""

    if choice == "2":
        voice_id = input(
            "Enter your saved voice reference ID: "
        ).strip()

        if not voice_id:
            print("Voice reference ID cannot be empty.")
            return

    text = input(
        "\nEnter the text you want to convert into speech:\n> "
    ).strip()

    if not text:
        print("Text cannot be empty.")
        return

    output_file = input(
        "\nEnter output filename "
        "(press Enter for generated_voice.mp3): "
    ).strip()

    if not output_file:
        output_file = "generated_voice.mp3"

    if not output_file.lower().endswith(".mp3"):
        output_file += ".mp3"

    generate_speech(
        text,
        api_key,
        voice_id,
        output_file,
    )


if __name__ == "__main__":
    main()
