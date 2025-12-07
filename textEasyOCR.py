import os
import easyocr
from time import sleep

# Folders
png_folder = "page_png"
output_file = "fizika2godEasyOCR.txt"

# EasyOCR reader
reader = easyocr.Reader(['bg'], gpu=False)  # 'bg' works decently for Macedonian

# Batch settings
batch_size = 10  # number of pages per batch
png_files = sorted([f for f in os.listdir(png_folder) if f.endswith(".png")])

# Clear the output file if it exists
open(output_file, "w", encoding="utf-8").close()

print(f"Processing {len(png_files)} pages in batches of {batch_size}...")

# Process pages in batches
for i in range(0, len(png_files), batch_size):
    batch_files = png_files[i:i+batch_size]
    batch_texts = []

    for png_file in batch_files:
        page_path = os.path.join(png_folder, png_file)
        result = reader.readtext(page_path)
        page_text = "\n".join([res[1] for res in result])
        batch_texts.append(page_text)

    # Append batch text to output file
    with open(output_file, "a", encoding="utf-8") as f:
        f.write("\n\n".join(batch_texts) + "\n\n")

    print(f"✅ Processed pages {i+1} to {i+len(batch_files)}")

print(f"\nAll pages processed. Full book saved as '{output_file}'")
