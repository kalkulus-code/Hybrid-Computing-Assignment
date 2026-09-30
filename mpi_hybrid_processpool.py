from mpi4py import MPI
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import time
import argparse

# Parameter tugas
TOTAL_TASKS = 8
SAMPLES_PER_TASK = 270_000  # 200.000 + (10.000 x A), A = 7


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def mc_pi(n_samples, seed):
    rng = np.random.default_rng(seed)
    x = rng.random(n_samples)
    y = rng.random(n_samples)
    inside = (x*x + y*y) <= 1.0
    return int(inside.sum())


def run_task(args):
    """
    Fungsi tingkat modul agar dapat di-pickle oleh ProcessPoolExecutor
    pada Windows (spawn).
    """
    n_samples, seed = args
    return mc_pi(n_samples, seed)


def chunk_range(total, parts, idx):
    base = total // parts
    rem = total % parts

    start = idx * base + min(idx, rem)
    end = start + base + (1 if idx < rem else 0)

    return start, end


def main(max_workers):
    # Membagi 8 task ke seluruh rank MPI
    start, end = chunk_range(TOTAL_TASKS, size, rank)
    my_tasks = range(start, end)

    # Setiap task memiliki jumlah sampel yang sama.
    # Seed dibuat berbeda antar-task dan antar-rank.
    tasks = [
        (SAMPLES_PER_TASK, 1234 + rank * 1000 + k)
        for k in my_tasks
    ]

    # Sinkronisasi sebelum pengukuran
    comm.Barrier()
    t0 = time.perf_counter()

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        local_hits = list(ex.map(run_task, tasks))

    t1 = time.perf_counter()

    local_sum = sum(local_hits)
    local_samples = len(tasks) * SAMPLES_PER_TASK

    # Reduce ke root
    global_hits = comm.reduce(local_sum, op=MPI.SUM, root=0)
    global_samples = comm.reduce(local_samples, op=MPI.SUM, root=0)

    # Makespan = waktu rank paling lambat
    elapsed = t1 - t0
    makespan = comm.reduce(elapsed, op=MPI.MAX, root=0)

    if rank == 0:
        pi_est = 4.0 * global_hits / global_samples

        print(f"[MPI ranks={size}] tasks={TOTAL_TASKS}, "
              f"per_task={SAMPLES_PER_TASK}")
        print(f"max_workers={max_workers}, "
              f"total_workers={size * max_workers}")
        print(f"Makespan       : {makespan:.6f} s")
        print(f"Total samples  : {global_samples:,}")
        print(f"Estimasi pi    : {pi_est:.6f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hybrid MPI + ProcessPool untuk Monte Carlo Pi"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        required=True,
        choices=[1, 2, 4],
        help="Jumlah worker ProcessPool pada setiap MPI rank"
    )
    args = parser.parse_args()

    main(args.max_workers)
