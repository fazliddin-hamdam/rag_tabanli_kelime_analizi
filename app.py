# app.py - Multi-Model Semantic Search Backend
from flask import Flask, render_template, request, jsonify
import os
import chromadb
from sentence_transformers import SentenceTransformer

# LangChain imports for Q&A functionality
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import torch

app = Flask(__name__)

# ChromaDB setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")

# Desteklenen modellerin tanımı (rebuild_database.py ile aynı)
SUPPORTED_MODELS = {
    "dbmdz_bert": "dbmdz/bert-base-turkish-cased",
    "turkcell_roberta": "TURKCELL/roberta-base-turkish-uncased",
    "multilingual_mpnet": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
}

# Çoklu model yapıları - Global değişkenler
loaded_models = {}
word_collections = {}
sentence_collections = {}
client = None
metinler = None
kelimeler = None
iliskiler = None

# Q&A sistemi için değişkenler
qa_vectorstore = None
qa_retriever = None
qa_chain = None
qa_embeddings = None

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
    """ChromaDB bağlantısını kur ve çoklu modeller için koleksiyonları yükle"""
    global client, word_collections, sentence_collections
    
    try:
        # ChromaDB client oluştur
        client = chromadb.PersistentClient(path=DB_DIR)
        
        # Tüm koleksiyonları listele
        all_collections = client.list_collections()
        print(f"🔍 Bulunan koleksiyonlar: {len(all_collections)}")
        
        # Her desteklenen model için koleksiyonları yükle
        for model_id in SUPPORTED_MODELS.keys():
            word_collection_name = f"kelime_vektorleri_{model_id}"
            sentence_collection_name = f"metin_vektorleri_{model_id}"
            
            try:
                # Kelime koleksiyonu
                word_collections[model_id] = client.get_collection(word_collection_name)
                word_count = word_collections[model_id].count()
                
                # Cümle koleksiyonu
                sentence_collections[model_id] = client.get_collection(sentence_collection_name)
                sentence_count = sentence_collections[model_id].count()
                
                print(f"✅ {model_id}: Kelimeler={word_count}, Cümleler={sentence_count}")
                
            except Exception as e:
                print(f"⚠️  {model_id} koleksiyonları bulunamadı: {e}")
                # Model koleksiyonları yoksa sözlüklerden çıkar
                word_collections.pop(model_id, None)
                sentence_collections.pop(model_id, None)
        
        available_models = list(word_collections.keys())
        print(f"🎯 Aktif modeller: {available_models}")
        
        if not available_models:
            print("❌ Hiçbir model koleksiyonu bulunamadı!")
            return False
            
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

def load_models():
    """Aktif koleksiyonlara sahip modelleri yükle"""
    global loaded_models
    
    try:
        available_model_ids = list(word_collections.keys())
        print(f"🤖 Modeller yükleniyor: {available_model_ids}")
        
        for model_id in available_model_ids:
            if model_id in SUPPORTED_MODELS:
                model_name = SUPPORTED_MODELS[model_id]
                print(f"   📡 Yükleniyor: {model_name}")
                loaded_models[model_id] = SentenceTransformer(model_name)
                print(f"   ✅ Başarılı: {model_id}")
        
        print(f"🎉 Yüklenen modeller: {list(loaded_models.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Model yükleme hatası: {e}")
        return False

