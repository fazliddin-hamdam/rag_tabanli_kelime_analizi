# vector_query.py
import os
import sys
import chromadb
from sentence_transformers import SentenceTransformer

# -------------------------------
# Sabitler ve Hazırlıklar
# -------------------------------

# Proje dizininde 'db/' klasörü oluşturulur
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

# -------------------------------
# ChromaDB PersistentClient Kurulumu
# -------------------------------

try:
    client = chromadb.PersistentClient(path=DB_DIR)
except Exception as e:
    print(f"[HATA] ChromaDB istemcisi başlatılamadı: {e}")
    sys.exit(1)

# Koleksiyonu al veya oluştur
try:
    collection = client.get_or_create_collection("kelime_vektorleri")
except Exception as e:
    print(f"[HATA] ChromaDB koleksiyonu alınamadı: {e}")
    sys.exit(1)

# -------------------------------
# Embedding Modeli Kurulumu
# -------------------------------

try:
    model = SentenceTransformer("dbmdz/bert-base-turkish-cased")
except Exception as e:
    print(f"[HATA] Embedding modeli yüklenemedi: {e}")
    sys.exit(1)

# -------------------------------
# Fonksiyonlar
# -------------------------------

def query_nearest(word: str, k: int = 5):
    """
    Verilen kelime için en yakın k komşuyu döndürür.
    Returns: (neighbors: List[str], distances: List[float])
    """
    try:
        vec = model.encode([word])[0].tolist()
        results = collection.query(
            query_embeddings=[vec],
            n_results=k
        )
        neighbors = results['documents'][0]
        distances = results['distances'][0]
        return neighbors, distances
    except Exception as e:
        print(f"[HATA] Sorgulama sırasında hata: {e}")
        return [], []

# -------------------------------
# Modül Testi
# -------------------------------

if __name__ == "__main__":
    try:
        count = collection.count()
        print(f"Kayıtlı kelime sayısı: {count}")
        if count == 0:
            print("Veritabanınız boş. Lütfen önce vektörleri yükleyin ve ekleyin!")
        else:
            test_word = "kitap"
            nbrs, dists = query_nearest(test_word, k=5)
            if not nbrs:
                print("Hiçbir sonuç bulunamadı.")
            else:
                print(f"\n'{test_word}' için komşular ve mesafeleri:")
                for w, dist in zip(nbrs, dists):
                    print(f"  {w:15} → {dist:.4f}")
    except Exception as e:
        print(f"[HATA] Test sırasında hata oluştu: {e}")

