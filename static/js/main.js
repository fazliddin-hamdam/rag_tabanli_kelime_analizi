// 🎯 Multi-Model Türkçe Semantik Arama Sistemi - Ana JavaScript

let currentSearchType = 'sentences';
let availableModels = {};
let systemStats = {};
let isDropdownOpen = false;

// Her arama tipi için son aramayı hafızada tut
let searchHistory = {
    sentences: { query: '', results: null },
    words: { query: '', results: null },
    relationships: { query: '', results: null }
};

// Sayfa yüklendiğinde sistem bilgilerini al
document.addEventListener('DOMContentLoaded', function() {
    loadSystemInfo();
    
    // Enter tuşu ile arama
    document.getElementById('searchQuery').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Dropdown dışına tıklandığında kapat
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('modelDropdown');
        if (!dropdown.contains(e.target)) {
            closeDropdown();
        }
    });
});

// Dropdown'u aç/kapat
function toggleModelDropdown() {
    const dropdownButton = document.getElementById('dropdownButton');
    const dropdownMenu = document.getElementById('dropdownMenu');
    
    if (isDropdownOpen) {
        closeDropdown();
    } else {
        openDropdown();
    }
}

function openDropdown() {
    const dropdownButton = document.getElementById('dropdownButton');
    const dropdownMenu = document.getElementById('dropdownMenu');
    
    dropdownButton.classList.add('active');
    dropdownMenu.classList.add('show');
    isDropdownOpen = true;
}

function closeDropdown() {
    const dropdownButton = document.getElementById('dropdownButton');
    const dropdownMenu = document.getElementById('dropdownMenu');
    
    dropdownButton.classList.remove('active');
    dropdownMenu.classList.remove('show');
    isDropdownOpen = false;
}

// Sistem bilgilerini ve modelleri yükle
function loadSystemInfo() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            systemStats = data;
            updateStatsDisplay(data);
            loadModelSelector(data);
        })
        .catch(error => {
            console.error('Sistem bilgisi yükleme hatası:', error);
            document.getElementById('stats').innerHTML = '❌ Sistem bilgisi yüklenemedi';
            document.getElementById('modelOptions').innerHTML = '<div class="model-error">❌ Modeller yüklenemedi</div>';
        });
}

// İstatistikleri güncelle
function updateStatsDisplay(data) {
    const statsDiv = document.getElementById('stats');
    if (data.error) {
        statsDiv.innerHTML = `❌ ${data.error}`;
        return;
    }
    
    statsDiv.innerHTML = `
        📚 <strong>${data.sentences_count}</strong> cümle |
        🔤 <strong>${data.words_count}</strong> kelime |
        🔗 <strong>${data.relationships_count}</strong> ilişki |
        🤖 <strong>${data.models_loaded}</strong> model yüklü
    `;
}

// Model seçici dropdown oluştur
function loadModelSelector(data) {
    const modelOptions = document.getElementById('modelOptions');
    
    if (data.error || !data.available_models || data.available_models.length === 0) {
        modelOptions.innerHTML = '<div class="model-error">❌ Hiçbir model yüklenmemiş</div>';
        updateDropdownText();
        return;
    }
    
    availableModels = data.supported_models || {};
    const availableModelIds = data.available_models || [];
    
    let modelsHTML = '';
    
    availableModelIds.forEach((modelId, index) => {
        const modelName = availableModels[modelId] || modelId;
        const isChecked = index === 0; // İlk model varsayılan olarak seçili
        
        // Model detaylarını al
        const modelDetails = data.model_details && data.model_details[modelId];
        const wordCount = modelDetails ? modelDetails.words : 0;
        const sentenceCount = modelDetails ? modelDetails.sentences : 0;
        
        modelsHTML += `
            <div class="model-option ${isChecked ? 'selected' : ''}" onclick="toggleModelSelection('${modelId}')">
                <label class="model-label">
                    <input type="checkbox" 
                           name="model" 
                           value="${modelId}" 
                           ${isChecked ? 'checked' : ''}
                           style="display: none;">
                    <div class="model-info-card">
                        <div class="model-check">${isChecked ? '✓' : ''}</div>
                        <div class="model-details">
                            <div class="model-name">${getModelDisplayName(modelId)}</div>
                            <div class="model-path">${modelName}</div>
                            <div class="model-stats">📚 ${sentenceCount} cümle • 🔤 ${wordCount} kelime</div>
                        </div>
                    </div>
                </label>
            </div>
        `;
    });
    
    modelOptions.innerHTML = modelsHTML;
    
    // Dropdown text'ini güncelle
    updateDropdownText();
    updateModelSelection();
}

