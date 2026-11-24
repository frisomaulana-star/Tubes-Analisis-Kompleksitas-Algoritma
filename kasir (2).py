"""
kasir.py - Aplikasi Kasir (GUI Tkinter, tampilan bergaya web)
Tugas Besar Algoritma & Rekursif

Jalankan:  python kasir.py
Fungsi rekursif ada di algoritma.py
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

import algoritma as alg
import grafik

try:  # Pillow opsional: dengan Pillow, foto JPG/PNG otomatis dipotong sesuai kartu
    from PIL import Image, ImageOps, ImageTk
except ImportError:
    Image = None

# Letakkan foto di folder "foto" (sebelah kasir.py), nama file = kode produk
# contoh: foto/P001.jpg, foto/P002.png
FOLDER_FOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "foto")
UKURAN_FOTO = (240, 110)

# ----------------------------------------------------------------- tema
C = {
    "bg": "#F1F6FD",        # latar biru sangat muda
    "card": "#FFFFFF",
    "ink": "#13233F",       # teks utama
    "muted": "#6B7A90",
    "primary": "#1F6FEB",   # biru
    "primary_d": "#1858BC",
    "accent": "#DCEAFF",
    "accent_h": "#C3DAFF",  # hover untuk warna accent
    "line": "#DCE6F4",
    "ok": "#2E9E5B",
    "danger": "#C0392B",
}
FONT = "Segoe UI"

PRODUK_AWAL = [
    {"kode": "P001", "nama": "Pulpen Gel 0.5mm", "desk": "Tinta halus, tidak mudah blobor", "harga": 3500, "stok": 100},
    {"kode": "P002", "nama": "Buku Tulis 38 Lembar", "desk": "Kertas tebal, sampul bergambar", "harga": 4500, "stok": 80},
    {"kode": "P003", "nama": "Pensil 2B", "desk": "Hitam pekat, cocok untuk ujian", "harga": 3000, "stok": 120},
    {"kode": "P004", "nama": "Penghapus Putih", "desk": "Bersih, tidak meninggalkan noda", "harga": 2000, "stok": 90},
    {"kode": "P005", "nama": "Penggaris 30cm", "desk": "Bening, skala jelas dan tahan lama", "harga": 4000, "stok": 60},
    {"kode": "P006", "nama": "Spidol Whiteboard", "desk": "Mudah dihapus, warna tajam", "harga": 8500, "stok": 40},
    {"kode": "P007", "nama": "Stabilo Highlighter", "desk": "Warna stabilo cerah dan tidak tembus", "harga": 9000, "stok": 35},
    {"kode": "P008", "nama": "Kertas HVS A4 (1 rim)", "desk": "80 gsm, 500 lembar, putih bersih", "harga": 52000, "stok": 15},
    {"kode": "P009", "nama": "Lem Stik", "desk": "Rekat kuat, tidak lengket di tangan", "harga": 6500, "stok": 45},
    {"kode": "P010", "nama": "Stapler Mini", "desk": "Ringan, termasuk isi staples", "harga": 12000, "stok": 25},
]

FILE_RIWAYAT = "riwayat_transaksi.txt"
KOLOM_GRID = 3


class Tombol(tk.Label):
    """Tombol datar berwarna dengan efek hover (Tkinter biasa tidak punya)."""

    def __init__(self, master, text, command, bg=None, fg="white", hover=None,
                 font=None, padx=14, pady=7, **kw):
        self._bg = bg or C["primary"]
        self._hover = hover or C["primary_d"]
        super().__init__(master, text=text, bg=self._bg, fg=fg, cursor="hand2",
                         font=font or (FONT, 10, "bold"), padx=padx, pady=pady, **kw)
        self._cmd = command
        self.bind("<Button-1>", lambda _e: self._cmd())
        self.bind("<Enter>", lambda _e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda _e: self.config(bg=self._bg))


class KasirApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Toko Alat Tulis - Aplikasi Kasir")
        self.geometry("1180x700")
        self.minsize(1000, 600)
        self.configure(bg=C["bg"])

        # produk selalu terurut menurut kode (syarat binary search)
        self.produk = alg.merge_sort(PRODUK_AWAL, key=lambda p: p["kode"])
        self.keranjang = []
        self.urut_key = "kode"
        self.urut_desc = False
        self.cari_kode = None
        self._toast_job = None
        self._foto_cache = {}

        print(f"[FOTO] Pillow: {'terpasang' if Image is not None else 'TIDAK terpasang'} | "
              f"folder foto: {FOLDER_FOTO}")
        self._gaya()
        self._buat_header()
        self._buat_body()
        self._buat_toast()
        self._gambar_produk()
        self._refresh_keranjang()

    # ----------------------------------------------------------------- gaya
    def _gaya(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TCombobox", fieldbackground="white", background="white")
        s.configure("Vertical.TScrollbar", background=C["line"], troughcolor=C["bg"],
                    bordercolor=C["bg"], arrowcolor=C["muted"])

    # --------------------------------------------------------------- header
    def _buat_header(self):
        h = tk.Frame(self, bg=C["card"], highlightbackground=C["line"], highlightthickness=1)
        h.pack(fill="x")
        isi = tk.Frame(h, bg=C["card"])
        isi.pack(fill="x", padx=24, pady=12)

        logo = tk.Label(isi, text=" AT ", bg=C["primary"], fg="white", font=(FONT, 12, "bold"))
        logo.pack(side="left")
        tk.Label(isi, text="Toko Alat Tulis", bg=C["card"], fg=C["ink"],
                 font=(FONT, 15, "bold")).pack(side="left", padx=10)

        self.btn_cart = Tombol(isi, "Keranjang (0)", self._fokus_keranjang)
        self.btn_cart.pack(side="right")
        Tombol(isi, "+ Produk", self.tambah_produk, bg=C["accent"], fg=C["primary_d"],
               hover=C["accent_h"]).pack(side="right", padx=8)
        Tombol(isi, "Grafik T(n)", lambda: grafik.buka(self, C, FONT), bg=C["accent"],
               fg=C["primary_d"], hover=C["accent_h"]).pack(side="right")

    # ----------------------------------------------------------------- body
    def _buat_body(self):
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=16)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        # ---- kiri: hero kecil + toolbar + grid kartu
        kiri = tk.Frame(body, bg=C["bg"])
        kiri.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        kiri.rowconfigure(3, weight=1)
        kiri.columnconfigure(0, weight=1)

        tk.Label(kiri, text="Menu Produk", bg=C["bg"], fg=C["ink"],
                 font=(FONT, 20, "bold")).grid(row=0, column=0, sticky="w")
        self.lbl_sub = tk.Label(kiri, text="", bg=C["bg"], fg=C["muted"], font=(FONT, 10))
        self.lbl_sub.grid(row=1, column=0, sticky="w", pady=(0, 8))

        bar = tk.Frame(kiri, bg=C["bg"])
        bar.grid(row=2, column=0, sticky="e")
        self.var_cari = tk.StringVar()
        e = tk.Entry(bar, textvariable=self.var_cari, width=9, font=(FONT, 10), relief="flat",
                     highlightbackground=C["line"], highlightcolor=C["primary"], highlightthickness=1)
        e.pack(side="left", ipady=5, padx=(0, 6))
        e.bind("<Return>", lambda _e: self.cari_produk())
        Tombol(bar, "Cari kode", self.cari_produk, pady=5).pack(side="left")

        chips = tk.Frame(kiri, bg=C["bg"])
        chips.grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.chips = {}
        for k, t in (("kode", "Kode"), ("nama", "Nama"), ("harga", "Harga"), ("stok", "Stok")):
            b = Tombol(chips, t, lambda kk=k: self.urutkan(kk), bg=C["card"], fg=C["ink"],
                       hover=C["accent"], font=(FONT, 9, "bold"), padx=12, pady=4)
            b.pack(side="left", padx=(0, 6))
            self.chips[k] = b
        tk.Label(chips, text="Urutkan (Merge Sort):", bg=C["bg"], fg=C["muted"],
                 font=(FONT, 9)).pack(side="left", padx=(4, 0))

        # area scroll untuk grid
        wrap = tk.Frame(kiri, bg=C["bg"])
        wrap.grid(row=3, column=0, sticky="nsew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(wrap, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        self.grid_frame = tk.Frame(self.canvas, bg=C["bg"])
        self._win = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>",
                             lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.bind_all("<MouseWheel>", self._scroll)
        self.bind_all("<Button-4>", lambda _e: self.canvas.yview_scroll(-2, "units"))
        self.bind_all("<Button-5>", lambda _e: self.canvas.yview_scroll(2, "units"))

        # ---- kanan: panel keranjang
        self.panel = tk.Frame(body, bg=C["card"], width=340,
                              highlightbackground=C["line"], highlightthickness=1)
        self.panel.grid(row=0, column=1, sticky="ns")
        self.panel.grid_propagate(False)
        self.panel.pack_propagate(False)
        self._buat_panel()

    def _scroll(self, e):
        self.canvas.yview_scroll(-1 * (e.delta // 120), "units")

    # --------------------------------------------------------------- panel
    def _buat_panel(self):
        p = self.panel
        self.lbl_judul_cart = tk.Label(p, text="Keranjang Saya", bg=C["card"], fg=C["ink"],
                                       font=(FONT, 14, "bold"), anchor="w")
        self.lbl_judul_cart.pack(fill="x", padx=16, pady=(14, 8))

        # bagian bawah dipasang dulu agar tidak terdorong keluar
        bawah = tk.Frame(p, bg=C["card"])
        bawah.pack(side="bottom", fill="x", padx=16, pady=14)

        def baris(label, var, **f):
            r = tk.Frame(bawah, bg=C["card"])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=label, bg=C["card"], fg=f.get("fg_l", C["muted"]),
                     font=f.get("font_l", (FONT, 10))).pack(side="left")
            tk.Label(r, textvariable=var, bg=C["card"], fg=f.get("fg", C["ink"]),
                     font=f.get("font", (FONT, 10))).pack(side="right")

        self.v_sub = tk.StringVar()
        self.v_pot = tk.StringVar()
        self.v_total = tk.StringVar()
        self.var_diskon = tk.StringVar(value="0")
        self.var_bayar = tk.StringVar()

        baris("Subtotal", self.v_sub)
        rd = tk.Frame(bawah, bg=C["card"])
        rd.pack(fill="x", pady=3)
        tk.Label(rd, text="Diskon (%)", bg=C["card"], fg=C["muted"], font=(FONT, 10)).pack(side="left")
        d = tk.Spinbox(rd, from_=0, to=100, textvariable=self.var_diskon, width=5, justify="right",
                       relief="flat", highlightbackground=C["line"], highlightthickness=1,
                       command=self._refresh_keranjang)
        d.pack(side="right")
        d.bind("<KeyRelease>", lambda _e: self._refresh_keranjang())
        baris("Potongan", self.v_pot)
        tk.Frame(bawah, bg=C["line"], height=1).pack(fill="x", pady=6)
        baris("TOTAL", self.v_total, font_l=(FONT, 12, "bold"), fg_l=C["ink"],
              font=(FONT, 15, "bold"), fg=C["primary"])

        tk.Label(bawah, text="Uang bayar (Rp)", bg=C["card"], fg=C["muted"],
                 font=(FONT, 9), anchor="w").pack(fill="x", pady=(10, 2))
        eb = tk.Entry(bawah, textvariable=self.var_bayar, justify="right", font=(FONT, 12), relief="flat",
                      highlightbackground=C["line"], highlightcolor=C["primary"], highlightthickness=1)
        eb.pack(fill="x", ipady=6)
        eb.bind("<Return>", lambda _e: self.bayar())
        self.entry_bayar = eb
        Tombol(bawah, "BAYAR", self.bayar, pady=10, font=(FONT, 11, "bold")).pack(fill="x", pady=(10, 0))
        Tombol(bawah, "Kosongkan keranjang", self.kosongkan, bg=C["card"], fg=C["muted"],
               hover=C["accent"], font=(FONT, 9), pady=4).pack(fill="x", pady=(6, 0))

        # daftar item
        self.cart_area = tk.Frame(p, bg=C["card"])
        self.cart_area.pack(fill="both", expand=True, padx=16)

    # --------------------------------------------------------------- toast
    def _buat_toast(self):
        self.toast = tk.Label(self, text="", bg=C["ink"], fg="white", font=(FONT, 10, "bold"),
                              padx=16, pady=9)

    def _tampil_toast(self, teks):
        self.toast.config(text=teks)
        self.toast.place(relx=0.5, rely=0.96, anchor="s")
        self.toast.lift()
        if self._toast_job:
            self.after_cancel(self._toast_job)
        self._toast_job = self.after(1800, self.toast.place_forget)

    # ------------------------------------------------------- kartu produk
    def _gambar_produk(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        data = alg.merge_sort(self.produk, key=lambda p: p[self.urut_key], desc=self.urut_desc)
        for k in range(KOLOM_GRID):
            self.grid_frame.columnconfigure(k, weight=1, uniform="kol")
        for i, p in enumerate(data):
            self._kartu(p, i // KOLOM_GRID, i % KOLOM_GRID)

        arah = "↓" if self.urut_desc else "↑"
        self.lbl_sub.config(text=f"{len(data)} produk · diurutkan menurut {self.urut_key} {arah}")
        for k, b in self.chips.items():
            aktif = k == self.urut_key
            b._bg = C["primary"] if aktif else C["card"]
            b._hover = C["primary_d"] if aktif else C["accent"]
            b.config(bg=b._bg, fg="white" if aktif else C["ink"])

    def _kartu(self, p, r, c):
        sorot = self.cari_kode == p["kode"]
        k = tk.Frame(self.grid_frame, bg=C["card"], highlightthickness=2 if sorot else 1,
                     highlightbackground=C["primary"] if sorot else C["line"])
        k.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

        # foto produk; jika tidak ada file-nya, tampil blok warna dengan inisial
        gambar = self._muat_foto(p["kode"])
        if gambar:
            tk.Label(k, image=gambar, bg=C["accent"], bd=0).pack(fill="x")
        else:
            tk.Label(k, text=p["nama"][0].upper(), bg=C["accent"], fg=C["primary"],
                     font=(FONT, 28, "bold"), height=2).pack(fill="x")
        isi = tk.Frame(k, bg=C["card"])
        isi.pack(fill="both", expand=True, padx=12, pady=10)
        tk.Label(isi, text=p["kode"], bg=C["card"], fg=C["muted"], font=(FONT, 8), anchor="w").pack(fill="x")
        tk.Label(isi, text=p["nama"], bg=C["card"], fg=C["ink"], font=(FONT, 11, "bold"),
                 anchor="w", wraplength=190, justify="left", height=2).pack(fill="x")
        tk.Label(isi, text=p["desk"], bg=C["card"], fg=C["muted"], font=(FONT, 9),
                 anchor="nw", wraplength=190, justify="left", height=2).pack(fill="x", pady=(2, 6))
        tk.Label(isi, text=alg.format_rupiah(p["harga"]), bg=C["card"], fg=C["primary"],
                 font=(FONT, 12, "bold"), anchor="w").pack(fill="x")
        habis = p["stok"] <= 0
        warna_stok = C["danger"] if habis or p["stok"] < 10 else C["ok"]
        tk.Label(isi, text="Habis" if habis else f"Stok {p['stok']}", bg=C["card"], fg=warna_stok,
                 font=(FONT, 9), anchor="w").pack(fill="x", pady=(0, 6))
        if habis:
            Tombol(isi, "Stok habis", lambda: None, bg=C["line"], fg=C["muted"], hover=C["line"],
                   pady=5).pack(fill="x")
        else:
            Tombol(isi, "+ Keranjang", lambda kd=p["kode"]: self.tambah_ke_keranjang(kd),
                   pady=5).pack(fill="x")

    def _muat_foto(self, kode):
        """Cari foto/<kode>.(png|jpg|jpeg|gif); None jika tidak ada atau gagal dibaca."""
        if kode in self._foto_cache:
            return self._foto_cache[kode]
        hasil = None
        try:
            daftar = os.listdir(FOLDER_FOTO)
        except OSError:
            daftar = []
        # toleran: P001.jpg, p001.JPG, "P001.jpg.jpg" (ekstensi tersembunyi di Windows), dst.
        cocok = [f for f in daftar
                 if f.lower().startswith(kode.lower())
                 and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
        for nama_file in cocok:
            path = os.path.join(FOLDER_FOTO, nama_file)
            ext = os.path.splitext(nama_file)[1].lower()
            try:
                if Image is not None:
                    im = ImageOps.fit(Image.open(path).convert("RGB"), UKURAN_FOTO)
                    hasil = ImageTk.PhotoImage(im)
                elif ext in (".png", ".gif"):
                    hasil = tk.PhotoImage(file=path)   # tanpa Pillow: hanya PNG/GIF
                else:
                    print(f"[FOTO] {nama_file} dilewati: format {ext} butuh Pillow "
                          f"(jalankan: pip install pillow)")
            except Exception as e:
                print(f"[FOTO] gagal membaca {nama_file}: {e}")
                hasil = None
            if hasil:
                break
        if not cocok and kode == self.produk[0]["kode"]:
            print(f"[FOTO] tidak ada file untuk {kode} di folder: {FOLDER_FOTO}")
            print(f"[FOTO] isi folder: {daftar if daftar else '(folder tidak ada / kosong)'}")
        self._foto_cache[kode] = hasil
        return hasil

    # -------------------------------------------------------------- produk
    def urutkan(self, kolom):
        if self.urut_key == kolom:
            self.urut_desc = not self.urut_desc
        else:
            self.urut_key, self.urut_desc = kolom, False
        self.cari_kode = None
        self._gambar_produk()

    def cari_produk(self):
        kode = self.var_cari.get().strip().upper()
        if not kode:
            return
        idx = alg.binary_search(self.produk, kode)             # rekursif
        if idx == -1:
            self.cari_kode = None
            self._gambar_produk()
            messagebox.showinfo("Cari", f"Produk dengan kode '{kode}' tidak ditemukan.")
            return
        self.cari_kode = kode
        self.urut_key, self.urut_desc = "kode", False
        self._gambar_produk()
        self.update_idletasks()
        n = len(self.produk)
        baris_total = max(1, (n + KOLOM_GRID - 1) // KOLOM_GRID)
        self.canvas.yview_moveto(max(0, (idx // KOLOM_GRID) / baris_total))
        self._tampil_toast(f"Ditemukan: {self.produk[idx]['nama']}")

    def tambah_produk(self):
        kode = simpledialog.askstring("Produk baru", "Kode produk (mis. P011):", parent=self)
        if not kode:
            return
        kode = kode.strip().upper()
        if alg.binary_search(self.produk, kode) != -1:
            messagebox.showerror("Gagal", "Kode sudah dipakai.")
            return
        nama = simpledialog.askstring("Produk baru", "Nama produk:", parent=self)
        harga = simpledialog.askinteger("Produk baru", "Harga (Rp):", parent=self, minvalue=1)
        stok = simpledialog.askinteger("Produk baru", "Stok:", parent=self, minvalue=0)
        if not nama or harga is None or stok is None:
            return
        self.produk = alg.merge_sort(
            self.produk + [{"kode": kode, "nama": nama.strip(), "desk": "Produk baru",
                            "harga": harga, "stok": stok}],
            key=lambda p: p["kode"])
        self._gambar_produk()

    def _produk_by_kode(self, kode):
        idx = alg.binary_search(self.produk, kode)
        return self.produk[idx] if idx != -1 else None

    # ----------------------------------------------------------- keranjang
    def tambah_ke_keranjang(self, kode):
        p = self._produk_by_kode(kode)
        sudah = next((it for it in self.keranjang if it["kode"] == kode), None)
        if (sudah["qty"] if sudah else 0) + 1 > p["stok"]:
            messagebox.showerror("Stok kurang", f"Stok {p['nama']} hanya {p['stok']}.")
            return
        if sudah:
            sudah["qty"] += 1
        else:
            self.keranjang.append({"kode": kode, "nama": p["nama"], "harga": p["harga"], "qty": 1})
        self._refresh_keranjang()
        self._tampil_toast(f"{p['nama']} masuk keranjang")

    def _ubah_qty(self, kode, delta):
        it = next((x for x in self.keranjang if x["kode"] == kode), None)
        if not it:
            return
        baru = it["qty"] + delta
        if baru > self._produk_by_kode(kode)["stok"]:
            self._tampil_toast("Stok tidak mencukupi")
            return
        if baru <= 0:
            self.keranjang.remove(it)
        else:
            it["qty"] = baru
        self._refresh_keranjang()

    def kosongkan(self):
        self.keranjang = []
        self._refresh_keranjang()

    def _fokus_keranjang(self):
        self.entry_bayar.focus_set()

    def _persen_diskon(self):
        try:
            return max(0, min(100, int(self.var_diskon.get() or 0)))
        except ValueError:
            return 0

    def _hitung(self):
        subtotal = alg.hitung_total(self.keranjang)            # rekursif
        potongan = subtotal * self._persen_diskon() // 100
        total = alg.bulatkan(subtotal - potongan)
        return subtotal, potongan, total

    def _refresh_keranjang(self):
        for w in self.cart_area.winfo_children():
            w.destroy()
        jumlah = sum(it["qty"] for it in self.keranjang)
        self.btn_cart.config(text=f"Keranjang ({jumlah})")
        self.lbl_judul_cart.config(text=f"Keranjang Saya ({jumlah})")

        if not self.keranjang:
            tk.Label(self.cart_area, text="🛒", bg=C["card"], font=(FONT, 34)).pack(pady=(40, 4))
            tk.Label(self.cart_area, text="Keranjangmu masih kosong", bg=C["card"], fg=C["muted"],
                     font=(FONT, 10)).pack()
        for it in self.keranjang:
            r = tk.Frame(self.cart_area, bg=C["card"])
            r.pack(fill="x", pady=5)
            kiri = tk.Frame(r, bg=C["card"])
            kiri.pack(side="left", fill="x", expand=True)
            tk.Label(kiri, text=it["nama"], bg=C["card"], fg=C["ink"], font=(FONT, 10, "bold"),
                     anchor="w").pack(fill="x")
            tk.Label(kiri, text=alg.format_rupiah(it["harga"] * it["qty"]), bg=C["card"],
                     fg=C["primary"], font=(FONT, 10), anchor="w").pack(fill="x")
            q = tk.Frame(r, bg=C["card"])
            q.pack(side="right")
            for t, d in (("−", -1), ("+", 1)):
                Tombol(q, t, lambda k=it["kode"], dd=d: self._ubah_qty(k, dd), bg=C["accent"],
                       fg=C["primary_d"], hover=C["accent_h"], padx=8, pady=0,
                       font=(FONT, 11, "bold")).pack(side="left" if d < 0 else "right")
                if d < 0:
                    tk.Label(q, text=str(it["qty"]), bg=C["card"], fg=C["ink"],
                             font=(FONT, 10, "bold"), width=3).pack(side="left")

        s, pot, tot = self._hitung()
        self.v_sub.set(alg.format_rupiah(s))
        self.v_pot.set("-" + alg.format_rupiah(pot))
        self.v_total.set(alg.format_rupiah(tot))

    # ------------------------------------------------------------ pembayaran
    def bayar(self):
        if not self.keranjang:
            messagebox.showwarning("Keranjang kosong", "Belum ada barang di keranjang.")
            return
        subtotal, potongan, total = self._hitung()
        try:
            uang = int(self.var_bayar.get().replace(".", "").strip())
        except ValueError:
            messagebox.showerror("Input salah", "Masukkan uang bayar berupa angka.")
            return
        if uang < total:
            messagebox.showerror("Uang kurang", f"Kurang {alg.format_rupiah(total - uang)}.")
            return

        kembalian = uang - total
        pecahan = alg.pecahan_kembalian(kembalian)             # rekursif
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        for it in self.keranjang:
            self._produk_by_kode(it["kode"])["stok"] -= it["qty"]

        struk = self._buat_struk(waktu, subtotal, potongan, total, uang, kembalian, pecahan)
        try:
            with open(FILE_RIWAYAT, "a", encoding="utf-8") as f:
                f.write(struk + "\n" + "=" * 36 + "\n")
        except OSError:
            pass

        self.keranjang = []
        self.var_bayar.set("")
        self.var_diskon.set("0")
        self._gambar_produk()
        self._refresh_keranjang()
        self._tampil_struk(struk)

    def _buat_struk(self, waktu, subtotal, potongan, total, uang, kembalian, pecahan):
        r = alg.format_rupiah
        baris = ["      TOKO ALAT TULIS", f"  {waktu}", "-" * 36]
        for it in self.keranjang:
            baris.append(it["nama"])
            baris.append(f"  {it['qty']} x {r(it['harga']):>12} {r(it['harga'] * it['qty']):>14}")
        baris += ["-" * 36,
                  f"{'Subtotal':<14}{r(subtotal):>22}",
                  f"{'Diskon':<14}{'-' + r(potongan):>22}",
                  f"{'TOTAL':<14}{r(total):>22}",
                  f"{'Bayar':<14}{r(uang):>22}",
                  f"{'Kembalian':<14}{r(kembalian):>22}"]
        if pecahan:
            baris += ["", "Rincian kembalian:"]
            for nominal, jml in pecahan:
                baris.append(f"  {jml} x {r(nominal)}")
        baris += ["", "   Terima kasih sudah berbelanja!"]
        return "\n".join(baris)

    def _tampil_struk(self, teks):
        w = tk.Toplevel(self)
        w.title("Struk Pembayaran")
        w.geometry("360x480")
        w.configure(bg=C["bg"])
        t = tk.Text(w, font=("Courier New", 10), wrap="none", relief="flat", bg="white")
        t.insert("1.0", teks)
        t.config(state="disabled")
        t.pack(fill="both", expand=True, padx=12, pady=12)
        Tombol(w, "Tutup", w.destroy).pack(pady=(0, 12))


if __name__ == "__main__":
    KasirApp().mainloop()
