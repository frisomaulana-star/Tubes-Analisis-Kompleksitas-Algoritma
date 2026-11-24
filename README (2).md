# Aplikasi Kasir Toko Alat Tulis (Tugas Besar Algoritma & Rekursif)

Aplikasi kasir desktop berbasis Python + Tkinter.

## Cara menjalankan
1. Pasang Python 3.8+ (Tkinter sudah termasuk di Windows/macOS; di Linux: `sudo apt install python3-tk`).
2. Letakkan `kasir.py`, `algoritma.py`, dan `grafik.py` dalam satu folder.
3. Jalankan: `python kasir.py`

## Fitur
- Daftar produk dengan stok, bisa diurutkan (klik judul kolom) dan ditambah (+ Produk)
- Cari produk berdasarkan kode
- Keranjang belanja (tambah, hapus, kosongkan; cek stok otomatis)
- Diskon persen, pembulatan total ke 100 rupiah
- Pembayaran, kembalian, struk, dan riwayat transaksi (`riwayat_transaksi.txt`)

## Penerapan rekursi (semua di `algoritma.py`)
| Fungsi | Dipakai untuk | Base case | Recursive case |
|---|---|---|---|
| `hitung_total` | Total belanja keranjang | indeks melewati item terakhir -> 0 | subtotal item ke-i + total sisanya |
| `format_angka` / `format_rupiah` | Format `1.250.000` | panjang string <= 3 | format bagian depan + `.` + 3 digit akhir |
| `pecahan_kembalian` | Rincian uang kembalian | sisa = 0 / pecahan habis | ambil pecahan terbesar, lanjut ke pecahan lebih kecil |
| `merge_sort` (+ `_gabung`) | Mengurutkan produk | panjang <= 1 | bagi dua, urutkan, gabungkan |
| `binary_search` | Mencari produk per kode | lo > hi atau ketemu | cari di separuh kiri/kanan |

Kompleksitas: `hitung_total` O(n), `merge_sort` O(n log n), `binary_search` O(log n).

## Grafik T(n) terhadap ukuran input n (`grafik.py`)
Tombol **Grafik T(n)** di header membuka jendela analisis kompleksitas empiris:
1. Pilih algoritma (Merge Sort, Hitung Total Keranjang, Binary Search kasus terburuk).
2. Atur n maksimum dan jumlah titik, lalu klik **Jalankan**.
3. Program mengukur waktu jalan fungsi rekursif untuk tiap n (terbaik dari 3 percobaan),
   menggambar grafik T(n) vs n, dan membandingkannya dengan kurva teori c * f(n)
   (c dicocokkan dengan kuadrat terkecil). Tabel nilai ada di sisi kanan.

| Algoritma | f(n) teori | Bentuk grafik |
|---|---|---|
| Merge Sort | n log n | sedikit melengkung ke atas |
| Hitung Total Keranjang | n | garis lurus |
| Binary Search | log n | melandai |

Catatan: `merge_sort` memakai penggabungan berindeks (tanpa slicing) supaya benar-benar O(n log n).
