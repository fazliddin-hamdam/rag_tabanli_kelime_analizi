#!/usr/bin/env python3
"""
🚀 Multi-Model ChromaDB Database Rebuild - Optimized Batch Processing
Çoklu model destekli tüm veritabanı koleksiyonlarını optimized batch processing ile yeniden oluşturur.
"""

import os
import sys
import time
import shutil
import numpy as np
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Desteklenecek modellerin tanımı
SUPPORTED_MODELS = {
    "dbmdz_bert": "dbmdz/bert-base-turkish-cased",
    "turkcell_roberta": "TURKCELL/roberta-base-turkish-uncased",
    "multilingual_mpnet": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
}

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
        "metinler.txt", 
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

def create_vectors_for_model(model_id, model_name, kelimeler, metinler):
    """Belirtilen model için vektörleri oluştur"""
    print(f"\n🤖 Model yükleniyor: {model_name}")
    try:
        model = SentenceTransformer(model_name)
        print(f"✅ Model başarıyla yüklendi: {model_id}")
        
        # Kelime vektörlerini oluştur
        print(f"🔤 Kelime vektörleri oluşturuluyor...")
        kelime_vektorleri = model.encode(kelimeler, show_progress_bar=True)
        
        # Cümle vektörlerini oluştur
        print(f"📚 Cümle vektörleri oluşturuluyor...")
        metin_vektorleri = model.encode(metinler, show_progress_bar=True)
        
        return kelime_vektorleri, metin_vektorleri, True
        
    except Exception as e:
        print(f"❌ Model {model_id} yüklenirken hata: {e}")
        return None, None, False

def rebuild_collections_for_model(model_id, kelimeler, metinler, kelime_vektorleri, metin_vektorleri):
    """Belirtilen model için ChromaDB koleksiyonlarını oluştur"""
    print(f"\n💾 {model_id} için koleksiyonlar oluşturuluyor...")
    
    # ChromaDB bağlantısı
    client = chromadb.PersistentClient(path="db")
    
    # Koleksiyon isimleri
    word_collection_name = f"kelime_vektorleri_{model_id}"
    sentence_collection_name = f"metin_vektorleri_{model_id}"
    
    try:
        # Kelime koleksiyonu
        print(f"📖 Kelime koleksiyonu oluşturuluyor: {word_collection_name}")
        word_collection = client.get_or_create_collection(
            name=word_collection_name,
            metadata={"hnsw:space": "cosine", "model_id": model_id}
        )
        
        # Kelime vektörlerini batch processing ile ekle
        batch_size = 1000
        for i in range(0, len(kelimeler), batch_size):
            end_idx = min(i + batch_size, len(kelimeler))
            
            batch_kelimeler = kelimeler[i:end_idx]
            batch_vektorler = kelime_vektorleri[i:end_idx]
            batch_ids = [str(j) for j in range(i, end_idx)]
            batch_embeddings = [vec.tolist() for vec in batch_vektorler]
            
            word_collection.add(
                embeddings=batch_embeddings,
                documents=batch_kelimeler,
                ids=batch_ids
            )
            
            print(f"  📦 {end_idx}/{len(kelimeler)} kelime işlendi...")
        
        print(f"✅ Kelime koleksiyonu tamamlandı: {word_collection.count()} kayıt")
        
        # Cümle koleksiyonu
        print(f"📝 Cümle koleksiyonu oluşturuluyor: {sentence_collection_name}")
        sentence_collection = client.get_or_create_collection(
            name=sentence_collection_name,
            metadata={"hnsw:space": "cosine", "model_id": model_id}
        )
        
        # Cümle vektörlerini batch processing ile ekle
        batch_size = 500
        for i in range(0, len(metinler), batch_size):
            end_idx = min(i + batch_size, len(metinler))
            
            batch_metinler = metinler[i:end_idx]
            batch_vektorler = metin_vektorleri[i:end_idx]
            batch_ids = [str(j) for j in range(i, end_idx)]
            batch_embeddings = [vec.tolist() for vec in batch_vektorler]
            
            sentence_collection.add(
                embeddings=batch_embeddings,
                documents=batch_metinler,
                ids=batch_ids
            )
            
            print(f"  📦 {end_idx}/{len(metinler)} cümle işlendi...")
        
        print(f"✅ Cümle koleksiyonu tamamlandı: {sentence_collection.count()} kayıt")
        return True
        
    except Exception as e:
        print(f"❌ {model_id} koleksiyonları oluşturulurken hata: {e}")
        return False