// Model seçimini toggle et
function toggleModelSelection(modelId) {
    const modelOption = document.querySelector(`.model-option[onclick="toggleModelSelection('${modelId}')"]`);
    const checkbox = modelOption.querySelector('input[type="checkbox"]');
    const checkIcon = modelOption.querySelector('.model-check');
    
    // Toggle selection
    const isSelected = modelOption.classList.contains('selected');
    
    if (isSelected) {
        modelOption.classList.remove('selected');
        checkbox.checked = false;
        checkIcon.textContent = '';
    } else {
        modelOption.classList.add('selected');
        checkbox.checked = true;
        checkIcon.textContent = '✓';
    }
    
    updateDropdownText();
    updateModelSelection();
}

// Dropdown text'ini güncelle
function updateDropdownText() {
    const selectedModels = getSelectedModels();
    const dropdownText = document.getElementById('dropdownText');
    
    if (selectedModels.length === 0) {
        dropdownText.textContent = 'Modelleri Seçin';
    } else if (selectedModels.length === 1) {
        dropdownText.textContent = getModelDisplayName(selectedModels[0]);
    } else {
        dropdownText.textContent = `${selectedModels.length} Model Seçili`;
    }
}

// Model display isimlerini düzenle
function getModelDisplayName(modelId) {
    const displayNames = {
        'dbmdz_bert': '🇹🇷 BERT Turkish',
        'turkcell_roberta': '🇹🇷 Turkcell RoBERTa',
        'multilingual_mpnet': '🌍 Multilingual MPNet'
    };
    return displayNames[modelId] || modelId.toUpperCase();
}

// Model seçimi değiştiğinde
function updateModelSelection() {
    const selectedModels = getSelectedModels();
    const searchBtn = document.querySelector('.search-btn');
    const selectionInfo = document.getElementById('selectionInfo');
    
    if (selectedModels.length === 0) {
        searchBtn.disabled = true;
        searchBtn.style.opacity = '0.5';
        searchBtn.title = 'En az bir model seçmelisiniz';
    } else {
        searchBtn.disabled = false;
        searchBtn.style.opacity = '1';
        searchBtn.title = `${selectedModels.length} model ile arama yap`;
    }
    
    // Seçili model sayısını göster
    if (selectionInfo) {
        if (selectedModels.length === 0) {
            selectionInfo.innerHTML = '<small>⚠️ <strong>Hiçbir model seçilmemiş!</strong> En az bir model seçin.</small>';
        } else if (selectedModels.length === 1) {
            selectionInfo.innerHTML = `<small>✅ <strong>1 model seçili:</strong> ${getModelDisplayName(selectedModels[0])}</small>`;
        } else {
            selectionInfo.innerHTML = `<small>✅ <strong>${selectedModels.length} model seçili</strong> - Karşılaştırmalı sonuçlar gösterilecek</small>`;
        }
    }
}

