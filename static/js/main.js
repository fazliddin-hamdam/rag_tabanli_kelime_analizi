// 🎯 Multi-Model Türkçe Semantik Arama Sistemi - Ana JavaScript

let currentSearchType = 'sentences';
let availableModels = {};
let systemStats = {};
let isDropdownOpen = false;
let searchDebounceTimer = null;
const DEBOUNCE_DELAY = 500; // 500ms debounce

// Her arama tipi için son aramayı hafızada tut
let searchHistory = {
    sentences: { query: '', results: null },
    words: { query: '', results: null },
    relationships: { query: '', results: null }
};

// Local storage key for caching search results
const CACHE_KEY_PREFIX = 'semantik_arama_cache_';
const CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

// Initialize cache data structure
function initializeCache() {
    return {
        query: '',
        searchType: '',
        models: [],
        results: null,
        timestamp: Date.now()
    };
}

// Generate cache key based on query, search type and models
function generateCacheKey(query, searchType, models) {
    const modelsString = models.sort().join(',');
    return CACHE_KEY_PREFIX + btoa(encodeURIComponent(query + '_' + searchType + '_' + modelsString));
}

// Save search results to localStorage
function saveSearchToCache(query, searchType, models, results) {
    try {
        const cacheKey = generateCacheKey(query, searchType, models);
        const cacheData = {
            query: query,
            searchType: searchType,
            models: models,
            results: results,
            timestamp: Date.now()
        };
        localStorage.setItem(cacheKey, JSON.stringify(cacheData));
        
        // Also maintain a list of cache keys for cleanup
        const cacheKeys = getCacheKeysList();
        if (!cacheKeys.includes(cacheKey)) {
            cacheKeys.push(cacheKey);
            localStorage.setItem(CACHE_KEY_PREFIX + 'keys', JSON.stringify(cacheKeys));
        }
        
        // Clean old cache entries
        cleanExpiredCache();
    } catch (e) {
        console.warn('Cache save failed:', e);
    }
}

// Load search results from localStorage
function loadSearchFromCache(query, searchType, models) {
    try {
        const cacheKey = generateCacheKey(query, searchType, models);
        const cachedData = localStorage.getItem(cacheKey);
        
        if (cachedData) {
            const parsedData = JSON.parse(cachedData);
            
            // Check if cache is still valid (not expired)
            if (Date.now() - parsedData.timestamp < CACHE_EXPIRY) {
                return parsedData.results;
            } else {
                // Remove expired cache
                localStorage.removeItem(cacheKey);
                removeCacheKeyFromList(cacheKey);
            }
        }
    } catch (e) {
        console.warn('Cache load failed:', e);
    }
    return null;
}

// Get list of cache keys
function getCacheKeysList() {
    try {
        const keys = localStorage.getItem(CACHE_KEY_PREFIX + 'keys');
        return keys ? JSON.parse(keys) : [];
    } catch (e) {
        return [];
    }
}

// Remove cache key from list
function removeCacheKeyFromList(keyToRemove) {
    try {
        const cacheKeys = getCacheKeysList();
        const updatedKeys = cacheKeys.filter(key => key !== keyToRemove);
        localStorage.setItem(CACHE_KEY_PREFIX + 'keys', JSON.stringify(updatedKeys));
    } catch (e) {
        console.warn('Cache key removal failed:', e);
    }
}

// Clean expired cache entries
function cleanExpiredCache() {
    try {
        const cacheKeys = getCacheKeysList();
        const validKeys = [];
        
        cacheKeys.forEach(key => {
            const cachedData = localStorage.getItem(key);
            if (cachedData) {
                try {
                    const parsedData = JSON.parse(cachedData);
                    if (Date.now() - parsedData.timestamp < CACHE_EXPIRY) {
                        validKeys.push(key);
                    } else {
                        localStorage.removeItem(key);
                    }
                } catch (e) {
                    localStorage.removeItem(key);
                }
            }
        });
        
        localStorage.setItem(CACHE_KEY_PREFIX + 'keys', JSON.stringify(validKeys));
    } catch (e) {
        console.warn('Cache cleanup failed:', e);
    }
}

