from pathlib import Path
from common import A, DATASET_SIZE_B1

OUT = Path("data/b1_dataset")
OUT.mkdir(parents=True, exist_ok=True)

paragraph = (
    "Hybrid computing menggabungkan paralelisme thread dan proses untuk "
    "menyeimbangkan pekerjaan I/O-bound dan CPU-bound. Data ini digunakan "
    "sebagai beban eksperimen pipeline. "
)

for i in range(DATASET_SIZE_B1):
    # File dibuat dengan isi berbeda agar pembacaan dan pemrosesan tidak identik.
    text = (paragraph + f"File ke-{i:03d}. " + ("abc123 " * (100 + i % 20))).strip()
    (OUT / f"sample_{i:03d}.txt").write_text(text, encoding="utf-8")

print(f"A={A}; dataset B1 dibuat: {DATASET_SIZE_B1} file di {OUT}")
