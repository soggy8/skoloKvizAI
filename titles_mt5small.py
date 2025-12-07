import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Load a small multilingual summarization model
model_name = "google/mt5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Create summarization pipeline
summarizer = pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer,
    device=-1  # CPU
)

# Macedonian instruction prefix
mkd_prefix = "Сумирај го следниот текст на македонски јазик: "

# Load your input data
with open("chunks/chunksOCR.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for d in data:
    text = d.get("text", "").strip()
    if not text:
        d["title"] = ""
        continue

    # Truncate safely to 512 tokens (mt5-small limit ~512)
    tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    truncated_text = tokenizer.decode(tokens["input_ids"][0], skip_special_tokens=True)

    try:
        summary = summarizer(
            mkd_prefix + truncated_text,
            max_length=60,   # adjust as needed
            min_length=10,
            do_sample=False,
            num_beams=4      # helps keep it coherent
        )
        d["title"] = summary[0]["summary_text"]
    except Exception as e:
        print(f"Error summarizing: {e} | First 50 chars: {truncated_text[:50]}...")
        d["title"] = truncated_text[:50]  # fallback to first part of text

# Save results
with open("labeled_chunks/labeled_chunks_OCR_mt5.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Summarization completed with mT5-small (Macedonian).")
