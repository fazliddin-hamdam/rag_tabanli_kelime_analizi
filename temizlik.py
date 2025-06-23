# kelimeler.txt dosyasından tekrar ve anlamsız kelimeleri siler, kelimeler_final.txt olarak kaydeder

stop_words = set([
    "ve", "bir", "bu", "da", "de", "ile", "ya", "ama", "gibi", "çok", "için", "ne", "değil", "veya",
    "ki", "o", "mi", "mu", "mı", "ben", "sen", "o", "biz", "siz", "onlar", "hem", "ya", "daha", "her",
    "şu", "şey", "şimdi", "bazı", "kadar", "sonra", "önce", "en", "çünkü", "ise", "ancak"
])

with open("kelimeler.txt", "r", encoding="utf-8") as f:
    kelimeler = [line.strip() for line in f if line.strip()]

kelimeler_unique = list(dict.fromkeys(kelimeler))
kelimeler_cleaned = [k for k in kelimeler_unique if k.lower() not in stop_words]

with open("kelimeler_final.txt", "w", encoding="utf-8") as f:
    for kelime in kelimeler_cleaned:
        f.write(kelime + "\n")
