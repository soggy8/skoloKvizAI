import json

with open("fizika2godOCR.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Подели по параграфи (двојни нови линии)
paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

# Групирај по ~400 зборови
chunks = []
current_chunk = []
word_count = 0

for para in paragraphs:
    words = para.split()
    if word_count + len(words) > 400:
        chunks.append(" ".join(current_chunk))
        current_chunk = []
        word_count = 0
    current_chunk.append(para)
    word_count += len(words)

# додај последно парче
if current_chunk:
    chunks.append(" ".join(current_chunk))

# Зачувај во JSON
data = [{"id": i+1, "text": chunk} for i, chunk in enumerate(chunks)]
with open("chunksOCR.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Зачувани {len(chunks)} chunks.")