// Seçili modelleri al
function getSelectedModels() {
    const checkboxes = document.querySelectorAll('#modelOptions input[name="model"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
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

// Ana arama fonksiyonu
function performSearch() {
    const query = document.getElementById('searchQuery').value.trim();
    
    if (!query) {
        alert('Lütfen bir arama terimi girin!');
        return;
    }

    // Seçili modelleri al
    const selectedModels = getSelectedModels();
    if (selectedModels.length === 0) {
        alert('Lütfen en az bir model seçin!');
        return;
    }

    // Loading göster
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <div>🔍 "${query}" araması yapılıyor...</div>
            <div><small>${selectedModels.length} model ile karşılaştırmalı arama</small></div>
        </div>
    `;

    // API çağrısı
    if (currentSearchType === 'relationships') {
        // İlişkiler için ayrı endpoint (tek model yeterli)
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
        // Multi-model arama
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                type: currentSearchType,
                models: selectedModels
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
                displayMultiModelResults(data);
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

// Multi-model sonuçları göster
function displayMultiModelResults(data) {
    const resultsDiv = document.getElementById('results');
    const searchResults = data.search_results || {};
    const modelsUsed = data.models_used || [];
    
    if (modelsUsed.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h3>Sonuç Bulunamadı</h3>
                <p>"${data.query}" için hiçbir modelde sonuç bulunamadı.</p>
            </div>
        `;
        return;
    }

    // Sonuç başlığı
    let resultsHTML = `
        <div class="search-summary">
            <h3>🔍 "${data.query}" Arama Sonuçları</h3>
            <p>${modelsUsed.length} model ile ${data.type === 'sentences' ? 'cümle' : 'kelime'} araması</p>
        </div>
        <div class="model-results-grid">
    `;

    // Her model için sonuçları göster
    modelsUsed.forEach(modelId => {
        const modelData = searchResults[modelId];
        if (!modelData) return;

        const modelName = getModelDisplayName(modelId);
        const results = modelData.results || [];
        
        resultsHTML += `
            <div class="model-results-column">
                <div class="model-header">
                    <h4>${modelName}</h4>
                    <div class="model-details">
                        <small>${modelData.model_name}</small>
                        <span class="result-count">${results.length} sonuç</span>
                    </div>
                </div>
                <div class="model-results-list">
        `;

        if (results.length === 0) {
            resultsHTML += `
                <div class="no-results-in-model">
                    <p>Bu modelde sonuç bulunamadı</p>
                </div>
            `;
        } else {
            results.forEach((result, index) => {
                if (data.type === 'sentences') {
                    resultsHTML += createSentenceResultHTML(result, index);
                } else {
                    resultsHTML += createWordResultHTML(result, index);
                }
            });
        }

        resultsHTML += `
                </div>
            </div>
        `;
    });

    resultsHTML += `</div>`;
    resultsDiv.innerHTML = resultsHTML;
}

// Cümle sonucu HTML'i oluştur
function createSentenceResultHTML(result, index) {
    const similarityColor = getSimilarityColor(result.similarity_percent);
    
    return `
        <div class="result-item sentence-result">
            <div class="result-header">
                <span class="result-rank">#${result.rank}</span>
                <span class="similarity-badge" style="background-color: ${similarityColor}">
                    ${result.similarity_percent}%
                </span>
            </div>
            <div class="result-content">
                <p class="sentence-text">"${result.sentence}"</p>
            </div>
        </div>
    `;
}

// Kelime sonucu HTML'i oluştur
function createWordResultHTML(result, index) {
    const similarityColor = getSimilarityColor(result.similarity_percent);
    
    let relationshipsHTML = '';
    if (result.relationships && Object.keys(result.relationships).length > 0) {
        relationshipsHTML = '<div class="word-relationships">';
        for (const [relType, words] of Object.entries(result.relationships)) {
            if (words && words.length > 0) {
                relationshipsHTML += `
                    <div class="relation-group">
                        <strong>${relType}:</strong> ${words.slice(0, 3).join(', ')}${words.length > 3 ? '...' : ''}
                    </div>
                `;
            }
        }
        relationshipsHTML += '</div>';
    }
    
    return `
        <div class="result-item word-result">
            <div class="result-header">
                <span class="result-rank">#${result.rank}</span>
                <span class="similarity-badge" style="background-color: ${similarityColor}">
                    ${result.similarity_percent}%
                </span>
            </div>
            <div class="result-content">
                <div class="word-text">${result.word}</div>
                ${relationshipsHTML}
            </div>
        </div>
    `;
}

// Benzerlik yüzdesine göre renk
function getSimilarityColor(percentage) {
    if (percentage >= 80) return '#28a745';
    if (percentage >= 60) return '#ffc107';
    if (percentage >= 40) return '#fd7e14';
    return '#dc3545';
}

// İlişki sonuçlarını göster (eski fonksiyon korundu)
function displayRelationships(data) {
    const resultsDiv = document.getElementById('results');
    
    if (data.error) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">❌</div>
                <h3>İlişki Bulunamadı</h3>
                <p>${data.error}</p>
            </div>
        `;
        return;
    }

    const relationships = data.relationships || {};
    let resultsHTML = `
        <div class="relationships-container">
            <h3>🔗 "${data.word}" Kelimesi İlişkileri</h3>
            <div class="relationships-grid">
    `;

    for (const [relationType, words] of Object.entries(relationships)) {
        if (words && words.length > 0) {
            resultsHTML += `
                <div class="relationship-group">
                    <h4 class="relationship-type">${relationType}</h4>
                    <div class="relationship-words">
            `;
            
            words.forEach(word => {
                resultsHTML += `
                    <span class="relationship-word" onclick="searchRelatedWord('${word}')">
                        ${word}
                    </span>
                `;
            });
            
            resultsHTML += `
                    </div>
                </div>
            `;
        }
    }

    resultsHTML += `
            </div>
        </div>
    `;

    resultsDiv.innerHTML = resultsHTML;
}

// İlişkili kelimeyi ara
function searchRelatedWord(word) {
    document.getElementById('searchQuery').value = word;
    // Kelime aramasına geç
    document.querySelector('[data-type="words"]').click();
    performSearch();
}

// Sonuçları geri yükle (arama tipi değiştirildiğinde)
function restoreSearchResults(data, query) {
    if (currentSearchType === 'relationships') {
        displayRelationships(data);
    } else {
        displayMultiModelResults(data);
    }
} 