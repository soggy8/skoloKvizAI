import fitz  # pymupdf

doc = fitz.open("fizika2god.pdf")
text = ""
for page in doc:
    text += page.get_text("text") + "\n"

with open("fizika2god.txt", "w", encoding="utf-8") as f:
    f.write(text)