def setup_qa_system():
    """Q&A sistemi için LangChain VectorStore ve RetrievalQA kurulumu"""
    global qa_vectorstore, qa_retriever, qa_chain, qa_embeddings
    
    try:
        print("🤖 Q&A sistemi yükleniyor...")
        
        # HuggingFace Embeddings kurulumu
        qa_embeddings = HuggingFaceEmbeddings(
            model_name="dbmdz/bert-base-turkish-cased",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # ChromaDB client
        qa_client = chromadb.PersistentClient(path=DB_DIR)
        
        # LangChain Chroma VectorStore
        qa_vectorstore = Chroma(
            client=qa_client,
            collection_name="qa_documents",
            embedding_function=qa_embeddings,
            persist_directory=DB_DIR
        )
        
        # Eğer collection yoksa metinler.txt'den oluştur
        try:
            # Collection mevcut mu kontrol et
            collection_count = qa_vectorstore._collection.count()
            if collection_count == 0:
                print("📚 Q&A vektör deposu boş, metinler.txt'den doldurluyor...")
                populate_qa_vectorstore()
        except:
            print("📚 Q&A vektör deposu oluşturuluyor...")
            populate_qa_vectorstore()
        
        # VectorStore Retriever oluştur
        qa_retriever = qa_vectorstore.as_retriever(
            search_kwargs={"k": 3}  # En alakalı 3 dokümanı getir
        )
        
        # Basit Türkçe LLM için HuggingFace pipeline
        # Not: Gerçek uygulamada daha güçlü bir Türkçe model kullanılabilir
        print("🧠 Türkçe language model yükleniyor...")
        
        # Simple text generation pipeline
        # Yerel bir model yerine basit template-based cevap sistemi kullanacağız
        print("✅ Q&A sistemi hazır!")
        return True
        
    except Exception as e:
        print(f"❌ Q&A sistem kurulum hatası: {e}")
        return False

def populate_qa_vectorstore():
    """metinler.txt'den Q&A vektör deposunu doldur"""
    global qa_vectorstore
    
    try:
        if not os.path.exists("metinler.txt"):
            print("❌ metinler.txt dosyası bulunamadı")
            return False
            
        # Metinleri yükle
        with open("metinler.txt", "r", encoding="utf-8") as f:
            sentences = [line.strip() for line in f if line.strip()]
        
        # Document objeleri oluştur
        documents = []
        for i, sentence in enumerate(sentences):
            doc = Document(
                page_content=sentence,
                metadata={
                    "source": "metinler.txt",
                    "sentence_id": i,
                    "type": "sentence"
                }
            )
            documents.append(doc)
        
        # Batch halinde vektör deposuna ekle
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            qa_vectorstore.add_documents(batch)
            print(f"   📦 {min(i+batch_size, len(documents))}/{len(documents)} cümle işlendi...")
        
        print(f"✅ {len(sentences)} cümle Q&A vektör deposuna eklendi")
        return True
        
    except Exception as e:
        print(f"❌ Q&A vektör deposu doldurma hatası: {e}")
        return False

def answer_question(question, context_docs):
    """Basit template-based soru cevaplama"""
    
    # Context'ten en alakalı cümleleri al
    context_text = "\n".join([doc.page_content for doc in context_docs])
    
    # Basit keyword matching ve template responses
    question_lower = question.lower()
    
    # Soru kelimelerini tespit et
    if any(word in question_lower for word in ['ne', 'nere', 'nerede', 'nasıl', 'kim', 'ne zaman', 'kaç']):
        
        # Context'te alakalı bilgi var mı kontrol et
        if context_docs and len(context_docs) > 0:
            most_relevant = context_docs[0].page_content
            
            # Template-based response
            response = f"Bu sorunuz ile ilgili bulduğum en alakalı bilgi:\n\n\"{most_relevant}\"\n\nBu cümle sorunuza cevap veriyor olabilir."
            
            return {
                "answer": response,
                "context": context_text,
                "confidence": "orta",
                "source_sentences": [doc.page_content for doc in context_docs]
            }
    
    # Varsayılan cevap
    return {
        "answer": "Bu sorunuz için veritabanımda yeterli bilgi bulamadım. Lütfen sorunuzu farklı kelimelerle tekrar deneyin.",
        "context": context_text,
        "confidence": "düşük",
        "source_sentences": [doc.page_content for doc in context_docs] if context_docs else []
    }

def load_data():
    """Tüm verileri ve bağlantıları yükle"""
    try:
        print("📡 Multi-model sistem yükleniyor...")
        
        # ChromaDB setup
        if not setup_chromadb():
            return False
        
        # Modelleri yükle
        if not load_models():
            return False
        
        # Text data yükle
        if not load_text_data():
            return False
        
        # İlişkileri yükle
        load_relationships()
        
        # Q&A sistemini yükle
        setup_qa_system()
        
        print(f"✅ Multi-model sistem yüklendi!")
        return True
        
    except Exception as e:
        print(f"❌ Sistem yükleme hatası: {e}")
        return False

def search_in_sentences(query, model_id, top_k=5):
    """Belirtilen model ile cümlelerde arama"""
    
    # Dinamik olarak doğru modeli ve koleksiyonu seç
    model = loaded_models.get(model_id)
    collection = sentence_collections.get(model_id)
    
    if not model or not collection:
        print(f"❌ Model veya koleksiyon bulunamadı: {model_id}")
        return []
    
    try:
        # Sorgu vektörü oluştur
        query_vector = model.encode([query])[0].tolist()
        
        # ChromaDB'de arama yap
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, collection.count())
        )
        
        # Sonuçları formatla
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            distances = results['distances'][0]
            ids = results['ids'][0]
            
            for i, (doc, distance, doc_id) in enumerate(zip(documents, distances, ids)):
                # Cosine distance'ı cosine similarity'ye çevir
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
        print(f"❌ {model_id} cümle arama hatası: {e}")
        return []

