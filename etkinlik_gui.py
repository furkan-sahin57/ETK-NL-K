# -*- coding: utf-8 -*-
"""
Etkinlik Kayıt Sistemi - Grafik Arayüz (PyQt5)
================================================
Sayfalar  : Dashboard | Etkinlik Ekle | Kayıt Yönetimi | Biletler | Rapor | Admin Paneli
Tema      : Beyaz içerik alanı + koyu (#0F172A) kenar çubuğu
Gereksinim: PyQt5  →  pip install PyQt5
Çalıştırma: python etkinlik_gui.py
"""

import sys
from datetime import date, datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QVBoxLayout, QHBoxLayout, QFormLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QDialog, QMessageBox, QSizePolicy, QSplitter,
    QTextEdit, QDateEdit,
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QColor, QFont

# ── Backend ──────────────────────────────────────────────────────────────────
try:
    from etkinlik_sistemi import Etkinlik, Katilimci, Bilet
except ImportError:
    # Bağımsız çalışabilmek için minimal inline fallback
    import uuid as _uuid

    class Katilimci:
        def __init__(self, i, a, m): self._i, self._a, self._m = i, a, m
        def get_id(self): return self._i
        def get_ad(self): return self._a
        def get_email(self): return self._m

    class Etkinlik:
        def __init__(self, i, a, t, k):
            self._i, self._a, self._t, self._k = i, a, t, k
            self._ks = []
        def get_id(self): return self._i
        def get_ad(self): return self._a
        def get_tarih(self): return self._t
        def get_kapasite(self): return self._k
        def get_katilimcilar(self): return list(self._ks)
        def get_katilimci_sayisi(self): return len(self._ks)
        def katilimci_ekle(self, k):
            if len(self._ks) < self._k:
                self._ks.append(k); return True, "Başarılı"
            return False, "Kapasite dolu!"
        def katilimci_cikar(self, kid):
            for k in self._ks:
                if k.get_id() == kid:
                    self._ks.remove(k); return True, f"'{k.get_ad()}' silindi."
            return False, "Bulunamadı."

    class Bilet:
        def __init__(self, e, k, bid=None):
            self._bid = bid or str(_uuid.uuid4()).upper()[:12]
            self._e, self._k = e, k
        def get_bilet_id(self): return self._bid
        def get_etkinlik(self): return self._e
        def get_katilimci(self): return self._k
        def bilet_olustur(self):
            return (f"BİLET NO  : {self._bid}\n"
                    f"ETKİNLİK  : {self._e.get_ad()}\n"
                    f"TARİH     : {self._e.get_tarih()}\n"
                    f"KATILIMCI : {self._k.get_ad()}\n"
                    f"E-POSTA   : {self._k.get_email()}")

# ── Renk Paleti ──────────────────────────────────────────────────────────────
# Sidebar: koyu kahve (#1C1917) — içerik alanı: krem/amber (#FFFBEB)

SB = "#1C1917"          # sidebar arka plan (koyu kahve)
SB_AKT = "#292524"      # sidebar aktif satır
SB_TXT = "#A8A29E"      # sidebar pasif metin
SB_AKT_TXT = "#F59E0B"  # sidebar aktif metin (amber/altın)
SB_BORDER = "#292524"   # sidebar sağ kenar

IC_BG = "#FFFBEB"       # içerik arka plan (krem/amber)
IC_CARD = "#FFFFFF"     # kart arka planı
IC_CARD2 = "#FEF3C7"    # ikincil kart / zebra (açık amber)
IC_BORDER = "#FDE68A"   # içerik kenarlık (amber tonu)
IC_TXT = "#1C1917"      # ana metin (koyu kahve)
IC_TXT2 = "#78716C"     # ikincil metin (stone gri)

VURGU = "#F59E0B"       # amber vurgu
BASARI = "#10B981"      # yeşil
UYARI = "#EF4444"       # kırmızı (uyarı)
HATA = "#EF4444"        # kırmızı
MOR = "#8B5CF6"         # mor

ADMIN_SIFRE = "123"        # Admin paneli şifresi


# ── Yardımcı Widget'lar ───────────────────────────────────────────────────────

class KpiCard(QFrame):
    """Dashboard'daki özet sayı kartı."""

    def __init__(self, baslik: str, deger, renk: str):
        super().__init__()
        self.setFixedHeight(110)
        self.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 12px; "
            f"border: 1px solid {IC_BORDER};"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        t = QLabel(baslik.upper())
        t.setStyleSheet(
            f"color: {IC_TXT2}; font-size: 11px; font-weight: 700; letter-spacing: 1px;"
        )
        v = QLabel(str(deger))
        v.setStyleSheet(f"color: {renk}; font-size: 28px; font-weight: 900;")
        lay.addWidget(t)
        lay.addWidget(v)


