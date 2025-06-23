# vektor_veritabani.py

import os
import numpy as np
import chromadb

# 1) Kalıcı DB yolunu ayarla
BASE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

# 2) PersistentClient ile bağlantı
client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection("kelime_vektorleri")

# 3) Kelimeleri ve vektörleri yükle
kelimeler = [l.strip() for l in open("kelimeler.txt", encoding="utf-8") if l.strip()]
kelime_vektorleri = np.load("kelime_vektorleri.npy")

# 4) Varolan kayıtları sil (isteğe bağlı, tekrar eklemede önerilir)
try:
    ids = [str(i) for i in range(len(kelimeler))]
    collection.delete(ids=ids)
except Exception:
    pass

# 5) Toplu ekleme (batch)
for i, (kelime, vektor) in enumerate(zip(kelimeler, kelime_vektorleri)):
    collection.add(
        embeddings=[vektor.tolist()],
        documents=[kelime],
        ids=[str(i)]
    )

print(f"{len(kelimeler)} kelime başarıyla ChromaDB'ye yüklendi.")
