# -*- coding: utf-8 -*-
"""
Etkinlik Kayıt Sistemi - Backend
=================================
Sınıflar: Katilimci, Etkinlik, Bilet
Tüm attribute'lar private (name mangling) olarak tanımlanmıştır.
Erişim yalnızca getter metodlar üzerinden sağlanır.
"""

from datetime import date
import uuid


class Katilimci:
    """
    Sisteme kayıt olan bir katılımcıyı temsil eder.

    Attributes:
        __id    (int): Benzersiz katılımcı kimliği
        __ad    (str): Katılımcının adı soyadı
        __email (str): Katılımcının e-posta adresi
    """

    def __init__(self, katilimci_id: int, ad: str, email: str):
        """
        Katilimci nesnesini oluşturur.

        Args:
            katilimci_id (int): Benzersiz kimlik numarası
            ad           (str): Ad soyad
            email        (str): E-posta adresi
        """
        self.__id    = katilimci_id
        self.__ad    = ad
        self.__email = email

    # --- Getter Metodlar ---

    def get_id(self) -> int:
        """Katılımcının ID'sini döndürür."""
        return self.__id

    def get_ad(self) -> str:
        """Katılımcının adını döndürür."""
        return self.__ad

    def get_email(self) -> str:
        """Katılımcının e-posta adresini döndürür."""
        return self.__email

    def bilgileri_guncelle(self, yeni_ad: str = None, yeni_email: str = None) -> tuple:
        """
        Katılımcının ad veya e-posta bilgisini günceller.

        Args:
            yeni_ad    (str|None): Güncellenecek ad; None ise değiştirilmez
            yeni_email (str|None): Güncellenecek e-posta; None ise değiştirilmez

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        if yeni_ad:
            self.__ad = yeni_ad
        if yeni_email:
            self.__email = yeni_email
        if not yeni_ad and not yeni_email:
            return False, "Güncellenecek bilgi girilmedi."
        return True, "Katılımcı bilgileri güncellendi."

    def __repr__(self) -> str:
        return f"Katilimci(id={self.__id}, ad='{self.__ad}', email='{self.__email}')"


# ---------------------------------------------------------------------------


class Etkinlik:
    """
    Bir etkinliği ve o etkinliğe ait katılımcıları yönetir.

    Attributes:
        __id           (int):  Benzersiz etkinlik kimliği
        __ad           (str):  Etkinlik adı
        __tarih        (date): Etkinlik tarihi
        __kapasite     (int):  Maksimum katılımcı sayısı
        __katilimcilar (list): Kayıtlı Katilimci nesnelerinin listesi
    """

    def __init__(self, etkinlik_id: int, ad: str, tarih: date, kapasite: int):
        """
        Etkinlik nesnesini oluşturur.

        Args:
            etkinlik_id (int):  Benzersiz kimlik numarası
            ad          (str):  Etkinlik adı
            tarih       (date): Etkinlik tarihi
            kapasite    (int):  Maksimum katılımcı kapasitesi
        """
        self.__id           = etkinlik_id
        self.__ad           = ad
        self.__tarih        = tarih
        self.__kapasite     = kapasite
        self.__katilimcilar = []   # list[Katilimci]

    # --- Getter Metodlar ---

    def get_id(self) -> int:
        """Etkinlik ID'sini döndürür."""
        return self.__id

    def get_ad(self) -> str:
        """Etkinlik adını döndürür."""
        return self.__ad

    def get_tarih(self) -> date:
        """Etkinlik tarihini döndürür."""
        return self.__tarih

    def get_kapasite(self) -> int:
        """Maksimum kapasiteyi döndürür."""
        return self.__kapasite

    def get_katilimcilar(self) -> list:
        """Kayıtlı katılımcıların listesini döndürür (kopya)."""
        return list(self.__katilimcilar)

    def get_katilimci_sayisi(self) -> int:
        """Kayıtlı katılımcı sayısını döndürür."""
        return len(self.__katilimcilar)

    # --- İşlem Metodları ---

    def katilimci_ekle(self, katilimci: "Katilimci") -> tuple:
        """
        Etkinliğe yeni bir katılımcı ekler.
        Kapasite doluysa ekleme yapılmaz.

        Args:
            katilimci (Katilimci): Eklenecek katılımcı nesnesi

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
                - (True,  "Kayıt başarılı.")  → ekleme yapıldı
                - (False, "Kapasite dolu!")   → ekleme yapılamadı
        """
        if len(self.__katilimcilar) < self.__kapasite:
            self.__katilimcilar.append(katilimci)
            return True, "Kayıt başarılı."
        return False, "Kapasite dolu!"

    def katilimci_cikar(self, katilimci_id: int) -> tuple:
        """
        Verilen ID'ye sahip katılımcıyı etkinlikten çıkarır.

        Args:
            katilimci_id (int): Çıkarılacak katılımcının ID'si

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        for k in self.__katilimcilar:
            if k.get_id() == katilimci_id:
                self.__katilimcilar.remove(k)
                return True, f"'{k.get_ad()}' kaydı silindi."
        return False, "Katılımcı bulunamadı."

    def katilimci_raporu(self) -> str:
        """
        Etkinliğe ait metin tabanlı raporu döndürür.
        Kapasite, doluluk ve katılımcı listesi içerir.

        Returns:
            str: Biçimlendirilmiş rapor metni
        """
        bos = self.__kapasite - len(self.__katilimcilar)
        pct = int(len(self.__katilimcilar) / self.__kapasite * 100) if self.__kapasite else 0

        rapor  = f"{'=' * 50}\n"
        rapor += f"  ETKİNLİK RAPORU : {self.__ad}\n"
        rapor += f"{'=' * 50}\n"
        rapor += f"  Tarih          : {self.__tarih}\n"
        rapor += f"  Kapasite       : {self.__kapasite}\n"
        rapor += f"  Katılımcı      : {len(self.__katilimcilar)}\n"
        rapor += f"  Boş Kontenjan  : {bos}\n"
        rapor += f"  Doluluk        : %{pct}\n"
        rapor += f"{'=' * 50}\n"

        if self.__katilimcilar:
            rapor += "  KATILIMCI LİSTESİ:\n"
            for i, k in enumerate(self.__katilimcilar, 1):
                rapor += (f"  {i:>3}. [{k.get_id():>4}] "
                          f"{k.get_ad():<25} | {k.get_email()}\n")
        else:
            rapor += "  Henüz kayıtlı katılımcı yok.\n"

        rapor += f"{'=' * 50}\n"
        return rapor

    def __repr__(self) -> str:
        return (f"Etkinlik(id={self.__id}, ad='{self.__ad}', "
                f"tarih={self.__tarih}, kapasite={self.__kapasite}, "
                f"kayitli={len(self.__katilimcilar)})")


# ---------------------------------------------------------------------------


class Bilet:
    """
    Bir katılımcının bir etkinliğe kaydını belgeleyen bilet nesnesi.

    Attributes:
        __bilet_id   (str):       UUID tabanlı benzersiz bilet numarası
        __etkinlik   (Etkinlik):  İlişkili etkinlik nesnesi
        __katilimci  (Katilimci): İlişkili katılımcı nesnesi
    """

    def __init__(self, etkinlik: Etkinlik, katilimci: Katilimci,
                 bilet_id: str = None):
        """
        Bilet nesnesini oluşturur. bilet_id verilmezse otomatik UUID üretilir.

        Args:
            etkinlik   (Etkinlik):  Biletin ait olduğu etkinlik
            katilimci  (Katilimci): Biletin sahibi katılımcı
            bilet_id   (str|None):  İsteğe bağlı özel bilet ID'si
        """
        self.__bilet_id  = bilet_id if bilet_id else str(uuid.uuid4()).upper()[:12]
        self.__etkinlik  = etkinlik
        self.__katilimci = katilimci

    # --- Getter Metodlar ---

    def get_bilet_id(self) -> str:
        """Bilet numarasını döndürür."""
        return self.__bilet_id

    def get_etkinlik(self) -> Etkinlik:
        """İlişkili etkinlik nesnesini döndürür."""
        return self.__etkinlik

    def get_katilimci(self) -> Katilimci:
        """İlişkili katılımcı nesnesini döndürür."""
        return self.__katilimci

    # --- İşlem Metodları ---

    def bilet_olustur(self) -> str:
        """
        Bilet bilgilerini okunabilir metin formatında döndürür.

        Returns:
            str: Bilet no, etkinlik adı, tarih, katılımcı adı ve e-postasını
                 içeren biçimlendirilmiş metin
        """
        return (
            f"{'*' * 42}\n"
            f"  BİLET NO   : {self.__bilet_id}\n"
            f"  ETKİNLİK   : {self.__etkinlik.get_ad()}\n"
            f"  TARİH      : {self.__etkinlik.get_tarih()}\n"
            f"  KATILIMCI  : {self.__katilimci.get_ad()}\n"
            f"  E-POSTA    : {self.__katilimci.get_email()}\n"
            f"{'*' * 42}"
        )

    def bilet_iptal(self) -> tuple:
        """
        Bileti iptal eder; ilişkili etkinlikten katılımcıyı çıkarır.

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        ok, mesaj = self.__etkinlik.katilimci_cikar(self.__katilimci.get_id())
        if ok:
            return True, f"Bilet [{self.__bilet_id}] iptal edildi. {mesaj}"
        return False, f"İptal başarısız: {mesaj}"

    def __repr__(self) -> str:
        return (f"Bilet(id='{self.__bilet_id}', "
                f"etkinlik='{self.__etkinlik.get_ad()}', "
                f"katilimci='{self.__katilimci.get_ad()}')")
