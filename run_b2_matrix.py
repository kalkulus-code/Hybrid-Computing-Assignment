from __future__ import annotations
import csv, os, subprocess, sys
from pathlib import Path

OUT = Path("results/b2_results.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

rows = []
for ranks in [1, 2, 4]:
    for workers in [1, 2, 4]:
        cmd = ["mpiexec", "-n", str(ranks), sys.executable, "code/mpi_processpool.py",
               "--max-workers", str(workers)]
        print("RUN:", " ".join(cmd))
        p = subprocess.run(cmd, text=True, capture_output=True)
        print(p.stdout)
        if p.returncode != 0:
            print(p.stderr)
            raise SystemExit("Konfigurasi MPI gagal. Pastikan MPI + mpi4py sudah terpasang.")
        # Ambil baris hasil dari stdout.
        line = next(x for x in p.stdout.splitlines() if x.startswith("ranks="))
        parts = dict(item.split("=") for item in line.split(", "))
        rows.append({
            "ranks": int(parts["ranks"]),
            "max_workers": int(parts["max_workers"]),
            "total_workers": int(parts["total_workers"]),
            "makespan_s": float(parts["makespan_s"]),
        })

baseline = next(r["makespan_s"] for r in rows if r["ranks"] == 1 and r["max_workers"] == 1)
for r in rows:
    r["speedup"] = baseline / r["makespan_s"]
    r["efficiency"] = r["speedup"] / r["total_workers"]
    r["oversubscribed_vs_14_cores"] = r["total_workers"] > 14

with OUT.open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=rows[0].keys())
    wr.writeheader(); wr.writerows(rows)

print(f"Hasil B2 tersimpan di {OUT}")
