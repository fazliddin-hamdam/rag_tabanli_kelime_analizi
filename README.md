# 🎯 Turkish RAG-Based Multi-Model Semantic Search System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-yellow.svg)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Latest-orange.svg)](https://chromadb.ai)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

## 📋 Proje Hakkında

Bu proje, **RAG (Retrieval-Augmented Generation)** teknolojisini kullanarak Türkçe dil için geliştirilmiş gelişmiş bir semantik arama sistemidir. Sistem, **çoklu AI modelleri** ile 2000+ kelime ve 1000+ cümle üzerinde karşılaştırmalı arama yapabilme yeteneğine sahiptir.

### 🎯 Ana Özellikler

- **🤖 Çoklu AI Model Desteği**: BERT, RoBERTa ve MPNet modellerle karşılaştırmalı arama
- **📚 Dual Search System**: Hem kelime hem de cümle bazında semantik arama
- **🔗 Word Embeddings**: SentenceTransformers ile yüksek kaliteli vektör temsilleri
- **💾 Vector Database**: ChromaDB ile hızlı ve ölçeklenebilir vektör depolama
- **🌐 Modern Web UI**: Flask tabanlı responsive web arayüzü
- **🧠 Q&A System**: LangChain entegrasyonu ile soru-cevap sistemi
- **🔍 Relationship Analysis**: Kelime ilişkileri (hiperonim, hiponim, meronim) analizi
- **📊 Performance Testing**: Kapsamlı test senaryoları ve raporlama

## 🏗️ Sistem Mimarisi

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │───▶│   Flask Backend  │───▶│   AI Models     │
│   (HTML/CSS/JS) │    │   (app.py)       │    │   (3 Models)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   ChromaDB       │
                       │   Vector Store   │
                       │   (8 Collections)│
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   LangChain      │
                       │   RAG System     │
                       └──────────────────┘
```

## 📦 Kurulum

### Gereksinimler
- Python 3.8+
- pip package manager
- 4GB+ RAM (AI modelleri için)

### Adım 1: Repository'yi klonlayın
```bash
git clone https://github.com/username/turkish-rag-search-system.git
cd turkish-rag-search-system
```

### Adım 2: Virtual environment oluşturun
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

### Adım 3: Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Vektör veritabanını oluşturun
```bash
python rebuild_database.py
```

## 🚀 Kullanım

### Web Uygulamasını Başlatma
```bash
python app.py
```
Uygulama `http://localhost:5001` adresinde çalışacaktır.

### Alternatif LangChain Uygulaması
```bash
python app_langchain.py
```

## 📊 Desteklenen AI Modelleri

| Model | Açıklama | Boyut |
|-------|----------|-------|
| `dbmdz/bert-base-turkish-cased` | Türkçe BERT modeli | 768 dim |
| `TURKCELL/roberta-base-turkish-uncased` | Türkçe RoBERTa modeli | 768 dim |
| `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | Çok dilli MPNet | 768 dim |

## 💡 Özellikler

### 🔍 Arama Tipleri

#### 1. Kelime Araması
```python
# API örneği
POST /search
{
    "query": "teknoloji",
    "type": "words",
    "models": ["dbmdz_bert"],
    "top_k": 5
}
```

#### 2. Cümle Araması
```python
POST /search
{
    "query": "Eğitim sisteminin geliştirilmesi gerekiyor",
    "type": "sentences",
    "models": ["dbmdz_bert", "turkcell_roberta"],
    "top_k": 3
}
```

#### 3. Soru-Cevap Sistemi
```python
POST /qa
{
    "question": "Teknoloji hayatımızı nasıl etkiler?"
}
```

#### 4. Kelime İlişkileri
```python
GET /relationships/teknoloji
```

### 📈 Performans Özellikleri

- **8.4 metin/saniye** embedding hızı
- **1999 kelime** vektör veritabanında
- **1008 cümle** semantik arama için
- **100% web arayüzü uptime**
- **Multi-threading** desteği

## 🗂️ Proje Yapısı

```
bitirme/
├── 📁 app.py                 # Ana Flask uygulaması
├── 📁 app_langchain.py       # LangChain entegrasyonlu uygulama
├── 📁 langchain_arama.py     # LangChain arama sistemi
├── 📁 vektor_olustur.py      # Vektör oluşturma utilities
├── 📁 rebuild_database.py    # Veritabanı yeniden oluşturma
├── 📁 requirements.txt       # Python bağımlılıkları
├── 📁 templates/             # HTML şablonları
│   └── index.html           # Ana web arayüzü
├── 📁 static/               # CSS, JS, images
│   ├── css/main.css
│   └── js/main.js
├── 📁 db/                   # ChromaDB vektör veritabanı
├── 📁 test_results/         # Test raporları
├── 📁 kelimeler.txt         # Kelime veri seti (2000 kelime)
├── 📁 metinler.txt          # Cümle veri seti (1008 cümle)
└── 📁 iliskiler.txt         # Kelime ilişkileri veri seti
```

## 🧪 Test Sistemi

Proje kapsamlı test senaryolarına sahiptir:

```bash
# Tüm testleri çalıştır
python search_test_scenarios.py

