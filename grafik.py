"""
grafik.py - Grafik T(n) terhadap ukuran input n (analisis kompleksitas empiris).

Mengukur waktu jalan fungsi rekursif di algoritma.py untuk beberapa nilai n,
lalu menggambarnya bersama kurva teori c * f(n) sebagai pembanding.
Digambar dengan Canvas Tkinter, jadi tidak perlu pustaka tambahan.
"""
import math
import random
import time
import tkinter as tk
from tkinter import ttk

import algoritma as alg

ORANYE = "#F59E0B"


# ------------------------------------------------------------ data uji
def _data_sort(n):
    rnd = random.Random(1)
    return [rnd.randint(0, 10 ** 6) for _ in range(n)]


def _data_total(n):
    return [{"harga": 1000 + (i % 50), "qty": 1 + (i % 5)} for i in range(n)]


def _data_cari(n):
    return [{"kode": f"P{i:07d}"} for i in range(n)]


ALGORITMA = {
    "Merge Sort": dict(
        buat=_data_sort, jalan=lambda d: alg.merge_sort(d),
        teori=lambda n: n * math.log2(max(n, 2)), notasi="O(n log n)", ulang=1),
    "Hitung Total Keranjang": dict(
        buat=_data_total, jalan=lambda d: alg.hitung_total(d),
        teori=lambda n: n, notasi="O(n)", ulang=5),
    "Binary Search (kasus terburuk)": dict(
        buat=_data_cari, jalan=lambda d: alg.binary_search(d, "Q"),   # "Q" > semua kode
        teori=lambda n: math.log2(max(n, 2)), notasi="O(log n)", ulang=3000),
}


def ukur(spec, n):
    """Waktu rata-rata satu pemanggilan (detik); diambil yang terbaik dari 3 percobaan."""
    data = spec["buat"](n)
    terbaik = float("inf")
    for _ in range(3):
        t0 = time.perf_counter()
        for _ in range(spec["ulang"]):
            spec["jalan"](data)
        terbaik = min(terbaik, (time.perf_counter() - t0) / spec["ulang"])
    return terbaik


# ------------------------------------------------------------ sumbu
def _tick_bagus(vmax, target=5):
    """Daftar tick 0..atas dengan langkah 'bulat' (1, 2, 2.5, 5 x 10^k)."""
    if vmax <= 0:
        return [0, 1]
    mentah = vmax / target
    mag = 10 ** math.floor(math.log10(mentah))
    langkah = 10 * mag
    for m in (1, 2, 2.5, 5, 10):
        if mentah <= m * mag:
            langkah = m * mag
            break
    return [langkah * i for i in range(int(math.ceil(vmax / langkah - 1e-9)) + 1)]


def _fmt(v):
    return f"{v:g}"


