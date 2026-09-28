from __future__ import annotations
import argparse, csv, hashlib, os, time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
from threading import Semaphore

from common import A, DATASET_SIZE_B1, print_device_info, physical_cores

def cpu_bound_transform(payload: str) -> str:
    # Beban CPU sengaja dibuat deterministik untuk membandingkan konfigurasi.
    data = payload.encode("utf-8")
    digest = data
    for _ in range(80):
        digest = hashlib.sha256(digest).digest()
    return digest.hex()

def run_once(paths, n_loader_threads: int, n_workers: int, q_max: int):
    start = time.perf_counter()
    latencies = []
    sem = Semaphore(q_max)
    futures = set()

    def load(path: Path):
        t0 = time.perf_counter()
        text = path.read_text(encoding="utf-8")
        return text, t0

    with ThreadPoolExecutor(max_workers=n_loader_threads) as loaders, \
         ProcessPoolExecutor(max_workers=n_workers) as workers:
        # Loader threads menangani I/O; semaphore membatasi pekerjaan yang
        # sedang menunggu/berjalan sehingga q_max merepresentasikan backpressure.
        load_futures = [loaders.submit(load, p) for p in paths]
        for lf in load_futures:
            text, t0 = lf.result()
            sem.acquire()
            f = workers.submit(cpu_bound_transform, text)
            f._submitted_at = time.perf_counter()
            futures.add(f)

            # Jaga jumlah in-flight task agar tidak melebihi Q_MAX.
            if len(futures) >= q_max:
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
                for d in done:
                    latencies.append(time.perf_counter() - d._submitted_at)
                    sem.release()

        if futures:
            done, _ = wait(futures)
            for d in done:
                latencies.append(time.perf_counter() - d._submitted_at)
                sem.release()

    total = time.perf_counter() - start
    throughput = len(paths) / total
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    return total, throughput, avg_latency

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/b1_dataset")
    ap.add_argument("--out", default="results/b1_results.csv")
    ap.add_argument("--quick", action="store_true", help="hanya 1 kombinasi untuk uji cepat")
    args = ap.parse_args()

    print_device_info()
    paths = sorted(Path(args.data).glob("*.txt"))
    if len(paths) != DATASET_SIZE_B1:
        raise SystemExit(f"Dataset harus {DATASET_SIZE_B1} file; ditemukan {len(paths)}.")

    worker_values = [1, 2, 4, physical_cores()]
    loader_values = [1, 2, 4]
    q_values = [4, 32]
    if args.quick:
        configs = [(2, 2, 4)]
    else:
        configs = [(lt, w, q) for lt in loader_values for w in worker_values for q in q_values]

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for lt, w, q in configs:
        total, thr, lat = run_once(paths, lt, w, q)
        row = {"N_LOADER_THREADS": lt, "N_WORKERS": w, "Q_MAX": q,
               "total_time_s": total, "throughput_files_s": thr, "avg_latency_s": lat}
        rows.append(row)
        print(row)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=rows[0].keys())
        wr.writeheader(); wr.writerows(rows)
    print(f"Hasil B1 tersimpan di {args.out}")

if __name__ == "__main__":
    main()