def verify_database():
    """Veritabanını doğrula"""
    print("\n🔍 VERİTABANI DOĞRULAMA")
    print("=" * 50)
    
    try:
        client = chromadb.PersistentClient(path="db")
        
        # Koleksiyonları kontrol et
        collections = client.list_collections()
        print(f"📋 Bulunan koleksiyonlar: {len(collections)}")
        
        model_stats = {}
        for collection_info in collections:
            collection = client.get_collection(collection_info.name)
            count = collection.count()
            print(f"  • {collection_info.name}: {count} kayıt")
            
            # Model istatistiklerini topla
            for model_id in SUPPORTED_MODELS.keys():
                if model_id in collection_info.name:
                    if model_id not in model_stats:
                        model_stats[model_id] = {'words': 0, 'sentences': 0}
                    if 'kelime' in collection_info.name:
                        model_stats[model_id]['words'] = count
                    elif 'metin' in collection_info.name:
                        model_stats[model_id]['sentences'] = count
        
        # Model bazlı istatistikler
        print(f"\n📊 MODEL İSTATİSTİKLERİ:")
        for model_id, stats in model_stats.items():
            model_name = SUPPORTED_MODELS.get(model_id, "Unknown")
            print(f"  🤖 {model_name} ({model_id}):")
            print(f"     - Kelimeler: {stats['words']}")
            print(f"     - Cümleler: {stats['sentences']}")
        
        # Test araması yap
        print(f"\n🧪 TEST ARAMALARI:")
        for model_id in SUPPORTED_MODELS.keys():
            try:
                word_collection = client.get_collection(f"kelime_vektorleri_{model_id}")
                sentence_collection = client.get_collection(f"metin_vektorleri_{model_id}")
                
                # Test queries
                word_results = word_collection.query(query_texts=["test"], n_results=3)
                sentence_results = sentence_collection.query(query_texts=["test cümlesi"], n_results=3)
                
                print(f"  ✅ {model_id}: Kelime={len(word_results['documents'][0])}, Cümle={len(sentence_results['documents'][0])}")
                
            except Exception as e:
                print(f"  ❌ {model_id}: Test başarısız - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı doğrulama hatası: {e}")
        return False

def main():
    print("🎯 Multi-Model ChromaDB Database Rebuild")
    print("=" * 60)
    print(f"🤖 Desteklenen modeller: {len(SUPPORTED_MODELS)}")
    for model_id, model_name in SUPPORTED_MODELS.items():
        print(f"   • {model_id}: {model_name}")
    print("=" * 60)
    
    total_start_time = time.time()
    
    # Dosyaları kontrol et
    if not check_files():
        print("❌ Gerekli dosyalar eksik. İşlem sonlandırılıyor.")
        return False
    
    # Veritabanını temizle
    clear_database()
    
    # Verileri yükle
    print("\n📖 TEMEL VERİLER YÜKLENİYOR")
    print("=" * 40)
    
    with open("kelimeler.txt", "r", encoding="utf-8") as f:
        kelimeler = [line.strip() for line in f if line.strip()]
    
    with open("metinler.txt", "r", encoding="utf-8") as f:
        metinler = [line.strip() for line in f if line.strip()]
    
    print(f"📊 Yüklenen veri:")
    print(f"   • Kelimeler: {len(kelimeler)}")
    print(f"   • Cümleler: {len(metinler)}")
    
    # Her model için işlemleri yap
    successful_models = []
    failed_models = []
    
    for model_id, model_name in SUPPORTED_MODELS.items():
        print(f"\n{'='*60}")
        print(f"🚀 {model_id.upper()} MODELİ İŞLENİYOR")
        print(f"{'='*60}")
        
        model_start_time = time.time()
        
        # Vektörleri oluştur
        kelime_vektorleri, metin_vektorleri, success = create_vectors_for_model(
            model_id, model_name, kelimeler, metinler
        )
        
        if not success:
            failed_models.append(model_id)
            print(f"❌ {model_id} modeli başarısız oldu, atlanıyor...")
            continue
        
        # Koleksiyonları oluştur
        if rebuild_collections_for_model(model_id, kelimeler, metinler, kelime_vektorleri, metin_vektorleri):
            model_end_time = time.time()
            model_duration = model_end_time - model_start_time
            successful_models.append(model_id)
            print(f"✅ {model_id} modeli tamamlandı: {model_duration:.2f} saniye")
        else:
            failed_models.append(model_id)
            print(f"❌ {model_id} koleksiyonları oluşturulamadı")
    
    # Final verification
    print(f"\n{'='*60}")
    if successful_models:
        verify_database()
    
    # Özet rapor
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    print(f"\n🏁 İŞLEM TAMAMLANDI")
    print(f"{'='*40}")
    print(f"⏱️  Toplam süre: {total_duration:.2f} saniye")
    print(f"✅ Başarılı modeller: {len(successful_models)} - {successful_models}")
    print(f"❌ Başarısız modeller: {len(failed_models)} - {failed_models}")
    
    if successful_models:
        print(f"\n🎉 Multi-model veritabanı başarıyla oluşturuldu!")
        print(f"🚀 Flask uygulamasını başlatabilirsiniz: python app.py")
        return True
    else:
        print(f"\n💥 Hiçbir model başarıyla yüklenemedi!")
        return False

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