# ------------------------------------------------------------ jendela
class JendelaGrafik(tk.Toplevel):
    def __init__(self, master, C, font):
        super().__init__(master)
        self.C, self.F = C, font
        self.title("Grafik T(n) terhadap ukuran input n")
        self.geometry("980x600")
        self.minsize(760, 480)
        self.configure(bg=C["bg"])
        self.hasil = None   # dict: nama, notasi, ns, ts (detik), teo (detik)

        self._buat_kontrol()
        self._buat_isi()
        self.canvas.bind("<Configure>", lambda _e: self._gambar())
        self._gambar()

    # --------------------------------------------------------- UI
    def _buat_kontrol(self):
        C, F = self.C, self.F
        bar = tk.Frame(self, bg=C["card"], highlightbackground=C["line"], highlightthickness=1)
        bar.pack(fill="x", padx=14, pady=(14, 8))
        isi = tk.Frame(bar, bg=C["card"])
        isi.pack(fill="x", padx=12, pady=10)

        def lbl(t):
            tk.Label(isi, text=t, bg=C["card"], fg=C["muted"], font=(F, 9)).pack(side="left", padx=(10, 4))

        lbl("Algoritma")
        self.var_algo = tk.StringVar(value="Merge Sort")
        cb = ttk.Combobox(isi, textvariable=self.var_algo, values=list(ALGORITMA),
                          state="readonly", width=28)
        cb.pack(side="left")

        lbl("n maksimum")
        self.var_nmax = tk.IntVar(value=3000)
        tk.Spinbox(isi, from_=100, to=8000, increment=100, textvariable=self.var_nmax, width=6,
                   relief="flat", highlightbackground=C["line"], highlightthickness=1).pack(side="left")

        lbl("Jumlah titik")
        self.var_titik = tk.IntVar(value=8)
        tk.Spinbox(isi, from_=3, to=15, textvariable=self.var_titik, width=4,
                   relief="flat", highlightbackground=C["line"], highlightthickness=1).pack(side="left")

        self.btn = tk.Label(isi, text="Jalankan", bg=C["primary"], fg="white", cursor="hand2",
                            font=(F, 10, "bold"), padx=16, pady=6)
        self.btn.pack(side="right")
        self.btn.bind("<Button-1>", lambda _e: self.jalankan())
        self.btn.bind("<Enter>", lambda _e: self.btn.config(bg=C["primary_d"]))
        self.btn.bind("<Leave>", lambda _e: self.btn.config(bg=C["primary"]))

    def _buat_isi(self):
        C, F = self.C, self.F
        isi = tk.Frame(self, bg=C["bg"])
        isi.pack(fill="both", expand=True, padx=14, pady=(0, 6))
        isi.columnconfigure(0, weight=1)
        isi.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(isi, bg=C["card"], highlightbackground=C["line"], highlightthickness=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        samping = tk.Frame(isi, bg=C["bg"], width=230)
        samping.grid(row=0, column=1, sticky="ns", padx=(12, 0))
        samping.pack_propagate(False)
        tk.Label(samping, text="Data pengukuran", bg=C["bg"], fg=C["ink"],
                 font=(F, 11, "bold"), anchor="w").pack(fill="x")
        self.tree = ttk.Treeview(samping, columns=("n", "t", "teo"), show="headings", height=14)
        for k, t, w in (("n", "n", 55), ("t", "T(n) ukur", 80), ("teo", "c·f(n)", 80)):
            self.tree.heading(k, text=t)
            self.tree.column(k, width=w, anchor="e")
        self.tree.pack(fill="x", pady=(6, 8))
        self.lbl_info = tk.Label(samping, text="", bg=C["bg"], fg=C["muted"], font=(F, 9),
                                 justify="left", anchor="nw", wraplength=220)
        self.lbl_info.pack(fill="x")

        self.lbl_status = tk.Label(self, text="Pilih algoritma lalu klik Jalankan.", bg=C["bg"],
                                   fg=C["muted"], font=(F, 9), anchor="w")
        self.lbl_status.pack(fill="x", padx=16, pady=(0, 10))

    # ------------------------------------------------------ ukur
    def jalankan(self):
        try:
            nmax = max(100, min(8000, int(self.var_nmax.get())))
            titik = max(3, min(15, int(self.var_titik.get())))
        except (ValueError, tk.TclError):
            self.lbl_status.config(text="n maksimum dan jumlah titik harus berupa angka.")
            return
        nama = self.var_algo.get()
        spec = ALGORITMA[nama]
        ns = sorted({max(2, round(nmax * (k + 1) / titik)) for k in range(titik)})

        self.lbl_status.config(text=f"Mengukur {nama} ...")
        self.update_idletasks()
        ts = []
        for n in ns:
            ts.append(ukur(spec, n))
            self.lbl_status.config(text=f"Mengukur {nama}: n = {n} ...")
            self.update()

        f = [spec["teori"](n) for n in ns]
        c = sum(t * x for t, x in zip(ts, f)) / sum(x * x for x in f)   # kuadrat terkecil
        self.hasil = dict(nama=nama, notasi=spec["notasi"], ns=ns, ts=ts, c=c, teori=spec["teori"])
        self.lbl_status.config(text=f"Selesai: {nama}, {len(ns)} titik, n = {ns[0]} sampai {ns[-1]}.")
        self._isi_tabel()
        self._gambar()

    def _satuan(self, maks):
        if maks < 1e-3:
            return 1e6, "µs"
        if maks < 1:
            return 1e3, "ms"
        return 1.0, "detik"

    def _isi_tabel(self):
        h = self.hasil
        faktor, sat = self._satuan(max(h["ts"]))
        self.tree.delete(*self.tree.get_children())
        for n, t in zip(h["ns"], h["ts"]):
            self.tree.insert("", "end", values=(n, f"{t * faktor:.4g}", f"{h['c'] * h['teori'](n) * faktor:.4g}"))
        self.lbl_info.config(
            text=f"Satuan: {sat}\nKompleksitas teori: {h['notasi']}\n"
                 f"Kurva putus-putus = c · f(n), c dicocokkan ke data. "
                 f"Jika titik biru mengikuti kurva, hasil ukur sesuai teori.")

    # ----------------------------------------------------- gambar
    def _gambar(self):
        C, F = self.C, self.F
        cv = self.canvas
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 50 or h < 50:
            return
        if not self.hasil:
            cv.create_text(w / 2, h / 2, text="Klik 'Jalankan' untuk membuat grafik T(n) vs n",
                           fill=C["muted"], font=(F, 12))
            return

        r = self.hasil
        ns, ts = r["ns"], r["ts"]
        kurva_n = [ns[0] + (ns[-1] - ns[0]) * i / 60 for i in range(61)]
        kurva_t = [r["c"] * r["teori"](n) for n in kurva_n]
        faktor, sat = self._satuan(max(max(ts), max(kurva_t)))

        kiri, kanan, atas, bawah = 78, 24, 58, 56
        pw, ph = w - kiri - kanan, h - atas - bawah
        xticks = _tick_bagus(max(ns))
        yticks = _tick_bagus(max(max(ts), max(kurva_t)) * faktor)
        xtop, ytop = xticks[-1], yticks[-1]

        def px(n):
            return kiri + n / xtop * pw

        def py(t_unit):
            return atas + ph - t_unit / ytop * ph

        cv.create_text(kiri, 18, anchor="w", fill=C["ink"], font=(F, 12, "bold"),
                       text=f"T(n) {r['nama']}  -  teori {r['notasi']}")
        # grid + tick
        for v in yticks:
            y = py(v)
            cv.create_line(kiri, y, kiri + pw, y, fill=C["line"])
            cv.create_text(kiri - 8, y, anchor="e", text=_fmt(v), fill=C["muted"], font=(F, 9))
        for v in xticks:
            x = px(v)
            cv.create_line(x, atas + ph, x, atas + ph + 4, fill=C["muted"])
            cv.create_text(x, atas + ph + 16, text=_fmt(v), fill=C["muted"], font=(F, 9))
        cv.create_line(kiri, atas, kiri, atas + ph, fill=C["muted"])
        cv.create_line(kiri, atas + ph, kiri + pw, atas + ph, fill=C["muted"])
        cv.create_text(kiri + pw / 2, h - 12, text="n (ukuran input)", fill=C["ink"], font=(F, 10, "bold"))
        cv.create_text(16, atas + ph / 2, text=f"T(n) ({sat})", angle=90, fill=C["ink"], font=(F, 10, "bold"))

        # kurva teori (putus-putus)
        pts = []
        for n, t in zip(kurva_n, kurva_t):
            pts += [px(n), py(t * faktor)]
        cv.create_line(*pts, fill=ORANYE, width=2, dash=(6, 4), smooth=True)

        # data ukur
        pts = []
        for n, t in zip(ns, ts):
            pts += [px(n), py(t * faktor)]
        if len(ns) > 1:
            cv.create_line(*pts, fill=C["primary"], width=2)
        for n, t in zip(ns, ts):
            x, y = px(n), py(t * faktor)
            cv.create_oval(x - 4, y - 4, x + 4, y + 4, fill=C["primary"], outline="white", width=1)

        # legenda
        lx, ly = kiri + 14, atas + 12
        cv.create_line(lx, ly, lx + 26, ly, fill=C["primary"], width=2)
        cv.create_oval(lx + 9, ly - 4, lx + 17, ly + 4, fill=C["primary"], outline="white")
        cv.create_text(lx + 34, ly, anchor="w", text="Hasil pengukuran T(n)", fill=C["ink"], font=(F, 9))
        cv.create_line(lx, ly + 18, lx + 26, ly + 18, fill=ORANYE, width=2, dash=(6, 4))
        cv.create_text(lx + 34, ly + 18, anchor="w", text=f"Teori c · {r['notasi']}",
                       fill=C["ink"], font=(F, 9))


def buka(master, C, font):
    JendelaGrafik(master, C, font)
