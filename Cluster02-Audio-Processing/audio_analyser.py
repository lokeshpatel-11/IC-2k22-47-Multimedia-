import os
import json
import subprocess
import shutil
from pathlib import Path


def format_file_size(size_in_bytes):
    """Convert bytes into readable file size."""

    size = float(size_in_bytes)

    units = ["Bytes", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def format_duration(seconds):
    """Convert duration from seconds to HH:MM:SS."""

    try:
        seconds = float(seconds)

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60

        return f"{hours:02}:{minutes:02}:{seconds:06.3f}"

    except (ValueError, TypeError):
        return "Not Available"


def check_ffprobe():
    """Check whether FFprobe is installed."""

    return shutil.which("ffprobe") is not None


def get_audio_metadata(audio_path):
    """
    Extract audio metadata using FFprobe.
    """

    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        audio_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return json.loads(result.stdout)


def get_audio_stream(streams):
    """Find and return the first audio stream."""

    for stream in streams:
        if stream.get("codec_type") == "audio":
            return stream

    return None


def print_tag(label, value):
    """Print metadata in a formatted way."""

    if value is None or value == "":
        value = "Not Available"

    print(f"{label:<20}: {value}")


def print_tags(tags):
    """Print all available metadata tags."""

    if not tags:
        print("No additional metadata available.")
        return

    for key, value in tags.items():
        print(f"{key:<25}: {value}")


def analyze_audio(audio_path):
    """Analyze an audio file and generate metadata report."""

    if not os.path.exists(audio_path):
        print("\nError: Audio file not found.")
        return

    if not os.path.isfile(audio_path):
        print("\nError: Provided path is not a file.")
        return

    if not check_ffprobe():
        print("\nError: FFprobe is not installed or not added to PATH.")
        print("Please install FFmpeg first.")
        return

    try:
        metadata = get_audio_metadata(audio_path)

        file_path = Path(audio_path)
        file_size = os.path.getsize(audio_path)

        format_data = metadata.get("format", {})
        streams = metadata.get("streams", [])

        audio_stream = get_audio_stream(streams)

        print()
        print("=" * 40)
        print("AUDIO METADATA REPORT")
        print("=" * 40)

        # Basic File Information

        print("\nBasic Information")
        print("-" * 40)

        print_tag("File Name", file_path.name)
        print_tag("File Extension", file_path.suffix.upper())
        print_tag("File Size", format_file_size(file_size))

        # Format Information

        print("\nFormat Information")
        print("-" * 40)

        print_tag(
            "File Format",
            format_data.get("format_long_name")
        )

        print_tag(
            "Format Name",
            format_data.get("format_name")
        )

        print_tag(
            "Duration",
            format_duration(format_data.get("duration"))
        )

        print_tag(
            "Bit Rate",
            (
                f"{int(format_data.get('bit_rate')) / 1000:.2f} kbps"
                if format_data.get("bit_rate")
                else "Not Available"
            )
        )

        print_tag(
            "Start Time",
            format_data.get("start_time")
        )

        # Audio Stream Information

        print("\nAudio Properties")
        print("-" * 40)

        if audio_stream:

            print_tag(
                "Codec",
                audio_stream.get("codec_long_name")
            )

            print_tag(
                "Codec Name",
                audio_stream.get("codec_name")
            )

            print_tag(
                "Sample Rate",
                (
                    f"{audio_stream.get('sample_rate')} Hz"
                    if audio_stream.get("sample_rate")
                    else "Not Available"
                )
            )

            print_tag(
                "Channels",
                audio_stream.get("channels")
            )

            print_tag(
                "Channel Layout",
                audio_stream.get("channel_layout")
            )

            print_tag(
                "Sample Format",
                audio_stream.get("sample_fmt")
            )

            print_tag(
                "Bit Rate",
                (
                    f"{int(audio_stream.get('bit_rate')) / 1000:.2f} kbps"
                    if audio_stream.get("bit_rate")
                    else "Not Available"
                )
            )

            print_tag(
                "Bits Per Sample",
                audio_stream.get("bits_per_sample")
            )

            print_tag(
                "Bits Per Raw Sample",
                audio_stream.get("bits_per_raw_sample")
            )

            print_tag(
                "Number of Frames",
                audio_stream.get("nb_frames")
            )

        else:
            print("No audio stream found.")

        # Metadata Tags

        print("\nAudio Metadata / Tags")
        print("-" * 40)

        format_tags = format_data.get("tags", {})

        print_tags(format_tags)

        # Stream Metadata

        if audio_stream:

            stream_tags = audio_stream.get("tags", {})

            if stream_tags:
                print("\nStream Metadata")
                print("-" * 40)

                print_tags(stream_tags)

        print("\n" + "=" * 40)
        print("REPORT COMPLETED")
        print("=" * 40)

    except Exception as error:
        print(f"\nError while processing audio: {error}")


def main():

    print("=" * 40)
    print("AUDIO FILE ANALYZER")
    print("=" * 40)

    audio_path = "/Users/sachinyaduwanshi/Desktop/mm_lab/audio.ogg"

    # Remove quotes if user copies a path with quotes
    audio_path = audio_path.strip('"').strip("'")

    analyze_audio(audio_path)


if __name__ == "__main__":
    main()