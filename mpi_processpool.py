from __future__ import annotations

import argparse
import math
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

from common import A, SAMPLES_PER_TASK_B2


def cpu_work(task):
    start, n = task
    total = 0.0

    for i in range(start, start + n):
        x = (i % 10000) + 1.0

        for _ in range(60):
            x = math.sqrt(x * x + 3.141592653589793)

        total += x

    return total


def run_mpi(max_workers: int):
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Membagi sampel secara merata ke seluruh rank MPI.
    base = SAMPLES_PER_TASK_B2 // size
    rem = SAMPLES_PER_TASK_B2 % size

    local_n = base + (1 if rank < rem else 0)
    rank_start = rank * base + min(rank, rem)

    # Membagi pekerjaan setiap rank ke ProcessPool.
    chunk_base = local_n // max_workers
    chunk_rem = local_n % max_workers

    tasks = []
    offset = rank_start

    for i in range(max_workers):
        n = chunk_base + (1 if i < chunk_rem else 0)

        if n > 0:
            tasks.append((offset, n))
            offset += n

    # Sinkronisasi seluruh rank sebelum pengukuran waktu.
    comm.Barrier()

    t0 = time.perf_counter()

    with ProcessPoolExecutor(
        max_workers=max_workers,
        mp_context=mp.get_context("spawn")
    ) as pool:
        results = list(pool.map(cpu_work, tasks))

    local_sum = sum(results)
    elapsed = time.perf_counter() - t0

    # Makespan = waktu rank yang paling lambat.
    makespan = comm.reduce(elapsed, op=MPI.MAX, root=0)

    # Gabungkan checksum dari seluruh rank.
    total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

    if rank == 0:
        return makespan, total_sum, size * max_workers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-workers", type=int, required=True)
    ap.add_argument("--out", default="results/b2_results.csv")
    args = ap.parse_args()

    result = run_mpi(args.max_workers)

    if result is not None:
        makespan, total_sum, n = result

        print(
            f"ranks={n // args.max_workers}, "
            f"max_workers={args.max_workers}, "
            f"total_workers={n}, "
            f"makespan_s={makespan:.6f}, "
            f"checksum={total_sum:.3f}"
        )

        print(
            f"SAMPLES_PER_TASK={SAMPLES_PER_TASK_B2}, "
            f"A={A}"
        )


if __name__ == "__main__":
    main()