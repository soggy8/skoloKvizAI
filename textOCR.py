import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os

# --------------- CONFIG ----------------
pdf_path = "fizika2god.pdf"
output_text_file = "fizika2godOCR.txt"
png_folder = "page_png"
ocr_lang = "mkd"  # Cyrillic: mkd/rus/srp
dpi = 300
keep_pngs = True  # Set False to delete PNGs after OCR
# ---------------------------------------

# Ensure output folder exists
if not os.path.exists(png_folder):
    os.makedirs(png_folder)

# Point pytesseract to system tesseract binary
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Open PDF
doc = fitz.open(pdf_path)
num_pages = doc.page_count
print(f"PDF opened: {num_pages} pages.")

full_text = ""

for i in range(num_pages):
    print(f"Processing page {i+1}/{num_pages}...")

    # Render page to image
    page = doc.load_page(i)
    pix = page.get_pixmap(dpi=dpi)
    png_path = os.path.join(png_folder, f"page_{i+1}.png")
    pix.save(png_path)

    # OCR the PNG
    img = Image.open(png_path)
    text = pytesseract.image_to_string(img, lang=ocr_lang)
    full_text += f"\n--- Page {i+1} ---\n{text}"

    # Optional: delete PNG immediately after OCR
    if not keep_pngs:
        os.remove(png_path)

# Save all OCR text
with open(output_text_file, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"OCR completed! Text saved to '{output_text_file}'")
