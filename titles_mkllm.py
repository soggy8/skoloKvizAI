# Make sure you have accelerate installed:
# pip install accelerate

import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_name = "trajkovnikola/MKLLM-7B-Instruct"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load model with CPU offloading
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",            # automatically assigns devices
    offload_folder="offload",     # folder for offloaded weights
    offload_state_dict=True
)

# Summarization pipeline
summarizer = pipeline(
    "text-generation",  # causal LM; MKLLM is not seq2seq
    model=model,
    tokenizer=tokenizer,
    device_map="auto"
)

# Load your data
with open("chunks.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for d in data:
    text = d.get("text", "").strip()
    if not text:
        d["title"] = ""
        continue

    # Truncate or chunk text safely
    tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    truncated_text = tokenizer.decode(tokens["input_ids"][0])

    try:
        # Generate a short "summary" with the causal model
        summary_output = summarizer(
            truncated_text,
            max_new_tokens=50,
            do_sample=False
        )
        d["title"] = summary_output[0]["generated_text"]
    except Exception as e:
        print(f"Error summarizing: {e} | First 50 chars: {truncated_text[:50]}...")
        d["title"] = truncated_text[:50]  # fallback

# Save results
with open("labeled_chunks_mkd2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Summarization completed successfully!")
