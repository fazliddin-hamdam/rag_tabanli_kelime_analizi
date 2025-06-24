// 🎯 Türkçe Semantik Arama Sistemi - Ana JavaScript

let currentSearchType = 'sentences';

// Her arama tipi için son aramayı hafızada tut
let searchHistory = {
    sentences: { query: '', results: null },
    words: { query: '', results: null },
    relationships: { query: '', results: null }
};

// Sayfa yüklendiğinde istatistikleri al
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    
    // Enter tuşu ile arama
    document.getElementById('searchQuery').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});

// İstatistikleri yükle
function loadStats() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            const statsDiv = document.getElementById('stats');
            statsDiv.innerHTML = `
                📚 <strong>${data.sentences_count}</strong> cümle |
                🔤 <strong>${data.words_count}</strong> kelime |
                🔗 <strong>${data.relationships_count}</strong> ilişki |
                🤖 Model: ${data.model_loaded ? '✅ Yüklü' : '❌ Yüklenmemiş'}
            `;
        })
        .catch(error => {
            console.error('İstatistik yükleme hatası:', error);
        });
}

// Arama tipi değiştirme
document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // Aktif buton stilini değiştir
        document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // Arama tipini güncelle
        currentSearchType = this.getAttribute('data-type');
        
        // Placeholder'ı güncelle
        const input = document.getElementById('searchQuery');
        if (currentSearchType === 'sentences') {
            input.placeholder = 'Cümleler içinde aramak istediğiniz kelime veya ifadeyi yazın...';
        } else if (currentSearchType === 'words') {
            input.placeholder = 'Kelimeler içinde aramak istediğiniz kelimeyi yazın...';
        } else {
            input.placeholder = 'İlişkilerini öğrenmek istediğiniz kelimeyi yazın...';
        }
        
        // Örnek aramaları güncelle
        document.getElementById('sentenceExamples').style.display = currentSearchType === 'sentences' ? 'block' : 'none';
        document.getElementById('wordExamples').style.display = currentSearchType === 'words' ? 'block' : 'none';
        document.getElementById('relationshipExamples').style.display = currentSearchType === 'relationships' ? 'block' : 'none';
        
        // Bu arama tipi için kaydedilmiş arama var mı kontrol et
        const savedSearch = searchHistory[currentSearchType];
        if (savedSearch && savedSearch.query && savedSearch.results) {
            // Kaydedilmiş aramayı geri yükle
            input.value = savedSearch.query;
            restoreSearchResults(savedSearch.results, savedSearch.query);
        } else {
            // Sonuçları temizle
            input.value = '';
            document.getElementById('results').innerHTML = '';
        }
    });
});

// Örnek sorgu seç
function setQuery(query) {
    // Önceki aramayı temizle çünkü yeni bir arama başlatılıyor
    searchHistory[currentSearchType] = { query: '', results: null };
    document.getElementById('searchQuery').value = query;
    performSearch();
}

// Arama yap
function performSearch() {
    const query = document.getElementById('searchQuery').value.trim();
    
    if (!query) {
        alert('Lütfen bir arama terimi girin!');
        return;
    }

    // Loading göster
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <div>🔍 "${query}" araması yapılıyor...</div>
        </div>
    `;

    // API çağrısı
    if (currentSearchType === 'relationships') {
        // İlişkiler için ayrı endpoint
        fetch(`/relationships/${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `
                    <div class="no-results">
                        <div class="no-results-icon">❌</div>
                        <h3>Hata Oluştu</h3>
                        <p>${data.error}</p>
                    </div>
                `;
            } else {
                displayRelationships(data);
                // Başarılı aramayı kaydet
                searchHistory[currentSearchType] = {
                    query: query,
                    results: data
                };
            }
        })
        .catch(error => {
            console.error('İlişki arama hatası:', error);
            resultsDiv.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon">⚠️</div>
                    <h3>Bağlantı Hatası</h3>
                    <p>İlişki bilgileri alınırken bir hata oluştu.</p>
                </div>
            `;
        });
    } else {
        // Normal arama
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                type: currentSearchType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `
                    <div class="no-results">
                        <div class="no-results-icon">❌</div>
                        <h3>Hata Oluştu</h3>
                        <p>${data.error}</p>
                    </div>
                `;
            } else {
                displayResults(data);
                // Başarılı aramayı kaydet
                searchHistory[currentSearchType] = {
                    query: query,
                    results: data
                };
            }
        })
        .catch(error => {
            console.error('Arama hatası:', error);
            resultsDiv.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon">⚠️</div>
                    <h3>Bağlantı Hatası</h3>
                    <p>Arama yapılırken bir hata oluştu.</p>
                </div>
            `;
        });
    }
}

