import os
from io import BytesIO
from typing import List
from pathlib import Path
from fpdf import FPDF
import re
from PIL import Image

# Paths to the first and last images in the root directory
FIRST_IMG = Path("first.jpg")
LAST_IMG = Path("last.jpg")


def fld2pdf(folder: Path, out: str):
    # Get all images in the folder
    files = [file for file in folder.glob(r'*') if re.match(r'.*\.(jpg|png|jpeg|webp)', file.name)]
    files.sort(key=lambda x: x.name)

    # Insert first.jpg and last.jpg from the root directory
    files.insert(0, "first.jpg")
    files.append("last.jpg")

    # Get the target width (smallest width among the images)
    target_width = get_target_width(files)

    # Compress the images to the target width
    compressed_images = [compress_image(file, folder / f"compressed_{file.name}", target_width=target_width) for file in files]

    # Generate the PDF from the compressed images
    pdf = folder / f'{out}.pdf'
    img2pdf(compressed_images, pdf)
    return pdf


def get_target_width(files: List[Path]) -> int:
    """Get the smallest width among all images."""
    min_width = float('inf')
    for file in files:
        img = Image.open(file)
        min_width = min(min_width, img.width)
        img.close()
    return min_width


def compress_image(image_path, output_path, quality=90, target_width=None):
    """Compress the image by resizing and reducing its quality."""
    try:
        img = Image.open(image_path)
        img_width, img_height = img.size

        # If a target width is specified, adjust the height to maintain the aspect ratio
        if target_width:
            new_height = int((target_width / img_width) * img_height)
            img = img.resize((target_width, new_height), Image.LANCZOS)

        # Save the compressed image
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        img.close()
        return output_path
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")
        return image_path  # Return original image if compression fails


def new_img(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return img


def old_img2pdf(files: List[Path], out: Path):
    img_list = [new_img(img) for img in files]
    img_list[0].save(out, resolution=100.0, save_all=True, append_images=img_list[1:])
    for img in img_list:
        img.close()


def pil_image(path: Path) -> (BytesIO, int, int):
    img = new_img(path)
    width, height = img.width, img.height
    try:
        membuf = BytesIO()
        img.save(membuf, format='JPEG')
    finally:
        img.close()
    return membuf, width, height


def unicode_to_latin1(s):
    # Substitute the ' character
    s = s.replace('\u2019', '\x92')
    # Substitute the " character
    s = s.replace('\u201d', '\x94')
    # Substitute the - character
    s = s.replace('\u2013', '\x96')
    # Remove all other non-latin1 characters
    s = s.encode('latin1', 'replace').decode('latin1')
    return s


def img2pdf(files: List[Path], out: Path):
    pdf = FPDF('P', 'pt')
    for imageFile in files:
        img_bytes, width, height = pil_image(imageFile)

        pdf.add_page(format=(width, height))

        pdf.image(img_bytes, 0, 0, width, height)

        img_bytes.close()

    pdf.set_title(unicode_to_latin1(out.stem))
    pdf.output(out, "F")


def fld2thumb(folder: Path):
    files = [file for file in folder.glob(r'*') if re.match(r'.*\.(jpg|png|jpeg|webp)', file.name)]
    files.sort(key=lambda x: x.name)
    thumb_path = make_thumb(folder, files)
    return thumb_path


def make_thumb(folder, files):
    aspect_ratio = 0.7
    if len(files) > 1:
        with Image.open(files[1]) as img:
            aspect_ratio = img.width / img.height

    thumbnail = Image.open(files[0]).convert('RGB')
    tg_max_size = (300, 300)
    thumbnail = crop_thumb(thumbnail, aspect_ratio)
    thumbnail.thumbnail(tg_max_size)
    thumb_path = folder / 'thumbnail' / f'thumbnail.jpg'
    os.makedirs(thumb_path.parent, exist_ok=True)
    thumbnail.save(thumb_path)
    thumbnail.close()
    return thumb_path


def crop_thumb(thumb: Image.Image, aspect_ratio):
    w, h = thumb.width, thumb.height
    if w * 2 <= h:
        b = int(h - (w / aspect_ratio))
        if b <= 0:
            b = w
        thumb = thumb.crop((0, 0, w, b))
    return thumb
