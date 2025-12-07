# Simple Latin -> Cyrillic mapping for Macedonian
latin_to_cyrillic = {
    "gj":"ѓ", "dz":"ѕ", "lj":"љ", "nj":"њ", "kj":"ќ", "ch":"ч", "sh":"ш", "dh":"џ",
    "a":"а", "b":"б", "v":"в", "g":"г", "d":"д", "e":"е", "zh":"ж", "z":"з",
    "i":"и", "j":"ј", "k":"к", "l":"л", "m":"м", "n":"н", "o":"о", "p":"п",
    "r":"р", "s":"с", "t":"т", "u":"у", "f":"ф", "h":"х", "c":"ц"
}

def latin_to_cyrillic_text(text):
    # Convert digraphs first
    for digraph in ["gj", "dz", "lj", "nj", "kj", "ch", "sh", "dh", "zh"]:
        if digraph in text:
            text = text.replace(digraph, latin_to_cyrillic[digraph])
    # Then single letters
    for latin, cyrillic in latin_to_cyrillic.items():
        text = text.replace(latin, cyrillic)
        text = text.replace(latin.upper(), cyrillic.upper())
    return text

# Read input file
with open("fizika2god.txt", "r", encoding="utf-8") as f:
    latin_text = f.read()

# Convert
cyrillic_text = latin_to_cyrillic_text(latin_text)

# Save output file
with open("output_cyrillic.txt", "w", encoding="utf-8") as f:
    f.write(cyrillic_text)

print("Conversion done! Saved as output_cyrillic.txt")