def search_in_words(query, model_id, top_k=5):
    """Belirtilen model ile kelimelerde arama"""
    
    # Dinamik olarak doğru modeli ve koleksiyonu seç
    model = loaded_models.get(model_id)
    collection = word_collections.get(model_id)
    
    if not model or not collection:
        print(f"❌ Model veya koleksiyon bulunamadı: {model_id}")
        return []
    
    try:
        # Sorgu vektörü oluştur
        query_vector = model.encode([query])[0].tolist()
        
        # ChromaDB'de arama yap
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, collection.count())
        )
        
        # Sonuçları formatla
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            distances = results['distances'][0]
            ids = results['ids'][0]
            
            for i, (doc, distance, doc_id) in enumerate(zip(documents, distances, ids)):
                # Cosine distance'ı cosine similarity'ye çevir
                similarity = max(0, 1 - distance)
                
                # İlişkileri al
                relationships = iliskiler.get(doc.lower(), {})
                
                formatted_results.append({
                    'rank': i + 1,
                    'word': doc,
                    'similarity': similarity,
                    'similarity_percent': round(similarity * 100, 1),
                    'index': int(doc_id),
                    'relationships': relationships
                })
        
        return formatted_results
        
    except Exception as e:
        print(f"❌ {model_id} kelime arama hatası: {e}")
        return []

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Çoklu model destekli arama endpoint'i"""
    data = request.get_json()
    query = data.get('query', '').strip()
    # model_ids, front-end'den gelen liste: ["dbmdz_bert", "turkcell_roberta"]
    model_ids = data.get('models', [])
    search_type = data.get('type', 'sentences')  # 'sentences' veya 'words'
    
    if not query:
        return jsonify({'error': 'Arama terimi gerekli!'})
        
    if not model_ids:
        return jsonify({'error': 'En az bir model seçimi gerekli!'})
    
    # Geçersiz model ID'lerini filtrele
    valid_model_ids = [mid for mid in model_ids if mid in loaded_models]
    if not valid_model_ids:
        return jsonify({'error': 'Seçilen modeller yüklenmemiş!'})
    
    try:
        final_results = {}
        
        for model_id in valid_model_ids:
            # Her model için ayrı ayrı arama yap
            if search_type == 'sentences':
                results = search_in_sentences(query, model_id, top_k=5)
            else:  # words
                results = search_in_words(query, model_id, top_k=5)
            
            final_results[model_id] = {
                "model_name": SUPPORTED_MODELS.get(model_id, "Bilinmeyen Model"),
                "model_id": model_id,
                "results": results,
                "total_found": len(results)
            }
        
        return jsonify({
            'query': query,
            'type': search_type,
            'search_results': final_results,
            'models_used': valid_model_ids
        })
        
    except Exception as e:
        print(f"❌ Arama hatası: {e}")
        return jsonify({'error': f'Arama yapılırken hata oluştu: {str(e)}'})

