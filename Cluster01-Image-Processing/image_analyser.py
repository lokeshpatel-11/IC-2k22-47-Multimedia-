import os
import sys
from PIL import Image, ExifTags


def format_file_size(size_in_bytes):
    """
    Convert file size from bytes to KB, MB, GB, etc.
    """

    units = ["Bytes", "KB", "MB", "GB", "TB"]
    size = float(size_in_bytes)

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"


def get_exif_data(image):
    """
    Extract EXIF metadata from the image.
    """

    exif_data = {}

    try:
        raw_exif = image.getexif()

        for tag_id, value in raw_exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            exif_data[tag_name] = value

    except Exception:
        pass

    return exif_data


def get_resolution(image):
    """
    Get image DPI / resolution if available.
    """

    dpi = image.info.get("dpi")

    if dpi:
        return f"{dpi[0]} x {dpi[1]} DPI"

    return "Not Available"


def print_exif_metadata(exif_data):
    """
    Print important EXIF metadata.
    """

    print("\nEXIF Metadata")
    print("-" * 31)

    important_fields = {
        "Camera": "Model",
        "Date Taken": "DateTimeOriginal",
        "Date Modified": "DateTime",
        "Orientation": "Orientation",
        "Make": "Make",
        "Software": "Software",
    }

    for display_name, exif_key in important_fields.items():

        value = exif_data.get(exif_key, "Not Available")

        print(f"{display_name:<16}: {value}")

    # Print remaining EXIF metadata
    other_exif = {
        key: value
        for key, value in exif_data.items()
        if key not in important_fields.values()
    }

    if other_exif:
        print("\nOther EXIF Data")
        print("-" * 31)

        for key, value in other_exif.items():
            print(f"{key:<25}: {value}")


def analyze_image(image_path):
    """
    Analyze image and print metadata report.
    """

    # Check whether file exists
    if not os.path.exists(image_path):
        print("Error: File not found.")
        return

    # Check supported formats
    supported_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".tif",
        ".webp",
        ".bmp"
    ]

    extension = os.path.splitext(image_path)[1].lower()

    if extension not in supported_extensions:
        print("Error: Unsupported image format.")
        print("Supported formats: JPG, JPEG, PNG, TIFF, WEBP, BMP")
        return

    try:
        with Image.open(image_path) as image:

            file_name = os.path.basename(image_path)
            file_size = os.path.getsize(image_path)

            width, height = image.size

            exif_data = get_exif_data(image)

            print("=" * 32)
            print("IMAGE METADATA REPORT")
            print("=" * 32)

            print(f"\nFile Name       : {file_name}")
            print(f"File Size       : {format_file_size(file_size)}")
            print(f"File Format     : {image.format}")
            print(f"Width           : {width} pixels")
            print(f"Height          : {height} pixels")
            print(f"Resolution      : {get_resolution(image)}")
            print(f"Color Mode      : {image.mode}")

            print_exif_metadata(exif_data)

            print("\n" + "=" * 32)
            print("REPORT COMPLETED")
            print("=" * 32)

    except Exception as error:
        print(f"Error while analyzing image: {error}")


def main():

    print("Image Analyzer")
    print("-" * 30)

    # Take image path from user
    image_path = "/Users/sachinyaduwanshi/Desktop/mm_lab/Multimedia-Systems-Lab/Cluster02-Image-Processing/image_analyser.py"


if __name__ == "__main__":
    main()