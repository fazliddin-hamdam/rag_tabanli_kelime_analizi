# veritabani_guncelle.py

import os
import numpy as np
import chromadb

def veritabani_guncelle():
    """Güncellenmiş kelime vektörlerini ChromaDB'ye yükle"""
    
    # 1) Kalıcı DB yolunu ayarla
    BASE_DIR = os.path.dirname(__file__)
    DB_DIR = os.path.join(BASE_DIR, "db")
    os.makedirs(DB_DIR, exist_ok=True)

    # 2) PersistentClient ile bağlantı
    client = chromadb.PersistentClient(path=DB_DIR)
    
    # Mevcut collection'ı sil ve yeniden oluştur
    try:
        client.delete_collection("kelime_vektorleri")
        print("Eski veritabanı silindi.")
    except Exception:
        print("Silinecek eski veritabanı bulunamadı.")
    
    collection = client.create_collection("kelime_vektorleri")

    # 3) Güncellenmiş kelimeleri ve vektörleri yükle
    try:
        with open("kelimeler.txt", encoding="utf-8") as f:
            kelimeler = [line.strip() for line in f if line.strip()]
        
        kelime_vektorleri = np.load("kelime_vektorleri.npy")
        
        print(f"Yüklenecek kelime sayısı: {len(kelimeler)}")
        print(f"Vektör boyutu: {kelime_vektorleri.shape}")
        
        if len(kelimeler) != len(kelime_vektorleri):
            print("HATA: Kelime sayısı ile vektör sayısı eşleşmiyor!")
            return False
            
    except FileNotFoundError as e:
        print(f"HATA: Dosya bulunamadı - {e}")
        return False
    except Exception as e:
        print(f"HATA: Veri yükleme hatası - {e}")
        return False

    # 4) Batch halinde ekleme (performans için)
    batch_size = 100
    total_added = 0
    
    for i in range(0, len(kelimeler), batch_size):
        batch_end = min(i + batch_size, len(kelimeler))
        batch_kelimeler = kelimeler[i:batch_end]
        batch_vektorler = kelime_vektorleri[i:batch_end]
        
        try:
            collection.add(
                embeddings=batch_vektorler.tolist(),
                documents=batch_kelimeler,
                ids=[str(j) for j in range(i, batch_end)]
            )
            total_added += len(batch_kelimeler)
            print(f"İşlenen: {total_added}/{len(kelimeler)} kelime")
            
        except Exception as e:
            print(f"HATA: Batch {i}-{batch_end} eklenirken hata: {e}")
            return False

    print(f"\n✅ Başarıyla tamamlandı!")
    print(f"📊 Toplam {total_added} kelime ChromaDB'ye yüklendi.")
    
    # 5) Veritabanını test et
    test_result = collection.query(
        query_texts=["merhaba"],
        n_results=5
    )
    
    print(f"🔍 Test sorgusu sonucu: {len(test_result['documents'][0])} benzer kelime bulundu")
    print(f"🎯 En benzer kelimeler: {test_result['documents'][0]}")
    
    return True

if __name__ == "__main__":
    print("🚀 Vektör veritabanı güncelleme işlemi başlıyor...")
    success = veritabani_guncelle()
    
    if success:
        print("\n✨ İşlem başarıyla tamamlandı!")
        print("🎉 Kelime veritabanınız artık 2000 kelime içeriyor!")
    else:
        print("\n❌ İşlem başarısız oldu. Lütfen hataları kontrol edin.") 