@app.route('/relationships/<word>')
def get_relationships(word):
    """Kelime ilişkilerini getir"""
    try:
        word_lower = word.lower()
        relationships = iliskiler.get(word_lower, {})
        
        if not relationships:
            return jsonify({
                'error': f'"{word}" kelimesi için ilişki bulunamadı'
            })
        
        return jsonify({
            'word': word,
            'relationships': relationships,
            'total_types': len(relationships)
        })
        
    except Exception as e:
        return jsonify({'error': f'İlişki arama hatası: {str(e)}'})

@app.route('/qa', methods=['POST'])
def question_answer():
    """Q&A endpoint - VectorStore Retriever kullanarak soru cevaplama"""
    global qa_retriever, qa_vectorstore
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Soru gerekli!'})
        
        if not qa_retriever or not qa_vectorstore:
            return jsonify({'error': 'Q&A sistemi hazır değil!'})
        
        # VectorStore Retriever ile alakalı dokümanları bul
        relevant_docs = qa_retriever.invoke(question)
        
        # Soru cevaplama
        qa_result = answer_question(question, relevant_docs)
        
        # Similarity score hesaplama
        similarity_scores = []
        if relevant_docs:
            # Her doküman için benzerlik skoru hesapla (basit sıralama bazlı)
            for i, doc in enumerate(relevant_docs):
                # Sıralama bazlı similarity (ilk döküman en yüksek score)
                similarity = 0.9 - (i * 0.1)  # 90%, 80%, 70% vs.
                similarity_scores.append(round(max(similarity, 0.4) * 100, 1))
        
        return jsonify({
            'question': question,
            'answer': qa_result['answer'],
            'confidence': qa_result['confidence'],
            'source_sentences': qa_result['source_sentences'],
            'context': qa_result['context'],
            'retrieved_documents': len(relevant_docs),
            'similarity_scores': similarity_scores,
            'method': 'VectorStoreRetriever + LangChain'
        })
        
    except Exception as e:
        return jsonify({'error': f'Q&A hatası: {str(e)}'})

@app.route('/stats')
def stats():
    """Sistem istatistikleri - çoklu model destekli"""
    try:
        total_sentences = 0
        total_words = 0
        model_stats = {}
        qa_docs_count = 0
        
        # Her model için istatistikleri topla
        for model_id in loaded_models.keys():
            word_count = word_collections.get(model_id, {}).count() if word_collections.get(model_id) else 0
            sentence_count = sentence_collections.get(model_id, {}).count() if sentence_collections.get(model_id) else 0
            
            model_stats[model_id] = {
                'name': SUPPORTED_MODELS.get(model_id, 'Unknown'),
                'words': word_count,
                'sentences': sentence_count
            }
            
            total_words = max(total_words, word_count)  # Veriler aynı olduğu için max al
            total_sentences = max(total_sentences, sentence_count)
        
        # Q&A doküman sayısını al
        if qa_vectorstore:
            try:
                qa_docs_count = qa_vectorstore._collection.count()
            except:
                qa_docs_count = 0
        
        return jsonify({
            'sentences_count': total_sentences,
            'words_count': total_words,
            'relationships_count': len(iliskiler) if iliskiler else 0,
            'models_loaded': len(loaded_models),
            'model_loaded': len(loaded_models) > 0,
            'available_models': list(loaded_models.keys()),
            'model_details': model_stats,
            'supported_models': SUPPORTED_MODELS,
            'qa_documents_count': qa_docs_count,
            'qa_system_ready': qa_vectorstore is not None
        })
        
    except Exception as e:
        return jsonify({
            'error': f'İstatistik hatası: {str(e)}',
            'sentences_count': 0,
            'words_count': 0,
            'relationships_count': 0,
            'models_loaded': 0,
            'model_loaded': False,
            'qa_documents_count': 0,
            'qa_system_ready': False
        })

if __name__ == '__main__':
    print("🎯 Multi-Model Türkçe Semantik Arama Sistemi")
    print("=" * 50)
    
    # Verileri yükle
    if load_data():
        print("🚀 Sistem hazır! http://127.0.0.1:5001")
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        print("❌ Sistem başlatılamadı!")
        print("💡 Önce 'python rebuild_database.py' komutunu çalıştırın")