# Test simülasyonları
python test_simulations.py
```

### Test Kapsamı
- ✅ Vector Database işlemleri
- ✅ Çoklu model fonksiyonalitesi  
- ✅ LangChain RAG entegrasyonu
- ✅ Web arayüzü entegrasyonu
- ✅ Performans ve yük testleri

## 📊 API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Ana sayfa |
| `/search` | POST | Semantik arama |
| `/qa` | POST | Soru-cevap sistemi |
| `/relationships/<word>` | GET | Kelime ilişkileri |
| `/stats` | GET | Sistem istatistikleri |
| `/health` | GET | Sistem durumu |

## 🎨 Web Arayüzü

Modern ve kullanıcı dostu web arayüzü özellikleri:
- **Responsive design** (mobil uyumlu)
- **Real-time search** (canlı arama)
- **Model comparison** (model karşılaştırma)
- **Visual similarity scores** (görsel benzerlik skorları)
- **Dark/Light theme** desteği

## 📈 Performans Metrikleri

| Metrik | Değer | Durum |
|--------|-------|-------|
| Toplam Koleksiyon | 8 | ✅ Optimal |
| Kelime Sayısı | 1999 | ✅ Zengin |
| Cümle Sayısı | 1008 | ✅ Yeterli |
| Embedding Hızı | 8.4 text/sec | ✅ Hızlı |
| Vector Boyutu | 768 | ✅ Standart |
| API Response Time | <200ms | ✅ Hızlı |

## 🔧 Konfigürasyon

### Model Ayarları
```python
SUPPORTED_MODELS = {
    "dbmdz_bert": "dbmdz/bert-base-turkish-cased",
    "turkcell_roberta": "TURKCELL/roberta-base-turkish-uncased", 
    "multilingual_mpnet": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
}
```

### Veritabanı Ayarları
```python
DB_DIR = "./db"
COLLECTION_PREFIX = "kelime_vektorleri_"
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (örnek)
```bash
gunicorn --bind 0.0.0.0:5001 app:app
```

## 🤝 Katkı Sağlama

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında dağıtılmaktadır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Yazarlar

- **[İsim Soyisim]** - *Initial work* - [GitHub](https://github.com/username)

## 🙏 Teşekkürler

- [HuggingFace](https://huggingface.co/) - Transformers ve model desteği için
- [LangChain](https://langchain.com/) - RAG framework için
- [ChromaDB](https://chromadb.ai/) - Vector database için
- [Flask](https://flask.palletsprojects.com/) - Web framework için

## 📞 İletişim

- 📧 Email: your.email@example.com
- 🐦 Twitter: [@username](https://twitter.com/username)
- 💼 LinkedIn: [Profile](https://linkedin.com/in/username)

---

⭐ **Bu projeyi beğendiyseniz bir yıldız vermeyi unutmayın!** 