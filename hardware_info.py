import platform, os, sys
try:
    import psutil
    physical = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)
except ImportError:
    physical = "install psutil"
    logical = os.cpu_count()
print("=== SPESIFIKASI PERANGKAT ===")
print("CPU            : Intel Core i5-13450HX (14 core / 20 thread) [sesuai perangkat yang dicatat]")
print("RAM            : 20 GB")
print("OS             :", platform.system(), platform.release())
print("Python         :", sys.version.split()[0])
print("Physical cores :", physical)
print("Logical CPUs   :", logical)