// Sonuçları göster
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    
    if (!data.results || data.results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h3>Sonuç Bulunamadı</h3>
                <p>"${data.query}" için ${data.type === 'sentences' ? 'cümle' : 'kelime'} bulunamadı.</p>
                <p>Farklı arama terimleri deneyebilirsiniz.</p>
            </div>
        `;
        return;
    }

    let resultsHTML = `
        <h3>🎯 "${data.query}" araması için ${data.results.length} sonuç bulundu</h3>
    `;

    data.results.forEach(result => {
        if (data.type === 'sentences') {
            resultsHTML += `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-rank">${result.rank}. sıra</span>
                        <span class="similarity-badge">%${result.similarity_percent} benzer</span>
                    </div>
                    <div class="result-content">
                        📝 ${result.sentence}
                    </div>
                    <div class="result-meta">
                        🔢 İndeks: ${result.index} | 🎯 Benzerlik Skoru: ${result.similarity.toFixed(4)}
                    </div>
                </div>
            `;
        } else {
            resultsHTML += `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-rank">${result.rank}. sıra</span>
                        <span class="similarity-badge">%${result.similarity_percent} benzer</span>
                    </div>
                    <div class="result-content">
                        🔤 <strong>${result.word}</strong>
                    </div>
                    <div class="result-meta">
                        🔢 İndeks: ${result.index} | 🎯 Benzerlik Skoru: ${result.similarity.toFixed(4)}
                    </div>
                </div>
            `;
        }
    });

    resultsDiv.innerHTML = resultsHTML;
}

// İlişkileri göster
function displayRelationships(data) {
    const resultsDiv = document.getElementById('results');
    
    if (!data.found) {
        resultsDiv.innerHTML = `
            <div class="no-relationships">
                <div class="no-results-icon">🔍</div>
                <h3>İlişki Bulunamadı</h3>
                <p>${data.message}</p>
                <p>💡 Deneyin: <strong>kitap, araba, kedi, okul, ev</strong></p>
            </div>
        `;
        return;
    }

    const relationships = data.relationships;
    let relationshipHTML = `
        <h3>🔗 "${data.word}" kelimesinin ilişkileri</h3>
    `;

    // Hiperonim (Üst kavram)
    if (relationships.hiperonim && relationships.hiperonim.length > 0) {
        relationshipHTML += `
            <div class="relationship-section">
                <div class="relationship-type">
                    <div class="relationship-title">📈 Hiperonim (Üst Kavram)</div>
                    <div class="relationship-words">
                        ${relationships.hiperonim.map(word => 
                            `<span class="relationship-word" onclick="searchRelatedWord('${word}')">${word}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Hiponim (Alt kavram)
    if (relationships.hiponim && relationships.hiponim.length > 0) {
        relationshipHTML += `
            <div class="relationship-section">
                <div class="relationship-type">
                    <div class="relationship-title">📉 Hiponim (Alt Kavram)</div>
                    <div class="relationship-words">
                        ${relationships.hiponim.map(word => 
                            `<span class="relationship-word" onclick="searchRelatedWord('${word}')">${word}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Meronim (Parça-bütün ilişkisi)
    if (relationships.meronim && relationships.meronim.length > 0) {
        relationshipHTML += `
            <div class="relationship-section">
                <div class="relationship-type">
                    <div class="relationship-title">🧩 Meronim (Parça-Bütün)</div>
                    <div class="relationship-words">
                        ${relationships.meronim.map(word => 
                            `<span class="relationship-word" onclick="searchRelatedWord('${word}')">${word}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Eğer hiçbir ilişki yoksa
    if ((!relationships.hiperonim || relationships.hiperonim.length === 0) &&
        (!relationships.hiponim || relationships.hiponim.length === 0) &&
        (!relationships.meronim || relationships.meronim.length === 0)) {
        relationshipHTML += `
            <div class="no-relationships">
                <h4>Bu kelime için ilişki bilgisi bulunamadı</h4>
                <p>Diğer kelimeleri deneyebilirsiniz.</p>
            </div>
        `;
    }

    resultsDiv.innerHTML = relationshipHTML;
}

// İlişkili kelimeye tıklandığında arama yap
function searchRelatedWord(word) {
    document.getElementById('searchQuery').value = word;
    performSearch();
}

// Kaydedilmiş arama sonuçlarını geri yükle
function restoreSearchResults(data, query) {
    if (currentSearchType === 'relationships') {
        displayRelationships(data);
    } else {
        displayResults(data);
    }
} 