class RaporKarti(QFrame):
    """Rapor sayfasında etkinlik istatistiklerini gösteren kart."""

    def __init__(self, etkinlik: Etkinlik):
        super().__init__()
        self.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        ana = QVBoxLayout(self)
        ana.setContentsMargins(24, 20, 24, 20)
        ana.setSpacing(14)

        # — Başlık —
        blay = QHBoxLayout()
        ad_lbl = QLabel(f"📅  {etkinlik.get_ad()}")
        ad_lbl.setStyleSheet(f"color: {IC_TXT}; font-size: 16px; font-weight: 900;")
        blay.addWidget(ad_lbl)
        blay.addStretch()
        t_lbl = QLabel(str(etkinlik.get_tarih()))
        t_lbl.setStyleSheet(f"color: {IC_TXT2}; font-size: 12px; font-weight: 600;")
        blay.addWidget(t_lbl)
        ana.addLayout(blay)

        # — İstatistik kutucukları —
        kapasite = etkinlik.get_kapasite()
        katildi  = etkinlik.get_katilimci_sayisi()
        bos      = kapasite - katildi
        pct      = int(katildi / kapasite * 100) if kapasite else 0

        stat_lay = QHBoxLayout()
        stat_lay.setSpacing(12)
        for etiket, deger, renk in [
            ("Kapasite", str(kapasite), VURGU),
            ("Katıldı",  str(katildi),  BASARI),
            ("Boş",      str(bos),      UYARI),
            ("Doluluk",  f"%{pct}",     MOR),
        ]:
            kutu = QFrame()
            kutu.setStyleSheet(
                f"background-color: {IC_CARD2}; border-radius: 8px; border: 1px solid {IC_BORDER};"
            )
            kutu.setFixedHeight(64)
            klay = QVBoxLayout(kutu)
            klay.setContentsMargins(10, 6, 10, 6)
            klay.setSpacing(2)
            d = QLabel(deger)
            d.setStyleSheet(f"color: {renk}; font-size: 20px; font-weight: 900;")
            d.setAlignment(Qt.AlignCenter)
            e = QLabel(etiket)
            e.setStyleSheet(f"color: {IC_TXT2}; font-size: 10px; font-weight: 700;")
            e.setAlignment(Qt.AlignCenter)
            klay.addWidget(d)
            klay.addWidget(e)
            stat_lay.addWidget(kutu)
        ana.addLayout(stat_lay)

        # — Progress bar —
        bar_bg = QFrame()
        bar_bg.setFixedHeight(8)
        bar_bg.setStyleSheet(f"background-color: {IC_BORDER}; border-radius: 4px; border: none;")
        bar_bg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        ana.addWidget(bar_bg)

        bar_dolu = QFrame(bar_bg)
        bar_dolu.setFixedHeight(8)
        renk_bar = BASARI if pct < 80 else HATA
        bar_dolu.setStyleSheet(f"background-color: {renk_bar}; border-radius: 4px; border: none;")
        self._bar_dolu = bar_dolu
        self._bar_bg   = bar_bg
        self._pct      = pct

        # — Katılımcı tablosu —
        katilimcilar = etkinlik.get_katilimcilar()
        if katilimcilar:
            tb_lbl = QLabel("Katılımcı Listesi")
            tb_lbl.setStyleSheet(
                f"color: {IC_TXT2}; font-size: 11px; font-weight: 800; letter-spacing: 1px;"
            )
            ana.addWidget(tb_lbl)

            tablo = QTableWidget()
            tablo.setColumnCount(3)
            tablo.setHorizontalHeaderLabels(["#", "Ad Soyad", "E-Posta"])
            tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tablo.verticalHeader().setVisible(False)
            tablo.setShowGrid(False)
            tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
            tablo.setFixedHeight(min(len(katilimcilar), 6) * 36 + 42)
            tablo.setStyleSheet(self._tablo_stili())
            for i, k in enumerate(katilimcilar):
                tablo.insertRow(i)
                tablo.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                tablo.setItem(i, 1, QTableWidgetItem(k.get_ad()))
                tablo.setItem(i, 2, QTableWidgetItem(k.get_email()))
            ana.addWidget(tablo)
        else:
            bos_lbl = QLabel("Henüz kayıtlı katılımcı yok.")
            bos_lbl.setStyleSheet(f"color: {IC_TXT2}; font-size: 13px; font-style: italic;")
            ana.addWidget(bos_lbl)

    def _tablo_stili(self) -> str:
        return (
            f"QTableWidget {{ background-color: {IC_BG}; color: {IC_TXT}; "
            f"border: none; border-radius: 8px; gridline-color: transparent; }} "
            f"QHeaderView::section {{ background-color: {IC_CARD2}; color: {VURGU}; "
            f"padding: 8px; font-weight: bold; border: none; "
            f"border-bottom: 1px solid {IC_BORDER}; }} "
            f"QTableWidget::item {{ padding: 6px 10px; }}"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self._bar_bg.width()
        self._bar_dolu.setFixedWidth(max(0, int(w * self._pct / 100)))


class BiletDetayDialog(QDialog):
    """Seçili biletin detaylarını gösteren diyalog penceresi."""

    def __init__(self, parent, bilet_verisi: dict):
        super().__init__(parent)
        self.setWindowTitle("Bilet Detayı")
        self.setFixedSize(480, 380)
        self.setStyleSheet(f"background-color: {IC_BG};")

        eid  = bilet_verisi["etkinlik_id"]
        kat  = bilet_verisi["katilimci"]
        bil  = bilet_verisi["bilet"]
        etk  = parent.etkinlikler.get(eid)
        etk_adi   = etk.get_ad()         if etk else "-"
        etk_tarih = str(etk.get_tarih()) if etk else "-"

        ana = QVBoxLayout(self)
        ana.setContentsMargins(30, 30, 30, 30)
        ana.setSpacing(16)

        # Başlık çubuğu
        baslik_frame = QFrame()
        baslik_frame.setStyleSheet(
            f"background-color: {VURGU}; border-radius: 10px; border: none;"
        )
        baslik_frame.setFixedHeight(64)
        b_lay = QHBoxLayout(baslik_frame)
        b_lay.setContentsMargins(20, 0, 20, 0)
        ikon_lbl = QLabel("🎫")
        ikon_lbl.setStyleSheet("font-size: 26px; background: transparent;")
        b_lay.addWidget(ikon_lbl)
        baslik_lbl = QLabel("BİLET DETAYI")
        baslik_lbl.setStyleSheet(
            "color: #ffffff; font-size: 17px; font-weight: 900; "
            "letter-spacing: 2px; background: transparent;"
        )
        b_lay.addWidget(baslik_lbl)
        b_lay.addStretch()
        no_lbl = QLabel(bil.get_bilet_id())
        no_lbl.setStyleSheet(
            "color: #ffffff; font-size: 13px; font-weight: 900; "
            "font-family: 'Consolas', monospace; background: transparent;"
        )
        b_lay.addWidget(no_lbl)
        ana.addWidget(baslik_frame)

        # Detay kartı
        kart = QFrame()
        kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 12px; border: 1px solid {IC_BORDER};"
        )
        kart_lay = QVBoxLayout(kart)
        kart_lay.setContentsMargins(24, 18, 24, 18)
        kart_lay.setSpacing(14)

        satirlar = [
            ("📌", "Etkinlik",   etk_adi,        VURGU),
            ("📅", "Tarih",      etk_tarih,       UYARI),
            ("👤", "Katılımcı",  kat.get_ad(),    IC_TXT),
            ("✉",  "E-Posta",    kat.get_email(), IC_TXT2),
        ]
        for i, (ikon, etiket, deger, renk) in enumerate(satirlar):
            satir = QHBoxLayout()
            satir.setSpacing(12)

            ikon_w = QLabel(ikon)
            ikon_w.setFixedWidth(28)
            ikon_w.setStyleSheet("font-size: 16px; background: transparent;")
            ikon_w.setAlignment(Qt.AlignCenter)

            etiket_w = QLabel(etiket)
            etiket_w.setFixedWidth(80)
            etiket_w.setStyleSheet(
                f"color: {IC_TXT2}; font-size: 12px; font-weight: 700; background: transparent;"
            )

            deger_w = QLabel(deger)
            deger_w.setStyleSheet(
                f"color: {renk}; font-size: 13px; font-weight: 700; background: transparent;"
            )
            deger_w.setWordWrap(True)

            satir.addWidget(ikon_w)
            satir.addWidget(etiket_w)
            satir.addWidget(deger_w, 1)
            kart_lay.addLayout(satir)

            if i < len(satirlar) - 1:
                ayrac = QFrame()
                ayrac.setFrameShape(QFrame.HLine)
                ayrac.setStyleSheet(f"color: {IC_BORDER}; background-color: {IC_BORDER}; border: none;")
                ayrac.setFixedHeight(1)
                kart_lay.addWidget(ayrac)

        ana.addWidget(kart)

        # Kapat butonu
        btn_kapat = QPushButton("KAPAT")
        btn_kapat.setFixedHeight(44)
        btn_kapat.setFont(QFont("Arial", 11, QFont.Bold))
        btn_kapat.setCursor(Qt.PointingHandCursor)
        btn_kapat.setStyleSheet(f"""
            QPushButton {{
                background-color: {IC_CARD};
                color: {VURGU};
                font-weight: 900;
                border-radius: 8px;
                border: 2px solid {VURGU};
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {VURGU};
                color: white;
            }}
        """)
        btn_kapat.clicked.connect(self.accept)
        ana.addWidget(btn_kapat)