// Debounced search function
function debouncedSearch() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        const query = document.getElementById('searchQuery').value.trim();
        if (query.length >= 2) { // Minimum 2 character for search
            performSearch();
        } else {
            // Clear results if query is too short
            document.getElementById('results').innerHTML = '';
        }
    }, DEBOUNCE_DELAY);
}

// Auto search when search type changes
function autoSearchOnTypeChange() {
    const query = document.getElementById('searchQuery').value.trim();
    if (query.length >= 2) {
        performSearch();
    }
}

// Sayfa yüklendiğinde sistem bilgilerini al
document.addEventListener('DOMContentLoaded', function() {
    loadSystemInfo();
    
    // Enter tuşu ile arama
    const searchInput = document.getElementById('searchQuery');
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            clearTimeout(searchDebounceTimer); // Cancel debounce on enter
            performSearch();
        }
    });

    // Input change event for automatic search
    searchInput.addEventListener('input', function(e) {
        debouncedSearch();
    });

    // Dropdown dışına tıklandığında kapat
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('modelDropdown');
        if (!dropdown.contains(e.target)) {
            closeDropdown();
        }
    });

    // Arama tipi değiştirme event listeners
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
            } else if (currentSearchType === 'relationships') {
                input.placeholder = 'İlişkilerini öğrenmek istediğiniz kelimeyi yazın...';
            } else if (currentSearchType === 'qa') {
                input.placeholder = 'Sormak istediğiniz soruyu yazın... (örn: Annem pazardan ne aldı?)';
            }
            
            // Örnek aramaları güncelle
            document.getElementById('sentenceExamples').style.display = currentSearchType === 'sentences' ? 'block' : 'none';
            document.getElementById('wordExamples').style.display = currentSearchType === 'words' ? 'block' : 'none';
            document.getElementById('relationshipExamples').style.display = currentSearchType === 'relationships' ? 'block' : 'none';
            document.getElementById('qaExamples').style.display = currentSearchType === 'qa' ? 'block' : 'none';
            
            // Auto search when type changes if query exists
            autoSearchOnTypeChange();
        });
    });

    // Clean old cache on page load
    cleanExpiredCache();
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
            <div class="model-option ${isChecked ? 'selected' : ''}" data-model-id="${modelId}">
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
    
    // Event listeners ekle
    addModelOptionEventListeners();
    
    // Dropdown text'ini güncelle
    updateDropdownText();
    updateModelSelection();
}

// Model seçeneklerine event listener ekle
function addModelOptionEventListeners() {
    const modelOptions = document.querySelectorAll('.model-option');
    
    modelOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const modelId = this.getAttribute('data-model-id');
            toggleModelSelection(modelId);
        });
    });
}

