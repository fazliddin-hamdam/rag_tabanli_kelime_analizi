#!/usr/bin/env python3
"""
Arama Tabanlı Test Senaryoları - DÜZELTILMIŞ VERSIYON
RAG sisteminin gerçek arama örnekleri üzerinden 5 farklı test senaryosu
"""

import requests
import json
import time
from datetime import datetime

class SearchTestRunner:
    """Arama tabanlı test senaryolarını çalıştıran sınıf"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test_result(self, scenario_name, test_name, success, details, duration):
        """Test sonucunu kaydet"""
        result = {
            'scenario': scenario_name,
            'test': test_name,
            'success': success,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {details} ({duration:.2f}s)")
        
    def scenario_1_word_search_tests(self):
        """Senaryo 1: Kelime Arama Testleri"""
        print("\n" + "="*60)
        print("🔍 SENARYO 1: KELİME ARAMA TESTLERİ")
        print("="*60)
        
        test_words = ["teknoloji", "eğitim", "bilgisayar", "sevgi", "kitap"]
        
        for word in test_words:
            start_time = time.time()
            
            try:
                # DÜZELTILMIŞ API formatı
                payload = {
                    "query": word,
                    "type": "words",  # search_type yerine type
                    "models": ["dbmdz_bert"],  # model yerine models (liste)
                    "top_k": 5
                }
                
                response = requests.post(f"{self.base_url}/search", json=payload, timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Yanıt formatını kontrol et
                    if 'search_results' in data:
                        # Başarılı yanıt
                        model_results = data['search_results']
                        if model_results:
                            first_model = list(model_results.keys())[0]
                            results = model_results[first_model]['results']
                            
                            if results:
                                top_similarity = results[0].get('similarity_percent', 0)
                                self.log_test_result(
                                    "Kelime Arama", 
                                    f"'{word}' arama",
                                    True,
                                    f"{len(results)} sonuç, en iyi: %{top_similarity}",
                                    duration
                                )
                            else:
                                self.log_test_result("Kelime Arama", f"'{word}' arama", False, "Sonuç bulunamadı", duration)
                        else:
                            self.log_test_result("Kelime Arama", f"'{word}' arama", False, "Model sonucu yok", duration)
                    elif 'error' in data:
                        self.log_test_result("Kelime Arama", f"'{word}' arama", False, f"API hatası: {data['error']}", duration)
                    else:
                        self.log_test_result("Kelime Arama", f"'{word}' arama", False, "Beklenmeyen yanıt formatı", duration)
                else:
                    self.log_test_result("Kelime Arama", f"'{word}' arama", False, f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result("Kelime Arama", f"'{word}' arama", False, f"İstek hatası: {str(e)}", duration)
                
    def scenario_2_sentence_search_tests(self):
        """Senaryo 2: Cümle Arama Testleri"""
        print("\n" + "="*60)
        print("📝 SENARYO 2: CÜMLE ARAMA TESTLERİ")
        print("="*60)
        
        test_sentences = [
            "Eğitim sisteminin geliştirilmesi gerekiyor",
            "Teknoloji hayatımızı kolaylaştırır",
            "Çevre koruma önemli",
            "Bilim ve araştırma kritik rol oynar",
            "Kitap okumak faydalı"
        ]
        
        for sentence in test_sentences:
            start_time = time.time()
            
            try:
                payload = {
                    "query": sentence,
                    "type": "sentences",  # Düzeltildi
                    "models": ["dbmdz_bert"],  # Düzeltildi
                    "top_k": 3
                }
                
                response = requests.post(f"{self.base_url}/search", json=payload, timeout=15)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if 'search_results' in data:
                        model_results = data['search_results']
                        if model_results:
                            first_model = list(model_results.keys())[0]
                            results = model_results[first_model]['results']
                            
                            if results:
                                avg_similarity = sum(s.get('similarity_percent', 0) for s in results) / len(results)
                                self.log_test_result(
                                    "Cümle Arama", 
                                    f"'{sentence[:30]}...' arama",
                                    True,
                                    f"{len(results)} sonuç, ort: %{avg_similarity:.1f}",
                                    duration
                                )
                            else:
                                self.log_test_result("Cümle Arama", f"'{sentence[:30]}...' arama", False, "Sonuç bulunamadı", duration)
                        else:
                            self.log_test_result("Cümle Arama", f"'{sentence[:30]}...' arama", False, "Model sonucu yok", duration)
                    elif 'error' in data:
                        self.log_test_result("Cümle Arama", f"'{sentence[:30]}...' arama", False, f"API hatası: {data['error']}", duration)
                    else:
                        self.log_test_result("Cümle Arama", f"'{sentence[:30]}...' arama", False, "Beklenmeyen yanıt", duration)
                else:
                    self.log_test_result("Cümle Arama", f"'{sentence[:30]}...' arama", False, f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result("Cümle Arama", f"'{sentence[:30]}...' arama", False, f"İstek hatası: {str(e)}", duration)
                
    def scenario_3_multi_model_comparison(self):
        """Senaryo 3: Çoklu Model Karşılaştırma Testleri"""
        print("\n" + "="*60)
        print("🤖 SENARYO 3: ÇOKLU MODEL KARŞILAŞTIRMA")
        print("="*60)
        
        models = ["dbmdz_bert", "turkcell_roberta", "multilingual_mpnet"]
        test_query = "yapay zeka teknolojisi"
        
        for model in models:
            start_time = time.time()
            
            try:
                payload = {
                    "query": test_query,
                    "type": "sentences",  # Düzeltildi
                    "models": [model],  # Düzeltildi - tek model liste içinde
                    "top_k": 3
                }
                
                response = requests.post(f"{self.base_url}/search", json=payload, timeout=15)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if 'search_results' in data:
                        model_results = data['search_results']
                        if model_results and model in model_results:
                            results = model_results[model]['results']
                            word_count = len(results) if results else 0
                            
                            self.log_test_result(
                                "Model Karşılaştırma", 
                                f"{model} modeli",
                                True,
                                f"Cümle: {word_count} sonuç",
                                duration
                            )
                        else:
                            self.log_test_result("Model Karşılaştırma", f"{model} modeli", False, "Model sonucu yok", duration)
                    elif 'error' in data:
                        self.log_test_result("Model Karşılaştırma", f"{model} modeli", False, f"API hatası: {data['error']}", duration)
                    else:
                        self.log_test_result("Model Karşılaştırma", f"{model} modeli", False, "Beklenmeyen yanıt", duration)
                else:
                    self.log_test_result("Model Karşılaştırma", f"{model} modeli", False, f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result("Model Karşılaştırma", f"{model} modeli", False, f"İstek hatası: {str(e)}", duration)
                
    def scenario_4_qa_system_tests(self):
        """Senaryo 4: Soru-Cevap Sistemi Testleri"""
        print("\n" + "="*60)
        print("❓ SENARYO 4: SORU-CEVAP SİSTEMİ TESTLERİ")
        print("="*60)
        
        test_questions = [
            "Teknoloji nedir?",
            "Eğitim sistemi nasıl gelişir?",
            "Çevre koruma neden önemli?",
            "Yapay zeka nasıl çalışır?",
            "Bilgisayar ne işe yarar?"
        ]
        
        for question in test_questions:
            start_time = time.time()
            
            try:
                payload = {"question": question}
                
                response = requests.post(f"{self.base_url}/qa", json=payload, timeout=30)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if 'answer' in data and not data.get('error'):
                        answer = data.get('answer', '')
                        
                        if answer and len(answer.strip()) > 10:
                            answer_preview = answer[:50] + "..." if len(answer) > 50 else answer
                            context_count = len(data.get('context', []))
                            self.log_test_result(
                                "Q&A Sistemi", 
                                f"'{question}' sorusu",
                                True,
                                f"Cevap: '{answer_preview}' Bağlam: {context_count}",
                                duration
                            )
                        else:
                            self.log_test_result("Q&A Sistemi", f"'{question}' sorusu", False, "Yetersiz cevap", duration)
                    elif 'error' in data:
                        self.log_test_result("Q&A Sistemi", f"'{question}' sorusu", False, f"API hatası: {data['error']}", duration)
                    else:
                        self.log_test_result("Q&A Sistemi", f"'{question}' sorusu", False, "Beklenmeyen yanıt", duration)
                else:
                    self.log_test_result("Q&A Sistemi", f"'{question}' sorusu", False, f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result("Q&A Sistemi", f"'{question}' sorusu", False, f"İstek hatası: {str(e)}", duration)
                
    def scenario_5_relationship_search_tests(self):
        """Senaryo 5: İlişkili Kelime Arama Testleri"""
        print("\n" + "="*60)
        print("🔗 SENARYO 5: İLİŞKİLİ KELİME ARAMA TESTLERİ")
        print("="*60)
        
        test_words = ["teknoloji", "eğitim", "bilim", "sanat", "spor"]
        
        for word in test_words:
            start_time = time.time()
            
            try:
                response = requests.get(f"{self.base_url}/relationships/{word}", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'relationships' in data and not data.get('error'):
                        relationships = data['relationships']
                        relationship_count = sum(len(v) if isinstance(v, list) else 0 for v in relationships.values())
                        relationship_types = list(relationships.keys())
                        
                        self.log_test_result(
                            "İlişki Arama", 
                            f"'{word}' ilişkileri",
                            True,
                            f"{relationship_count} ilişki, türler: {relationship_types}",
                            duration
                        )
                    elif 'error' in data:
                        self.log_test_result("İlişki Arama", f"'{word}' ilişkileri", True, f"İlişki yok: {data['error']}", duration)
                    else:
                        self.log_test_result("İlişki Arama", f"'{word}' ilişkileri", False, "Beklenmeyen yanıt", duration)
                else:
                    self.log_test_result("İlişki Arama", f"'{word}' ilişkileri", False, f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test_result("İlişki Arama", f"'{word}' ilişkileri", False, f"İstek hatası: {str(e)}", duration)
                
    def run_all_scenarios(self):
        """Tüm test senaryolarını çalıştır"""
        print("🚀 ARAMA TABANLI TEST SENARYOLARİ BAŞLATIYOR - DÜZELTILMIŞ VERSIYON")
        print("5 farklı arama senaryosu test edilecek")
        print("-" * 60)
        
        # Sistem durumunu kontrol et
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Sistem erişilebilir - {len(stats.get('available_models', []))} model aktif")
            else:
                print(f"⚠️  Sistem uyarısı: HTTP {response.status_code}")
        except:
            print("❌ Sistem erişilemiyor! Flask uygulamasının çalıştığından emin olun.")
            return
        
        start_time = time.time()
        
        # Test senaryolarını çalıştır
        scenarios = [
            self.scenario_1_word_search_tests,
            self.scenario_2_sentence_search_tests, 
            self.scenario_3_multi_model_comparison,
            self.scenario_4_qa_system_tests,
            self.scenario_5_relationship_search_tests
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            try:
                scenario()
                if i < len(scenarios):
                    print(f"\n⏳ Sonraki senaryoya geçiş için 2 saniye bekleniyor...")
                    time.sleep(2)
            except Exception as e:
                print(f"💥 Senaryo {i} hatası: {e}")
        
        total_duration = time.time() - start_time
        self.generate_search_report(total_duration)
        
    def generate_search_report(self, total_duration):
        """Arama test raporu oluştur"""
        print("\n" + "="*80)
        print("📊 ARAMA TESTLERİ SONUÇ RAPORU - DÜZELTILMIŞ VERSIYON")
        print("="*80)
        
        # Senaryo bazında özet
        scenarios = {}
        for result in self.test_results:
            scenario = result['scenario']
            if scenario not in scenarios:
                scenarios[scenario] = {'total': 0, 'success': 0, 'total_time': 0}
            
            scenarios[scenario]['total'] += 1
            if result['success']:
                scenarios[scenario]['success'] += 1
            scenarios[scenario]['total_time'] += result['duration']
        
        print(f"📈 SENARYO BAŞARI ORANLARI:")
        overall_success = 0
        overall_total = 0
        
        for scenario, stats in scenarios.items():
            success_rate = (stats['success'] / stats['total']) * 100
            avg_time = stats['total_time'] / stats['total']
            status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            
            print(f"   {status_icon} {scenario}: {stats['success']}/{stats['total']} (%{success_rate:.1f}) - Ort: {avg_time:.2f}s")
            overall_success += stats['success']
            overall_total += stats['total']
        
        overall_rate = (overall_success / overall_total) * 100 if overall_total > 0 else 0
        
        print(f"\n🎯 GENEL SONUÇ:")
        print(f"   Toplam Test: {overall_total}")
        print(f"   Başarılı: {overall_success}")
        print(f"   Başarı Oranı: %{overall_rate:.1f}")
        print(f"   Toplam Süre: {total_duration:.2f} saniye")
        
        # JSON rapor kaydet
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_duration': total_duration,
            'overall_success_rate': overall_rate,
            'scenario_summary': scenarios,
            'detailed_results': self.test_results,
            'version': 'DÜZELTILMIŞ API FORMAT'
        }
        
        try:
            with open('search_test_report_fixed.json', 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detaylı rapor kaydedildi: search_test_report_fixed.json")
        except Exception as e:
            print(f"\n❌ Rapor kaydetme hatası: {e}")
        
        print("="*80)

def main():
    """Ana çalıştırma fonksiyonu"""
    print("🎯 RAG Sistemi Arama Tabanlı Test Senaryoları - DÜZELTILMIŞ VERSIYON")
    print("Bu script Flask uygulamasının çalıştığını varsayar (port 5001)")
    print("-" * 60)
    
    # Test runner oluştur ve çalıştır
    test_runner = SearchTestRunner()
    test_runner.run_all_scenarios()

if __name__ == "__main__":
    main()
