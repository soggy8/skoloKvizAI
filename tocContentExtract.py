import re
import json

ocr_file = "txt/toc.txt"
output_file = "toc_from_ocr.json"

with open(ocr_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

toc_entries = []
current_entry = None

def clean_line(line):
    # Remove repeating garbage letters (from OCR)
    line = re.sub(r"[^\w\s\.\-\(\)]", " ", line)
    # Replace long sequences of dots with a single space
    line = re.sub(r"\.{2,}", " ", line)
    return line.strip()

for line in lines:
    line = clean_line(line)
    if not line:
        continue

    # Try to find a section number at the start or after some spaces
    match = re.match(r"^(\d+(?:\.\d+)+)\s*(.*)", line)
    if match:
        # Save previous entry
        if current_entry:
            toc_entries.append(current_entry)

        number = match.group(1)
        rest = match.group(2)

        # Try to extract page number at the end
        page_match = re.search(r"(\d+)$", rest)
        if page_match:
            page = int(page_match.group(1))
            title = rest[:page_match.start()].strip()
        else:
            page = None
            title = rest.strip()

        current_entry = {"number": number, "title": title, "page": page}
    else:
        # Continuation of previous title
        if current_entry:
            current_entry["title"] += " " + line

# Add last entry
if current_entry:
    toc_entries.append(current_entry)

# Save JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(toc_entries, f, ensure_ascii=False, indent=4)

print(f"✅ Extracted {len(toc_entries)} entries from OCR text into {output_file}")
