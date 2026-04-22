🎨 Minecraft Map Art Studio Pro

Görsellerinizi Minecraft harita sanatlarına (Map Art) ve şematiklerine dönüştüren en gelişmiş, Türkçe dil destekli masaüstü uygulaması. Gelişmiş doku (texture) motoru, 3D inşa seçenekleri ve detaylı renk filtreleme özellikleriyle hayatta kalma (survival) sunucularında harita sanatı yapmak hiç bu kadar kolay olmamıştı!

🌟 Öne Çıkan Özellikler

🖼️ Gerçek Doku (Texture) Motoru: Düz renkler yerine Minecraft'ın orijinal blok dokularını (16x16) kullanarak yüksek çözünürlüklü önizlemeler oluşturur.

🧊 Litematica Dışa Aktarma: Haritanızı doğrudan .litematic formatında kaydederek oyun içinde kolayca inşa edin.

📐 3 Farklı İnşa Tipi: * Zemin (Yatay): Klasik yer haritaları (Maksimum 10x10 harita).

Duvar (Dikey): Görselleri duvara dik olarak inşa eder.

3D (Merdivenli): Gölgelendirme hileleri (Dithering/Shadow) için blokları \ (Kuzey'e yükselen) şeklinde merdiven gibi dizer.

🎨 Gelişmiş Renk Filtreleme: * 150'den fazla blok otomatik olarak "Kırmızı, Mavi, Beton, Yün" gibi kategorilere ayrılır.

Sadece elinizde olan blokları seçmek için gelişmiş arama çubuğu ve Shift+Tık ile çoklu seçim desteği.

💾 Renk Profili (Import/Export): Kendi özel blok paletlerinizi oluşturun, .json olarak dışa aktarın ve istediğiniz zaman tekrar yükleyin.

✨ Dithering (Harmanlama): Sınırlı sayıdaki blokla daha pürüzsüz renk geçişleri (gradient) elde edin.

🎯 Hassas Yerleşim: Görselinizi 1'er piksel hassasiyetle ve sayısal veri girerek X ve Y eksenlerinde kaydırın, oranları milimetrik olarak ayarlayın.

📦 Kurulum ve Çalıştırma

Programı bilgisayarınızda çalıştırmak için Python 3.x yüklü olması gerekmektedir. Adımları takip ederek hemen kullanmaya başlayabilirsiniz:

1. Gerekli Kütüphaneleri Kurun

Terminal veya komut satırını (CMD) açarak projenin çalışması için gereken görüntü işleme ve şematik kütüphanelerini indirin:

pip install Pillow litemapy


2. Klasör Yapısını Doğrulayın

Programın resimleri ve renkleri doğru okuyabilmesi için indirdiğiniz dizinde blocks klasörü ve colors.json dosyası bulunmalıdır. Klasör yapınız şöyle görünmelidir:

/Minecraft-Map-Art-Studio/
 ├── blocks/             # Minecraft bloklarının 16x16 .png resimleri
 ├── colors.json         # Renk veritabanı ve Türkçe isim karşılıkları
 ├── mapart.py           # Ana uygulama dosyası
 └── README.md


3. Uygulamayı Başlatın

Terminalden mapart.py dosyasının bulunduğu klasöre gidin ve aşağıdaki komutu çalıştırın:

python mapart.py


(Not: macOS veya Linux kullanıyorsanız komutu python3 mapart.py şeklinde girmeniz gerekebilir.)

👨‍💻 Geliştirici & İletişim

Geliştirici: Muhittin Efecan Türk

Discord: efecan.turk0

Herhangi bir hata (bug) bulursanız veya yeni bir özellik eklenmesini isterseniz, Discord üzerinden bana ulaşabilir veya bu repoda bir "Issue" açabilirsiniz!
