import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

# Vektör ve kelime dosyalarını yükle
kelime_vektorleri = np.load("kelime_vektorleri.npy")
with open("kelimeler.txt", encoding="utf-8") as f:
    kelimeler = [line.strip() for line in f if line.strip()]

# İlk 50 kelimeyle örnekleyelim (daha fazlası RAM ve GPU kullanır)
N = min(50, len(kelimeler))
X = kelime_vektorleri[:N]
labels = kelimeler[:N]

# t-SNE ile 2 boyuta indir
tsne = TSNE(n_components=2, random_state=42)
X_2d = tsne.fit_transform(X)

plt.figure(figsize=(12, 8))
plt.scatter(X_2d[:, 0], X_2d[:, 1], alpha=0.6)

for i, label in enumerate(labels):
    plt.annotate(label, (X_2d[i, 0], X_2d[i, 1]), fontsize=10, alpha=0.8)

plt.title("Kelime Vektörlerinin t-SNE ile Görselleştirilmesi")
plt.xlabel("Boyut 1")
plt.ylabel("Boyut 2")
plt.tight_layout()
plt.show()
