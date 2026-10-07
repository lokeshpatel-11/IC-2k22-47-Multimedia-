import os
import cv2
import numpy as np
import pytesseract
from PIL import Image

def optimize_image(input_path, output_path=None, max_width=1920, max_height=1080, quality=75, format="WebP"):
    """
    Optimizes an image by resizing, compressing, and removing unnecessary metadata.
    """
    if not os.path.exists(input_path):
        print(f"Error: Could not find image at {input_path}")
        return

    # Original size in KB
    original_size_kb = os.path.getsize(input_path) / 1024

    print(f"\n--- Original Image Stats ---")
    print(f"Path: {input_path}")
    print(f"File Size: {original_size_kb:.2f} KB")

    try:
        # 1. Open the image
        img = Image.open(input_path)
        
        # Strip metadata by pasting into a new image
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.paste(img)
        img = image_without_exif

        print(f"Dimensions: {img.size[0]}x{img.size[1]}")

        # 2. Check dimensions & Resize if necessary
        # We use LANCZOS for high quality downsampling
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        print(f"New Dimensions after resize: {img.size[0]}x{img.size[1]}")

        # 3. Determine output format and path
        if not output_path:
            filename, _ = os.path.splitext(input_path)
            output_path = f"{filename}_optimized.{format.lower()}"

        # 4. Save with Compression
        if img.mode in ("RGBA", "P") and format.upper() == "JPEG":
            # JPEG doesn't support alpha channel, convert to RGB
            img = img.convert("RGB")

        print(f"\n[Processing...] Saving as {format.upper()} with Quality={quality}...")
        
        img.save(output_path, format=format, quality=quality, optimize=True)

        # 5. Output comparison
        optimized_size_kb = os.path.getsize(output_path) / 1024
        saved_kb = original_size_kb - optimized_size_kb
        saved_percent = (saved_kb / original_size_kb) * 100

        print(f"\n--- Optimized Image Stats ---")
        print(f"Path: {output_path}")
        print(f"New File Size: {optimized_size_kb:.2f} KB")
        print(f"Saved: {saved_kb:.2f} KB ({saved_percent:.2f}% reduction)")
        print("-" * 30)

    except Exception as e:
        print(f"An error occurred: {e}")

def recognize_text(image_path):
    """
    Extracts text from an image using robust OCR preprocessing techniques.
    Handles blur, noise, and high contrast conditions.
    """
    print("\n--- Text Recognition (OCR) ---")
    if not os.path.exists(image_path):
        print(f"Error: Could not find image at {image_path}")
        return

    try:
        # Load image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            print("Failed to load image for OCR.")
            return

        # 1. Convert to Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Rescale the image (improves OCR accuracy for smaller texts)
        gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        
        # 3. Denoising/Blurring to handle noisy or blurry backgrounds
        # Bilateral filter keeps edges sharp while removing noise
        blur = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # 4. Adaptive Thresholding to handle varying lighting/contrast
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
        )
        
        print("Extracting text...")
        # Page segmentation mode 6 assumes a single uniform block of text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(thresh, config=custom_config)
        
        if text.strip():
            print("\nExtracted Text:\n")
            print("-" * 40)
            print(text.strip())
            print("-" * 40)
        else:
            print("\nNo text could be extracted from the image.")
            
    except Exception as e:
        print(f"An error occurred during text recognition: {e}")
        print("Note: Ensure 'tesseract' is installed on your system (e.g., 'brew install tesseract').")

def main():
    print("=" * 50)
    print("IMAGE OPTIMIZATION & TEXT RECOGNITION TOOL")
    print("=" * 50)

    input_img = input("Enter the path to your image:\n> ").strip()
    
    # Remove quotes if user drag-drops the file in terminal
    input_img = input_img.strip('"').strip("'")

    if not input_img:
        print("Path is required! Exiting...")
        return
        
    print("\nSelect an action:")
    print("1. Optimize Image (Resize, Format, Compress)")
    print("2. Recognize Text (OCR with preprocessing)")
    print("3. Do Both (Optimize & Extract Text)")
    
    action = input("Enter choice (1/2/3): ").strip()
    
    if action in ["1", "3"]:
        print("\n[Optimization Settings]")
        choice = input("Format (1: WebP, 2: JPEG, 3: PNG) [Default=1]: ").strip()
        fmt = "JPEG" if choice == "2" else ("PNG" if choice == "3" else "WebP")
        
        quality_input = input("Compression quality (1-100) [Default=75]: ").strip()
        quality = int(quality_input) if quality_input.isdigit() else 75

        optimize_image(input_img, quality=quality, format=fmt)
        
    if action in ["2", "3"]:
        recognize_text(input_img)

if __name__ == "__main__":
    main()
