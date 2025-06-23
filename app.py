# app.py
from flask import Flask, render_template, request, jsonify
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)

# Global değişkenler
model = None
metinler = None
metin_vektorleri = None
kelimeler = None
kelime_vektorleri = None
iliskiler = None

def load_relationships():
    """Kelime ilişkilerini yükle"""
    global iliskiler
    iliskiler = {}
    
    try:
        if os.path.exists("iliskiler.txt"):
            with open("iliskiler.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    
                    parts = line.split("|")
                    if len(parts) < 2:
                        continue
                        
                    word = parts[0].strip().lower()
                    relationships = {}
                    
                    for part in parts[1:]:
                        if ":" in part:
                            rel_type, values = part.split(":", 1)
                            rel_type = rel_type.strip()
                            values_list = [v.strip() for v in values.split(",") if v.strip()]
                            relationships[rel_type] = values_list
                    
                    iliskiler[word] = relationships
        
        print(f"📚 İlişkiler yüklendi: {len(iliskiler)} kelime")
        return True
        
    except Exception as e:
        print(f"❌ İlişki yükleme hatası: {e}")
        return False

def load_data():
    """Tüm verileri yükle"""
    global model, metinler, metin_vektorleri, kelimeler, kelime_vektorleri
    
    try:
        print("📡 Model ve veriler yükleniyor...")
        
        # Model yükleme
        model = SentenceTransformer("dbmdz/bert-base-turkish-cased")
        
        # İlişkileri yükle
        load_relationships()
        
        # Metinleri yükleme
        if os.path.exists("metinler.txt"):
            with open("metinler.txt", "r", encoding="utf-8") as f:
                metinler = [line.strip() for line in f if line.strip()]
        
        # Kelimeleri yükleme
        if os.path.exists("kelimeler.txt"):
            with open("kelimeler.txt", "r", encoding="utf-8") as f:
                kelimeler = [line.strip() for line in f if line.strip()]
        
        # Vektörleri yükleme
        if os.path.exists("metin_vektorleri.npy"):
            metin_vektorleri = np.load("metin_vektorleri.npy")
            
        if os.path.exists("kelime_vektorleri.npy"):
            kelime_vektorleri = np.load("kelime_vektorleri.npy")
        
        print(f"✅ Yükleme tamamlandı!")
        if metinler:
            print(f"📚 Toplam cümle: {len(metinler)}")
        if kelimeler:
            print(f"🔤 Toplam kelime: {len(kelimeler)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Veri yükleme hatası: {e}")
        return False

def search_in_sentences(query, top_k=5):
    """Cümleler içinde arama"""
    if model is None or metinler is None or metin_vektorleri is None:
        return []
    
    try:
        # Sorgu vektörü oluştur
        query_vector = model.encode([query])
        
        # Benzerlik hesapla
        similarities = cosine_similarity(query_vector, metin_vektorleri)[0]
        
        # En benzer cümleleri bul
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            sentence = metinler[idx]
            similarity = float(similarities[idx])  # NumPy float32'yi Python float'a çevir
            results.append({
                'rank': i + 1,
                'sentence': sentence,
                'similarity': similarity,
                'similarity_percent': round(similarity * 100, 1),
                'index': int(idx)
            })
        
        return results
        
    except Exception as e:
        print(f"❌ Cümle arama hatası: {e}")
        return []

def search_in_words(query, top_k=5):
    """Kelimeler içinde arama"""
    if model is None or kelimeler is None or kelime_vektorleri is None:
        return []
    
    try:
        # Sorgu vektörü oluştur
        query_vector = model.encode([query])
        
        # Benzerlik hesapla
        similarities = cosine_similarity(query_vector, kelime_vektorleri)[0]
        
        # En benzer kelimeleri bul
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            word = kelimeler[idx]
            similarity = float(similarities[idx])  # NumPy float32'yi Python float'a çevir
            results.append({
                'rank': i + 1,
                'word': word,
                'similarity': similarity,
                'similarity_percent': round(similarity * 100, 1),
                'index': int(idx)
            })
        
        return results
        
    except Exception as e:
        print(f"❌ Kelime arama hatası: {e}")
        return []

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Arama endpoint'i"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'sentences')  # 'sentences' veya 'words'
        
        if not query:
            return jsonify({'error': 'Arama terimi gerekli!'})
        
        if search_type == 'sentences':
            results = search_in_sentences(query, top_k=5)
            return jsonify({
                'query': query,
                'type': 'sentences',
                'results': results,
                'total_data': len(metinler) if metinler else 0
            })
        else:
            results = search_in_words(query, top_k=5)
            return jsonify({
                'query': query,
                'type': 'words',
                'results': results,
                'total_data': len(kelimeler) if kelimeler else 0
            })
            
    except Exception as e:
        return jsonify({'error': f'Arama hatası: {str(e)}'})

@app.route('/relationships/<word>')
def get_relationships(word):
    """Kelime ilişkilerini getir"""
    try:
        word_lower = word.lower()
        relationships = iliskiler.get(word_lower, {})
        
        if not relationships:
            return jsonify({
                'word': word,
                'found': False,
                'message': f'"{word}" kelimesi için ilişki bilgisi bulunamadı.'
            })
        
        return jsonify({
            'word': word,
            'found': True,
            'relationships': {
                'hiperonim': relationships.get('hiperonim', []),
                'hiponim': relationships.get('hiponim', []), 
                'meronim': relationships.get('meronim', [])
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'İlişki getirme hatası: {str(e)}'})

@app.route('/stats')
def stats():
    """İstatistikler"""
    return jsonify({
        'sentences_count': len(metinler) if metinler else 0,
        'words_count': len(kelimeler) if kelimeler else 0,
        'relationships_count': len(iliskiler) if iliskiler else 0,
        'model_loaded': model is not None,
        'sentence_vectors_loaded': metin_vektorleri is not None,
        'word_vectors_loaded': kelime_vektorleri is not None
    })

if __name__ == '__main__':
    print("🚀 Flask Uygulaması Başlatılıyor...")
    
    # Verileri yükle
    if load_data():
        print("🎯 Semantik Arama Sistemi Hazır!")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        print("❌ Veri yüklenemedi, uygulama başlatılamıyor!")
