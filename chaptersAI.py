import os
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# ---------------- CONFIG ----------------
pdf_text_file = "txt/fizika2godOCR.txt"      # OCRed physics book
output_json = "chunksAI.json"     # JSON output
chunk_size = 3000                 # Number of characters per chunk (adjust for token limits)
model_name = "google/mt5-small"  # Small MT5 model for text2text
device = "cuda" if torch.cuda.is_available() else "cpu"
# ---------------------------------------

# Load MT5 tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

# Read the OCRed text
with open(pdf_text_file, "r", encoding="utf-8") as f:
    full_text = f.read()

# Split text into chunks
chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]

chapters_list = []
chapter_counter = 1

for idx, chunk in enumerate(chunks):
    print(f"Processing chunk {idx+1}/{len(chunks)}...")

    # Prompt the model to split into chapters
    prompt = f"""
    Split the following text into chapters. 
    For each chapter, start with "Chapter X:" and provide a short heading. 
    Text: {chunk}
    """

    inputs = tokenizer(prompt, return_tensors="pt", max_length=4096, truncation=True).to(device)

    output_ids = model.generate(
        **inputs,
        max_new_tokens=500,
        do_sample=False  # deterministic output
    )

    result = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Split by detected chapters
    chapters = result.split("Chapter ")
    for chapter_text in chapters[1:]:
        # Extract title as first line, content as the rest
        lines = chapter_text.strip().split("\n")
        title = lines[0].strip() if lines else f"Chapter {chapter_counter}"
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        chapters_list.append({
            "chapter_number": chapter_counter,
            "title": title,
            "content": content
        })

        chapter_counter += 1

# Save to JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(chapters_list, f, ensure_ascii=False, indent=4)

print(f"Finished! Chapters saved in JSON file '{output_json}'")
