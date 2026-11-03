import os
import json
import shutil
import subprocess
from pathlib import Path


def readable_size(byte_count):
    """Convert a file size into a readable unit."""
    size = float(byte_count)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def readable_duration(seconds):
    """Convert seconds into HH:MM:SS format."""
    try:
        total_seconds = float(seconds)
        if total_seconds < 0:
            return "Not Available"

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        remaining = total_seconds % 60

        return f"{hours:02}:{minutes:02}:{remaining:06.3f}"

    except (ValueError, TypeError):
        return "Not Available"


def get_value(data, key):
    """Return a value or a fallback message."""
    value = data.get(key)
    return value if value not in (None, "") else "Not Available"


def show_item(label, value):
    """Display one report field neatly."""
    print(f"{label:<23} : {value}")


def show_section(title):
    """Print a section heading."""
    print(f"\n--- {title} ---")


def fetch_metadata(file_path):
    """Read media information through FFprobe."""
    command = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(file_path)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=60,
        check=False
    )

    if result.returncode != 0:
        message = result.stderr.strip()
        raise RuntimeError(message or "Unable to read this media file.")

    return json.loads(result.stdout)


def find_audio_stream(streams):
    """Return the first audio stream, if present."""
    for stream in streams:
        if stream.get("codec_type") == "audio":
            return stream
    return None


def bitrate_kbps(value):
    """Convert a bitrate in bits per second to kbps."""
    try:
        return f"{int(value) / 1000:.2f} kbps"
    except (ValueError, TypeError):
        return "Not Available"


def display_tags(title, tags):
    """Display available metadata tags."""
    show_section(title)

    if not tags:
        print("No metadata tags were found.")
        return

    for key, value in sorted(tags.items()):
        show_item(str(key).replace("_", " ").title(), value)


def analyze_audio(file_path):
    """Generate an audio information report."""
    path = Path(file_path).expanduser()

    if not path.exists():
        print("\nError: The specified file does not exist.")
        return

    if not path.is_file():
        print("\nError: Please enter a file path, not a folder.")
        return

    if shutil.which("ffprobe") is None:
        print("\nError: FFprobe was not found.")
        print("Install FFmpeg and add it to your system PATH.")
        return

    try:
        metadata = fetch_metadata(path)
        file_info = metadata.get("format", {})
        streams = metadata.get("streams", [])
        audio = find_audio_stream(streams)

        if audio is None:
            print("\nError: No audio stream was found in this file.")
            return

        print("\n" + "=" * 48)
        print("         MULTIMEDIA AUDIO REPORT")
        print("=" * 48)

        show_section("FILE DETAILS")
        show_item("Name", path.name)
        show_item("Extension", path.suffix.upper() or "None")
        show_item("File Size", readable_size(path.stat().st_size))

        show_section("FORMAT DETAILS")
        show_item("Format", get_value(file_info, "format_long_name"))
        show_item("Format Identifier", get_value(file_info, "format_name"))
        show_item(
            "Duration",
            readable_duration(file_info.get("duration"))
        )
        show_item("Overall Bitrate", bitrate_kbps(file_info.get("bit_rate")))
        show_item("Start Time", get_value(file_info, "start_time"))

        show_section("AUDIO STREAM")
        show_item("Codec", get_value(audio, "codec_long_name"))
        show_item("Codec Identifier", get_value(audio, "codec_name"))

        sample_rate = audio.get("sample_rate")
        show_item(
            "Sample Rate",
            f"{sample_rate} Hz" if sample_rate else "Not Available"
        )

        show_item("Channels", get_value(audio, "channels"))
        show_item("Channel Layout", get_value(audio, "channel_layout"))
        show_item("Sample Format", get_value(audio, "sample_fmt"))
        show_item("Stream Bitrate", bitrate_kbps(audio.get("bit_rate")))
        show_item("Bits Per Sample", get_value(audio, "bits_per_sample"))
        show_item(
            "Raw Bits Per Sample",
            get_value(audio, "bits_per_raw_sample")
        )
        show_item("Frame Count", get_value(audio, "nb_frames"))

        display_tags("FILE METADATA TAGS", file_info.get("tags", {}))

        if audio.get("tags"):
            display_tags("AUDIO STREAM TAGS", audio["tags"])

        print("\n" + "=" * 48)
        print("       ANALYSIS FINISHED SUCCESSFULLY")
        print("=" * 48)

    except subprocess.TimeoutExpired:
        print("\nError: FFprobe took too long to analyze the file.")
    except (OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"\nUnable to analyze audio: {error}")


def main():
    print("\n" + "*" * 48)
    print("          AUDIO FILE INFORMATION TOOL")
    print("*" * 48)

    print("Enter the full path of an audio or media file.")
    file_path = input("File path: ").strip().strip('"').strip("'")

    if not file_path:
        print("No file path was entered.")
        return

    analyze_audio(file_path)


if __name__ == "__main__":
    main()