# cümle_veritabani.py

import os
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

print("🚀 Cümle Vektörleri ChromaDB'ye Yükleniyor...")

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
collection = client.get_or_create_collection(
    name="metin_vektorleri",
    metadata={"hnsw:space": "cosine"}
)

# 4) Metin dosyası var mı kontrol et
if not os.path.exists("metinler.txt"):
    print("❌ metinler.txt dosyası bulunamadı!")
    exit(1)

if not os.path.exists("metin_vektorleri.npy"):
    print("❌ metin_vektorleri.npy dosyası bulunamadı!")
    print("💡 Önce metin vektörlerini oluşturun!")
    exit(1)

# 5) Metinleri ve vektörleri yükle
print("📚 Metinler yükleniyor...")
with open("metinler.txt", "r", encoding="utf-8") as f:
    metinler = [line.strip() for line in f if line.strip()]

print("🔢 Metin vektörleri yükleniyor...")
metin_vektorleri = np.load("metin_vektorleri.npy")

print(f"📊 Toplam cümle sayısı: {len(metinler)}")
print(f"🧮 Vektör boyutu: {metin_vektorleri.shape}")

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

# 7) Cümleleri toplu olarak ekle
print("💾 Cümleler ChromaDB'ye ekleniyor...")
try:
    # ⚡ Optimized batch boyutu - daha büyük batchler daha hızlı!
    batch_size = 500  # 100'den 500'e çıkardık
    
    for i in range(0, len(metinler), batch_size):
        end_idx = min(i + batch_size, len(metinler))
        batch_metinler = metinler[i:end_idx]
        batch_vektorler = metin_vektorleri[i:end_idx]
        batch_ids = [str(j) for j in range(i, end_idx)]
        
        # Vektörleri liste formatına çevir
        batch_embeddings = [vec.tolist() for vec in batch_vektorler]
        
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_metinler,
            ids=batch_ids
        )
        
        print(f"  📦 {end_idx}/{len(metinler)} cümle işlendi...")

    print(f"✅ {len(metinler)} cümle başarıyla ChromaDB'ye yüklendi!")
    print(f"🏁 Toplam kayıt sayısı: {collection.count()}")
    
except Exception as e:
    print(f"❌ Ekleme sırasında hata: {e}")
    exit(1)

print("🎯 İşlem tamamlandı!") 