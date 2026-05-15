# -*- coding: utf-8 -*-
"""
Online Kurs Platformu - Backend
================================
Sınıflar: Egitmen, Ogrenci, Kurs
Tüm attribute'lar private (name mangling) olarak tanımlanmıştır.
Erişim yalnızca getter metodlar üzerinden sağlanır.
"""

from datetime import date
import uuid


class Egitmen:
    """
    Platformda ders veren bir eğitmeni temsil eder.

    Attributes:
        __id        (int): Benzersiz eğitmen kimliği
        __ad        (str): Eğitmenin adı soyadı
        __uzmanlik  (str): Uzmanlık alanı
        __email     (str): E-posta adresi
    """

    def __init__(self, egitmen_id: int, ad: str, uzmanlik: str, email: str):
        """
        Egitmen nesnesini oluşturur.

        Args:
            egitmen_id (int): Benzersiz kimlik numarası
            ad         (str): Ad soyad
            uzmanlik   (str): Uzmanlık alanı
            email      (str): E-posta adresi
        """
        self.__id       = egitmen_id
        self.__ad       = ad
        self.__uzmanlik = uzmanlik
        self.__email    = email

    # --- Getter Metodlar ---

    def get_id(self) -> int:
        """Eğitmenin ID'sini döndürür."""
        return self.__id

    def get_ad(self) -> str:
        """Eğitmenin adını döndürür."""
        return self.__ad

    def get_uzmanlik(self) -> str:
        """Eğitmenin uzmanlık alanını döndürür."""
        return self.__uzmanlik

    def get_email(self) -> str:
        """Eğitmenin e-posta adresini döndürür."""
        return self.__email

    # --- İşlem Metodları ---

    def bilgileri_guncelle(self, yeni_ad: str = None,
                           yeni_uzmanlik: str = None,
                           yeni_email: str = None) -> tuple:
        """
        Eğitmenin bilgilerini günceller.

        Args:
            yeni_ad        (str|None): Yeni ad; None ise değiştirilmez
            yeni_uzmanlik  (str|None): Yeni uzmanlık; None ise değiştirilmez
            yeni_email     (str|None): Yeni e-posta; None ise değiştirilmez

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        if not any([yeni_ad, yeni_uzmanlik, yeni_email]):
            return False, "Güncellenecek bilgi girilmedi."
        if yeni_ad:
            self.__ad = yeni_ad
        if yeni_uzmanlik:
            self.__uzmanlik = yeni_uzmanlik
        if yeni_email:
            self.__email = yeni_email
        return True, "Eğitmen bilgileri güncellendi."

    def __repr__(self) -> str:
        return (f"Egitmen(id={self.__id}, ad='{self.__ad}', "
                f"uzmanlik='{self.__uzmanlik}')")


# ---------------------------------------------------------------------------


class Ogrenci:
    """
    Platforma kayıtlı bir öğrenciyi temsil eder.

    Attributes:
        __id     (int): Benzersiz öğrenci kimliği
        __ad     (str): Öğrencinin adı soyadı
        __email  (str): E-posta adresi
        __kurslar (list): Kayıtlı olunan kurs ID'lerinin listesi
    """

    def __init__(self, ogrenci_id: int, ad: str, email: str):
        """
        Ogrenci nesnesini oluşturur.

        Args:
            ogrenci_id (int): Benzersiz kimlik numarası
            ad         (str): Ad soyad
            email      (str): E-posta adresi
        """
        self.__id      = ogrenci_id
        self.__ad      = ad
        self.__email   = email
        self.__kurslar = []   # list[int] – kurs_id listesi

    # --- Getter Metodlar ---

    def get_id(self) -> int:
        """Öğrencinin ID'sini döndürür."""
        return self.__id

    def get_ad(self) -> str:
        """Öğrencinin adını döndürür."""
        return self.__ad

    def get_email(self) -> str:
        """Öğrencinin e-posta adresini döndürür."""
        return self.__email

    def get_kurslar(self) -> list:
        """Kayıtlı olunan kurs ID'lerinin kopyasını döndürür."""
        return list(self.__kurslar)

    # --- İşlem Metodları ---

    def kurs_ekle(self, kurs_id: int):
        """Öğrencinin kurs listesine yeni bir kurs ID'si ekler."""
        if kurs_id not in self.__kurslar:
            self.__kurslar.append(kurs_id)

    def kurs_cikar(self, kurs_id: int):
        """Öğrencinin kurs listesinden ilgili kurs ID'sini çıkarır."""
        if kurs_id in self.__kurslar:
            self.__kurslar.remove(kurs_id)

    def bilgi_guncelle(self, yeni_ad: str = None, yeni_email: str = None) -> tuple:
        """
        Öğrencinin ad veya e-posta bilgisini günceller.

        Args:
            yeni_ad    (str|None): Yeni ad; None ise değiştirilmez
            yeni_email (str|None): Yeni e-posta; None ise değiştirilmez

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        if not yeni_ad and not yeni_email:
            return False, "Güncellenecek bilgi girilmedi."
        if yeni_ad:
            self.__ad = yeni_ad
        if yeni_email:
            self.__email = yeni_email
        return True, "Öğrenci bilgileri güncellendi."

    def kurs_listesi(self, tum_kurslar: dict) -> str:
        """
        Öğrencinin kayıtlı olduğu kursları okunabilir formatta döndürür.

        Args:
            tum_kurslar (dict): {kurs_id: Kurs} sözlüğü

        Returns:
            str: Biçimlendirilmiş kurs listesi
        """
        if not self.__kurslar:
            return f"{self.__ad} henüz hiçbir kursa kayıtlı değil."

        rapor  = f"{'=' * 50}\n"
        rapor += f"  {self.__ad} — KAYITLI KURSLAR\n"
        rapor += f"{'=' * 50}\n"
        for i, kid in enumerate(self.__kurslar, 1):
            k = tum_kurslar.get(kid)
            if k:
                rapor += (f"  {i:>3}. [{k.get_id():>4}] "
                          f"{k.get_ad():<28} | {k.get_egitmen().get_ad()}\n")
        rapor += f"{'=' * 50}\n"
        return rapor

    def __repr__(self) -> str:
        return (f"Ogrenci(id={self.__id}, ad='{self.__ad}', "
                f"email='{self.__email}', kurs_sayisi={len(self.__kurslar)})")


# ---------------------------------------------------------------------------


class Kurs:
    """
    Platformdaki bir kursu ve kayıtlı öğrencileri yönetir.

    Attributes:
        __kurs_id   (int):      Benzersiz kurs kimliği
        __kurs_adi  (str):      Kurs adı
        __egitmen   (Egitmen):  İlgili eğitmen nesnesi
        __kontenjan (int):      Maksimum öğrenci sayısı
        __ogrenciler (list):    Kayıtlı Ogrenci nesnelerinin listesi
        __tarih     (date):     Kursun başlangıç tarihi
    """

    def __init__(self, kurs_id: int, kurs_adi: str,
                 egitmen: "Egitmen", kontenjan: int, tarih: date):
        """
        Kurs nesnesini oluşturur.

        Args:
            kurs_id    (int):     Benzersiz kimlik numarası
            kurs_adi   (str):     Kurs adı
            egitmen    (Egitmen): İlgili eğitmen nesnesi
            kontenjan  (int):     Maksimum öğrenci sayısı
            tarih      (date):    Kursun başlangıç tarihi
        """
        self.__kurs_id    = kurs_id
        self.__kurs_adi   = kurs_adi
        self.__egitmen    = egitmen
        self.__kontenjan  = kontenjan
        self.__ogrenciler = []   # list[Ogrenci]
        self.__tarih      = tarih

    # --- Getter Metodlar ---

    def get_id(self) -> int:
        """Kurs ID'sini döndürür."""
        return self.__kurs_id

    def get_ad(self) -> str:
        """Kurs adını döndürür."""
        return self.__kurs_adi

    def get_egitmen(self) -> "Egitmen":
        """İlgili eğitmen nesnesini döndürür."""
        return self.__egitmen

    def get_kontenjan(self) -> int:
        """Maksimum kontenjanı döndürür."""
        return self.__kontenjan

    def get_ogrenciler(self) -> list:
        """Kayıtlı öğrencilerin listesini döndürür (kopya)."""
        return list(self.__ogrenciler)

    def get_ogrenci_sayisi(self) -> int:
        """Kayıtlı öğrenci sayısını döndürür."""
        return len(self.__ogrenciler)

    def get_tarih(self) -> date:
        """Kursun başlangıç tarihini döndürür."""
        return self.__tarih

    # --- İşlem Metodları ---

    def kurs_guncelle(self, yeni_ad: str = None,
                      yeni_kontenjan: int = None,
                      yeni_tarih: date = None) -> tuple:
        """
        Kursun adını, kontenjanını veya başlangıç tarihini günceller.
        Yeni kontenjan mevcut kayıtlı öğrenci sayısından küçük olamaz.

        Args:
            yeni_ad        (str|None):  Yeni kurs adı
            yeni_kontenjan (int|None):  Yeni kontenjan değeri
            yeni_tarih     (date|None): Yeni başlangıç tarihi

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        if not any([yeni_ad, yeni_kontenjan is not None, yeni_tarih]):
            return False, "Güncellenecek bilgi girilmedi."
        if yeni_kontenjan is not None:
            if yeni_kontenjan < len(self.__ogrenciler):
                return False, (f"Yeni kontenjan ({yeni_kontenjan}), "
                               f"mevcut kayıt sayısından ({len(self.__ogrenciler)}) küçük olamaz.")
            self.__kontenjan = yeni_kontenjan
        if yeni_ad:
            self.__kurs_adi = yeni_ad
        if yeni_tarih:
            self.__tarih = yeni_tarih
        return True, "Kurs bilgileri güncellendi."

    def ogrenci_kaydet(self, ogrenci: "Ogrenci") -> tuple:
        """
        Kursa yeni bir öğrenci kaydeder.
        Kontenjan doluysa veya öğrenci zaten kayıtlıysa ekleme yapılmaz.

        Args:
            ogrenci (Ogrenci): Kaydedilecek öğrenci nesnesi

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        for o in self.__ogrenciler:
            if o.get_id() == ogrenci.get_id():
                return False, "Öğrenci zaten bu kursa kayıtlı!"
        if len(self.__ogrenciler) < self.__kontenjan:
            self.__ogrenciler.append(ogrenci)
            ogrenci.kurs_ekle(self.__kurs_id)
            return True, "Kayıt başarılı."
        return False, "Kontenjan dolu!"

    def ogrenci_cikar(self, ogrenci_id: int) -> tuple:
        """
        Verilen ID'ye sahip öğrenciyi kurstan çıkarır.

        Args:
            ogrenci_id (int): Çıkarılacak öğrencinin ID'si

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        for o in self.__ogrenciler:
            if o.get_id() == ogrenci_id:
                self.__ogrenciler.remove(o)
                o.kurs_cikar(self.__kurs_id)
                return True, f"'{o.get_ad()}' kaydı silindi."
        return False, "Öğrenci bulunamadı."

    def kurs_raporu(self) -> str:
        """
        Kursa ait metin tabanlı raporu döndürür.

        Returns:
            str: Biçimlendirilmiş rapor metni
        """
        bos = self.__kontenjan - len(self.__ogrenciler)
        pct = int(len(self.__ogrenciler) / self.__kontenjan * 100) if self.__kontenjan else 0

        rapor  = f"{'=' * 50}\n"
        rapor += f"  KURS RAPORU : {self.__kurs_adi}\n"
        rapor += f"{'=' * 50}\n"
        rapor += f"  Eğitmen        : {self.__egitmen.get_ad()}\n"
        rapor += f"  Uzmanlık       : {self.__egitmen.get_uzmanlik()}\n"
        rapor += f"  Başlangıç      : {self.__tarih}\n"
        rapor += f"  Kontenjan      : {self.__kontenjan}\n"
        rapor += f"  Kayıtlı        : {len(self.__ogrenciler)}\n"
        rapor += f"  Boş Kontenjan  : {bos}\n"
        rapor += f"  Doluluk        : %{pct}\n"
        rapor += f"{'=' * 50}\n"

        if self.__ogrenciler:
            rapor += "  ÖĞRENCİ LİSTESİ:\n"
            for i, o in enumerate(self.__ogrenciler, 1):
                rapor += (f"  {i:>3}. [{o.get_id():>4}] "
                          f"{o.get_ad():<25} | {o.get_email()}\n")
        else:
            rapor += "  Henüz kayıtlı öğrenci yok.\n"

        rapor += f"{'=' * 50}\n"
        return rapor

    def __repr__(self) -> str:
        return (f"Kurs(id={self.__kurs_id}, ad='{self.__kurs_adi}', "
                f"egitmen='{self.__egitmen.get_ad()}', "
                f"kontenjan={self.__kontenjan}, "
                f"kayitli={len(self.__ogrenciler)})")
