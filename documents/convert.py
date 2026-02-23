# Import Pillow for image processing
from PIL import Image, ImageOps

# Import operating system utilities
import os

# Import logging module for report file
import logging

# Import multi-threading executor
from concurrent.futures import ThreadPoolExecutor

# Try to import OpenCV and NumPy for AI cropping
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True  # Flag if OpenCV is available
except ImportError:
    OPENCV_AVAILABLE = False  # Disable AI cropping if OpenCV missing

# ---------------- CONFIGURATION ---------------- #

# Final image dimensions including border
TARGET_WIDTH = 930
TARGET_HEIGHT = 1230

# Border thickness in pixels
BORDER_SIZE = 15

# Compute usable image area inside border
INNER_WIDTH = TARGET_WIDTH - (BORDER_SIZE * 2)
INNER_HEIGHT = TARGET_HEIGHT - (BORDER_SIZE * 2)

# Supported image file extensions
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp")

# Number of threads for batch processing
MAX_THREADS = os.cpu_count() or 4

# ------------------------------------------------ #

# Get the folder where the script is located
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

# Configure logging to file
logging.basicConfig(
    filename="conversion_log.txt",  # Log filename
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(message)s"  # Log format
)

# -------- SAFE SMART CROP FUNCTION -------- #

def smart_crop_if_needed(image):
    """
    Crop only when aspect ratio mismatches target.
    Uses AI saliency if available, otherwise center crop.
    """

    # Calculate target aspect ratio
    target_ratio = INNER_WIDTH / INNER_HEIGHT

    # Get current image size
    w, h = image.size

    # Calculate current aspect ratio
    current_ratio = w / h

    # If aspect ratio already matches, return original image (no crop)
    if abs(current_ratio - target_ratio) < 0.01:
        return image

    # If OpenCV is NOT available, fallback to center crop
    if not OPENCV_AVAILABLE:
        return ImageOps.fit(image, (INNER_WIDTH, INNER_HEIGHT), Image.LANCZOS, centering=(0.5, 0.5))

    # Convert PIL image to OpenCV format (BGR)
    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Create saliency detector
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

    # Compute saliency map
    success, saliency_map = saliency.computeSaliency(cv_img)

    # Convert saliency map to binary mask
    _, binary_map = cv2.threshold(
        (saliency_map * 255).astype("uint8"),  # Convert to uint8
        0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )

    # Find contours in saliency mask
    contours, _ = cv2.findContours(binary_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If no contours found, fallback to center crop
    if not contours:
        return ImageOps.fit(image, (INNER_WIDTH, INNER_HEIGHT), Image.LANCZOS, centering=(0.5, 0.5))

    # Get bounding box of largest salient region
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))

    # Crop the image to the salient bounding box
    return image.crop((x, y, x + w, y + h))

# -------- IMAGE PROCESSING FUNCTION -------- #

def process_image(filename):
    """Process a single image file safely."""

    # Skip unsupported file types
    if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
        return

    # Build full input file path
    input_path = os.path.join(FOLDER_PATH, filename)

    try:
        # Open the image
        with Image.open(input_path) as img:

            # Get original size
            original_width, original_height = img.size

            # Apply safe crop only if aspect ratio mismatch
            img = smart_crop_if_needed(img)

            # Update dimensions after crop
            cropped_width, cropped_height = img.size

            # Check if upscaling would be required
            if cropped_width < INNER_WIDTH or cropped_height < INNER_HEIGHT:
                msg = f"SKIPPED (too small): {filename}"
                print(msg)
                logging.warning(msg)
                return  # Skip this file, continue loop

            # Resize while preserving aspect ratio (no distortion)
            resized = ImageOps.contain(img, (INNER_WIDTH, INNER_HEIGHT), Image.LANCZOS)

            # Create final black background image
            final_img = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))

            # Compute centered placement coordinates
            x_offset = BORDER_SIZE + (INNER_WIDTH - resized.width) // 2
            y_offset = BORDER_SIZE + (INNER_HEIGHT - resized.height) // 2

            # Paste resized image onto black canvas
            final_img.paste(resized, (x_offset, y_offset))

            # Determine if lossless WebP is possible
            # Lossless only if no resizing occurred
            lossless = (resized.width == original_width and resized.height == original_height)

            # Create output filename
            output_name = os.path.splitext(filename)[0] + ".webp"
            output_path = os.path.join(FOLDER_PATH, output_name)

            # Save WebP file with no EXIF metadata
            final_img.save(
                output_path,
                "WEBP",
                lossless=lossless,  # Lossless if possible
                quality=95,          # High quality if lossy
                method=6              # Best compression method
            )

            # Log success
            msg = f"CONVERTED: {filename} -> {output_name} | Lossless={lossless}"
            print(msg)
            logging.info(msg)

    except Exception as e:
        # Log any errors
        logging.error(f"ERROR processing {filename}: {str(e)}")

# -------- MULTI-THREADED MAIN FUNCTION -------- #

def main():
    """Run batch processing using multiple threads."""

    # List all files in folder
    files = os.listdir(FOLDER_PATH)

    # Create thread pool
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(process_image, files)  # Process files in parallel

    # Print and log completion
    print("Batch processing complete.")
    logging.info("Batch processing complete.")

# Run script entry point
if __name__ == "__main__":
    main()
