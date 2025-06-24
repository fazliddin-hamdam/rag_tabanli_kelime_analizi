# vektor_veritabani.py - Optimized Batch Processing

import os
import numpy as np
import chromadb

print("🚀 Kelime Vektörleri ChromaDB'ye Yükleniyor...")

# 1) Kalıcı DB yolunu ayarla
BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

# 2) PersistentClient ile bağlantı
try:
    client = chromadb.PersistentClient(path=DB_DIR)
    print("✅ ChromaDB bağlantısı kuruldu")
except Exception as e:
    print(f"❌ ChromaDB bağlantı hatası: {e}")
    exit(1)

# 3) Koleksiyonu oluştur/al (cosine distance ile)
try:
    collection = client.get_or_create_collection(
        name="kelime_vektorleri",
        metadata={"hnsw:space": "cosine"}
    )
    print("✅ Kelime vektörleri koleksiyonu hazır")
except Exception as e:
    print(f"❌ Koleksiyon oluşturma hatası: {e}")
    exit(1)

# 4) Dosyaları kontrol et
if not os.path.exists("kelimeler.txt"):
    print("❌ kelimeler.txt dosyası bulunamadı!")
    exit(1)

if not os.path.exists("kelime_vektorleri.npy"):
    print("❌ kelime_vektorleri.npy dosyası bulunamadı!")
    exit(1)

# 5) Kelimeleri ve vektörleri yükle
print("📚 Kelimeler yükleniyor...")
kelimeler = [l.strip() for l in open("kelimeler.txt", encoding="utf-8") if l.strip()]

print("🔢 Kelime vektörleri yükleniyor...")
kelime_vektorleri = np.load("kelime_vektorleri.npy")

print(f"📊 Toplam kelime sayısı: {len(kelimeler)}")
print(f"🧮 Vektör boyutu: {kelime_vektorleri.shape}")

# 6) Varolan kayıtları temizle (isteğe bağlı)
try:
    existing_count = collection.count()
    if existing_count > 0:
        print(f"🗑️  Mevcut {existing_count} kayıt temizleniyor...")
        # Tüm kayıtları sil
        all_ids = [str(i) for i in range(existing_count)]
        collection.delete(ids=all_ids)
except Exception as e:
    print(f"⚠️  Temizleme sırasında hata (normal olabilir): {e}")

# 7) ⚡ BATCH PROCESSING - Çok daha hızlı!
print("💾 Kelimeler toplu olarak ChromaDB'ye ekleniyor...")
try:
    # Büyük koleksiyonlar için batch boyutu
    batch_size = 1000  # Kelimeler için daha büyük batch boyutu kullanabiliriz
    
    for i in range(0, len(kelimeler), batch_size):
        end_idx = min(i + batch_size, len(kelimeler))
        
        # Batch verileri hazırla
        batch_kelimeler = kelimeler[i:end_idx]
        batch_vektorler = kelime_vektorleri[i:end_idx]
        batch_ids = [str(j) for j in range(i, end_idx)]
        
        # Vektörleri liste formatına çevir
        batch_embeddings = [vec.tolist() for vec in batch_vektorler]
        
        # Toplu ekleme - tek seferde 1000 kelime!
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_kelimeler,
            ids=batch_ids
        )
        
        print(f"  📦 {end_idx}/{len(kelimeler)} kelime işlendi...")

    print(f"✅ {len(kelimeler)} kelime başarıyla ChromaDB'ye yüklendi!")
    print(f"🏁 Toplam kayıt sayısı: {collection.count()}")
    
except Exception as e:
    print(f"❌ Ekleme sırasında hata: {e}")
    exit(1)

print("🎯 İşlem tamamlandı!")
print("💡 Artık app.py'yi çalıştırarak arama yapabilirsiniz!")
