import os
import json
import shutil
import subprocess
from pathlib import Path


def format_size(size_bytes):
    """Convert bytes into a readable file size."""
    size = float(size_bytes)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def format_duration(value):
    """Convert duration in seconds to HH:MM:SS."""
    try:
        seconds = float(value)
        if seconds < 0:
            return "Not Available"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining = seconds % 60

        return f"{hours:02}:{minutes:02}:{remaining:06.3f}"

    except (ValueError, TypeError):
        return "Not Available"


def get_field(data, key):
    """Return a metadata value or a fallback."""
    value = data.get(key)
    return value if value not in (None, "") else "Not Available"


def show_field(label, value):
    """Print a consistently aligned report field."""
    if value is None or value == "":
        value = "Not Available"

    print(f"{label:<22} : {value}")


def show_heading(title):
    print(f"\n{'-' * 46}")
    print(f"{title}")
    print("-" * 46)


def convert_bitrate(value):
    """Convert bits per second to kilobits per second."""
    try:
        return f"{int(value) / 1000:.2f} kbps"
    except (ValueError, TypeError):
        return "Not Available"


def calculate_fps(value):
    """Calculate frames per second from a fraction."""
    try:
        numerator, denominator = value.split("/")
        denominator = float(denominator)

        if denominator == 0:
            return "Not Available"

        return f"{float(numerator) / denominator:.2f} fps"

    except (ValueError, TypeError, AttributeError):
        return "Not Available"


def read_video_info(file_path):
    """Extract media details using FFprobe."""
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
        raise RuntimeError(
            result.stderr.strip() or "FFprobe could not read this file."
        )

    return json.loads(result.stdout)


def separate_streams(streams):
    """Identify the first video and audio streams."""
    video = None
    audio = None

    for stream in streams:
        stream_type = stream.get("codec_type")

        if stream_type == "video" and video is None:
            video = stream
        elif stream_type == "audio" and audio is None:
            audio = stream

    return video, audio


def print_tags(title, tags):
    """Display available metadata tags."""
    show_heading(title)

    if not tags:
        print("No metadata tags available.")
        return

    for key, value in sorted(tags.items()):
        show_field(str(key).replace("_", " ").title(), value)


def analyze_video(file_name):
    """Generate a report for a video or media file."""
    path = Path(file_name).expanduser()

    if not path.exists():
        print("\nError: The specified file does not exist.")
        return

    if not path.is_file():
        print("\nError: Please provide a file path, not a folder.")
        return

    if shutil.which("ffprobe") is None:
        print("\nError: FFprobe is not installed or not in PATH.")
        print("Please install FFmpeg and restart your terminal.")
        return

    try:
        metadata = read_video_info(path)

        file_info = metadata.get("format", {})
        streams = metadata.get("streams", [])
        video, audio = separate_streams(streams)

        if video is None:
            print("\nError: No video stream was found in this file.")
            return

        print("\n" + "=" * 46)
        print("          VIDEO INSPECTION REPORT")
        print("=" * 46)

        # File details
        show_heading("1. FILE INFORMATION")
        show_field("File Name", path.name)
        show_field("File Extension", path.suffix.upper() or "None")
        show_field("File Size", format_size(path.stat().st_size))

        # Container details
        show_heading("2. CONTAINER INFORMATION")
        show_field("Format", get_field(file_info, "format_long_name"))
        show_field("Format Identifier", get_field(file_info, "format_name"))
        show_field(
            "Duration",
            format_duration(file_info.get("duration"))
        )
        show_field(
            "Overall Bitrate",
            convert_bitrate(file_info.get("bit_rate"))
        )
        show_field("Start Time", get_field(file_info, "start_time"))

        # Video details
        show_heading("3. VIDEO STREAM DETAILS")
        show_field("Video Codec", get_field(video, "codec_long_name"))
        show_field("Codec Identifier", get_field(video, "codec_name"))

        width = video.get("width")
        height = video.get("height")

        resolution = (
            f"{width} x {height}"
            if width and height
            else "Not Available"
        )
        show_field("Resolution", resolution)

        show_field(
            "Frame Rate",
            calculate_fps(video.get("avg_frame_rate"))
        )
        show_field("Video Bitrate", convert_bitrate(video.get("bit_rate")))
        show_field(
            "Display Aspect Ratio",
            get_field(video, "display_aspect_ratio")
        )
        show_field("Pixel Format", get_field(video, "pix_fmt"))
        show_field("Pixel Format Profile", get_field(video, "profile"))

        # Audio details
        show_heading("4. AUDIO STREAM DETAILS")

        if audio:
            show_field("Audio Codec", get_field(audio, "codec_long_name"))
            show_field("Codec Identifier", get_field(audio, "codec_name"))

            rate = audio.get("sample_rate")
            show_field(
                "Sample Rate",
                f"{rate} Hz" if rate else "Not Available"
            )
            show_field("Channels", get_field(audio, "channels"))
            show_field("Channel Layout", get_field(audio, "channel_layout"))
            show_field("Sample Format", get_field(audio, "sample_fmt"))
            show_field("Audio Bitrate", convert_bitrate(audio.get("bit_rate")))
        else:
            print("No audio stream is present.")

        # Metadata tags
        print_tags("5. FILE METADATA", file_info.get("tags", {}))

        if video.get("tags"):
            print_tags("6. VIDEO STREAM METADATA", video["tags"])

        print("\n" + "=" * 46)
        print("          REPORT GENERATED")
        print("=" * 46)

    except subprocess.TimeoutExpired:
        print("\nError: Analysis timed out after 60 seconds.")
    except (OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"\nError while analyzing the video: {error}")


def main():
    print("\n" + "*" * 46)
    print("          VIDEO FILE INSPECTOR")
    print("*" * 46)
    print("Enter the complete path to your video file.")

    file_name = input("Video path: ").strip().strip('"').strip("'")

    if not file_name:
        print("No file path entered.")
        return

    analyze_video(file_name)


if __name__ == "__main__":
    main()