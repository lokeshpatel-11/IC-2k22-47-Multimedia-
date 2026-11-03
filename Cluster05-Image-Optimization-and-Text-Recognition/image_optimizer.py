from pathlib import Path

import cv2
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


# =========================================================
# CONFIGURATION
# =========================================================

TESSERACT_EXE = r"E:\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

# Save output in the same folder as this Python script.
REPOSITORY_FOLDER = Path(__file__).resolve().parent


# =========================================================
# CHECK TESSERACT
# =========================================================

def check_tesseract():
    if not Path(TESSERACT_EXE).is_file():
        print("ERROR: Tesseract not found:", TESSERACT_EXE)
        return False

    try:
        languages = pytesseract.get_languages(config="")
        if "eng" not in languages:
            print("ERROR: English OCR language data is missing.")
            return False
        return True
    except Exception as error:
        print("Tesseract check failed:", error)
        return False


# =========================================================
# GET OPTIMIZED IMAGE NAME AND FORMAT
# =========================================================

def get_output_image_path():
    image_name = input(
        "\nEnter the optimized image name (without extension): "
    ).strip()

    if not image_name:
        print("ERROR: Image name cannot be empty.")
        return None

    # Prevent a path or folder from being entered as the name.
    if Path(image_name).name != image_name or "/" in image_name or "\\" in image_name:
        print("ERROR: Enter only a filename, not a path.")
        return None

    print("\nChoose output image format:")
    print("1. WebP")
    print("2. JPEG")
    print("3. PNG")

    format_choice = input("Enter your choice (1-3): ").strip()

    formats = {
        "1": (".webp", "WEBP"),
        "2": (".jpg", "JPEG"),
        "3": (".png", "PNG"),
    }

    if format_choice not in formats:
        print("ERROR: Invalid format choice.")
        return None

    extension, image_format = formats[format_choice]

    # Remove a supported extension if the user typed one anyway.
    supplied_path = Path(image_name)
    if supplied_path.suffix.lower() in (".webp", ".jpg", ".jpeg", ".png"):
        image_name = supplied_path.stem

    if not image_name:
        print("ERROR: Invalid image name.")
        return None

    destination = REPOSITORY_FOLDER / (image_name + extension)
    return destination, image_format


# =========================================================
# IMAGE OPTIMIZATION
# =========================================================

def optimize_image(image_path=None):
    if image_path is None:
        image_path = input(
            "\nEnter the full path of the original image: "
        ).strip().strip('"')

    source = Path(image_path)

    if not source.is_file():
        print("ERROR: Image file not found:", source)
        return None

    output = get_output_image_path()

    if output is None:
        return None

    destination, image_format = output

    # Avoid accidentally overwriting the original image.
    try:
        if source.resolve() == destination.resolve():
            print("ERROR: Output name matches the original image.")
            print("Choose a different optimized image name.")
            return None
    except OSError:
        pass

    try:
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original).copy()

        print("\nOriginal dimensions:", image.size)
        print(f"Original size: {source.stat().st_size:,} bytes")

        # Resize only if larger than the maximum dimensions.
        image.thumbnail(
            (1920, 1080),
            Image.Resampling.LANCZOS
        )

        # Apply mild contrast and sharpness enhancement.
        image = ImageEnhance.Contrast(image).enhance(1.05)
        image = ImageEnhance.Sharpness(image).enhance(1.10)
        image = image.filter(
            ImageFilter.UnsharpMask(
                radius=1,
                percent=110,
                threshold=3
            )
        )

        REPOSITORY_FOLDER.mkdir(parents=True, exist_ok=True)

        if image_format == "JPEG":
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            image.save(
                destination,
                "JPEG",
                quality=85,
                optimize=True
            )

        elif image_format == "PNG":
            image.save(
                destination,
                "PNG",
                optimize=True
            )

        elif image_format == "WEBP":
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")

            image.save(
                destination,
                "WEBP",
                quality=85,
                method=6
            )

        print("\nImage optimization completed!")
        print("Saved image:", destination)
        print("Output dimensions:", image.size)
        print(f"Output size: {destination.stat().st_size:,} bytes")

        return str(destination)

    except Exception as error:
        print("Image optimization failed:", error)
        return None


# =========================================================
# TEXT RECOGNITION (OCR)
# =========================================================

def extract_text(image_path=None):
    if not check_tesseract():
        return None

    if image_path is None:
        image_path = input(
            "\nEnter the full path of the image to read: "
        ).strip().strip('"')

    source = Path(image_path)

    if not source.is_file():
        print("ERROR: Image file not found:", source)
        return None

    try:
        image = cv2.imread(str(source))

        if image is None:
            print("ERROR: Could not open image:", source)
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Enlarge small images to improve recognition.
        height, width = gray.shape

        if width < 1600:
            scale = 1600 / width
            gray = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )

        threshold = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        print("\nReading text from image...")

        # PSM 8 worked best for your test image.
        attempts = [
            ("Grayscale", gray),
            ("Otsu threshold", threshold)
        ]

        results = []

        for method_name, processed in attempts:
            text = pytesseract.image_to_string(
                processed,
                lang="eng",
                config="--oem 3 --psm 8"
            ).strip()

            if text:
                results.append((method_name, text))

        if not results:
            print("No text detected in this image.")
            return None

        method_name, recognized_text = results[0]

        print(f"\n--- OCR Results ({method_name}) ---")
        print(recognized_text)

        if len(results) > 1 and results[1][1] != recognized_text:
            print("\nAlternative OCR result:")
            print(results[1][1])

        return recognized_text

    except Exception as error:
        print("Text extraction failed:", error)
        return None


# =========================================================
# COMBINED: OPTIMIZE IMAGE AND EXTRACT TEXT
# =========================================================

def optimize_and_extract():
    image_path = input(
        "\nEnter the full path of the original image: "
    ).strip().strip('"')

    optimized_path = optimize_image(image_path)

    if optimized_path is None:
        print("Combined operation stopped because optimization failed.")
        return

    print("\n" + "=" * 45)
    print("EXTRACTING TEXT FROM OPTIMIZED IMAGE")
    print("=" * 45)

    recognized_text = extract_text(optimized_path)

    if recognized_text:
        save_choice = input(
            "\nSave extracted text to a .txt file? (y/n): "
        ).strip().lower()

        if save_choice == "y":
            output_name = input(
                "Enter the text filename (without extension): "
            ).strip()

            if (
                not output_name
                or Path(output_name).name != output_name
                or "/" in output_name
                or "\\" in output_name
            ):
                print("ERROR: Enter a valid filename only.")
                return

            # Ensure the .txt extension is added only once.
            if output_name.lower().endswith(".txt"):
                output_name = output_name[:-4]

            if not output_name:
                print("ERROR: Invalid text filename.")
                return

            destination = REPOSITORY_FOLDER / (output_name + ".txt")

            try:
                destination.write_text(
                    recognized_text,
                    encoding="utf-8"
                )
                print("Extracted text saved to:", destination)

            except Exception as error:
                print("Could not save text:", error)


# =========================================================
# MAIN MENU
# =========================================================

def main():
    print("=" * 50)
    print("    IMAGE OPTIMIZER AND TEXT RECOGNITION")
    print("=" * 50)

    while True:
        print("\nChoose an option:")
        print("1. Optimize an image")
        print("2. Extract text from an image (OCR)")
        print("3. Optimize Image and Extract Text")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            optimize_image()

        elif choice == "2":
            extract_text()

        elif choice == "3":
            optimize_and_extract()

        elif choice == "4":
            print("Program closed.")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
