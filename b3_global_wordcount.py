from __future__ import annotations
import argparse, re, time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from collections import Counter

STOPWORDS = {"dan", "yang", "di", "the", "of", "and"}

def tokenize(text: str):
    # Regex menjadi bagian CPU-bound yang dapat dibandingkan pada thread vs process.
    return [w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]+", text)
            if w.lower() not in STOPWORDS]

def read_and_tokenize(path: Path):
    return tokenize(path.read_text(encoding="utf-8", errors="ignore"))

def count_thread(paths, workers):
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        chunks = list(ex.map(read_and_tokenize, paths))
    c = Counter()
    for x in chunks: c.update(x)
    return time.perf_counter() - t0, c

def count_process(paths, workers):
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        chunks = list(ex.map(read_and_tokenize, paths))
    c = Counter()
    for x in chunks: c.update(x)
    return time.perf_counter() - t0, c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/b3_dataset")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    paths = sorted(Path(args.data).glob("*.txt"))
    if len(paths) < 30:
        raise SystemExit("Dataset B3 harus minimal 30 file teks nyata.")

    tt, ct = count_thread(paths, args.workers)
    tp, cp = count_process(paths, args.workers)
    print(f"files={len(paths)}, workers={args.workers}")
    print(f"ThreadPoolExecutor time={tt:.6f}s")
    print(f"ProcessPoolExecutor time={tp:.6f}s")
    print("\nTop 10 — ThreadPool:")
    print(ct.most_common(10))
    print("\nTop 10 — ProcessPool:")
    print(cp.most_common(10))

if __name__ == "__main__":
    main()
