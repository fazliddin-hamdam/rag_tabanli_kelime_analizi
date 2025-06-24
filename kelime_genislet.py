# kelime_genislet.py
import numpy as np
from sentence_transformers import SentenceTransformer

def mevcut_kelimeleri_yukle():
    """Mevcut kelimeleri yükle"""
    try:
        with open("kelimeler.txt", "r", encoding="utf-8") as f:
            kelimeler = [line.strip() for line in f if line.strip()]
        return set(kelimeler)
    except FileNotFoundError:
        return set()

def turkce_sikkullanilan_kelimeler():
    """En sık kullanılan Türkçe kelimelerin listesi"""
    kelimeler = [
        # Zamir ve Belirteçler
        "ben", "sen", "o", "biz", "siz", "onlar", "bu", "şu", "böyle", "şöyle",
        "her", "hiç", "çok", "az", "daha", "en", "çok", "kendi", "birisi", "hiçbiri",
        
        # Edatlar ve Bağlaçlar
        "ve", "ile", "için", "gibi", "kadar", "ancak", "fakat", "ama", "veya", "ya da",
        "eğer", "çünkü", "rağmen", "karşın", "sonra", "önce", "üzere", "göre", "karşı",
        
        # Sık Kullanılan Fiiller
        "olmak", "etmek", "yapmak", "almak", "vermek", "gelmek", "gitmek", "görmek",
        "bilmek", "istemek", "çıkmak", "girmek", "kalmak", "dökmek", "koymak", "aramak",
        "bulmak", "demek", "söylemek", "düşünmek", "anlamak", "öğrenmek", "çalışmak",
        "oturmak", "kalkmak", "yürümek", "koşmak", "yemek", "içmek", "uyumak", "uyanmak",
        "durmak", "başlamak", "bitirmek", "devam", "etmek", "kullanmak", "yazmak", "okumak",
        "dinlemek", "konuşmak", "sormak", "cevaplamak", "açmak", "kapatmak", "beklemek",
        "gülmek", "ağlamak", "sevmek", "nefret", "korkmak", "endişe", "merak", "unutmak",
        "hatırlamak", "taşımak", "bırakmak", "tutmak", "atmak", "düşmek", "kaldırmak",
        "vurmak", "çekmek", "itmek", "oynamak", "kazanmak", "kaybetmek", "satmak",
        "satın", "almak", "ödemek", "harcanmak", "biriktirmek", "göndermek", "almak",
        
        # Sıfatlar
        "iyi", "kötü", "güzel", "çirkin", "büyük", "küçük", "uzun", "kısa", "geniş",
        "dar", "yüksek", "alçak", "kalın", "ince", "ağır", "hafif", "sıcak", "soğuk",
        "yeni", "eski", "genç", "yaşlı", "hızlı", "yavaş", "kolay", "zor", "basit",
        "karmaşık", "temiz", "kirli", "beyaz", "siyah", "kırmızı", "mavi", "yeşil",
        "sarı", "turuncu", "mor", "pembe", "gri", "kahverengi", "açık", "koyu",
        "parlak", "mat", "yumuşak", "sert", "tatlı", "tuzlu", "acı", "ekşi",
        "lezzetli", "lezzetsiz", "doğru", "yanlış", "haklı", "haksız", "adil", "adaletsiz",
        "güvenli", "tehlikeli", "rahat", "rahatsız", "mutlu", "üzgün", "neşeli", "kederli",
        "sakin", "gergin", "özgür", "esir", "zengin", "fakir", "sağlıklı", "hasta",
        "güçlü", "zayıf", "cesur", "korkak", "akıllı", "ahmak", "başarılı", "başarısız",
        
        # Zaman İfadeleri
        "şimdi", "sonra", "önce", "bugün", "dün", "yarın", "geçen", "gelecek", "hafta",
        "ay", "yıl", "sabah", "öğle", "akşam", "gece", "erken", "geç", "yakında", "uzakta",
        "arada", "sırada", "bazen", "her zaman", "hiçbir zaman", "genellikle", "sık sık",
        "nadiren", "hemen", "derhal", "yavaş yavaş", "birden", "aniden", "ansızın",
        
        # Mekân İfadeleri
        "burası", "şurası", "orası", "yukarı", "aşağı", "ileri", "geri", "sağ", "sol",
        "orta", "kenar", "köşe", "içeri", "dışarı", "yanı", "karşı", "arkası", "önü",
        "altı", "üstü", "arasında", "içinde", "dışında", "üzerinde", "altında",
        
        # Sayılar ve Miktar
        "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
        "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan", "yüz",
        "bin", "milyon", "milyar", "birinci", "ikinci", "üçüncü", "son", "tüm", "bütün",
        "yarım", "çeyrek", "katı", "misli", "tek", "çift", "fazla", "eksik", "yeterli",
        
        # Aile ve İlişkiler
        "aile", "anne", "baba", "çocuk", "kız", "oğul", "erkek", "kardeş", "abla", "abi",
        "dede", "nine", "amca", "dayı", "hala", "teyze", "kuzen", "eş", "karı", "koca",
        "sevgili", "nişanlı", "arkadaş", "dost", "komşu", "tanıdık", "yabancı", "misafir",
        
        # Vücut ve Sağlık
        "baş", "saç", "yüz", "göz", "kulak", "burun", "ağız", "diş", "boyun", "omuz",
        "kol", "el", "parmak", "göğüs", "karın", "sırt", "bel", "kalça", "bacak", "ayak",
        "deri", "kemik", "kas", "kan", "kalp", "akciğer", "mide", "beyin", "sağlık",
        "hastalık", "ağrı", "acı", "yorgunluk", "dinlenmek", "iyileşmek",
        
        # Yiyecek ve İçecek
        "yemek", "ekmek", "su", "süt", "çay", "kahve", "et", "balık", "tavuk", "sebze",
        "meyve", "elma", "armut", "üzüm", "portakal", "limon", "domates", "patates",
        "soğan", "sarımsak", "pirinç", "bulgur", "makarna", "yoğurt", "peynir", "yumurta",
        "bal", "şeker", "tuz", "biber", "salata", "çorba", "pilav", "kebap", "börek",
        
        # Ev ve Eşyalar
        "ev", "oda", "salon", "mutfak", "banyo", "yatak", "odası", "balkon", "bahçe",
        "kapı", "pencere", "duvar", "tavan", "zemin", "döşeme", "halı", "masa", "sandalye",
        "koltuk", "dolap", "raf", "yatak", "yastık", "battaniye", "çarşaf", "ayna",
        "lamba", "elektrik", "su", "gaz", "ısıtma", "klima", "televizyon", "radyo",
        "buzdolabı", "fırın", "ocak", "çamaşır", "makinesi", "çanak", "tabak", "kaşık",
        "bıçak", "çatal", "bardak", "fincan", "tencere", "tava",
        
        # Giyim
        "elbise", "gömlek", "tişört", "kazak", "ceket", "mont", "pantolon", "etek",
        "şort", "ayakkabı", "çorap", "külot", "sütyen", "şapka", "eldiven", "atkı",
        "kemer", "çanta", "saat", "kolye", "küpe", "yüzük", "gözlük",
        
        # Ulaşım
        "araba", "otobüs", "dolmuş", "taksi", "tren", "metro", "otobüs", "uçak", "gemi",
        "vapur", "bisiklet", "motosiklet", "yürümek", "koşmak", "sürücü", "yolcu", "yol",
        "sokak", "cadde", "bulvar", "köprü", "tünel", "kavşak", "durak", "istasyon",
        "havaalanı", "liman", "garaj", "park", "benzin", "yakıt",
        
        # Doğa ve Hava
        "hava", "güneş", "ay", "yıldız", "bulut", "yağmur", "kar", "rüzgar", "fırtına",
        "gök", "gürültü", "şimşek", "sıcak", "soğuk", "ılık", "serin", "nemli", "kuru",
        "doğa", "orman", "ağaç", "çiçek", "ot", "yaprak", "meyve", "tohum", "kök",
        "dallar", "gölge", "hayvan", "kuş", "kedi", "köpek", "at", "inek", "koyun",
        "balık", "böcek", "arı", "kelebek", "karınca", "dağ", "tepe", "vadi", "ova",
        "deniz", "göl", "ırmak", "dere", "kaynak", "plaj", "kum", "taş", "toprak",
        
        # Teknoloji
        "telefon", "bilgisayar", "tablet", "internet", "site", "sayfa", "program",
        "uygulama", "oyun", "video", "müzik", "fotoğraf", "resim", "dosya", "klasör",
        "yazılım", "donanım", "ekran", "klavye", "fare", "kamera", "mikrofon", "hoparlör",
        "kulaklık", "şarj", "pil", "elektrik", "kablo", "wifi", "bluetooth", "usb",
        
        # Eğitim ve Meslek
        "okul", "üniversite", "öğrenci", "öğretmen", "hoca", "dersane", "sınıf", "ders",
        "konu", "kitap", "defter", "kalem", "kağıt", "tahta", "sıra", "çanta", "ödev",
        "sınav", "not", "diploma", "mezuniyet", "meslek", "iş", "işçi", "patron", "şef",
        "mühendis", "doktor", "hemşire", "avukat", "öğretmen", "satıcı", "garson", "şoför",
        "berber", "kuaför", "temizlikçi", "güvenlik", "polis", "asker", "itfaiyeci",
        
        # Ekonomi ve Alışveriş
        "para", "lira", "dolar", "euro", "fiyat", "ucuz", "pahalı", "indirim", "zam",
        "maaş", "ücret", "borç", "kredi", "banka", "hesap", "kart", "nakit", "market",
        "dükkan", "mağaza", "alışveriş", "satış", "müşteri", "fiş", "fatura", "ödeme",
        
        # Sosyal ve Kültür
        "toplum", "kültür", "gelenek", "görenek", "bayram", "düğün", "cenaze", "doğum",
        "günü", "parti", "eğlence", "müzik", "dans", "şarkı", "film", "sinema", "tiyatro",
        "kitap", "roman", "hikaye", "şiir", "gazete", "dergi", "haber", "televizyon",
        "radyo", "sanat", "ressam", "müzisyen", "oyuncu", "yazar", "şair",
        
        # Duygular ve Davranış
        "sevgi", "aşk", "nefret", "öfke", "kızgınlık", "üzüntü", "sevinç", "mutluluk",
        "hüzün", "korku", "endişe", "merak", "şaşkınlık", "hayranlık", "gurur", "utanç",
        "pişmanlık", "özlem", "hasret", "umut", "ümit", "güven", "şüphe", "tereddüt",
        "cesaret", "korkusuzluk", "sabır", "acele", "heyecan", "sakinlik", "sinir",
        
        # Zaman ve Takvim
        "pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar",
        "ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos",
        "eylül", "ekim", "kasım", "aralık", "ilkbahar", "yaz", "sonbahar", "kış",
        "mevsim", "tarih", "takvim", "saat", "dakika", "saniye", "an", "süre", "vakit",
        
        # Eylemler ve Durumlar
        "yaşamak", "doğmak", "ölmek", "büyümek", "küçülmek", "değişmek", "kalmak",
        "hareket", "durmak", "dinlenmek", "çalışmak", "oynak", "sabit", "hareketli",
        "hareketsiz", "açık", "kapalı", "dolu", "boş", "temiz", "kirli", "düzenli",
        "dağınık", "sessiz", "gürültülü", "sakin", "hareketli", "canlı", "cansız",
        
        # Soyut Kavramlar
        "fikir", "düşünce", "akıl", "zeka", "bilgi", "bilim", "teknoloji", "gelişme",
        "ilerleme", "değişim", "yenilik", "buluş", "keşif", "deneyim", "tecrübe", "alışkanlık",
        "gelenek", "kural", "yasa", "hukuk", "adalet", "hak", "özgürlük", "demokrasi",
        "barış", "savaş", "güvenlik", "tehlike", "risk", "şans", "talih", "kader",
        "gelecek", "geçmiş", "şimdi", "zaman", "süre", "hız", "yavaşlık", "mesafe",
        "uzaklık", "yakınlık", "büyüklük", "küçüklük", "ağırlık", "hafiflik", "sıcaklık",
        "soğukluk", "sıklık", "seyreklik", "yoğunluk", "inceligy", "kalınlık", "yükseklik",
        "alçaklık", "derinlik", "sığlık", "genişlik", "darlık", "uzunluk", "kısalık"
    ]
    
    return kelimeler

