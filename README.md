# Tugas Individu Hybrid Computing — NIM 247006111157

Parameter pribadi:
- A = 7
- B1 dataset = 100 + 10A = 170 file
- B2 SAMPLES_PER_TASK = 200000 + 10000A = 270000
- CPU laptop yang dicatat sebelumnya: Intel Core i5-13450HX (14 core / 20 thread)
- RAM: 20 GB
- OS: Windows 11 (di laptop mahasiswa)

## Urutan menjalankan

Semua perintah dijalankan dari folder utama proyek.

### B1
```bash
python code/prepare_b1_dataset.py
python code/hybrid_pipeline.py
python code/plot_b1.py
```
Hasil: `results/b1_results.csv` dan `figures/b1_throughput.png`.

### B2
Pasang MPI + `mpi4py` sesuai lingkungan (Windows: MS-MPI/WSL; alternatif: Google Colab). Lalu:
```bash
python code/run_b2_matrix.py
```
Script menjalankan 1/2/4 rank × 1/2/4 worker dan menghitung speedup, efficiency, serta oversubscription terhadap 14 core.

### B3
```bash
python code/prepare_b3_dataset.py
python code/b3_global_wordcount.py --workers 4
```
Dataset diambil dari Project Gutenberg dan dipecah menjadi 30 file teks nyata.
