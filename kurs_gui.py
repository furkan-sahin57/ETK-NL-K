# -*- coding: utf-8 -*-
"""
Online Kurs Platformu - Grafik Arayüz (PyQt5)
===============================================
Sayfalar  : Dashboard | Kurs Ekle | Kayıt Yönetimi | Öğrenciler | Rapor | Admin Paneli
Tema      : Beyaz içerik alanı + koyu (#0F172A) kenar çubuğu
Gereksinim: PyQt5  →  pip install PyQt5
Çalıştırma: python kurs_gui.py
"""

import sys
from datetime import date, datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QVBoxLayout, QHBoxLayout, QFormLayout, QStackedWidget,
    QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QDialog, QMessageBox, QSizePolicy,
    QTextEdit, QDateEdit,
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont

# ── Backend ──────────────────────────────────────────────────────────────────
try:
    from kurs_sistemi import Egitmen, Ogrenci, Kurs
except ImportError:
    import uuid as _uuid

    class Egitmen:
        def __init__(self, i, a, u, m): self._i, self._a, self._u, self._m = i, a, u, m
        def get_id(self): return self._i
        def get_ad(self): return self._a
        def get_uzmanlik(self): return self._u
        def get_email(self): return self._m

    class Ogrenci:
        def __init__(self, i, a, m):
            self._i, self._a, self._m = i, a, m
            self._kurslar = []
        def get_id(self): return self._i
        def get_ad(self): return self._a
        def get_email(self): return self._m
        def get_kurslar(self): return list(self._kurslar)
        def kurs_ekle(self, kid):
            if kid not in self._kurslar: self._kurslar.append(kid)
        def kurs_cikar(self, kid):
            if kid in self._kurslar: self._kurslar.remove(kid)

    class Kurs:
        def __init__(self, i, a, e, k, t):
            self._i, self._a, self._e, self._k, self._t = i, a, e, k, t
            self._os = []
        def get_id(self): return self._i
        def get_ad(self): return self._a
        def get_egitmen(self): return self._e
        def get_kontenjan(self): return self._k
        def get_tarih(self): return self._t
        def get_ogrenciler(self): return list(self._os)
        def get_ogrenci_sayisi(self): return len(self._os)
        def ogrenci_kaydet(self, o):
            for x in self._os:
                if x.get_id() == o.get_id(): return False, "Zaten kayıtlı!"
            if len(self._os) < self._k:
                self._os.append(o); o.kurs_ekle(self._i); return True, "Kayıt başarılı."
            return False, "Kontenjan dolu!"
        def ogrenci_cikar(self, oid):
            for o in self._os:
                if o.get_id() == oid:
                    self._os.remove(o); o.kurs_cikar(self._i)
                    return True, f"'{o.get_ad()}' silindi."
            return False, "Öğrenci bulunamadı."

# ── Renk Paleti ──────────────────────────────────────────────────────────────
SB        = "#0F172A"
SB_AKT    = "#1E293B"
SB_TXT    = "#94A3B8"
SB_AKT_TXT = "#6366F1"   # indigo
SB_BORDER = "#1E293B"

IC_BG     = "#F8FAFF"
IC_CARD   = "#FFFFFF"
IC_CARD2  = "#EEF2FF"
IC_BORDER = "#C7D2FE"
IC_TXT    = "#1E1B4B"
IC_TXT2   = "#6B7280"

VURGU   = "#6366F1"   # indigo
BASARI  = "#10B981"   # yeşil
UYARI   = "#F59E0B"   # amber
HATA    = "#EF4444"   # kırmızı
MOR     = "#8B5CF6"   # mor

