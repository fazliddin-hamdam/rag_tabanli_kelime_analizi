# langchain_arama.py

import os
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from sentence_transformers import SentenceTransformer

class TurkishSemanticSearch:
    """Langchain ve ChromaDB kullanarak Türkçe semantik arama sistemi"""
    
    def __init__(self, db_path="./db"):
        self.db_path = db_path
        self.embedding_model_name = "dbmdz/bert-base-turkish-cased"
        self.embeddings = None
        self.word_vectorstore = None
        self.sentence_vectorstore = None
        self._setup_embeddings()
    
    def _setup_embeddings(self):
        """Embedding modelini hazırla"""
        try:
            # HuggingFace embeddings with Turkish BERT model
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ Langchain embedding modeli hazırlandı")
        except Exception as e:
            print(f"❌ Embedding modeli hatası: {e}")
            raise e
    
    def setup_word_vectorstore(self):
        """Kelime vektör deposunu kur"""
        try:
            # ChromaDB client
            client = chromadb.PersistentClient(path=self.db_path)
            
            # Langchain ile Chroma vectorstore
            self.word_vectorstore = Chroma(
                client=client,
                collection_name="kelime_vektorleri_langchain",
                embedding_function=self.embeddings,
                persist_directory=self.db_path
            )
            print("✅ Kelime vektör deposu hazır")
            return True
            
        except Exception as e:
            print(f"❌ Kelime vektör deposu hatası: {e}")
            return False
    
    def setup_sentence_vectorstore(self):
        """Cümle vektör deposunu kur"""
        try:
            # ChromaDB client
            client = chromadb.PersistentClient(path=self.db_path)
            
            # Langchain ile Chroma vectorstore
            self.sentence_vectorstore = Chroma(
                client=client,
                collection_name="metin_vektorleri_langchain",
                embedding_function=self.embeddings,
                persist_directory=self.db_path
            )
            print("✅ Cümle vektör deposu hazır")
            return True
            
        except Exception as e:
            print(f"❌ Cümle vektör deposu hatası: {e}")
            return False
    
    def add_words_to_vectorstore(self, words_file="kelimeler.txt"):
        """Kelimeleri vektör deposuna ekle"""
        if not self.word_vectorstore:
            self.setup_word_vectorstore()
        
        try:
            # Kelimeleri yükle
            with open(words_file, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
            
            # Document objelerini oluştur
            documents = [
                Document(
                    page_content=word,
                    metadata={"type": "word", "index": i}
                ) for i, word in enumerate(words)
            ]
            
            # Vektör deposuna ekle
            self.word_vectorstore.add_documents(documents)
            print(f"✅ {len(words)} kelime vektör deposuna eklendi")
            return True
            
        except Exception as e:
            print(f"❌ Kelime ekleme hatası: {e}")
            return False
    
    def add_sentences_to_vectorstore(self, sentences_file="metinler.txt"):
        """Cümleleri vektör deposuna ekle"""
        if not self.sentence_vectorstore:
            self.setup_sentence_vectorstore()
        
        try:
            # Cümleleri yükle
            with open(sentences_file, "r", encoding="utf-8") as f:
                sentences = [line.strip() for line in f if line.strip()]
            
            # Document objelerini oluştur
            documents = [
                Document(
                    page_content=sentence,
                    metadata={"type": "sentence", "index": i}
                ) for i, sentence in enumerate(sentences)
            ]
            
            # Batch olarak ekle
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                self.sentence_vectorstore.add_documents(batch)
                print(f"  📦 {min(i+batch_size, len(documents))}/{len(documents)} cümle işlendi...")
            
            print(f"✅ {len(sentences)} cümle vektör deposuna eklendi")
            return True
            
        except Exception as e:
            print(f"❌ Cümle ekleme hatası: {e}")
            return False
    
    def search_words(self, query, k=5):
        """Kelimelerde arama yap"""
        if not self.word_vectorstore:
            return []
        
        try:
            # Similarity search
            results = self.word_vectorstore.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for i, (doc, score) in enumerate(results):
                # Score'u similarity'ye çevir (1 - score, çünkü düşük score = yüksek benzerlik)
                similarity = max(0, 1 - score)
                
                formatted_results.append({
                    'rank': i + 1,
                    'word': doc.page_content,
                    'similarity': similarity,
                    'similarity_percent': round(similarity * 100, 1),
                    'index': doc.metadata.get('index', i),
                    'score': score
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Kelime arama hatası: {e}")
            return []
    
    def search_sentences(self, query, k=5):
        """Cümlelerde arama yap"""
        if not self.sentence_vectorstore:
            return []
        
        try:
            # Similarity search
            results = self.sentence_vectorstore.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for i, (doc, score) in enumerate(results):
                # Score'u similarity'ye çevir (1 - score, çünkü düşük score = yüksek benzerlik)
                similarity = max(0, 1 - score)
                
                formatted_results.append({
                    'rank': i + 1,
                    'sentence': doc.page_content,
                    'similarity': similarity,
                    'similarity_percent': round(similarity * 100, 1),
                    'index': doc.metadata.get('index', i),
                    'score': score
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Cümle arama hatası: {e}")
            return []
    
    def get_stats(self):
        """İstatistikleri getir"""
        stats = {
            'words_count': 0,
            'sentences_count': 0,
            'embedding_model': self.embedding_model_name,
            'db_path': self.db_path
        }
        
        try:
            if self.word_vectorstore:
                # Koleksiyon sayısını almaya çalış
                word_collection = self.word_vectorstore._collection
                stats['words_count'] = word_collection.count() if word_collection else 0
        except:
            pass
        
        try:
            if self.sentence_vectorstore:
                # Koleksiyon sayısını almaya çalış
                sentence_collection = self.sentence_vectorstore._collection
                stats['sentences_count'] = sentence_collection.count() if sentence_collection else 0
        except:
            pass
        
        return stats

# Test fonksiyonu
def test_langchain_search():
    """Langchain arama sistemini test et"""
    print("🔬 Langchain Arama Sistemi Test Ediliyor...")
    
    # Arama sistemini başlat
    search_system = TurkishSemanticSearch()
    
    # Vektör depolarını kur
    search_system.setup_word_vectorstore()
    search_system.setup_sentence_vectorstore()
    
    # İstatistikleri göster
    stats = search_system.get_stats()
    print(f"📊 İstatistikler: {stats}")
    
    # Test aramaları
    test_queries = ["kitap", "okul", "mutluluk"]
    
    for query in test_queries:
        print(f"\n🔍 '{query}' araması:")
        
        # Kelime araması
        word_results = search_system.search_words(query, k=3)
        print(f"  📝 Kelimeler: {[r['word'] for r in word_results[:3]]}")
        
        # Cümle araması
        sentence_results = search_system.search_sentences(query, k=3)
        print(f"  📚 Cümleler: {[r['sentence'][:50] + '...' for r in sentence_results[:3]]}")

if __name__ == "__main__":
    test_langchain_search() 