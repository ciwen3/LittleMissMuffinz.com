from PIL import Image
import glob
import os

EXTENSIONS = (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp")

def remove_exif(file):
    base, ext = os.path.splitext(file)
    out = f"{base}_noexif{ext}"

    img = Image.open(file)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)

    clean.save(out)
    print(f"Cleaned: {out}")

def main():
    for f in glob.glob("*"):
        if f.lower().endswith(EXTENSIONS) and "_noexif" not in f:
            remove_exif(f)

if __name__ == "__main__":
    main()
