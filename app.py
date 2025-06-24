# app.py
from flask import Flask, render_template, request, jsonify
import os
import chromadb
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# ChromaDB setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")

# Global değişkenler
model = None
client = None
word_collection = None
sentence_collection = None
metinler = None
kelimeler = None
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

def setup_chromadb():
    """ChromaDB bağlantısını kur"""
    global client, word_collection, sentence_collection
    
    try:
        # ChromaDB client oluştur
        client = chromadb.PersistentClient(path=DB_DIR)
        
        # Koleksiyonları cosine distance ile al/oluştur
        word_collection = client.get_or_create_collection(
            "kelime_vektorleri",
            metadata={"hnsw:space": "cosine"}  # Cosine distance kullan
        )
        sentence_collection = client.get_or_create_collection(
            "metin_vektorleri",
            metadata={"hnsw:space": "cosine"}  # Cosine distance kullan
        )
        
        print(f"✅ ChromaDB bağlantısı kuruldu (Cosine distance)")
        print(f"🔤 Kelime sayısı: {word_collection.count()}")
        print(f"📚 Cümle sayısı: {sentence_collection.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB bağlantı hatası: {e}")
        return False

def load_text_data():
    """Metin verilerini yükle (sadece dosyalardan okuma için)"""
    global metinler, kelimeler
    
    try:
        # Metinleri yükleme
        if os.path.exists("metinler.txt"):
            with open("metinler.txt", "r", encoding="utf-8") as f:
                metinler = [line.strip() for line in f if line.strip()]
        
        # Kelimeleri yükleme
        if os.path.exists("kelimeler.txt"):
            with open("kelimeler.txt", "r", encoding="utf-8") as f:
                kelimeler = [line.strip() for line in f if line.strip()]
        
        return True
        
    except Exception as e:
        print(f"❌ Metin veri yükleme hatası: {e}")
        return False

def load_data():
    """Tüm verileri ve bağlantıları yükle"""
    global model
    
    try:
        print("📡 Model ve veriler yükleniyor...")
        
        # Model yükleme
        model = SentenceTransformer("dbmdz/bert-base-turkish-cased")
        
        # ChromaDB setup
        if not setup_chromadb():
            return False
        
        # Text data yükle
        if not load_text_data():
            return False
        
        # İlişkileri yükle
        load_relationships()
        
        print(f"✅ Yükleme tamamlandı!")
        
        return True
        
    except Exception as e:
        print(f"❌ Veri yükleme hatası: {e}")
        return False

def search_in_sentences(query, top_k=5):
    """ChromaDB kullanarak cümlelerde arama"""
    if model is None or sentence_collection is None:
        return []
    
    try:
        # Sorgu vektörü oluştur
        query_vector = model.encode([query])[0].tolist()
        
        # ChromaDB'de arama yap
        results = sentence_collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, sentence_collection.count())
        )
        
        # Sonuçları formatla
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            distances = results['distances'][0]
            ids = results['ids'][0]
            
            for i, (doc, distance, doc_id) in enumerate(zip(documents, distances, ids)):
                # Cosine distance'ı cosine similarity'ye çevir
                # Cosine distance = 1 - cosine similarity
                # Bu yüzden: cosine similarity = 1 - cosine distance
                similarity = max(0, 1 - distance)
                
                formatted_results.append({
                    'rank': i + 1,
                    'sentence': doc,
                    'similarity': similarity,
                    'similarity_percent': round(similarity * 100, 1),
                    'index': int(doc_id)
                })
        
        return formatted_results
        
    except Exception as e:
        print(f"❌ Cümle arama hatası: {e}")
        return []

def search_in_words(query, top_k=5):
    """ChromaDB kullanarak kelimelerde arama"""
    if model is None or word_collection is None:
        return []
    
    try:
        # Sorgu vektörü oluştur
        query_vector = model.encode([query])[0].tolist()
        
        # ChromaDB'de arama yap
        results = word_collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, word_collection.count())
        )
        
        # Sonuçları formatla
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            distances = results['distances'][0]
            ids = results['ids'][0]
            
            for i, (doc, distance, doc_id) in enumerate(zip(documents, distances, ids)):
                # Cosine distance'ı cosine similarity'ye çevir
                # Cosine distance = 1 - cosine similarity
                # Bu yüzden: cosine similarity = 1 - cosine distance
                similarity = max(0, 1 - distance)
                
                formatted_results.append({
                    'rank': i + 1,
                    'word': doc,
                    'similarity': similarity,
                    'similarity_percent': round(similarity * 100, 1),
                    'index': int(doc_id)
                })
        
        return formatted_results
        
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
            total_data = sentence_collection.count() if sentence_collection else 0
            return jsonify({
                'query': query,
                'type': 'sentences',
                'results': results,
                'total_data': total_data
            })
        else:
            results = search_in_words(query, top_k=5)
            total_data = word_collection.count() if word_collection else 0
            return jsonify({
                'query': query,
                'type': 'words',
                'results': results,
                'total_data': total_data
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
        'sentences_count': sentence_collection.count() if sentence_collection else 0,
        'words_count': word_collection.count() if word_collection else 0,
        'relationships_count': len(iliskiler) if iliskiler else 0,
        'model_loaded': model is not None,
        'chromadb_connected': client is not None,
        'sentence_collection_ready': sentence_collection is not None,
        'word_collection_ready': word_collection is not None
    })

if __name__ == '__main__':
    print("🚀 Flask Uygulaması Başlatılıyor...")
    
    # Verileri yükle
    if load_data():
        print("🎯 ChromaDB Tabanlı Semantik Arama Sistemi Hazır!")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        print("❌ Veri yüklenemedi, uygulama başlatılamıyor!")
