import argparse
import pandas as pd
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="results/b1_results.csv")
ap.add_argument("--out", default="figures/b1_throughput.png")
args = ap.parse_args()

df = pd.read_csv(args.csv)
for q in sorted(df.Q_MAX.unique()):
    for lt in sorted(df.N_LOADER_THREADS.unique()):
        sub = df[(df.Q_MAX == q) & (df.N_LOADER_THREADS == lt)].sort_values("N_WORKERS")
        plt.plot(sub.N_WORKERS, sub.throughput_files_s, marker="o",
                 label=f"loader={lt}, Q_MAX={q}")
plt.xlabel("N_WORKERS")
plt.ylabel("Throughput (file/s)")
plt.title("B1 — Throughput terhadap N_WORKERS")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(args.out, dpi=180)
print(f"Grafik disimpan: {args.out}")
