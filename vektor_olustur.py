# vektor_olustur.py (bunu zaten kullanıyordun)
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("dbmdz/bert-base-turkish-cased")

with open("kelimeler.txt", encoding="utf-8") as f:
    kelimeler = [line.strip() for line in f if line.strip()]

kelime_vektorleri = model.encode(kelimeler, show_progress_bar=True)
np.save("kelime_vektorleri.npy", kelime_vektorleri)