// Model seçimini toggle et - FIX edildi
function toggleModelSelection(modelId) {
    const modelOption = document.querySelector(`.model-option[data-model-id="${modelId}"]`);
    if (!modelOption) return;
    
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
    
    // Auto search when model selection changes if query exists
    autoSearchOnTypeChange();
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

    // Check cache first
    const cachedResults = loadSearchFromCache(query, currentSearchType, selectedModels);
    if (cachedResults) {
        console.log('🎯 Cache hit - loading from localStorage');
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="cache-indicator">
                <small>📱 Cached results loaded • ${new Date().toLocaleTimeString()}</small>
            </div>
        `;
        
        if (currentSearchType === 'relationships') {
            displayRelationships(cachedResults);
        } else {
            displayMultiModelResults(cachedResults);
        }
        
        // Update search history
        searchHistory[currentSearchType] = {
            query: query,
            results: cachedResults
        };
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
                // Save to cache
                saveSearchToCache(query, currentSearchType, selectedModels, data);
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
    } else if (currentSearchType === 'qa') {
        // Q&A için ayrı endpoint
        fetch('/qa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: query
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
                displayQAResults(data);
                // Save to cache
                saveSearchToCache(query, currentSearchType, [], data); // Q&A model independent
                // Başarılı aramayı kaydet
                searchHistory[currentSearchType] = {
                    query: query,
                    results: data
                };
            }
        })
        .catch(error => {
            console.error('Q&A arama hatası:', error);
            resultsDiv.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon">⚠️</div>
                    <h3>Bağlantı Hatası</h3>
                    <p>Q&A sistemi ile bağlantı kurulamadı.</p>
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
                // Save to cache
                saveSearchToCache(query, currentSearchType, selectedModels, data);
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
    
    // Model sayısına göre grid layout sınıfını belirle
    const gridClass = modelsUsed.length === 3 ? 'model-results-grid three-models' : 'model-results-grid';
    
    // 3 model için container'ı geniş yap
    const container = document.querySelector('.container');
    if (modelsUsed.length === 3) {
        container.classList.add('wide-layout');
    } else {
        container.classList.remove('wide-layout');
    }
    
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
        <div class="search-summary compact">
            <small>🔍 "${data.query}" • ${modelsUsed.length} model • ${data.type === 'sentences' ? 'cümle' : 'kelime'}</small>
        </div>
        <div class="${gridClass}">
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
    // Arama tipini kelimeler olarak değiştir
    currentSearchType = 'words';
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.toggle-btn[data-type="words"]').classList.add('active');
    
    // Placeholder'ı güncelle
    const input = document.getElementById('searchQuery');
    input.placeholder = 'Kelimeler içinde aramak istediğiniz kelimeyi yazın...';
    
    // Örnek aramaları güncelle
    document.getElementById('sentenceExamples').style.display = 'none';
    document.getElementById('wordExamples').style.display = 'block';
    document.getElementById('relationshipExamples').style.display = 'none';
    
    // Aramayı gerçekleştir
    setQuery(word);
}

// Q&A sonuçlarını göster
function displayQAResults(data) {
    const resultsDiv = document.getElementById('results');
    
    // Container'ı normal layout'a çevir
    const container = document.querySelector('.container');
    container.classList.remove('wide-layout');
    
    let resultsHTML = `
        <div class="qa-results-container">
            <div class="qa-header">
                <h3>🤖 Soru-Cevap Sonucu</h3>
                <div class="qa-method">
                    <small>📚 ${data.method} • ${data.retrieved_documents} doküman incelendi</small>
                </div>
            </div>
            
            <div class="qa-question-section">
                <h4 class="qa-question-label">❓ Soru:</h4>
                <div class="qa-question">"${data.question}"</div>
            </div>
            
            <div class="qa-answer-section">
                <div class="qa-answer-header">
                    <h4 class="qa-answer-label">💡 Cevap:</h4>
                    <span class="qa-confidence confidence-${data.confidence}">
                        ${data.confidence === 'orta' ? '🟡' : data.confidence === 'yüksek' ? '🟢' : '🔴'} 
                        ${data.confidence.charAt(0).toUpperCase() + data.confidence.slice(1)} Güven
                    </span>
                </div>
                <div class="qa-answer">${data.answer}</div>
            </div>
    `;
    
    // Kaynak cümleler varsa göster
    if (data.source_sentences && data.source_sentences.length > 0) {
        resultsHTML += `
            <div class="qa-sources-section">
                <h4 class="qa-sources-label">📖 Kaynak Cümleler:</h4>
                <div class="qa-sources-list">
        `;
        
        data.source_sentences.forEach((sentence, index) => {
            const similarity = data.similarity_scores && data.similarity_scores[index] ? data.similarity_scores[index] : 70;
            const similarityColor = getSimilarityColor(similarity);
            
            resultsHTML += `
                <div class="qa-source-item">
                    <div class="qa-source-header">
                        <span class="qa-source-rank">#${index + 1}</span>
                        <span class="similarity-badge" style="background-color: ${similarityColor}">
                            ${similarity}%
                        </span>
                    </div>
                    <div class="qa-source-text">"${sentence}"</div>
                </div>
            `;
        });
        
        resultsHTML += `
                </div>
            </div>
        `;
    }
    
    resultsHTML += `
        </div>
    `;
    
    resultsDiv.innerHTML = resultsHTML;
}

// Arama sonuçlarını geri yükle
function restoreSearchResults(data, query) {
    if (currentSearchType === 'relationships') {
        displayRelationships(data);
    } else if (currentSearchType === 'qa') {
        displayQAResults(data);
    } else {
        displayMultiModelResults(data);
    }
} 