ADMIN_SIFRE = "123"


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
    """Rapor sayfasında kurs istatistiklerini gösteren kart."""

    def __init__(self, kurs: "Kurs"):
        super().__init__()
        self.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        ana = QVBoxLayout(self)
        ana.setContentsMargins(24, 20, 24, 20)
        ana.setSpacing(14)

        # Başlık
        blay = QHBoxLayout()
        ad_lbl = QLabel(f"🎓  {kurs.get_ad()}")
        ad_lbl.setStyleSheet(f"color: {IC_TXT}; font-size: 16px; font-weight: 900;")
        blay.addWidget(ad_lbl)
        blay.addStretch()
        e_lbl = QLabel(f"👨‍🏫 {kurs.get_egitmen().get_ad()}")
        e_lbl.setStyleSheet(f"color: {IC_TXT2}; font-size: 12px; font-weight: 600;")
        blay.addWidget(e_lbl)
        ana.addLayout(blay)

        kontenjan = kurs.get_kontenjan()
        kayitli   = kurs.get_ogrenci_sayisi()
        bos       = kontenjan - kayitli
        pct       = int(kayitli / kontenjan * 100) if kontenjan else 0

        stat_lay = QHBoxLayout()
        stat_lay.setSpacing(12)
        for etiket, deger, renk in [
            ("Kontenjan", str(kontenjan), VURGU),
            ("Kayıtlı",   str(kayitli),  BASARI),
            ("Boş",       str(bos),      UYARI),
            ("Doluluk",   f"%{pct}",     MOR),
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

        # Progress bar
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

        # Öğrenci tablosu
        ogrenciler = kurs.get_ogrenciler()
        if ogrenciler:
            tb_lbl = QLabel("Öğrenci Listesi")
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
            tablo.setFixedHeight(min(len(ogrenciler), 6) * 36 + 42)
            tablo.setStyleSheet(self._tablo_stili())
            for i, o in enumerate(ogrenciler):
                tablo.insertRow(i)
                tablo.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                tablo.setItem(i, 1, QTableWidgetItem(o.get_ad()))
                tablo.setItem(i, 2, QTableWidgetItem(o.get_email()))
            ana.addWidget(tablo)
        else:
            bos_lbl = QLabel("Henüz kayıtlı öğrenci yok.")
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
            QPushButton {{ background-color: {VURGU}; color: white;
                border-radius: 8px; border: none; font-weight: 900; }}
            QPushButton:hover {{ background-color: #818CF8; }}
        """)
        btn.clicked.connect(self._dogrula)
        lay.addWidget(btn)

    def _input_stili(self):
        return (f"QLineEdit {{ background: {IC_CARD}; color: {IC_TXT}; "
                f"padding: 10px 14px; border-radius: 8px; border: 1px solid {IC_BORDER}; "
                f"font-size: 13px; }} "
                f"QLineEdit:focus {{ border: 1.5px solid {VURGU}; }}")

    def _dogrula(self):
        if self.sifre_input.text() == ADMIN_SIFRE:
            self.giris_basarili = True
            self.accept()
        else:
            QMessageBox.warning(self, "Hatalı Şifre", "Girdiğiniz şifre yanlış.")
            self.sifre_input.clear()
            self.sifre_input.setFocus()


# ── Ana Pencere ───────────────────────────────────────────────────────────────

class KursApp(QMainWindow):
    """
    EduPlatform ana uygulama penceresi.

    Sayfalar:
        0 - Dashboard       : KPI özeti + kurs takvimi
        1 - Kurs Ekle       : Yeni kurs oluşturma formu
        2 - Kayıt Yönetimi  : Öğrenci kayıt + listeleme
        3 - Öğrenciler      : Tüm öğrenciler ve kayıtlı kursları
        4 - Rapor           : Kurs bazlı öğrenci raporu
        5 - Admin Paneli    : Kurs / öğrenci silme, sistem bilgisi
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduPlatform — Kurs Yönetim Paneli")
        self.resize(1300, 880)

        # Demo eğitmenler
        eg1 = Egitmen(1, "Dr. Ayşe Kaya",    "Python & Veri Bilimi", "ayse@edu.com")
        eg2 = Egitmen(2, "Mert Yılmaz",       "Web Geliştirme",       "mert@edu.com")
        eg3 = Egitmen(3, "Prof. Zeynep Demir","Yapay Zeka",           "zeynep@edu.com")

        self.egitmenler: dict[int, Egitmen] = {
            1: eg1, 2: eg2, 3: eg3
        }

        # Demo kurslar
        self.kurslar: dict[int, Kurs] = {
            1: Kurs(1, "Python ile Veri Bilimi",  eg1, 30, date(2026, 6, 1)),
            2: Kurs(2, "Full-Stack Web Geliştirme", eg2, 25, date(2026, 6, 15)),
            3: Kurs(3, "Makine Öğrenmesi 101",    eg3, 20, date(2026, 7, 1)),
        }

        # Demo öğrenciler ve kayıtlar
        _demo_ogrenciler = [
            Ogrenci(1,  "Ahmet Çelik",      "ahmet.celik@gmail.com"),
            Ogrenci(2,  "Fatma Şahin",       "fatma.sahin@hotmail.com"),
            Ogrenci(3,  "Mehmet Arslan",     "mehmet.arslan@yahoo.com"),
            Ogrenci(4,  "Elif Yıldız",       "elif.yildiz@outlook.com"),
            Ogrenci(5,  "Burak Doğan",       "burak.dogan@gmail.com"),
            Ogrenci(6,  "Selin Aydın",       "selin.aydin@edu.com"),
            Ogrenci(7,  "Emre Kara",         "emre.kara@gmail.com"),
            Ogrenci(8,  "Zeynep Polat",      "zeynep.polat@hotmail.com"),
            Ogrenci(9,  "Can Öztürk",        "can.ozturk@gmail.com"),
            Ogrenci(10, "Merve Güneş",       "merve.gunes@yahoo.com"),
            Ogrenci(11, "Serkan Yılmaz",     "serkan.yilmaz@gmail.com"),
            Ogrenci(12, "Ayşe Koç",          "ayse.koc@outlook.com"),
            Ogrenci(13, "Oğuz Acar",         "oguz.acar@gmail.com"),
            Ogrenci(14, "Deniz Çetin",       "deniz.cetin@hotmail.com"),
            Ogrenci(15, "Gizem Erdoğan",     "gizem.erdogan@gmail.com"),
        ]

        # Kurs 1: Python ile Veri Bilimi — 8 öğrenci
        for ogr in _demo_ogrenciler[:8]:
            self.kurslar[1].ogrenci_kaydet(ogr)

        # Kurs 2: Full-Stack Web Geliştirme — 6 öğrenci
        for ogr in _demo_ogrenciler[3:9]:
            self.kurslar[2].ogrenci_kaydet(ogr)

        # Kurs 3: Makine Öğrenmesi 101 — 5 öğrenci
        for ogr in _demo_ogrenciler[10:15]:
            self.kurslar[3].ogrenci_kaydet(ogr)

        self.ogrenciler: dict[int, Ogrenci] = {o.get_id(): o for o in _demo_ogrenciler}
        self.toplam_ogrenci_sayisi: int = len(_demo_ogrenciler)
        self._secili_kurs_id: int | None = None
        self._kurs_butonlari: dict = {}

        self._build_ui()
        self._saat_baslat()

    # ── Arayüz İnşası ────────────────────────────────────────────────────────

    def _build_ui(self):
        merkez = QWidget()
        merkez.setStyleSheet(f"background-color: {IC_BG};")
        self.setCentralWidget(merkez)

        ana_lay = QHBoxLayout(merkez)
        ana_lay.setContentsMargins(0, 0, 0, 0)
        ana_lay.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background-color: {SB}; border-right: 1px solid {SB_BORDER};")
        s_lay = QVBoxLayout(sidebar)
        s_lay.setContentsMargins(0, 0, 0, 0)
        s_lay.setSpacing(0)

        logo_frame = QFrame()
        logo_frame.setFixedHeight(72)
        logo_frame.setStyleSheet(f"background-color: {SB}; border-bottom: 1px solid {SB_BORDER}; border-right: none;")
        l_lay = QHBoxLayout(logo_frame)
        l_lay.setContentsMargins(20, 0, 20, 0)
        logo_lbl = QLabel("🎓  EduPlatform")
        logo_lbl.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: 900; letter-spacing: 1px;")
        l_lay.addWidget(logo_lbl)
        s_lay.addWidget(logo_frame)
        s_lay.addSpacing(12)

        nav_items = [
            ("📊", "Dashboard"),
            ("➕", "Kurs Ekle"),
            ("👥", "Kayıt Yönetimi"),
            ("🎓", "Öğrenciler"),
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

        self.lbl_saat = QLabel()
        self.lbl_saat.setStyleSheet(
            f"color: {SB_TXT}; margin: 16px 20px; font-family: 'Consolas'; font-size: 11px;"
        )
        s_lay.addWidget(self.lbl_saat)
        ana_lay.addWidget(sidebar)

        # Sayfa yığını
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {IC_BG};")
        self.stack.addWidget(self._ui_dashboard())        # 0
        self.stack.addWidget(self._ui_kurs_ekle())        # 1
        self.stack.addWidget(self._ui_kayit_yonetimi())   # 2
        self.stack.addWidget(self._ui_ogrenciler())       # 3
        self.stack.addWidget(self._ui_rapor())            # 4
        self.stack.addWidget(self._ui_admin())            # 5
        ana_lay.addWidget(self.stack)

        self._goto("Dashboard")

    # ── Sayfa: Dashboard ─────────────────────────────────────────────────────

    def _ui_dashboard(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(24)

        ust = QHBoxLayout()
        baslik = QLabel("Dashboard")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        ust.addWidget(baslik)
        ust.addStretch()
        tarih_lbl = QLabel(datetime.now().strftime("%d %B %Y"))
        tarih_lbl.setStyleSheet(f"color: {IC_TXT2}; font-size: 13px;")
        ust.addWidget(tarih_lbl)
        lay.addLayout(ust)

        self.kpi_lay = QHBoxLayout()
        self.kpi_lay.setSpacing(16)
        lay.addLayout(self.kpi_lay)

        ayrac = QFrame()
        ayrac.setFrameShape(QFrame.HLine)
        ayrac.setStyleSheet(f"color: {IC_BORDER};")
        lay.addWidget(ayrac)

        t_lbl = QLabel("Aktif Kurs Takvimi")
        t_lbl.setStyleSheet(f"color: {IC_TXT}; font-size: 16px; font-weight: 800;")
        lay.addWidget(t_lbl)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(
            ["ID", "Kurs Adı", "Eğitmen", "Başlangıç", "Doluluk", "Durum"]
        )
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setStyleSheet(self._tablo_stili())
        self.tablo.setAlternatingRowColors(True)
        lay.addWidget(self.tablo)

        btn = QPushButton("⚡   HIZLI ÖĞRENCİ KAYDI YAP")
        btn.setFixedHeight(52)
        btn.setFont(QFont("Arial", 11, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._birincil_buton_stili())
        btn.clicked.connect(lambda: self._goto("Kayıt Yönetimi"))
        lay.addWidget(btn)

        return w

    # ── Sayfa: Kurs Ekle ─────────────────────────────────────────────────────

    def _ui_kurs_ekle(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(28)

        baslik = QLabel("Yeni Kurs Oluştur")
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

        self.in_kurs_ad = QLineEdit()
        self.in_kurs_ad.setPlaceholderText("Örnek: React ile Modern Web Geliştirme")
        self.in_kurs_ad.setFixedHeight(44)
        self.in_kurs_ad.setStyleSheet(self._input_stili())

        self.in_kurs_egitmen = QComboBox()
        self.in_kurs_egitmen.setFixedHeight(44)
        self.in_kurs_egitmen.setStyleSheet(self._combobox_stili())

        self.in_kurs_tarih = QDateEdit()
        self.in_kurs_tarih.setCalendarPopup(True)
        self.in_kurs_tarih.setDate(QDate.currentDate().addDays(30))
        self.in_kurs_tarih.setFixedHeight(44)
        self.in_kurs_tarih.setStyleSheet(self._input_stili())
        self.in_kurs_tarih.setDisplayFormat("dd.MM.yyyy")

        self.in_kontenjan = QSpinBox()
        self.in_kontenjan.setRange(1, 500)
        self.in_kontenjan.setValue(25)
        self.in_kontenjan.setFixedHeight(44)
        self.in_kontenjan.setStyleSheet(self._input_stili())

        flay.addRow(QLabel("Kurs Adı      :", styleSheet=lbl_stili), self.in_kurs_ad)
        flay.addRow(QLabel("Eğitmen       :", styleSheet=lbl_stili), self.in_kurs_egitmen)
        flay.addRow(QLabel("Başlangıç     :", styleSheet=lbl_stili), self.in_kurs_tarih)
        flay.addRow(QLabel("Kontenjan     :", styleSheet=lbl_stili), self.in_kontenjan)

        lay.addWidget(form)

        btn = QPushButton("💾   SİSTEME KAYDET")
        btn.setFixedHeight(52)
        btn.setFont(QFont("Arial", 11, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._birincil_buton_stili())
        btn.clicked.connect(self._kurs_kaydet)
        lay.addWidget(btn)
        lay.addStretch()

        return w

    # ── Sayfa: Kayıt Yönetimi ────────────────────────────────────────────────

    def _ui_kayit_yonetimi(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        baslik = QLabel("Öğrenci Kayıt Yönetimi")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        lay.addWidget(baslik)

        # Kayıt formu kartı
        form = QFrame()
        form.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        form_lay = QVBoxLayout(form)
        form_lay.setContentsMargins(22, 18, 22, 18)
        form_lay.setSpacing(14)

        etk_lbl = QLabel("KURS SEÇİN")
        etk_lbl.setStyleSheet(
            f"color: {IC_TXT2}; font-size: 11px; font-weight: 800; letter-spacing: 1px;"
        )
        form_lay.addWidget(etk_lbl)

        self.kurs_buton_widget = QWidget()
        self.kurs_buton_widget.setStyleSheet("background: transparent;")
        self.kurs_buton_lay = QHBoxLayout(self.kurs_buton_widget)
        self.kurs_buton_lay.setContentsMargins(0, 0, 0, 0)
        self.kurs_buton_lay.setSpacing(8)
        self.kurs_buton_lay.addStretch()
        form_lay.addWidget(self.kurs_buton_widget)

        alt_lay = QHBoxLayout()
        alt_lay.setSpacing(12)

        self.in_ogr_ad = QLineEdit()
        self.in_ogr_ad.setPlaceholderText("Öğrenci Adı Soyadı")
        self.in_ogr_ad.setFixedHeight(44)
        self.in_ogr_ad.setStyleSheet(self._input_stili())

        self.in_ogr_mail = QLineEdit()
        self.in_ogr_mail.setPlaceholderText("ornek@email.com")
        self.in_ogr_mail.setFixedHeight(44)
        self.in_ogr_mail.setStyleSheet(self._input_stili())

        btn_kaydet = QPushButton("KAYDET")
        btn_kaydet.setFixedHeight(44)
        btn_kaydet.setFixedWidth(120)
        btn_kaydet.setFont(QFont("Arial", 10, QFont.Bold))
        btn_kaydet.setCursor(Qt.PointingHandCursor)
        btn_kaydet.setStyleSheet(self._birincil_buton_stili())
        btn_kaydet.clicked.connect(self._ogrenci_kaydet)

        alt_lay.addWidget(self.in_ogr_ad, 2)
        alt_lay.addWidget(self.in_ogr_mail, 2)
        alt_lay.addWidget(btn_kaydet)
        form_lay.addLayout(alt_lay)
        lay.addWidget(form)

        # Kayıtlı öğrenciler tablosu
        tb_lbl = QLabel("Seçili Kursa Kayıtlı Öğrenciler")
        tb_lbl.setStyleSheet(f"color: {IC_TXT}; font-size: 14px; font-weight: 800;")
        lay.addWidget(tb_lbl)

        self.kayit_tablo = QTableWidget()
        self.kayit_tablo.setColumnCount(4)
        self.kayit_tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad", "E-Posta", "Kurs Sayısı"])
        self.kayit_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.kayit_tablo.verticalHeader().setVisible(False)
        self.kayit_tablo.setStyleSheet(self._tablo_stili())
        self.kayit_tablo.setAlternatingRowColors(True)
        self.kayit_tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        lay.addWidget(self.kayit_tablo)

        return w

    # ── Sayfa: Öğrenciler ────────────────────────────────────────────────────

    def _ui_ogrenciler(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        baslik = QLabel("Tüm Öğrenciler")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        lay.addWidget(baslik)

        self.ogr_tablo = QTableWidget()
        self.ogr_tablo.setColumnCount(4)
        self.ogr_tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad", "E-Posta", "Kayıtlı Kurs"])
        self.ogr_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ogr_tablo.verticalHeader().setVisible(False)
        self.ogr_tablo.setStyleSheet(self._tablo_stili())
        self.ogr_tablo.setAlternatingRowColors(True)
        self.ogr_tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        lay.addWidget(self.ogr_tablo)

        btn = QPushButton("📋   SEÇİLİ ÖĞRENCİNİN KURS LİSTESİ")
        btn.setFixedHeight(48)
        btn.setFont(QFont("Arial", 10, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._ikincil_buton_stili(VURGU))
        btn.clicked.connect(self._ogrenci_kurs_listesi_goster)
        lay.addWidget(btn)

        return w

    # ── Sayfa: Rapor ─────────────────────────────────────────────────────────

    def _ui_rapor(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        ust = QHBoxLayout()
        baslik = QLabel("Kurs Raporu")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        ust.addWidget(baslik)

        self.cb_rapor = QComboBox()
        self.cb_rapor.setFixedHeight(42)
        self.cb_rapor.setFixedWidth(280)
        self.cb_rapor.setStyleSheet(self._combobox_stili())
        ust.addStretch()
        ust.addWidget(self.cb_rapor)

        btn_rapor = QPushButton("📋  RAPOR OLUŞTUR")
        btn_rapor.setFixedHeight(42)
        btn_rapor.setFont(QFont("Arial", 10, QFont.Bold))
        btn_rapor.setCursor(Qt.PointingHandCursor)
        btn_rapor.setStyleSheet(self._birincil_buton_stili())
        btn_rapor.clicked.connect(self._rapor_olustur)
        ust.addWidget(btn_rapor)
        lay.addLayout(ust)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        ic = QWidget()
        ic.setStyleSheet(f"background-color: {IC_BG};")
        self.rapor_icerik_lay = QVBoxLayout(ic)
        self.rapor_icerik_lay.setContentsMargins(0, 0, 0, 0)
        self.rapor_icerik_lay.setSpacing(16)
        scroll.setWidget(ic)
        lay.addWidget(scroll)

        return w

    # ── Sayfa: Admin Paneli ──────────────────────────────────────────────────

    def _ui_admin(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background-color: {IC_BG};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(20)

        baslik = QLabel("Admin Paneli")
        baslik.setStyleSheet(f"color: {IC_TXT}; font-size: 26px; font-weight: 900;")
        lay.addWidget(baslik)

        # Kurs silme kartı
        kurs_kart = QFrame()
        kurs_kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        kk_lay = QVBoxLayout(kurs_kart)
        kk_lay.setContentsMargins(22, 18, 22, 18)
        kk_lay.setSpacing(12)
        kk_lay.addWidget(QLabel("KURS SİL", styleSheet=f"color: {HATA}; font-size: 12px; font-weight: 800; letter-spacing: 1px;"))

        kurs_row = QHBoxLayout()
        self.admin_cb_kurs = QComboBox()
        self.admin_cb_kurs.setFixedHeight(42)
        self.admin_cb_kurs.setStyleSheet(self._combobox_stili())
        btn_kurs_sil = QPushButton("🗑  KURSU SİL")
        btn_kurs_sil.setFixedHeight(42)
        btn_kurs_sil.setFont(QFont("Arial", 10, QFont.Bold))
        btn_kurs_sil.setCursor(Qt.PointingHandCursor)
        btn_kurs_sil.setStyleSheet(self._ikincil_buton_stili(HATA))
        btn_kurs_sil.clicked.connect(self._admin_kurs_sil)
        kurs_row.addWidget(self.admin_cb_kurs, 1)
        kurs_row.addWidget(btn_kurs_sil)
        kk_lay.addLayout(kurs_row)
        lay.addWidget(kurs_kart)

        # Öğrenci silme kartı
        ogr_kart = QFrame()
        ogr_kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        ok_lay = QVBoxLayout(ogr_kart)
        ok_lay.setContentsMargins(22, 18, 22, 18)
        ok_lay.setSpacing(12)
        ok_lay.addWidget(QLabel("ÖĞRENCİ KAYDINI SİL", styleSheet=f"color: {UYARI}; font-size: 12px; font-weight: 800; letter-spacing: 1px;"))

        ogr_row = QHBoxLayout()
        self.admin_cb_ogr_kurs = QComboBox()
        self.admin_cb_ogr_kurs.setFixedHeight(42)
        self.admin_cb_ogr_kurs.setStyleSheet(self._combobox_stili())
        self.admin_cb_ogr_kurs.currentIndexChanged.connect(self._admin_ogr_kurs_degisti)

        self.admin_cb_ogr = QComboBox()
        self.admin_cb_ogr.setFixedHeight(42)
        self.admin_cb_ogr.setStyleSheet(self._combobox_stili())

        btn_ogr_sil = QPushButton("🗑  KAYDI SİL")
        btn_ogr_sil.setFixedHeight(42)
        btn_ogr_sil.setFont(QFont("Arial", 10, QFont.Bold))
        btn_ogr_sil.setCursor(Qt.PointingHandCursor)
        btn_ogr_sil.setStyleSheet(self._ikincil_buton_stili(UYARI))
        btn_ogr_sil.clicked.connect(self._admin_ogrenci_sil)

        ogr_row.addWidget(self.admin_cb_ogr_kurs, 1)
        ogr_row.addWidget(self.admin_cb_ogr, 1)
        ogr_row.addWidget(btn_ogr_sil)
        ok_lay.addLayout(ogr_row)
        lay.addWidget(ogr_kart)

        # Sistem bilgisi
        sys_kart = QFrame()
        sys_kart.setStyleSheet(
            f"background-color: {IC_CARD}; border-radius: 14px; border: 1px solid {IC_BORDER};"
        )
        sk_lay = QVBoxLayout(sys_kart)
        sk_lay.setContentsMargins(22, 18, 22, 18)
        sk_lay.setSpacing(8)
        sk_lay.addWidget(QLabel("SİSTEM BİLGİSİ", styleSheet=f"color: {IC_TXT2}; font-size: 12px; font-weight: 800; letter-spacing: 1px;"))
        self.admin_sys_lbl = QLabel()
        self.admin_sys_lbl.setStyleSheet(f"color: {IC_TXT}; font-size: 13px;")
        sk_lay.addWidget(self.admin_sys_lbl)
        lay.addWidget(sys_kart)

        # Log
        log_lbl = QLabel("İŞLEM LOGU", styleSheet=f"color: {IC_TXT2}; font-size: 12px; font-weight: 800; letter-spacing: 1px;")
        lay.addWidget(log_lbl)
        self.admin_log = QTextEdit()
        self.admin_log.setReadOnly(True)
        self.admin_log.setFixedHeight(160)
        self.admin_log.setStyleSheet(
            f"background: {IC_CARD}; color: {IC_TXT}; border: 1px solid {IC_BORDER}; "
            f"border-radius: 10px; font-family: 'Consolas'; font-size: 12px; padding: 8px;"
        )
        lay.addWidget(self.admin_log)

        return w

    # ── Sayfa Geçişi & Yenileme ──────────────────────────────────────────────

    def _goto(self, sayfa: str):
        sayfa_index = {
            "Dashboard": 0, "Kurs Ekle": 1, "Kayıt Yönetimi": 2,
            "Öğrenciler": 3, "Rapor": 4, "Admin Paneli": 5,
        }

        if sayfa == "Admin Paneli":
            dlg = AdminGirisDialog(self)
            dlg.exec_()
            if not dlg.giris_basarili:
                return

        idx = sayfa_index.get(sayfa, 0)
        self.stack.setCurrentIndex(idx)

        for i, btn in enumerate(self.nav):
            btn.setChecked(i == idx)

        refreshers = {
            0: self._refresh_dashboard,
            1: self._refresh_kurs_ekle,
            2: self._refresh_kayit_sayfasi,
            3: self._refresh_ogrenciler,
            4: self._refresh_rapor,
            5: self._refresh_admin,
        }
        refreshers[idx]()

    def _refresh_dashboard(self):
        # KPI kartlarını temizle ve yeniden çiz
        while self.kpi_lay.count():
            item = self.kpi_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        toplam_ogr = sum(k.get_ogrenci_sayisi() for k in self.kurslar.values())
        dolu_kurs  = sum(1 for k in self.kurslar.values() if k.get_ogrenci_sayisi() >= k.get_kontenjan())

        for baslik, deger, renk in [
            ("Toplam Kurs",       str(len(self.kurslar)),      VURGU),
            ("Kayıtlı Öğrenci",  str(toplam_ogr),             BASARI),
            ("Toplam Öğrenci",   str(len(self.ogrenciler)),    MOR),
            ("Dolu Kurs",        str(dolu_kurs),               UYARI),
        ]:
            self.kpi_lay.addWidget(KpiCard(baslik, deger, renk))

        # Tablo
        self.tablo.setRowCount(0)
        for k in self.kurslar.values():
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)
            pct  = int(k.get_ogrenci_sayisi() / k.get_kontenjan() * 100) if k.get_kontenjan() else 0
            durum = "🟢 Açık" if pct < 100 else "🔴 Dolu"
            for col, val in enumerate([
                str(k.get_id()), k.get_ad(), k.get_egitmen().get_ad(),
                str(k.get_tarih()), f"%{pct}", durum
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.tablo.setItem(row, col, item)

    def _refresh_kurs_ekle(self):
        self.in_kurs_egitmen.clear()
        for e in self.egitmenler.values():
            self.in_kurs_egitmen.addItem(
                f"{e.get_ad()} — {e.get_uzmanlik()}", e.get_id()
            )

    def _refresh_kayit_sayfasi(self):
        # Kurs seçim butonlarını yenile
        for btn in list(self._kurs_butonlari.values()):
            btn.deleteLater()
        self._kurs_butonlari.clear()

        while self.kurs_buton_lay.count() > 1:
            item = self.kurs_buton_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for k in self.kurslar.values():
            btn = QPushButton(k.get_ad())
            btn.setCheckable(True)
            btn.setFixedHeight(38)
            btn.setCursor(Qt.PointingHandCursor)
            is_secili = k.get_id() == self._secili_kurs_id
            btn.setChecked(is_secili)
            btn.setStyleSheet(self._kurs_btn_stili(is_secili))
            btn.clicked.connect(lambda _, kid=k.get_id(): self._kurs_sec(kid))
            self.kurs_buton_lay.insertWidget(self.kurs_buton_lay.count() - 1, btn)
            self._kurs_butonlari[k.get_id()] = btn

        # Tablo
        self.kayit_tablo.setRowCount(0)
        if self._secili_kurs_id and self._secili_kurs_id in self.kurslar:
            kurs = self.kurslar[self._secili_kurs_id]
            for o in kurs.get_ogrenciler():
                row = self.kayit_tablo.rowCount()
                self.kayit_tablo.insertRow(row)
                for col, val in enumerate([
                    str(o.get_id()), o.get_ad(), o.get_email(), str(len(o.get_kurslar()))
                ]):
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.kayit_tablo.setItem(row, col, item)

    def _refresh_ogrenciler(self):
        self.ogr_tablo.setRowCount(0)
        for o in self.ogrenciler.values():
            row = self.ogr_tablo.rowCount()
            self.ogr_tablo.insertRow(row)
            kurs_adlari = ", ".join(
                self.kurslar[kid].get_ad()
                for kid in o.get_kurslar()
                if kid in self.kurslar
            ) or "—"
            for col, val in enumerate([str(o.get_id()), o.get_ad(), o.get_email(), kurs_adlari]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.ogr_tablo.setItem(row, col, item)

    def _refresh_rapor(self):
        self.cb_rapor.clear()
        for k in self.kurslar.values():
            self.cb_rapor.addItem(k.get_ad(), k.get_id())

    def _refresh_admin(self):
        self.admin_cb_kurs.clear()
        self.admin_cb_ogr_kurs.clear()
        for k in self.kurslar.values():
            self.admin_cb_kurs.addItem(k.get_ad(), k.get_id())
            self.admin_cb_ogr_kurs.addItem(k.get_ad(), k.get_id())
        self._admin_ogr_kurs_degisti()
        toplam = sum(k.get_ogrenci_sayisi() for k in self.kurslar.values())
        self.admin_sys_lbl.setText(
            f"Kurs: {len(self.kurslar)}  |  Öğrenci: {len(self.ogrenciler)}  |  "
            f"Toplam Kayıt: {toplam}  |  Eğitmen: {len(self.egitmenler)}"
        )

    def _admin_ogr_kurs_degisti(self):
        self.admin_cb_ogr.clear()
        eid = self.admin_cb_ogr_kurs.currentData()
        if eid and eid in self.kurslar:
            for o in self.kurslar[eid].get_ogrenciler():
                self.admin_cb_ogr.addItem(o.get_ad(), o.get_id())

    # ── Kurs Seçimi ──────────────────────────────────────────────────────────

    def _kurs_sec(self, kurs_id: int):
        self._secili_kurs_id = kurs_id
        for kid, btn in self._kurs_butonlari.items():
            btn.setChecked(kid == kurs_id)
            btn.setStyleSheet(self._kurs_btn_stili(kid == kurs_id))
        self._refresh_kayit_sayfasi()

    # ── İşlem Metodları ──────────────────────────────────────────────────────

    def _ogrenci_kaydet(self):
        if self._secili_kurs_id is None:
            QMessageBox.warning(self, "Kurs Seçin", "Lütfen önce bir kurs seçin.")
            return

        ad   = self.in_ogr_ad.text().strip()
        mail = self.in_ogr_mail.text().strip()

        if not ad or not mail:
            QMessageBox.warning(self, "Eksik Bilgi", "Ad ve e-posta boş bırakılamaz.")
            return
        if "@" not in mail or "." not in mail.split("@")[-1]:
            QMessageBox.critical(self, "E-Posta Hatası", "Geçerli bir e-posta adresi girin.")
            return

        self.toplam_ogrenci_sayisi += 1
        kurs = self.kurslar[self._secili_kurs_id]
        ogr  = Ogrenci(self.toplam_ogrenci_sayisi, ad, mail)
        ok, mesaj = kurs.ogrenci_kaydet(ogr)

        if ok:
            self.ogrenciler[ogr.get_id()] = ogr
            self.in_ogr_ad.clear()
            self.in_ogr_mail.clear()
            self._refresh_kayit_sayfasi()
            QMessageBox.information(
                self, "Kayıt Başarılı",
                f"'{ad}' öğrencisi '{kurs.get_ad()}' kursuna kaydedildi."
            )
        else:
            self.toplam_ogrenci_sayisi -= 1
            QMessageBox.warning(self, "Kayıt Hatası", mesaj)

    def _kurs_kaydet(self):
        ad = self.in_kurs_ad.text().strip()
        if not ad:
            QMessageBox.warning(self, "Eksik Bilgi", "Kurs adı boş bırakılamaz.")
            return
        egitmen_id = self.in_kurs_egitmen.currentData()
        if not egitmen_id:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen bir eğitmen seçin.")
            return
        yid     = max(self.kurslar.keys(), default=0) + 1
        tarih_q = self.in_kurs_tarih.date()
        py_tarih = date(tarih_q.year(), tarih_q.month(), tarih_q.day())
        egitmen  = self.egitmenler[egitmen_id]
        self.kurslar[yid] = Kurs(yid, ad, egitmen, self.in_kontenjan.value(), py_tarih)
        self.in_kurs_ad.clear()
        QMessageBox.information(self, "Başarılı", f"'{ad}' kursu oluşturuldu.")
        self._goto("Dashboard")

    def _ogrenci_kurs_listesi_goster(self):
        secili = self.ogr_tablo.currentRow()
        if secili < 0:
            QMessageBox.information(self, "Bilgi", "Lütfen listeden bir öğrenci seçin.")
            return
        oid = int(self.ogr_tablo.item(secili, 0).text())
        ogr = self.ogrenciler.get(oid)
        if not ogr:
            return
        rapor = ogr.kurs_listesi(self.kurslar)
        QMessageBox.information(self, f"{ogr.get_ad()} — Kurs Listesi", rapor)

    def _rapor_olustur(self):
        eid = self.cb_rapor.currentData()
        if eid is None:
            return
        while self.rapor_icerik_lay.count():
            item = self.rapor_icerik_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        kart = RaporKarti(self.kurslar[eid])
        self.rapor_icerik_lay.addWidget(kart)
        self.rapor_icerik_lay.addStretch()

    def _admin_kurs_sil(self):
        kid = self.admin_cb_kurs.currentData()
        if kid is None:
            QMessageBox.warning(self, "Uyarı", "Silinecek kurs seçin.")
            return
        kurs_adi = self.kurslar[kid].get_ad()
        cevap = QMessageBox.question(
            self, "Kurs Sil",
            f"'{kurs_adi}' kursu ve tüm öğrenci kayıtları silinecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if cevap == QMessageBox.Yes:
            # Öğrencilerin kurs listesinden de çıkar
            for o in self.kurslar[kid].get_ogrenciler():
                o.kurs_cikar(kid)
            del self.kurslar[kid]
            if self._secili_kurs_id == kid:
                self._secili_kurs_id = None
            self._admin_log_ekle(f"KURS SİLİNDİ → [{kid}] {kurs_adi}")
            self._refresh_admin()
            QMessageBox.information(self, "Silindi", f"'{kurs_adi}' kursu silindi.")

    def _admin_ogrenci_sil(self):
        kid = self.admin_cb_ogr_kurs.currentData()
        oid = self.admin_cb_ogr.currentData()
        if kid is None or oid is None:
            QMessageBox.warning(self, "Uyarı", "Kurs ve öğrenci seçin.")
            return
        kurs = self.kurslar.get(kid)
        if not kurs:
            return
        ok, mesaj = kurs.ogrenci_cikar(oid)
        if ok:
            # Öğrenci başka kursa kayıtlı değilse sistemden de çıkar
            ogr = self.ogrenciler.get(oid)
            if ogr and not ogr.get_kurslar():
                del self.ogrenciler[oid]
            self._admin_log_ekle(f"ÖĞRENCİ KAYDI SİLİNDİ → {mesaj} (Kurs: {kurs.get_ad()})")
            self._refresh_admin()
            QMessageBox.information(self, "Silindi", mesaj)
        else:
            QMessageBox.warning(self, "Hata", mesaj)

    def _admin_log_ekle(self, mesaj: str):
        zaman = datetime.now().strftime("%H:%M:%S")
        self.admin_log.append(f"[{zaman}]  {mesaj}")

    # ── Saat ─────────────────────────────────────────────────────────────────

    def _saat_baslat(self):
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

    def _kurs_btn_stili(self, secili: bool) -> str:
        if secili:
            return (f"QPushButton {{ background-color: {VURGU}; color: white; "
                    f"border-radius: 8px; border: none; font-weight: 700; padding: 0 14px; }}")
        return (f"QPushButton {{ background-color: {IC_CARD}; color: {IC_TXT}; "
                f"border-radius: 8px; border: 1.5px solid {IC_BORDER}; padding: 0 14px; }} "
                f"QPushButton:hover {{ background-color: {IC_CARD2}; }}")

    def _tablo_stili(self) -> str:
        return (
            f"QTableWidget {{ background-color: {IC_CARD}; color: {IC_TXT}; "
            f"border: 1px solid {IC_BORDER}; border-radius: 10px; gridline-color: {IC_BORDER}; "
            f"alternate-background-color: {IC_CARD2}; }} "
            f"QHeaderView::section {{ background-color: {IC_CARD2}; color: {VURGU}; "
            f"padding: 10px; font-weight: bold; border: none; "
            f"border-bottom: 1px solid {IC_BORDER}; }} "
            f"QTableWidget::item {{ padding: 8px 10px; }} "
            f"QTableWidget::item:selected {{ background-color: {IC_CARD2}; color: {IC_TXT}; }}"
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
            f"QPushButton:hover {{ background-color: #818CF8; }} "
            f"QPushButton:pressed {{ background-color: #4F46E5; }}"
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
            f"selection-background-color: {IC_CARD2}; selection-color: {IC_TXT}; "
            f"outline: none; border: 1px solid {IC_BORDER}; padding: 4px; }}"
        )


# ── Giriş Noktası ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = KursApp()
    win.show()
    sys.exit(app.exec_())
