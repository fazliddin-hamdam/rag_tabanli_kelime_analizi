# app_langchain.py - Langchain ve ChromaDB ile Gelişmiş Semantik Arama

from flask import Flask, render_template, request, jsonify
import os
from langchain_arama import TurkishSemanticSearch

app = Flask(__name__)

# Global arama sistemi
search_system = None
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

def init_search_system():
    """Arama sistemini başlat"""
    global search_system
    
    try:
        print("🚀 Langchain Semantik Arama Sistemi Başlatılıyor...")
        
        # Arama sistemini oluştur
        search_system = TurkishSemanticSearch()
        
        # Vektör depolarını kur
        search_system.setup_word_vectorstore()
        search_system.setup_sentence_vectorstore()
        
        # İlişkileri yükle
        load_relationships()
        
        # İstatistikleri göster
        stats = search_system.get_stats()
        print(f"📊 Sistem İstatistikleri:")
        print(f"   🔤 Kelime sayısı: {stats['words_count']}")
        print(f"   📚 Cümle sayısı: {stats['sentences_count']}")
        print(f"   🧠 Model: {stats['embedding_model']}")
        print(f"   💾 Veritabanı: {stats['db_path']}")
        print(f"   🔗 İlişki sayısı: {len(iliskiler) if iliskiler else 0}")
        
        print("✅ Langchain Semantik Arama Sistemi Hazır!")
        return True
        
    except Exception as e:
        print(f"❌ Sistem başlatma hatası: {e}")
        return False

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Gelişmiş arama endpoint'i"""
    global search_system
    
    if not search_system:
        return jsonify({'error': 'Arama sistemi hazır değil!'})
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'sentences')  # 'sentences' veya 'words'
        top_k = data.get('top_k', 5)  # Varsayılan 5 sonuç
        
        if not query:
            return jsonify({'error': 'Arama terimi gerekli!'})
        
        if search_type == 'sentences':
            # Cümlelerde arama
            results = search_system.search_sentences(query, k=top_k)
            stats = search_system.get_stats()
            
            return jsonify({
                'query': query,
                'type': 'sentences',
                'results': results,
                'total_data': stats['sentences_count'],
                'search_method': 'langchain_chromadb',
                'model': stats['embedding_model']
            })
        else:
            # Kelimelerde arama
            results = search_system.search_words(query, k=top_k)
            stats = search_system.get_stats()
            
            return jsonify({
                'query': query,
                'type': 'words',
                'results': results,
                'total_data': stats['words_count'],
                'search_method': 'langchain_chromadb',
                'model': stats['embedding_model']
            })
            
    except Exception as e:
        return jsonify({'error': f'Arama hatası: {str(e)}'})

@app.route('/hybrid_search', methods=['POST'])
def hybrid_search():
    """Hibrit arama - hem kelime hem cümle araması"""
    global search_system
    
    if not search_system:
        return jsonify({'error': 'Arama sistemi hazır değil!'})
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 3)  # Her kategoriden 3 sonuç
        
        if not query:
            return jsonify({'error': 'Arama terimi gerekli!'})
        
        # Paralel arama
        word_results = search_system.search_words(query, k=top_k)
        sentence_results = search_system.search_sentences(query, k=top_k)
        
        stats = search_system.get_stats()
        
        return jsonify({
            'query': query,
            'type': 'hybrid',
            'word_results': word_results,
            'sentence_results': sentence_results,
            'stats': {
                'words_count': stats['words_count'],
                'sentences_count': stats['sentences_count']
            },
            'search_method': 'langchain_chromadb_hybrid',
            'model': stats['embedding_model']
        })
        
    except Exception as e:
        return jsonify({'error': f'Hibrit arama hatası: {str(e)}'})

@app.route('/relationships/<word>')
def get_relationships(word):
    """Kelime ilişkilerini getir"""
    try:
        word_lower = word.lower()
        relationships = iliskiler.get(word_lower, {}) if iliskiler else {}
        
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

@app.route('/similar_words/<word>')
def get_similar_words(word, k=5):
    """Benzer kelimeleri getir"""
    global search_system
    
    if not search_system:
        return jsonify({'error': 'Arama sistemi hazır değil!'})
    
    try:
        results = search_system.search_words(word, k=k)
        
        return jsonify({
            'query_word': word,
            'similar_words': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Benzer kelime arama hatası: {str(e)}'})

@app.route('/stats')
def stats():
    """Detaylı sistem istatistikleri"""
    global search_system
    
    if not search_system:
        return jsonify({'error': 'Arama sistemi hazır değil!'})
    
    try:
        system_stats = search_system.get_stats()
        
        return jsonify({
            'system_status': 'ready',
            'search_method': 'langchain_chromadb',
            'sentences_count': system_stats['sentences_count'],
            'words_count': system_stats['words_count'],
            'relationships_count': len(iliskiler) if iliskiler else 0,
            'embedding_model': system_stats['embedding_model'],
            'database_path': system_stats['db_path'],
            'langchain_enabled': True,
            'chromadb_enabled': True
        })
        
    except Exception as e:
        return jsonify({'error': f'İstatistik hatası: {str(e)}'})

@app.route('/health')
def health():
    """Sistem sağlık kontrolü"""
    global search_system
    
    health_status = {
        'status': 'healthy' if search_system else 'unhealthy',
        'search_system_ready': search_system is not None,
        'relationships_loaded': iliskiler is not None,
        'timestamp': int(__import__('time').time())
    }
    
    if search_system:
        try:
            stats = search_system.get_stats()
            health_status['data_available'] = {
                'words': stats['words_count'] > 0,
                'sentences': stats['sentences_count'] > 0
            }
        except:
            health_status['data_available'] = {
                'words': False,
                'sentences': False
            }
    
    return jsonify(health_status)

if __name__ == '__main__':
    print("🚀 Langchain Tabanlı Flask Uygulaması Başlatılıyor...")
    
    # Arama sistemini başlat
    if init_search_system():
        print("🎯 Gelişmiş Semantik Arama Sistemi Hazır!")
        print("🔍 Özellikler:")
        print("   ✅ Langchain entegrasyonu")
        print("   ✅ ChromaDB vektör veritabanı")
        print("   ✅ Türkçe BERT modeli")
        print("   ✅ Hibrit arama (kelime + cümle)")
        print("   ✅ İlişkisel kelime analizi")
        print("   ✅ RESTful API")
        
        app.run(debug=True, host='0.0.0.0', port=5002)
    else:
        print("❌ Sistem başlatılamadı!")
        print("💡 Gerekli veri dosyalarını ve ChromaDB'yi kontrol edin.") 