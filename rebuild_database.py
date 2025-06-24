#!/usr/bin/env python3
"""
🚀 ChromaDB Database Rebuild - Optimized Batch Processing
Tüm veritabanı koleksiyonlarını optimized batch processing ile yeniden oluşturur.
"""

import os
import sys
import time
import shutil
import numpy as np
import chromadb
from pathlib import Path

def clear_database():
    """Mevcut veritabanını temizle"""
    db_dir = "db"
    if os.path.exists(db_dir):
        print(f"🗑️  Mevcut veritabanı temizleniyor: {db_dir}")
        shutil.rmtree(db_dir)
    os.makedirs(db_dir, exist_ok=True)
    print("✅ Temiz veritabanı dizini oluşturuldu")

def check_files():
    """Gerekli dosyaları kontrol et"""
    required_files = [
        "kelimeler.txt",
        "kelime_vektorleri.npy",
        "metinler.txt", 
        "metin_vektorleri.npy",
        "iliskiler.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Eksik dosyalar: {', '.join(missing_files)}")
        return False
    
    print("✅ Tüm gerekli dosyalar mevcut")
    return True

def rebuild_word_vectors():
    """Kelime vektörlerini batch processing ile yeniden oluştur"""
    print("\n📚 KELIME VEKTÖRLERİ YENİDEN OLUŞTURULUYOR")
    print("=" * 50)
    
    start_time = time.time()
    
    # ChromaDB bağlantısı
    client = chromadb.PersistentClient(path="db")
    
    # Koleksiyon oluştur
    collection = client.get_or_create_collection(
        name="kelime_vektorleri",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Verileri yükle
    print("📖 Kelimeler yükleniyor...")
    with open("kelimeler.txt", "r", encoding="utf-8") as f:
        kelimeler = [line.strip() for line in f if line.strip()]
    
    print("🔢 Kelime vektörleri yükleniyor...")
    kelime_vektorleri = np.load("kelime_vektorleri.npy")
    
    print(f"📊 Toplam kelime sayısı: {len(kelimeler)}")
    
    # Batch processing
    batch_size = 1000
    print(f"💾 Batch processing başlıyor (batch_size={batch_size})...")
    
    for i in range(0, len(kelimeler), batch_size):
        end_idx = min(i + batch_size, len(kelimeler))
        
        batch_kelimeler = kelimeler[i:end_idx]
        batch_vektorler = kelime_vektorleri[i:end_idx]
        batch_ids = [str(j) for j in range(i, end_idx)]
        batch_embeddings = [vec.tolist() for vec in batch_vektorler]
        
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_kelimeler,
            ids=batch_ids
        )
        
        print(f"  📦 {end_idx}/{len(kelimeler)} kelime işlendi...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Kelime vektörleri tamamlandı: {duration:.2f} saniye")
    print(f"🏁 Toplam kayıt sayısı: {collection.count()}")
    
    return duration

def rebuild_sentence_vectors():
    """Cümle vektörlerini batch processing ile yeniden oluştur"""
    print("\n📝 CÜMLE VEKTÖRLERİ YENİDEN OLUŞTURULUYOR")
    print("=" * 50)
    
    start_time = time.time()
    
    # ChromaDB bağlantısı
    client = chromadb.PersistentClient(path="db")
    
    # Koleksiyon oluştur
    collection = client.get_or_create_collection(
        name="metin_vektorleri",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Verileri yükle
    print("📖 Cümleler yükleniyor...")
    with open("metinler.txt", "r", encoding="utf-8") as f:
        metinler = [line.strip() for line in f if line.strip()]
    
    print("🔢 Cümle vektörleri yükleniyor...")
    metin_vektorleri = np.load("metin_vektorleri.npy")
    
    print(f"📊 Toplam cümle sayısı: {len(metinler)}")
    
    # Batch processing
    batch_size = 500
    print(f"💾 Batch processing başlıyor (batch_size={batch_size})...")
    
    for i in range(0, len(metinler), batch_size):
        end_idx = min(i + batch_size, len(metinler))
        
        batch_metinler = metinler[i:end_idx]
        batch_vektorler = metin_vektorleri[i:end_idx]
        batch_ids = [str(j) for j in range(i, end_idx)]
        batch_embeddings = [vec.tolist() for vec in batch_vektorler]
        
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_metinler,
            ids=batch_ids
        )
        
        print(f"  📦 {end_idx}/{len(metinler)} cümle işlendi...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Cümle vektörleri tamamlandı: {duration:.2f} saniye")
    print(f"🏁 Toplam kayıt sayısı: {collection.count()}")
    
    return duration

def verify_database():
    """Veritabanını doğrula"""
    print("\n🔍 VERİTABANI DOĞRULAMA")
    print("=" * 30)
    
    client = chromadb.PersistentClient(path="db")
    
    # Koleksiyonları kontrol et
    collections = client.list_collections()
    print(f"📋 Bulunan koleksiyonlar: {len(collections)}")
    
    for collection_info in collections:
        collection = client.get_collection(collection_info.name)
        count = collection.count()
        print(f"  • {collection_info.name}: {count} kayıt")
    
    # Test araması yap
    try:
        word_collection = client.get_collection("kelime_vektorleri")
        results = word_collection.query(
            query_texts=["test"],
            n_results=3
        )
        print(f"✅ Kelime araması test edildi: {len(results['documents'][0])} sonuç")
        
        sentence_collection = client.get_collection("metin_vektorleri")
        results = sentence_collection.query(
            query_texts=["test cümlesi"],
            n_results=3
        )
        print(f"✅ Cümle araması test edildi: {len(results['documents'][0])} sonuç")
        
    except Exception as e:
        print(f"❌ Test araması başarısız: {e}")
        return False
    
    return True

def main():
    print("🎯 ChromaDB Database Rebuild - Optimized Batch Processing")
    print("=" * 60)
    
    total_start_time = time.time()
    
    # Dosyaları kontrol et
    if not check_files():
        print("❌ Gerekli dosyalar eksik. İşlem sonlandırılıyor.")
        sys.exit(1)
    
    # Onay al
    response = input("\n⚠️  Bu işlem mevcut veritabanını silecek. Devam etmek istiyor musunuz? (y/N): ")
    if response.lower() not in ['y', 'yes', 'evet']:
        print("❌ İşlem iptal edildi.")
        sys.exit(0)
    
    # Veritabanını temizle
    clear_database()
    
    # Koleksiyonları yeniden oluştur
    word_duration = rebuild_word_vectors()
    sentence_duration = rebuild_sentence_vectors()
    
    # Doğrulama
    if verify_database():
        print("✅ Veritabanı doğrulaması başarılı")
    else:
        print("❌ Veritabanı doğrulaması başarısız")
        sys.exit(1)
    
    # Özet
    total_duration = time.time() - total_start_time
    
    print(f"\n🏆 İŞLEM TAMAMLANDI!")
    print("=" * 30)
    print(f"⏱️  Kelime vektörleri: {word_duration:.2f} saniye")
    print(f"⏱️  Cümle vektörleri: {sentence_duration:.2f} saniye")
    print(f"⏱️  Toplam süre: {total_duration:.2f} saniye")
    
    print(f"\n💡 ÖNERİLER:")
    print(f"   • Artık 'python app.py' ile uygulamanızı başlatabilirsiniz")
    print(f"   • Performans testleri için: 'python batch_performance_test.py'")
    print(f"   • Veritabanı boyutu: {get_directory_size('db'):.1f} MB")

def get_directory_size(path):
    """Dizin boyutunu MB cinsinden hesapla"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # MB

if __name__ == "__main__":
    main() 