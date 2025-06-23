# metin_arama.py
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sys

# -------------------------------
# Model ve Veriler
# -------------------------------

def load_model_and_data():
    """Model ve metin verilerini yükle"""
    try:
        # Model yükleme
        print("📡 BERT Turkish modeli yükleniyor...")
        model = SentenceTransformer("dbmdz/bert-base-turkish-cased")
        
        # Metinleri yükleme
        print("📚 Metinler dosyası okunuyor...")
        with open("metinler.txt", "r", encoding="utf-8") as f:
            metinler = [line.strip() for line in f if line.strip()]
        
        # Vektörleri yükleme
        print("🔢 Metin vektörleri yükleniyor...")
        metin_vektorleri = np.load("metin_vektorleri.npy")
        
        print(f"✅ Yükleme tamamlandı!")
        print(f"📊 Toplam cümle sayısı: {len(metinler)}")
        print(f"🧮 Vektör boyutu: {metin_vektorleri.shape}")
        
        return model, metinler, metin_vektorleri
        
    except FileNotFoundError as e:
        print(f"❌ Dosya bulunamadı: {e}")
        print("💡 Önce metin vektörlerini oluşturun!")
        return None, None, None
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        return None, None, None

def search_similar_sentences(query, model, metinler, metin_vektorleri, top_k=5):
    """Verilen sorgu için en benzer cümleleri bul"""
    try:
        # Sorgu vektörü oluştur
        print(f"🔍 '{query}' için arama yapılıyor...")
        query_vector = model.encode([query])
        
        # Benzerlik hesapla
        similarities = cosine_similarity(query_vector, metin_vektorleri)[0]
        
        # En benzer cümleleri bul
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            sentence = metinler[idx]
            similarity = similarities[idx]
            results.append({
                'rank': i + 1,
                'sentence': sentence,
                'similarity': similarity,
                'index': idx
            })
        
        return results
        
    except Exception as e:
        print(f"❌ Arama sırasında hata: {e}")
        return []

def display_results(query, results):
    """Arama sonuçlarını göster"""
    print(f"\n🎯 '{query}' araması için sonuçlar:")
    print("=" * 80)
    
    if not results:
        print("❌ Sonuç bulunamadı!")
        return
    
    for result in results:
        similarity_percentage = result['similarity'] * 100
        print(f"\n{result['rank']}. 📍 Benzerlik: {similarity_percentage:.1f}%")
        print(f"   📝 Cümle: {result['sentence']}")
        print(f"   🔢 İndeks: {result['index']}")
    
    print("\n" + "=" * 80)

def interactive_search():
    """Etkileşimli arama modu"""
    # Model ve verileri yükle
    model, metinler, metin_vektorleri = load_model_and_data()
    
    if model is None:
        return
    
    print("\n🚀 METİN ARAMA SİSTEMİ HAZIR!")
    print("💡 Aranacak kelime veya cümleyi yazın (çıkmak için 'q' yazın)")
    print("📌 Örnek aramalar: 'okul', 'mutluluk', 'yemek yapmak', 'arkadaş'")
    
    while True:
        print("\n" + "-" * 50)
        query = input("🔍 Arama: ").strip()
        
        if query.lower() in ['q', 'quit', 'çık', 'exit']:
            print("👋 Görüşmek üzere!")
            break
        
        if not query:
            print("⚠️  Lütfen bir arama terimi girin!")
            continue
        
        # Arama yap
        results = search_similar_sentences(query, model, metinler, metin_vektorleri, top_k=5)
        
        # Sonuçları göster
        display_results(query, results)

def quick_search(query, top_k=5):
    """Hızlı arama (tek seferlik)"""
    model, metinler, metin_vektorleri = load_model_and_data()
    
    if model is None:
        return []
    
    results = search_similar_sentences(query, model, metinler, metin_vektorleri, top_k)
    display_results(query, results)
    return results

# -------------------------------
# Ana Program
# -------------------------------

if __name__ == "__main__":
    print("🎯 TÜRKÇe METİN ARAMA SİSTEMİ")
    print("🔥 1000+ Cümle İçinde Semantik Arama")
    print("🤖 BERT Turkish Model ile Desteklenir")
    
    # Komut satırı argümanı kontrolü
    if len(sys.argv) > 1:
        # Komut satırından arama
        search_term = " ".join(sys.argv[1:])
        print(f"\n🚀 Komut satırı araması: '{search_term}'")
        quick_search(search_term)
    else:
        # Etkileşimli mod
        interactive_search() 