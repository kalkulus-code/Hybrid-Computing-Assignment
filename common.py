from __future__ import annotations
import os, platform, sys
try:
    import psutil
except ImportError:
    psutil = None

A = 7
DATASET_SIZE_B1 = 100 + 10 * A
SAMPLES_PER_TASK_B2 = 200_000 + 10_000 * A

def physical_cores() -> int:
    if psutil:
        return psutil.cpu_count(logical=False) or (os.cpu_count() or 1)
    return os.cpu_count() or 1

def logical_threads() -> int:
    return os.cpu_count() or 1

def device_info() -> dict:
    return {
        "OS": platform.platform(),
        "Python": sys.version.split()[0],
        "CPU": platform.processor() or platform.machine(),
        "Physical cores": physical_cores(),
        "Logical CPUs": logical_threads(),
    }

def print_device_info():
    print("=== DEVICE INFO ===")
    for k, v in device_info().items():
        print(f"{k}: {v}")