class AdminGirisDialog(QDialog):
    """Admin paneline erişim için şifre doğrulama diyalogu."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Admin Girişi")
        self.setFixedSize(360, 220)
        self.setStyleSheet(f"background-color: {IC_BG};")
        self.giris_basarili = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(16)

        t = QLabel("🔐  Admin Paneli")
        t.setStyleSheet(f"color: {IC_TXT}; font-size: 18px; font-weight: 800;")
        t.setAlignment(Qt.AlignCenter)
        lay.addWidget(t)

        aciklama = QLabel("Devam etmek için admin şifresini girin.")
        aciklama.setStyleSheet(f"color: {IC_TXT2}; font-size: 12px;")
        aciklama.setAlignment(Qt.AlignCenter)
        lay.addWidget(aciklama)

        self.sifre_input = QLineEdit()
        self.sifre_input.setPlaceholderText("Şifre")
        self.sifre_input.setEchoMode(QLineEdit.Password)
        self.sifre_input.setFixedHeight(42)
        self.sifre_input.setStyleSheet(self._input_stili())
        self.sifre_input.returnPressed.connect(self._dogrula)
        lay.addWidget(self.sifre_input)

        btn = QPushButton("GİRİŞ YAP")
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Arial", 10, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VURGU}; color: white;
                border-radius: 8px; border: none; font-weight: 900;
            }}
            QPushButton:hover {{ background-color: #FBBF24; }}
        """)
        btn.clicked.connect(self._dogrula)
        lay.addWidget(btn)

    def _input_stili(self) -> str:
        return (
            f"QLineEdit {{ background: {IC_CARD}; color: {IC_TXT}; "
            f"padding: 10px 14px; border-radius: 8px; border: 1px solid {IC_BORDER}; "
            f"font-size: 13px; }} "
            f"QLineEdit:focus {{ border: 1.5px solid {VURGU}; }}"
        )

    def _dogrula(self):
        """Girilen şifreyi doğrular; hatalıysa uyarı gösterir."""
        if self.sifre_input.text() == ADMIN_SIFRE:
            self.giris_basarili = True
            self.accept()
        else:
            QMessageBox.warning(self, "Hatalı Şifre", "Girdiğiniz şifre yanlış.")
            self.sifre_input.clear()
            self.sifre_input.setFocus()


# ── Ana Pencere ───────────────────────────────────────────────────────────────

