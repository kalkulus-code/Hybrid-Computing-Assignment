from __future__ import annotations
import re, urllib.request
from pathlib import Path

# Public-domain texts from Project Gutenberg. Each downloaded book is split into
# six real-text files, giving 30 files total (5 books x 6 parts).
BOOKS = {
    1342: "Pride and Prejudice",
    84: "Frankenstein",
    1661: "The Adventures of Sherlock Holmes",
    11: "Alice's Adventures in Wonderland",
    2701: "Moby Dick",
}

OUT = Path("data/b3_dataset")
OUT.mkdir(parents=True, exist_ok=True)

def clean(s):
    s = re.sub(r"\r\n?", "\n", s)
    return s

idx = 0
for gid, title in BOOKS.items():
    url = f"https://www.gutenberg.org/files/{gid}/{gid}-8.txt"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            text = r.read().decode("utf-8", errors="ignore")
    except Exception:
        # Fallback URL used by current Gutenberg layout.
        url = f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"
        with urllib.request.urlopen(url, timeout=30) as r:
            text = r.read().decode("utf-8", errors="ignore")
    text = clean(text)
    parts = [p for p in text.split("\n\n") if p.strip()]
    chunks = []
    n = max(1, len(parts)//6)
    for i in range(6):
        start = i*n
        end = len(parts) if i == 5 else (i+1)*n
        chunks.append("\n\n".join(parts[start:end]))
    for j, chunk in enumerate(chunks, 1):
        idx += 1
        (OUT/f"text_{idx:02d}.txt").write_text(
            f"Source: Project Gutenberg — {title} (ID {gid})\n\n{chunk}",
            encoding="utf-8"
        )
print(f"Created {idx} real-text files in {OUT}")
