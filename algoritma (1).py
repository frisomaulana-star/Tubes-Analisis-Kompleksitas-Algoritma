"""
algoritma.py
Kumpulan fungsi REKURSIF yang dipakai oleh aplikasi kasir.

Setiap fungsi punya:
  - base case      : kondisi berhenti
  - recursive case : pemanggilan diri sendiri dengan masalah yang lebih kecil
"""

import sys

# Rekursi linear (hitung_total, _gabung) bisa sedalam n; naikkan batas bawaan Python (1000)
sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))

PECAHAN_UANG = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100]


# ---------------------------------------------------------------------------
# 1. Menjumlahkan total belanja (rekursi linear)
# ---------------------------------------------------------------------------
def hitung_total(items, i=0):
    """Jumlahkan harga * qty seluruh item di keranjang.

    Base case      : i sudah di luar indeks terakhir -> 0
    Recursive case : subtotal item ke-i + total item ke-(i+1) dst.
    """
    if i >= len(items):
        return 0
    return items[i]["harga"] * items[i]["qty"] + hitung_total(items, i + 1)


# ---------------------------------------------------------------------------
# 2. Format angka ke Rupiah (rekursi pada string)
# ---------------------------------------------------------------------------
def format_angka(s):
    """'1250000' -> '1.250.000' dengan memotong 3 digit dari belakang.

    Base case      : panjang string <= 3
    Recursive case : format bagian depan + '.' + 3 digit terakhir
    """
    if len(s) <= 3:
        return s
    return format_angka(s[:-3]) + "." + s[-3:]


def format_rupiah(n):
    n = int(n)
    if n < 0:
        return "-Rp " + format_angka(str(-n))
    return "Rp " + format_angka(str(n))


# ---------------------------------------------------------------------------
# 3. Pecahan uang kembalian (rekursi greedy)
# ---------------------------------------------------------------------------
def pecahan_kembalian(sisa, idx=0, pecahan=PECAHAN_UANG):
    """Pecah nominal kembalian menjadi lembar/koin terbesar lebih dulu.

    Mengembalikan list of (nominal, jumlah).
    Base case      : sisa == 0 atau pecahan sudah habis
    Recursive case : ambil sebanyak mungkin pecahan ke-idx, lanjutkan sisanya
                     dengan pecahan yang lebih kecil.
    """
    if sisa <= 0 or idx >= len(pecahan):
        return []
    nominal = pecahan[idx]
    jumlah = sisa // nominal
    sekarang = [(nominal, jumlah)] if jumlah > 0 else []
    return sekarang + pecahan_kembalian(sisa - jumlah * nominal, idx + 1, pecahan)


# ---------------------------------------------------------------------------
# 4. Merge Sort (divide and conquer) - mengurutkan daftar produk
# ---------------------------------------------------------------------------
def _gabung(kiri, kanan, key, desc, i=0, j=0, hasil=None):
    """Gabungkan dua list yang sudah terurut (rekursif, O(n)).

    i, j  : indeks elemen terdepan di kiri / kanan (tanpa slicing agar O(n))
    hasil : list penampung hasil gabungan
    Base case      : salah satu list habis -> sisa list lain ditambahkan
    Recursive case : ambil elemen terkecil (terbesar jika desc), lanjut i+1 / j+1
    """
    if hasil is None:
        hasil = []
    if i >= len(kiri):
        hasil.extend(kanan[j:])
        return hasil
    if j >= len(kanan):
        hasil.extend(kiri[i:])
        return hasil
    ambil_kiri = key(kiri[i]) >= key(kanan[j]) if desc else key(kiri[i]) <= key(kanan[j])
    if ambil_kiri:
        hasil.append(kiri[i])
        return _gabung(kiri, kanan, key, desc, i + 1, j, hasil)
    hasil.append(kanan[j])
    return _gabung(kiri, kanan, key, desc, i, j + 1, hasil)


def merge_sort(data, key=lambda x: x, desc=False):
    """Urutkan data tanpa mengubah list asli.

    Base case      : panjang data <= 1 sudah terurut
    Recursive case : bagi dua, urutkan masing-masing, lalu gabungkan.
    """
    if len(data) <= 1:
        return list(data)
    tengah = len(data) // 2
    kiri = merge_sort(data[:tengah], key, desc)
    kanan = merge_sort(data[tengah:], key, desc)
    return _gabung(kiri, kanan, key, desc)


# ---------------------------------------------------------------------------
# 5. Binary Search rekursif - mencari produk berdasarkan kode
# ---------------------------------------------------------------------------
def binary_search(produk, kode, lo=0, hi=None):
    """Cari kode pada list produk yang SUDAH terurut menurut kode.

    Mengembalikan indeks produk, atau -1 jika tidak ditemukan.
    Base case      : lo > hi (ruang pencarian kosong) atau kode ketemu
    Recursive case : cari di setengah kiri atau setengah kanan.
    """
    if hi is None:
        hi = len(produk) - 1
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    kode_mid = produk[mid]["kode"]
    if kode_mid == kode:
        return mid
    if kode < kode_mid:
        return binary_search(produk, kode, lo, mid - 1)
    return binary_search(produk, kode, mid + 1, hi)


# ---------------------------------------------------------------------------
# Pembulatan ke 100 rupiah terdekat (bukan rekursif, pelengkap)
# ---------------------------------------------------------------------------
def bulatkan(n, kelipatan=100):
    return int(-(-n // kelipatan) * kelipatan)