def kelime_veritabanini_genislet():
    """Mevcut kelime veritabanını genişlet"""
    print("Mevcut kelimeler yükleniyor...")
    mevcut_kelimeler = mevcut_kelimeleri_yukle()
    print(f"Mevcut kelime sayısı: {len(mevcut_kelimeler)}")
    
    print("Sık kullanılan Türkçe kelimeler yükleniyor...")
    yeni_kelimeler = turkce_sikkullanilan_kelimeler()
    
    # Mevcut kelimelerde olmayan yeni kelimeleri bul
    eklenecek_kelimeler = []
    for kelime in yeni_kelimeler:
        if kelime not in mevcut_kelimeler:
            eklenecek_kelimeler.append(kelime)
    
    print(f"Eklenebilecek yeni kelime sayısı: {len(eklenecek_kelimeler)}")
    
    # Toplam kelime sayısını 2000'e tamamla
    hedef_sayi = 2000
    mevcut_sayi = len(mevcut_kelimeler)
    eksik_sayi = hedef_sayi - mevcut_sayi
    
    if eksik_sayi <= 0:
        print("Zaten yeterli kelime var!")
        return
    
    # Gerekli sayı kadar kelime al
    if len(eklenecek_kelimeler) > eksik_sayi:
        eklenecek_kelimeler = eklenecek_kelimeler[:eksik_sayi]
    elif len(eklenecek_kelimeler) < eksik_sayi:
        print(f"Uyarı: Sadece {len(eklenecek_kelimeler)} yeni kelime eklenebilir. {eksik_sayi} kelime gerekiyordu.")
    
    # Yeni kelimeleri dosyaya ekle
    with open("kelimeler.txt", "a", encoding="utf-8") as f:
        for kelime in eklenecek_kelimeler:
            f.write(f"\n{kelime}")
    
    print(f"{len(eklenecek_kelimeler)} yeni kelime eklendi!")
    print(f"Toplam kelime sayısı: {len(mevcut_kelimeler) + len(eklenecek_kelimeler)}")

def vektorleri_yeniden_olustur():
    """Kelime vektörlerini yeniden oluştur"""
    print("Kelime vektörleri yeniden oluşturuluyor...")
    model = SentenceTransformer("dbmdz/bert-base-turkish-cased")
    
    with open("kelimeler.txt", encoding="utf-8") as f:
        kelimeler = [line.strip() for line in f if line.strip()]
    
    print(f"Toplam {len(kelimeler)} kelime için vektör oluşturuluyor...")
    kelime_vektorleri = model.encode(kelimeler, show_progress_bar=True)
    np.save("kelime_vektorleri.npy", kelime_vektorleri)
    print("Kelime vektörleri başarıyla kaydedildi!")

if __name__ == "__main__":
    print("Kelime veritabanı genişletme işlemi başlıyor...")
    kelime_veritabanini_genislet()
    print("\nVektör oluşturma işlemi başlıyor...")
    vektorleri_yeniden_olustur()
    print("\nİşlem tamamlandı!") 