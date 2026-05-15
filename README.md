1. Proje Genel Bakış
ProEvent, etkinliklerin organizasyonunu, katılımcı kayıtlarını ve bilet yönetimini
kolaylaştırmak amacıyla geliştirilmiş masaüstü tabanlı bir uygulamadır. Sistem, güçlü
bir backend mimarisi ile modern ve kullanıcı dostu bir grafik arayüzü (GUI) birleştirir.

Temel Özellikler:
Etkinlik oluşturma ve kontenjan yönetimi.
Katılımcı kaydı ve otomatik bilet üretimi.
Detaylı raporlama ve doluluk oranı takibi.
Admin paneli üzerinden güvenlikli yönetim.

2. Sistem Mimarisi

Uygulama iki ana katmandan oluşmaktadır:

Dosya Katman Açıklama
etkinlik_sistemi.py Backend Veri modelleri, iş mantığı ve nesne yönelimli sınıfları içerir.
etkinlik_gui.py Frontend PyQt5 kütüphanesi kullanılarak tasarlanmış kullanıcı arayüzü.

3. Backend Detayları (etkinlik_sistemi.py)
Sistemde veriler "Private" (gizli) attribute'lar ile korunur ve erişim kontrollü metodlar
üzerinden sağlanır.
•
•
•
•

Katilimci Sınıfı

Sisteme kayıt olan her bireyi temsil eder.
Metodlar: get_id(), get_ad(), get_email(), bilgileri_guncelle().
Etkinlik Sınıfı

Organizasyonları ve katılımcı listelerini yönetir.
Metodlar: katilimci_ekle(), katilimci_cikar(),
get_katilimci_sayisi(), katilimci_raporu().
Kontrol: Kontenjan dolduğunda kayıt işlemini otomatik olarak engeller.
Bilet Sınıfı

Etkinlik ve katılımcı arasındaki ilişkiyi belgeler.
Metodlar: bilet_olustur(): Benzersiz bir bilet ID'si ile tüm bilgileri formatlı
şekilde döndürür.

4. Arayüz Tasarımı (etkinlik_gui.py)

Uygulama, solda sabit bir navigasyon çubuğu ve sağda dinamik olarak değişen sayfa
yığınından (QStackedWidget) oluşur.
4.1. Dashboard (Panel)
Sistemin genel özetini gösterir. KPI kartları aracılığıyla toplam etkinlik ve katılımcı
sayısı anlık izlenebilir. Aktif etkinlik takvimi tablo halinde sunulur.
4.2. Kayıt Yönetimi
Katılımcıların sisteme eklendiği ana bölümdür. Kullanıcı önce bir etkinlik seçer,
ardından isim ve e-posta bilgilerini girerek kaydı tamamlar.
•

•

•

•

4.3. Biletler ve Raporlama
Biletler sekmesinde tüm kayıtlar aranabilir ve bilet detayları görüntülenebilir.
Raporlar sekmesi ise her etkinlik için doluluk oranlarını grafiksel (progress bar) olarak
görselleştirir.

5. Kurulum ve Çalıştırma

Uygulamanın çalışması için Python ve PyQt5 kütüphanesi gereklidir.

ProEvent Yazılım Dökümantasyonu | 2026

# Gerekli kütüphaneyi kurun
pip install PyQt5
# Uygulamayı başlatın
python etkinlik_gui.py