class EtkinlikApp(QMainWindow):
    """
    ProEvent ana uygulama penceresi.

    Sayfalar:
        0 - Dashboard       : KPI özeti + etkinlik takvimi
        1 - Etkinlik Ekle   : Yeni etkinlik oluşturma formu
        2 - Kayıt Yönetimi  : Katılımcı kayıt + listeleme
        3 - Biletler        : Oluşturulan biletler
        4 - Rapor           : Etkinlik bazlı katılımcı raporu
        5 - Admin Paneli    : Etkinlik / katılımcı silme, sistem bilgisi
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProEvent — Yönetim Paneli")
        self.resize(1300, 880)

        # Veri yapıları
        self.etkinlikler: dict[int, Etkinlik] = {
            1: Etkinlik(1, "Python Workshop",           date(2026, 6, 15), 50),
            2: Etkinlik(2, "Web Tasarım Semineri",      date(2026, 7, 10), 30),
            3: Etkinlik(3, "Yapay Zeka Konferansı",     date(2026, 8, 20), 100),
            4: Etkinlik(4, "Girişimcilik Zirvesi",      date(2026, 9,  5),  60),
            5: Etkinlik(5, "Siber Güvenlik Bootcamp",   date(2026, 7, 28),  25),
        }

        # ── Örnek katılımcı verileri ──────────────────────────────────────────
        _ornek_kayitlar = [
            # (etkinlik_id, ad_soyad, email)
            (1, "Ahmet Yılmaz",        "ahmet.yilmaz@gmail.com"),
            (1, "Zeynep Kaya",         "zeynep.kaya@hotmail.com"),
            (1, "Murat Demir",         "murat.demir@outlook.com"),
            (1, "Elif Şahin",          "elif.sahin@yahoo.com"),
            (1, "Can Arslan",          "can.arslan@gmail.com"),
            (2, "Selin Çelik",         "selin.celik@gmail.com"),
            (2, "Burak Öztürk",        "burak.ozturk@hotmail.com"),
            (2, "Fatma Aydın",         "fatma.aydin@gmail.com"),
            (2, "Emre Koç",            "emre.koc@outlook.com"),
            (3, "Ayşe Polat",          "ayse.polat@gmail.com"),
            (3, "Hasan Doğan",         "hasan.dogan@hotmail.com"),
            (3, "Merve Güneş",         "merve.gunes@yahoo.com"),
            (3, "Tarık Yıldız",        "tarik.yildiz@gmail.com"),
            (3, "Büşra Aktaş",         "busra.aktas@outlook.com"),
            (3, "Onur Kaplan",         "onur.kaplan@gmail.com"),
            (4, "Deniz Erdoğan",       "deniz.erdogan@gmail.com"),
            (4, "Pınar Çakır",         "pinar.cakir@hotmail.com"),
            (4, "Gökhan Şimşek",       "gokhan.simsek@gmail.com"),
            (5, "Cem Yücel",           "cem.yucel@gmail.com"),
            (5, "Nazlı Bozkurt",       "nazli.bozkurt@outlook.com"),
            (5, "Sercan Tunç",         "sercan.tunc@hotmail.com"),
        ]

        self.biletler:               list[dict] = []   # [{etkinlik_id, katilimci, bilet}]
        self.toplam_katilimci_sayisi: int        = len(_ornek_kayitlar)

        for eid, ad, email in _ornek_kayitlar:
            kid = _ornek_kayitlar.index((eid, ad, email)) + 1
            kat = Katilimci(kid, ad, email)
            ok, _ = self.etkinlikler[eid].katilimci_ekle(kat)
            if ok:
                bil = Bilet(self.etkinlikler[eid], kat)
                self.biletler.append({"etkinlik_id": eid, "katilimci": kat, "bilet": bil})
        self._secili_etkinlik_id:    int | None  = None
        self._etk_butonlari:         dict        = {}

        self._build_ui()
        self._saat_baslat()

    # ── Arayüz İnşası ────────────────────────────────────────────────────────

    def _build_ui(self):
        """Ana pencere düzenini oluşturur: sidebar + sayfa yığını."""
        merkez = QWidget()
        merkez.setStyleSheet(f"background-color: {IC_BG};")
        self.setCentralWidget(merkez)

        ana_lay = QHBoxLayout(merkez)
        ana_lay.setContentsMargins(0, 0, 0, 0)
        ana_lay.setSpacing(0)

        # — Sidebar —
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(
            f"background-color: {SB}; border-right: 1px solid {SB_BORDER};"
        )
        s_lay = QVBoxLayout(sidebar)
        s_lay.setContentsMargins(0, 0, 0, 0)
        s_lay.setSpacing(0)

        # Logo/başlık
        logo_frame = QFrame()
        logo_frame.setFixedHeight(72)
        logo_frame.setStyleSheet(f"background-color: {SB}; border-bottom: 1px solid {SB_BORDER}; border-right: none;")
        l_lay = QHBoxLayout(logo_frame)
        l_lay.setContentsMargins(20, 0, 20, 0)
        logo_lbl = QLabel("🎟  ProEvent")
        logo_lbl.setStyleSheet(
            "color: #F8FAFC; font-size: 18px; font-weight: 900; letter-spacing: 1px;"
        )
        l_lay.addWidget(logo_lbl)
        s_lay.addWidget(logo_frame)
        s_lay.addSpacing(12)

        # Navigasyon butonları
        nav_items = [
            ("📊", "Dashboard"),
            ("➕", "Etkinlik Ekle"),
            ("👥", "Kayıt Yönetimi"),
            ("🎫", "Biletler"),
            ("📋", "Rapor"),
            ("🔐", "Admin Paneli"),
        ]
        self.nav: list[QPushButton] = []
        for ikon, isim in nav_items:
            btn = QPushButton(f"  {ikon}   {isim}")
            btn.setCheckable(True)
            btn.setFixedHeight(52)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Arial", 11))
            btn.setStyleSheet(self._nav_btn_stili())
            btn.clicked.connect(lambda _, m=isim: self._goto(m))
            s_lay.addWidget(btn)
            self.nav.append(btn)

        s_lay.addStretch()

        # Saat
        self.lbl_saat = QLabel()
        self.lbl_saat.setStyleSheet(
            f"color: {SB_TXT}; margin: 16px 20px; font-family: 'Consolas'; font-size: 11px;"
        )
        s_lay.addWidget(self.lbl_saat)
        ana_lay.addWidget(sidebar)

        # — Sayfa yığını —
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {IC_BG};")
        self.stack.addWidget(self._ui_dashboard())        # 0
        self.stack.addWidget(self._ui_ekle())             # 1
        self.stack.addWidget(self._ui_kayit_yonetimi())   # 2
        self.stack.addWidget(self._ui_biletler())         # 3
        self.stack.addWidget(self._ui_rapor())            # 4
        self.stack.addWidget(self._ui_admin())            # 5
        ana_lay.addWidget(self.stack)

        self._goto("Dashboard")

    # ── Sayfa: Dashboard ─────────────────────────────────────────────────────

    def _ui_dashboard(self) -> QWidget:
        """Dashboard sayfasını oluşturur."""
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(24)

        # Başlık
        ust = QHBoxLayout()
        baslik = QLabel("Dashboard")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        ust.addWidget(baslik)
        ust.addStretch()
        tarih_lbl = QLabel(datetime.now().strftime("%d %B %Y"))
        tarih_lbl.setStyleSheet(f"color: {IC_TXT2}; font-size: 13px;")
        ust.addWidget(tarih_lbl)
        lay.addLayout(ust)

        # KPI kartları
        self.kpi_lay = QHBoxLayout()
        self.kpi_lay.setSpacing(16)
        lay.addLayout(self.kpi_lay)

        # Ayraç çizgisi
        ayrac = QFrame()
        ayrac.setFrameShape(QFrame.HLine)
        ayrac.setStyleSheet(f"color: {IC_BORDER};")
        lay.addWidget(ayrac)

        # Tablo başlığı
        t_lbl = QLabel("Aktif Etkinlik Takvimi")
        t_lbl.setStyleSheet(f"color: {IC_TXT}; font-size: 16px; font-weight: 800;")
        lay.addWidget(t_lbl)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(
            ["ID", "Etkinlik Adı", "Tarih", "Doluluk", "Durum"]
        )
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setStyleSheet(self._tablo_stili())
        self.tablo.setAlternatingRowColors(True)
        lay.addWidget(self.tablo)

        # Hızlı kayıt butonu
        btn = QPushButton("⚡   HIZLI KATILIMCI KAYDI YAP")
        btn.setFixedHeight(52)
        btn.setFont(QFont("Arial", 11, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._birincil_buton_stili())
        btn.clicked.connect(lambda: self._goto("Kayıt Yönetimi"))
        lay.addWidget(btn)

        return w

    # ── Sayfa: Etkinlik Ekle ─────────────────────────────────────────────────

    def _ui_ekle(self) -> QWidget:
        """Yeni etkinlik oluşturma sayfasını oluşturur."""
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(28)

        baslik = QLabel("Yeni Etkinlik Oluştur")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        lay.addWidget(baslik)

        form = QFrame()
        form.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 16px; border: 1px solid {IC_BORDER};"
        )
        flay = QFormLayout(form)
        flay.setContentsMargins(32, 28, 32, 28)
        flay.setSpacing(20)

        lbl_stili = f"color: {IC_TXT}; font-size: 13px; font-weight: 700;"

        self.in_ad = QLineEdit()
        self.in_ad.setPlaceholderText("Örnek: Python Workshop 2026")
        self.in_ad.setFixedHeight(44)
        self.in_ad.setStyleSheet(self._input_stili())

        self.in_tarih = QDateEdit()
        self.in_tarih.setCalendarPopup(True)
        self.in_tarih.setDate(QDate.currentDate().addDays(30))
        self.in_tarih.setFixedHeight(44)
        self.in_tarih.setStyleSheet(self._input_stili())
        self.in_tarih.setDisplayFormat("dd.MM.yyyy")

        self.in_kap = QSpinBox()
        self.in_kap.setRange(1, 5000)
        self.in_kap.setValue(50)
        self.in_kap.setFixedHeight(44)
        self.in_kap.setStyleSheet(self._input_stili())

        flay.addRow(QLabel("Etkinlik Adı :", styleSheet=lbl_stili), self.in_ad)
        flay.addRow(QLabel("Tarih        :", styleSheet=lbl_stili), self.in_tarih)
        flay.addRow(QLabel("Kontenjan    :", styleSheet=lbl_stili), self.in_kap)

        lay.addWidget(form)

        btn = QPushButton("💾   SİSTEME KAYDET")
        btn.setFixedHeight(52)
        btn.setFont(QFont("Arial", 11, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._birincil_buton_stili())
        btn.clicked.connect(self._etkinlik_kaydet)
        lay.addWidget(btn)
        lay.addStretch()

        return w

    # ── Sayfa: Kayıt Yönetimi ────────────────────────────────────────────────

    def _ui_kayit_yonetimi(self) -> QWidget:
        """Katılımcı kayıt ve listeleme sayfasını oluşturur."""
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        baslik = QLabel("Kayıt Yönetimi")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        lay.addWidget(baslik)

        # — Kayıt formu kartı —
        form = QFrame()
        form.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(22, 18, 22, 18)
        form_lay.setSpacing(14)

        etk_lbl = QLabel("ETKİNLİK SEÇİN")
        etk_lbl.setStyleSheet(
            f"color: {IC_TXT2}; font-size: 11px; font-weight: 800; letter-spacing: 1px;"
        )
        form_lay.addWidget(etk_lbl)

        # Etkinlik seçim butonları
        self.etk_buton_widget = QWidget()
        self.etk_buton_widget.setStyleSheet("background: transparent;")
        self.etk_buton_lay = QHBoxLayout(self.etk_buton_widget)
        self.etk_buton_lay.setContentsMargins(0, 0, 0, 0)
        self.etk_buton_lay.setSpacing(8)
        self.etk_buton_lay.addStretch()
        form_lay.addWidget(self.etk_buton_widget)

        # Giriş alanları
        alt_lay = QHBoxLayout()
        alt_lay.setSpacing(12)

        self.in_kat_ad = QLineEdit()
        self.in_kat_ad.setPlaceholderText("Katılımcı Adı Soyadı")
        self.in_kat_ad.setFixedHeight(44)
        self.in_kat_ad.setStyleSheet(self._input_stili())

        self.in_kat_mail = QLineEdit()
        self.in_kat_mail.setPlaceholderText("ornek@gmail.com")
        self.in_kat_mail.setFixedHeight(44)
        self.in_kat_mail.setStyleSheet(self._input_stili())

        btn_ekle = QPushButton("KAYDI TAMAMLA")
        btn_ekle.setFixedHeight(44)
        btn_ekle.setFixedWidth(180)
        btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.setFont(QFont("Arial", 10, QFont.Bold))
        btn_ekle.setStyleSheet(self._birincil_buton_stili())
        btn_ekle.clicked.connect(self._manuel_kayit_ekle)

        alt_lay.addWidget(self.in_kat_ad)
        alt_lay.addWidget(self.in_kat_mail)
        alt_lay.addWidget(btn_ekle)
        form_lay.addLayout(alt_lay)
        lay.addWidget(form)

        # Tüm kayıtlar tablosu
        k_lbl = QLabel("Tüm Kayıtlar")
        k_lbl.setStyleSheet(f"color: {IC_TXT}; font-size: 15px; font-weight: 800;")
        lay.addWidget(k_lbl)

        self.k_tablo = QTableWidget()
        self.k_tablo.setColumnCount(5)
        self.k_tablo.setHorizontalHeaderLabels(
            ["ID", "Katılımcı", "E-Posta", "Etkinlik", "Bilet No"]
        )
        self.k_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.k_tablo.verticalHeader().setVisible(False)
        self.k_tablo.setStyleSheet(self._tablo_stili())
        self.k_tablo.setAlternatingRowColors(True)
        lay.addWidget(self.k_tablo)

        return w

    # ── Sayfa: Biletler ──────────────────────────────────────────────────────

    def _ui_biletler(self) -> QWidget:
        """Oluşturulan biletlerin listelendiği sayfayı oluşturur."""
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        ust = QHBoxLayout()
        t = QLabel("Oluşturulan Biletler")
        t.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        ust.addWidget(t)
        ust.addStretch()

        btn_detay = QPushButton("BİLET DETAYINI GÖR")
        btn_detay.setFixedHeight(44)
        btn_detay.setFont(QFont("Arial", 10, QFont.Bold))
        btn_detay.setCursor(Qt.PointingHandCursor)
        btn_detay.setStyleSheet(self._ikincil_buton_stili(MOR))
        btn_detay.clicked.connect(self._bilet_detay_goster)
        ust.addWidget(btn_detay)
        lay.addLayout(ust)

        self.b_tablo = QTableWidget()
        self.b_tablo.setColumnCount(4)
        self.b_tablo.setHorizontalHeaderLabels(
            ["Bilet No", "Katılımcı", "E-Posta", "Etkinlik"]
        )
        self.b_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.b_tablo.verticalHeader().setVisible(False)
        self.b_tablo.setStyleSheet(self._tablo_stili())
        self.b_tablo.setAlternatingRowColors(True)
        lay.addWidget(self.b_tablo)

        return w

    # ── Sayfa: Rapor ─────────────────────────────────────────────────────────

    def _ui_rapor(self) -> QWidget:
        """Katılımcı raporunun görüntülendiği sayfayı oluşturur."""
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        ust = QHBoxLayout()
        t = QLabel("Katılımcı Raporu")
        t.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        ust.addWidget(t)
        ust.addStretch()

        self.cb_rapor = QComboBox()
        self.cb_rapor.setFixedWidth(220)
        self.cb_rapor.setFixedHeight(44)
        self.cb_rapor.setStyleSheet(self._combobox_stili())
        ust.addWidget(self.cb_rapor)

        btn_rapor = QPushButton("RAPORU OLUŞTUR")
        btn_rapor.setFixedHeight(44)
        btn_rapor.setFont(QFont("Arial", 10, QFont.Bold))
        btn_rapor.setCursor(Qt.PointingHandCursor)
        btn_rapor.setStyleSheet(self._ikincil_buton_stili(BASARI))
        btn_rapor.clicked.connect(self._rapor_olustur)
        ust.addWidget(btn_rapor)
        lay.addLayout(ust)

        self.rapor_scroll = QScrollArea()
        self.rapor_scroll.setWidgetResizable(True)
        self.rapor_scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {IC_BG}; }} "
            f"QScrollBar:vertical {{ background: {IC_CARD2}; width: 8px; border-radius: 4px; }} "
            f"QScrollBar::handle:vertical {{ background: #CBD5E1; border-radius: 4px; min-height: 20px; }} "
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}"
        )
        self.rapor_icerik = QWidget()
        self.rapor_icerik.setStyleSheet(f"background-color: {IC_BG};")
        self.rapor_icerik_lay = QVBoxLayout(self.rapor_icerik)
        self.rapor_icerik_lay.setSpacing(16)
        self.rapor_icerik_lay.setContentsMargins(0, 0, 0, 0)
        self.rapor_icerik_lay.addStretch()
        self.rapor_scroll.setWidget(self.rapor_icerik)
        lay.addWidget(self.rapor_scroll)

        return w

    # ── Sayfa: Admin Paneli ──────────────────────────────────────────────────

    def _ui_admin(self) -> QWidget:
        """
        Admin paneli sayfasını oluşturur.
        İşlevler: etkinlik silme, katılımcı silme, sistem özeti, log.
        """
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(24)

        # Başlık
        ust = QHBoxLayout()
        t = QLabel("🔐  Admin Paneli")
        t.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        ust.addWidget(t)
        ust.addStretch()
        rozet = QLabel("YETKİLİ ERİŞİM")
        rozet.setStyleSheet(
            f"background-color: #FEF2F2; color: {HATA}; font-size: 11px; font-weight: 800; "
            f"padding: 4px 12px; border-radius: 8px; border: 1px solid #FECACA;"
        )
        ust.addWidget(rozet)
        lay.addLayout(ust)

        # İki sütunlu düzen
        iki_sutun = QHBoxLayout()
        iki_sutun.setSpacing(20)

        # — Sol: İşlemler —
        sol = QVBoxLayout()
        sol.setSpacing(16)

        # Etkinlik Silme Kartı
        etk_kart = QFrame()
        etk_kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        etk_kart_lay = QVBoxLayout(etk_kart)
        etk_kart_lay.setContentsMargins(20, 16, 20, 16)
        etk_kart_lay.setSpacing(12)

        etk_kart_baslik = QLabel("Etkinlik Sil")
        etk_kart_baslik.setStyleSheet(
            f"color: {IC_TXT}; font-size: 14px; font-weight: 800;"
        )
        etk_kart_lay.addWidget(etk_kart_baslik)

        self.admin_cb_etk = QComboBox()
        self.admin_cb_etk.setFixedHeight(42)
        self.admin_cb_etk.setStyleSheet(self._combobox_stili())
        etk_kart_lay.addWidget(self.admin_cb_etk)

        btn_etk_sil = QPushButton("ETKİNLİĞİ SİL")
        btn_etk_sil.setFixedHeight(42)
        btn_etk_sil.setCursor(Qt.PointingHandCursor)
        btn_etk_sil.setFont(QFont("Arial", 10, QFont.Bold))
        btn_etk_sil.setStyleSheet(self._ikincil_buton_stili(HATA))
        btn_etk_sil.clicked.connect(self._admin_etkinlik_sil)
        etk_kart_lay.addWidget(btn_etk_sil)
        sol.addWidget(etk_kart)

        # Katılımcı Silme Kartı
        kat_kart = QFrame()
        kat_kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        kat_kart_lay = QVBoxLayout(kat_kart)
        kat_kart_lay.setContentsMargins(20, 16, 20, 16)
        kat_kart_lay.setSpacing(12)

        kat_kart_baslik = QLabel("Katılımcı Kaydını Sil")
        kat_kart_baslik.setStyleSheet(
            f"color: {IC_TXT}; font-size: 14px; font-weight: 800;"
        )
        kat_kart_lay.addWidget(kat_kart_baslik)

        self.admin_cb_kat_etk = QComboBox()
        self.admin_cb_kat_etk.setFixedHeight(42)
        self.admin_cb_kat_etk.setStyleSheet(self._combobox_stili())
        self.admin_cb_kat_etk.currentIndexChanged.connect(self._admin_kat_etk_degisti)
        kat_kart_lay.addWidget(self.admin_cb_kat_etk)

        self.admin_cb_kat = QComboBox()
        self.admin_cb_kat.setFixedHeight(42)
        self.admin_cb_kat.setStyleSheet(self._combobox_stili())
        kat_kart_lay.addWidget(self.admin_cb_kat)

        btn_kat_sil = QPushButton("KAYDOLMAYI İPTAL ET")
        btn_kat_sil.setFixedHeight(42)
        btn_kat_sil.setCursor(Qt.PointingHandCursor)
        btn_kat_sil.setFont(QFont("Arial", 10, QFont.Bold))
        btn_kat_sil.setStyleSheet(self._ikincil_buton_stili(UYARI))
        btn_kat_sil.clicked.connect(self._admin_katilimci_sil)
        kat_kart_lay.addWidget(btn_kat_sil)
        sol.addWidget(kat_kart)
        sol.addStretch()

        # — Sağ: Log & Sistem —
        sag = QVBoxLayout()
        sag.setSpacing(16)

        sistem_kart = QFrame()
        sistem_kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        sistem_lay = QVBoxLayout(sistem_kart)
        sistem_lay.setContentsMargins(20, 16, 20, 16)
        sistem_lay.setSpacing(10)

        s_baslik = QLabel("Sistem Özeti")
        s_baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 14px; font-weight: 800;")
        sistem_lay.addWidget(s_baslik)

        self.admin_sistem_lbl = QLabel()
        self.admin_sistem_lbl.setStyleSheet(
            f"color: {IC_TXT2}; font-size: 13px; line-height: 1.6;"
        )
        self.admin_sistem_lbl.setWordWrap(True)
        sistem_lay.addWidget(self.admin_sistem_lbl)
        sag.addWidget(sistem_kart)

        log_kart = QFrame()
        log_kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        log_lay = QVBoxLayout(log_kart)
        log_lay.setContentsMargins(20, 16, 20, 16)
        log_lay.setSpacing(10)

        log_baslik_lay = QHBoxLayout()
        log_baslik = QLabel("İşlem Geçmişi")
        log_baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 14px; font-weight: 800;")
        log_baslik_lay.addWidget(log_baslik)
        log_baslik_lay.addStretch()
        btn_log_temizle = QPushButton("Temizle")
        btn_log_temizle.setFixedHeight(28)
        btn_log_temizle.setCursor(Qt.PointingHandCursor)
        btn_log_temizle.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {HATA}; font-size: 11px; "
            f"border: 1px solid {HATA}; border-radius: 6px; padding: 0 8px; }} "
            f"QPushButton:hover {{ background: #FEF2F2; }}"
        )
        btn_log_temizle.clicked.connect(lambda: self.admin_log.clear())
        log_baslik_lay.addWidget(btn_log_temizle)
        log_lay.addLayout(log_baslik_lay)

        self.admin_log = QTextEdit()
        self.admin_log.setReadOnly(True)
        self.admin_log.setFixedHeight(180)
        self.admin_log.setStyleSheet(
            f"QTextEdit {{ background: {IC_CARD2}; color: {IC_TXT}; border: 1px solid {IC_BORDER}; "
            f"border-radius: 8px; font-family: 'Consolas'; font-size: 12px; padding: 8px; }}"
        )
        log_lay.addWidget(self.admin_log)
        sag.addWidget(log_kart)
        sag.addStretch()

        iki_sutun.addLayout(sol, 1)
        iki_sutun.addLayout(sag, 1)
        lay.addLayout(iki_sutun)

        return w

    # ── Navigasyon ───────────────────────────────────────────────────────────

    def _goto(self, isim: str):
        """
        Verilen sayfa adına göre stack'i günceller.
        Admin paneli için şifre doğrulaması yapar.
        """
        idx_map = {
            "Dashboard":       0,
            "Etkinlik Ekle":   1,
            "Kayıt Yönetimi":  2,
            "Biletler":        3,
            "Rapor":           4,
            "Admin Paneli":    5,
        }
        # Admin girişi doğrulama
        if isim == "Admin Paneli":
            dlg = AdminGirisDialog(self)
            dlg.exec_()
            if not dlg.giris_basarili:
                # Butonu seçili durumdan çıkar
                for i, b in enumerate(self.nav):
                    b.setChecked(i == self.stack.currentIndex())
                return

        idx = idx_map[isim]
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self.nav):
            b.setChecked(i == idx)

        # Sayfa yenileme
        if idx == 0:
            self._refresh_dashboard()
        elif idx == 2:
            self._refresh_kayit_sayfasi()
        elif idx == 3:
            self._refresh_biletler()
        elif idx == 4:
            self._refresh_rapor_cb()
        elif idx == 5:
            self._refresh_admin()

    # ── Yenileme Metodları ───────────────────────────────────────────────────

    def _refresh_dashboard(self):
        """Dashboard KPI kartlarını ve tablosunu günceller."""
        # KPI'ları temizle
        while self.kpi_lay.count():
            item = self.kpi_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        t_k = sum(e.get_katilimci_sayisi() for e in self.etkinlikler.values())
        self.kpi_lay.addWidget(KpiCard("Toplam Etkinlik", len(self.etkinlikler), VURGU))
        self.kpi_lay.addWidget(KpiCard("Toplam Kayıt",    t_k,                   BASARI))
        self.kpi_lay.addWidget(KpiCard("Toplam Bilet",    len(self.biletler),    MOR))
        self.kpi_lay.addWidget(KpiCard("Sistem Durumu",   "AKTİF",              UYARI))

        # Tabloyu güncelle
        self.tablo.setRowCount(0)
        for e in sorted(self.etkinlikler.values(), key=lambda x: x.get_id()):
            r = self.tablo.rowCount()
            self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(e.get_id())))
            self.tablo.setItem(r, 1, QTableWidgetItem(e.get_ad()))
            self.tablo.setItem(r, 2, QTableWidgetItem(str(e.get_tarih())))
            self.tablo.setItem(
                r, 3,
                QTableWidgetItem(f"{e.get_katilimci_sayisi()}/{e.get_kapasite()}")
            )
            dolu = e.get_katilimci_sayisi() >= e.get_kapasite()
            it = QTableWidgetItem("DOLU" if dolu else "MÜSAİT")
            it.setForeground(QColor(HATA if dolu else BASARI))
            self.tablo.setItem(r, 4, it)

    def _refresh_kayit_sayfasi(self):
        """Kayıt Yönetimi sayfasındaki etkinlik butonları ve tabloyu günceller."""
        # Etkinlik butonlarını temizle ve yeniden oluştur
        for i in reversed(range(self.etk_buton_lay.count())):
            item = self.etk_buton_lay.takeAt(i)
            if item.widget():
                item.widget().deleteLater()
        self.etk_buton_lay.addStretch()
        self._etk_butonlari.clear()

        for e in sorted(self.etkinlikler.values(), key=lambda x: x.get_id()):
            eid = e.get_id()
            btn = QPushButton(e.get_ad())
            btn.setFixedHeight(38)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            self._etk_butonlari[eid] = btn
            btn.clicked.connect(lambda _, i=eid: self._etkinlik_sec(i))
            self._etk_stili_guncelle(btn, False)
            self.etk_buton_lay.insertWidget(self.etk_buton_lay.count() - 1, btn)

        # İlk etkinliği seç
        if self.etkinlikler:
            if self._secili_etkinlik_id not in self.etkinlikler:
                self._secili_etkinlik_id = sorted(self.etkinlikler.keys())[0]
            if self._secili_etkinlik_id in self._etk_butonlari:
                self._etk_stili_guncelle(
                    self._etk_butonlari[self._secili_etkinlik_id], True
                )

        # Kayıt tablosunu doldur
        self.k_tablo.setRowCount(0)
        for bilet in self.biletler:
            etk = self.etkinlikler.get(bilet["etkinlik_id"])
            kat = bilet["katilimci"]
            bil = bilet["bilet"]
            r   = self.k_tablo.rowCount()
            self.k_tablo.insertRow(r)
            self.k_tablo.setItem(r, 0, QTableWidgetItem(str(kat.get_id())))
            self.k_tablo.setItem(r, 1, QTableWidgetItem(kat.get_ad()))
            self.k_tablo.setItem(r, 2, QTableWidgetItem(kat.get_email()))
            self.k_tablo.setItem(r, 3, QTableWidgetItem(etk.get_ad() if etk else "-"))
            it = QTableWidgetItem(bil.get_bilet_id())
            it.setForeground(QColor(MOR))
            self.k_tablo.setItem(r, 4, it)

    def _refresh_biletler(self):
        """Biletler tablosunu günceller."""
        self.b_tablo.setRowCount(0)
        for bilet in self.biletler:
            etk = self.etkinlikler.get(bilet["etkinlik_id"])
            kat = bilet["katilimci"]
            bil = bilet["bilet"]
            r   = self.b_tablo.rowCount()
            self.b_tablo.insertRow(r)
            it = QTableWidgetItem(bil.get_bilet_id())
            it.setForeground(QColor(MOR))
            self.b_tablo.setItem(r, 0, it)
            self.b_tablo.setItem(r, 1, QTableWidgetItem(kat.get_ad()))
            self.b_tablo.setItem(r, 2, QTableWidgetItem(kat.get_email()))
            self.b_tablo.setItem(r, 3, QTableWidgetItem(etk.get_ad() if etk else "-"))

    def _refresh_rapor_cb(self):
        """Rapor sayfasındaki etkinlik açılır listesini günceller."""
        self.cb_rapor.clear()
        for e in sorted(self.etkinlikler.values(), key=lambda x: x.get_id()):
            self.cb_rapor.addItem(e.get_ad(), e.get_id())

    def _refresh_admin(self):
        """Admin panelindeki açılır listeleri ve sistem özetini günceller."""
        # Etkinlik silme combo
        self.admin_cb_etk.clear()
        for e in sorted(self.etkinlikler.values(), key=lambda x: x.get_id()):
            self.admin_cb_etk.addItem(f"[{e.get_id()}] {e.get_ad()}", e.get_id())

        # Katılımcı silme — etkinlik seçimi
        self.admin_cb_kat_etk.clear()
        for e in sorted(self.etkinlikler.values(), key=lambda x: x.get_id()):
            self.admin_cb_kat_etk.addItem(f"[{e.get_id()}] {e.get_ad()}", e.get_id())
        self._admin_kat_etk_degisti()

        # Sistem özeti
        t_k = sum(e.get_katilimci_sayisi() for e in self.etkinlikler.values())
        self.admin_sistem_lbl.setText(
            f"Etkinlik sayısı   : {len(self.etkinlikler)}\n"
            f"Toplam kayıt      : {t_k}\n"
            f"Toplam bilet      : {len(self.biletler)}\n"
            f"Güncelleme zamanı : {datetime.now().strftime('%H:%M:%S')}"
        )

    def _admin_kat_etk_degisti(self):
        """Katılımcı silme combo'sunda etkinlik değişince katılımcı listesini günceller."""
        self.admin_cb_kat.clear()
        eid = self.admin_cb_kat_etk.currentData()
        if eid and eid in self.etkinlikler:
            for k in self.etkinlikler[eid].get_katilimcilar():
                self.admin_cb_kat.addItem(
                    f"[{k.get_id()}] {k.get_ad()}", k.get_id()
                )

    # ── Etkinlik Seçim Butonları ─────────────────────────────────────────────

    def _etk_stili_guncelle(self, btn: QPushButton, secili: bool):
        """Etkinlik seçim butonunun stilini günceller."""
        if secili:
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {VURGU}; color: white; "
                f"border-radius: 8px; border: none; padding: 0 16px; font-weight: 900; }}"
            )
        else:
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {IC_CARD2}; color: {IC_TXT2}; "
                f"border-radius: 8px; border: 1px solid {IC_BORDER}; padding: 0 16px; }} "
                f"QPushButton:hover {{ border-color: {VURGU}; color: {VURGU}; }}"
            )

    def _etkinlik_sec(self, eid: int):
        """Seçilen etkinliği işaretler ve buton stillerini günceller."""
        self._secili_etkinlik_id = eid
        for i, btn in self._etk_butonlari.items():
            self._etk_stili_guncelle(btn, i == eid)

    # ── Eylem Metodları ──────────────────────────────────────────────────────

    def _manuel_kayit_ekle(self):
        """
        Kayıt Yönetimi sayfasındaki formdan katılımcı ekler.
        E-posta doğrulaması ve kapasite kontrolü yapar.
        """
        eid  = self._secili_etkinlik_id
        ad   = self.in_kat_ad.text().strip()
        mail = self.in_kat_mail.text().strip().lower()

        if not eid:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir etkinlik seçin.")
            return
        if not ad or not mail:
            QMessageBox.warning(self, "Eksik Bilgi", "Ad ve e-posta alanları boş bırakılamaz.")
            return
        if "@" not in mail or "." not in mail.split("@")[-1]:
            QMessageBox.critical(self, "E-Posta Hatası", "Geçerli bir e-posta adresi girin.")
            return

        self.toplam_katilimci_sayisi += 1
        etk = self.etkinlikler[eid]
        kat = Katilimci(self.toplam_katilimci_sayisi, ad, mail)
        ok, mesaj = etk.katilimci_ekle(kat)

        if ok:
            bil = Bilet(etk, kat)
            self.biletler.append({"etkinlik_id": eid, "katilimci": kat, "bilet": bil})
            self.in_kat_ad.clear()
            self.in_kat_mail.clear()
            self._refresh_kayit_sayfasi()
            QMessageBox.information(
                self, "Kayıt Başarılı",
                f"Kayıt tamamlandı!\nBilet No: {bil.get_bilet_id()}"
            )
        else:
            self.toplam_katilimci_sayisi -= 1
            QMessageBox.warning(self, "Kayıt Hatası", mesaj)

    def _etkinlik_kaydet(self):
        """
        Etkinlik Ekle formundaki verileri doğrular ve yeni etkinlik oluşturur.
        """
        ad = self.in_ad.text().strip()
        if not ad:
            QMessageBox.warning(self, "Eksik Bilgi", "Etkinlik adı boş bırakılamaz.")
            return
        yid   = max(self.etkinlikler.keys(), default=0) + 1
        tarih = self.in_tarih.date()
        py_tarih = date(tarih.year(), tarih.month(), tarih.day())
        self.etkinlikler[yid] = Etkinlik(yid, ad, py_tarih, self.in_kap.value())
        self.in_ad.clear()
        QMessageBox.information(self, "Başarılı", f"'{ad}' etkinliği oluşturuldu.")
        self._goto("Dashboard")

    def _bilet_detay_goster(self):
        """Biletler tablosundan seçili biletin detay diyaloğunu açar."""
        secili = self.b_tablo.currentRow()
        if secili < 0:
            QMessageBox.information(self, "Bilgi", "Lütfen listeden bir bilet seçin.")
            return
        dlg = BiletDetayDialog(self, self.biletler[secili])
        dlg.exec_()

    def _rapor_olustur(self):
        """Seçili etkinlik için rapor kartını oluşturur ve ekrana getirir."""
        eid = self.cb_rapor.currentData()
        if eid is None:
            return
        while self.rapor_icerik_lay.count():
            item = self.rapor_icerik_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        kart = RaporKarti(self.etkinlikler[eid])
        self.rapor_icerik_lay.addWidget(kart)
        self.rapor_icerik_lay.addStretch()

    # — Admin Eylemler —

    def _admin_etkinlik_sil(self):
        """
        Seçili etkinliği ve ona bağlı tüm biletleri siler.
        Onay kutusu gösterir.
        """
        eid = self.admin_cb_etk.currentData()
        if eid is None:
            QMessageBox.warning(self, "Uyarı", "Silinecek etkinlik seçin.")
            return
        etk_adi = self.etkinlikler[eid].get_ad()
        cevap = QMessageBox.question(
            self, "Etkinlik Sil",
            f"'{etk_adi}' etkinliği ve ilgili TÜM biletler silinecek.\nEmin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if cevap == QMessageBox.Yes:
            del self.etkinlikler[eid]
            self.biletler = [b for b in self.biletler if b["etkinlik_id"] != eid]
            self._admin_log_ekle(f"ETKİNLİK SİLİNDİ → [{eid}] {etk_adi}")
            self._refresh_admin()
            QMessageBox.information(self, "Silindi", f"'{etk_adi}' etkinliği silindi.")

    def _admin_katilimci_sil(self):
        """
        Seçili katılımcının kaydını ilgili etkinlikten siler.
        Buna bağlı bileti de kaldırır.
        """
        eid = self.admin_cb_kat_etk.currentData()
        kid = self.admin_cb_kat.currentData()
        if eid is None or kid is None:
            QMessageBox.warning(self, "Uyarı", "Etkinlik ve katılımcı seçin.")
            return
        etk = self.etkinlikler.get(eid)
        if not etk:
            return
        ok, mesaj = etk.katilimci_cikar(kid)
        if ok:
            self.biletler = [
                b for b in self.biletler
                if not (b["etkinlik_id"] == eid and b["katilimci"].get_id() == kid)
            ]
            self._admin_log_ekle(f"KATILIMCI SİLİNDİ → {mesaj} (Etkinlik: {etk.get_ad()})")
            self._refresh_admin()
            QMessageBox.information(self, "Silindi", mesaj)
        else:
            QMessageBox.warning(self, "Hata", mesaj)

    def _admin_log_ekle(self, mesaj: str):
        """Admin log paneline zaman damgalı satır ekler."""
        zaman = datetime.now().strftime("%H:%M:%S")
        self.admin_log.append(f"[{zaman}]  {mesaj}")

    # ── Saat ─────────────────────────────────────────────────────────────────

    def _saat_baslat(self):
        """Sidebar'daki saati her saniye güncelleyen timer'ı başlatır."""
        t = QTimer(self)
        t.timeout.connect(
            lambda: self.lbl_saat.setText(
                datetime.now().strftime("%H:%M:%S\n%d.%m.%Y")
            )
        )
        t.start(1000)

    # ── Stil Metodları ───────────────────────────────────────────────────────

    def _nav_btn_stili(self) -> str:
        return (
            f"QPushButton {{ background: transparent; color: {SB_TXT}; "
            f"text-align: left; padding-left: 24px; border: none; font-size: 13px; }} "
            f"QPushButton:checked {{ background-color: {SB_AKT}; color: {SB_AKT_TXT}; "
            f"font-weight: bold; border-left: 3px solid {SB_AKT_TXT}; }} "
            f"QPushButton:hover:!checked {{ background-color: #1E293B; color: #CBD5E1; }}"
        )

    def _tablo_stili(self) -> str:
        return (
            f"QTableWidget {{ background-color: {IC_CARD}; color: {IC_TXT}; "
            f"border: 1px solid {IC_BORDER}; border-radius: 10px; gridline-color: {IC_BORDER}; "
            f"alternate-background-color: {IC_CARD2}; }} "
            f"QHeaderView::section {{ background-color: {IC_CARD2}; color: {VURGU}; "
            f"padding: 10px; font-weight: bold; border: none; "
            f"border-bottom: 1px solid {IC_BORDER}; }} "
            f"QTableWidget::item {{ padding: 8px 10px; }} "
            f"QTableWidget::item:selected {{ background-color: #FDE68A; color: {IC_TXT}; }}"
        )

    def _input_stili(self) -> str:
        return (
            f"QLineEdit, QSpinBox, QDateEdit {{ "
            f"background: {IC_CARD}; color: {IC_TXT}; "
            f"padding: 10px 14px; border-radius: 8px; border: 1px solid {IC_BORDER}; "
            f"font-size: 13px; }} "
            f"QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {{ "
            f"border: 1.5px solid {VURGU}; }}"
        )

    def _birincil_buton_stili(self) -> str:
        return (
            f"QPushButton {{ background-color: {VURGU}; color: white; "
            f"border-radius: 10px; border: none; font-weight: 900; }} "
            f"QPushButton:hover {{ background-color: #FBBF24; }} "
            f"QPushButton:pressed {{ background-color: #D97706; }}"
        )

    def _ikincil_buton_stili(self, renk: str) -> str:
        return (
            f"QPushButton {{ background-color: {IC_CARD}; color: {renk}; "
            f"font-weight: 900; border-radius: 8px; border: 1.5px solid {renk}; "
            f"padding: 0 15px; }} "
            f"QPushButton:hover {{ background-color: {renk}; color: white; }}"
        )

    def _combobox_stili(self) -> str:
        return (
            f"QComboBox {{ background-color: {IC_CARD}; color: {IC_TXT}; "
            f"border: 1px solid {IC_BORDER}; border-radius: 8px; "
            f"padding-left: 10px; font-size: 13px; font-weight: 600; }} "
            f"QComboBox:focus {{ border: 1.5px solid {VURGU}; }} "
            f"QComboBox::drop-down {{ border: none; width: 28px; }} "
            f"QAbstractItemView {{ background-color: {IC_CARD}; color: {IC_TXT}; "
            f"selection-background-color: #FDE68A; selection-color: {IC_TXT}; "
            f"outline: none; border: 1px solid {IC_BORDER}; padding: 4px; }}"
        )


# ── Giriş Noktası ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = EtkinlikApp()
    win.show()
    sys.exit(app.exec_())
