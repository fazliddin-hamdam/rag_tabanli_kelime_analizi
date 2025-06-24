#!/usr/bin/env python3
"""
🚀 ChromaDB Batch Processing Performance Test
Bu script batch ve tek tek ekleme performansını karşılaştırır.
"""

import os
import time
import numpy as np
import chromadb
from typing import List, Tuple

def setup_test_data(size: int = 1000) -> Tuple[List[str], np.ndarray]:
    """Test için sahte veri oluştur"""
    print(f"📊 {size} test verisi oluşturuluyor...")
    
    # Sahte kelimeler
    words = [f"test_kelime_{i}" for i in range(size)]
    
    # Sahte vektörler (384 boyutlu)
    vectors = np.random.rand(size, 384).astype(np.float32)
    
    return words, vectors

def test_single_insert(collection, words: List[str], vectors: np.ndarray) -> float:
    """Tek tek ekleme testi"""
    print("🐌 Tek tek ekleme testi başlıyor...")
    
    start_time = time.time()
    
    for i, (word, vector) in enumerate(zip(words, vectors)):
        collection.add(
            embeddings=[vector.tolist()],
            documents=[word],
            ids=[f"single_{i}"]
        )
        
        if (i + 1) % 100 == 0:
            print(f"  📝 {i + 1}/{len(words)} eklendi...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Tek tek ekleme tamamlandı: {duration:.2f} saniye")
    return duration

def test_batch_insert(collection, words: List[str], vectors: np.ndarray, batch_size: int = 500) -> float:
    """Batch ekleme testi"""
    print(f"⚡ Batch ekleme testi başlıyor (batch_size={batch_size})...")
    
    start_time = time.time()
    
    for i in range(0, len(words), batch_size):
        end_idx = min(i + batch_size, len(words))
        
        batch_words = words[i:end_idx]
        batch_vectors = vectors[i:end_idx]
        batch_ids = [f"batch_{j}" for j in range(i, end_idx)]
        batch_embeddings = [vec.tolist() for vec in batch_vectors]
        
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_words,
            ids=batch_ids
        )
        
        print(f"  📦 {end_idx}/{len(words)} eklendi (batch)...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Batch ekleme tamamlandı: {duration:.2f} saniye")
    return duration

def main():
    print("🎯 ChromaDB Batch Processing Performance Test")
    print("=" * 50)
    
    # Test veritabanı dizini
    test_db_dir = "test_db"
    os.makedirs(test_db_dir, exist_ok=True)
    
    # ChromaDB bağlantısı
    client = chromadb.PersistentClient(path=test_db_dir)
    
    # Test boyutları
    test_sizes = [500, 1000, 2000]
    batch_sizes = [100, 500, 1000]
    
    results = []
    
    for test_size in test_sizes:
        print(f"\n🔬 Test boyutu: {test_size} öğe")
        print("-" * 30)
        
        # Test verisi oluştur
        words, vectors = setup_test_data(test_size)
        
        # Tek tek ekleme testi
        single_collection = client.get_or_create_collection(
            f"single_test_{test_size}",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Koleksiyonu temizle
        try:
            single_collection.delete(ids=[f"single_{i}" for i in range(test_size)])
        except:
            pass
        
        single_time = test_single_insert(single_collection, words, vectors)
        
        # Batch ekleme testleri
        for batch_size in batch_sizes:
            batch_collection = client.get_or_create_collection(
                f"batch_test_{test_size}_{batch_size}",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Koleksiyonu temizle
            try:
                batch_collection.delete(ids=[f"batch_{i}" for i in range(test_size)])
            except:
                pass
            
            batch_time = test_batch_insert(batch_collection, words, vectors, batch_size)
            
            # Performans karşılaştırması
            speedup = single_time / batch_time
            improvement = ((single_time - batch_time) / single_time) * 100
            
            result = {
                'test_size': test_size,
                'batch_size': batch_size,
                'single_time': single_time,
                'batch_time': batch_time,
                'speedup': speedup,
                'improvement': improvement
            }
            results.append(result)
            
            print(f"📈 Batch Size {batch_size}: {speedup:.2f}x hızlı ({improvement:.1f}% iyileştirme)")
    
    # Sonuçları özetle
    print("\n🏆 PERFORMANS ÖZETİ")
    print("=" * 60)
    print(f"{'Test Size':<10} {'Batch Size':<10} {'Speedup':<10} {'Improvement':<12}")
    print("-" * 60)
    
    for result in results:
        print(f"{result['test_size']:<10} {result['batch_size']:<10} "
              f"{result['speedup']:.2f}x{'':<5} {result['improvement']:.1f}%")
    
    # En iyi performans
    best_result = max(results, key=lambda x: x['speedup'])
    print(f"\n🥇 En İyi Performans:")
    print(f"   Test Size: {best_result['test_size']}")
    print(f"   Batch Size: {best_result['batch_size']}")
    print(f"   Speedup: {best_result['speedup']:.2f}x")
    print(f"   Improvement: {best_result['improvement']:.1f}%")
    
    # Öneriler
    print(f"\n💡 ÖNERİLER:")
    print(f"   • Küçük koleksiyonlar (500-1000) için: Batch Size 500")
    print(f"   • Büyük koleksiyonlar (2000+) için: Batch Size 1000")
    print(f"   • Bellek sınırlı sistemler için: Batch Size 100-200")
    
    # Test dizinini temizle
    import shutil
    shutil.rmtree(test_db_dir)
    print(f"\n🗑️  Test dizini temizlendi: {test_db_dir}")

if __name__ == "__main__":
    main() 