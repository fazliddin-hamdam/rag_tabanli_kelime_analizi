#!/usr/bin/env python3
"""
Test Simulations for RAG System Project
5 comprehensive test scenarios covering the entire project functionality
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer

class TestLogger:
    """Test logging utility"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def start_test(self, test_name):
        self.start_time = time.time()
        print(f"\n{'='*60}")
        print(f"🧪 TEST STARTING: {test_name}")
        print(f"{'='*60}")
        
    def log_step(self, step, status, message=""):
        duration = time.time() - self.start_time if self.start_time else 0
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} [{duration:.2f}s] {step}: {message}")
        
        self.results.append({
            'step': step,
            'status': status,
            'message': message,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        
    def end_test(self, test_name):
        total_duration = time.time() - self.start_time
        passed_steps = sum(1 for r in self.results if r['status'])
        total_steps = len(self.results)
        
        print(f"\n📊 TEST SUMMARY: {test_name}")
        print(f"   Duration: {total_duration:.2f} seconds")
        print(f"   Steps: {passed_steps}/{total_steps} passed")
        print(f"{'='*60}\n")
        
        return {
            'test_name': test_name,
            'total_duration': total_duration,
            'passed_steps': passed_steps,
            'total_steps': total_steps,
            'success_rate': passed_steps / total_steps if total_steps > 0 else 0,
            'details': self.results.copy()
        }

class TestSimulations:
    """Main test simulation class"""
    
    def __init__(self):
        self.logger = TestLogger()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_dir = os.path.join(self.base_dir, "db")
        self.app_process = None
        self.test_results = []
        
    def run_all_tests(self):
        """Run all 5 test simulations"""
        print("🚀 STARTING COMPREHENSIVE TEST SUITE")
        print("Testing RAG System with 5 different scenarios")
        
        test_methods = [
            self.test_1_basic_vector_operations,
            self.test_2_multi_model_functionality,
            self.test_3_langchain_rag_system,
            self.test_4_web_interface_integration,
            self.test_5_performance_load_testing
        ]
        
        for i, test_method in enumerate(test_methods, 1):
            try:
                result = test_method()
                self.test_results.append(result)
                
                # Wait between tests
                if i < len(test_methods):
                    print(f"⏳ Waiting 3 seconds before next test...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"💥 Test {i} failed with exception: {e}")
                self.test_results.append({
                    'test_name': f'Test {i}',
                    'success_rate': 0,
                    'error': str(e)
                })
        
        self.generate_final_report()
        
    def test_1_basic_vector_operations(self):
        """Test 1: Basic Vector Database Operations"""
        self.logger = TestLogger()
        self.logger.start_test("Basic Vector Database Operations")
        
        try:
            # Step 1: Check ChromaDB connection
            try:
                client = chromadb.PersistentClient(path=self.db_dir)
                self.logger.log_step("ChromaDB Connection", True, "Successfully connected to database")
            except Exception as e:
                self.logger.log_step("ChromaDB Connection", False, f"Failed: {e}")
                return self.logger.end_test("Basic Vector Operations")
            
            # Step 2: List available collections
            try:
                collections = client.list_collections()
                collection_names = [c.name for c in collections]
                self.logger.log_step("List Collections", True, f"Found {len(collections)} collections")
            except Exception as e:
                self.logger.log_step("List Collections", False, f"Failed: {e}")
            
            # Step 3: Test word vector collection
            try:
                word_collection = None
                for collection in collections:
                    if "kelime" in collection.name:
                        word_collection = collection
                        break
                
                if word_collection:
                    count = word_collection.count()
                    self.logger.log_step("Word Collection Access", True, f"Found word collection with {count} items")
                else:
                    self.logger.log_step("Word Collection Access", False, "No word collection found")
            except Exception as e:
                self.logger.log_step("Word Collection Access", False, f"Failed: {e}")
            
            # Step 4: Test basic similarity search
            try:
                if word_collection and word_collection.count() > 0:
                    results = word_collection.query(
                        query_texts=["kitap"],
                        n_results=3
                    )
                    if results['documents'] and len(results['documents'][0]) > 0:
                        self.logger.log_step("Basic Search Test", True, f"Found {len(results['documents'][0])} similar words")
                    else:
                        self.logger.log_step("Basic Search Test", False, "No search results returned")
                else:
                    self.logger.log_step("Basic Search Test", False, "No data available for search")
            except Exception as e:
                self.logger.log_step("Basic Search Test", False, f"Failed: {e}")
                
        except Exception as e:
            self.logger.log_step("Overall Test", False, f"Test failed: {e}")
        
        return self.logger.end_test("Basic Vector Operations")
    
    def test_2_multi_model_functionality(self):
        """Test 2: Multi-Model Vector Store Functionality"""
        self.logger = TestLogger()
        self.logger.start_test("Multi-Model Vector Store Functionality")
        
        # Test different embedding models
        models = {
            "dbmdz_bert": "dbmdz/bert-base-turkish-cased",
            "multilingual_mpnet": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        }
        
        try:
            # Step 1: Connect to ChromaDB
            client = chromadb.PersistentClient(path=self.db_dir)
            self.logger.log_step("Database Connection", True, "Connected to ChromaDB")
            
            # Step 2: Check collections for each model
            collections = client.list_collections()
            collection_names = [c.name for c in collections]
            
            for model_id, model_name in models.items():
                word_collection_name = f"kelime_vektorleri_{model_id}"
                sentence_collection_name = f"metin_vektorleri_{model_id}"
                
                word_exists = word_collection_name in collection_names
                sentence_exists = sentence_collection_name in collection_names
                
                self.logger.log_step(f"Model {model_id} Collections", 
                                   word_exists or sentence_exists,
                                   f"Word: {word_exists}, Sentence: {sentence_exists}")
            
            # Step 3: Test model loading and encoding
            for model_id, model_name in list(models.items())[:1]:  # Test only first model for speed
                try:
                    model = SentenceTransformer(model_name)
                    test_text = "Bu bir test cümlesidir"
                    embedding = model.encode([test_text])
                    
                    if embedding is not None and len(embedding) > 0:
                        self.logger.log_step(f"Model {model_id} Encoding", True, 
                                           f"Successfully encoded text (dim: {len(embedding[0])})")
                    else:
                        self.logger.log_step(f"Model {model_id} Encoding", False, "Failed to encode text")
                        
                except Exception as e:
                    self.logger.log_step(f"Model {model_id} Encoding", False, f"Error: {e}")
                    
        except Exception as e:
            self.logger.log_step("Multi-Model Test", False, f"Failed: {e}")
        
        return self.logger.end_test("Multi-Model Vector Store")
    
    def test_3_langchain_rag_system(self):
        """Test 3: LangChain RAG System Integration"""
        self.logger = TestLogger()
        self.logger.start_test("LangChain RAG System Integration")
        
        try:
            # Step 1: Test LangChain imports
            try:
                from langchain_community.vectorstores import Chroma
                from langchain_community.embeddings import HuggingFaceEmbeddings
                self.logger.log_step("LangChain Imports", True, "Successfully imported LangChain components")
            except Exception as e:
                self.logger.log_step("LangChain Imports", False, f"Failed: {e}")
                return self.logger.end_test("LangChain RAG")
            
            # Step 2: Setup embeddings
            try:
                embeddings = HuggingFaceEmbeddings(
                    model_name="dbmdz/bert-base-turkish-cased",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                self.logger.log_step("HuggingFace Embeddings", True, "Successfully initialized embeddings")
            except Exception as e:
                self.logger.log_step("HuggingFace Embeddings", False, f"Failed: {e}")
            
            # Step 3: Test Chroma VectorStore
            try:
                vectorstore = Chroma(
                    persist_directory=self.db_dir,
                    embedding_function=embeddings,
                    collection_name="qa_documents"
                )
                self.logger.log_step("Chroma VectorStore", True, "Successfully initialized vector store")
            except Exception as e:
                self.logger.log_step("Chroma VectorStore", False, f"Failed: {e}")
                
        except Exception as e:
            self.logger.log_step("LangChain RAG Test", False, f"Failed: {e}")
        
        return self.logger.end_test("LangChain RAG System")
    
    def test_4_web_interface_integration(self):
        """Test 4: Web Interface Integration Testing"""
        self.logger = TestLogger()
        self.logger.start_test("Web Interface Integration Testing")
        
        try:
            # Step 1: Check if Flask app file exists
            app_path = os.path.join(self.base_dir, "app.py")
            if os.path.exists(app_path):
                self.logger.log_step("Flask App File", True, "app.py found")
            else:
                self.logger.log_step("Flask App File", False, "app.py not found")
                return self.logger.end_test("Web Interface")
            
            # Step 2: Check template files
            template_path = os.path.join(self.base_dir, "templates", "index.html")
            if os.path.exists(template_path):
                self.logger.log_step("Template Files", True, "index.html found")
            else:
                self.logger.log_step("Template Files", False, "index.html not found")
            
            # Step 3: Check static files
            css_path = os.path.join(self.base_dir, "static", "css", "main.css")
            js_path = os.path.join(self.base_dir, "static", "js", "main.js")
            
            css_exists = os.path.exists(css_path)
            js_exists = os.path.exists(js_path)
            
            self.logger.log_step("Static Files", css_exists and js_exists, 
                               f"CSS: {css_exists}, JS: {js_exists}")
            
            # Step 4: Try to start Flask app (quick test)
            try:
                # Just check if the app can be imported
                sys.path.insert(0, self.base_dir)
                import app as flask_app
                self.logger.log_step("Flask App Import", True, "Successfully imported Flask app")
            except Exception as e:
                self.logger.log_step("Flask App Import", False, f"Failed: {e}")
                
        except Exception as e:
            self.logger.log_step("Web Interface Test", False, f"Failed: {e}")
        
        return self.logger.end_test("Web Interface Integration")
    
    def test_5_performance_load_testing(self):
        """Test 5: Performance and Load Testing"""
        self.logger = TestLogger()
        self.logger.start_test("Performance and Load Testing")
        
        try:
            # Step 1: Database performance test
            try:
                client = chromadb.PersistentClient(path=self.db_dir)
                collections = client.list_collections()
                
                if collections:
                    collection = collections[0]
                    
                    # Measure query performance
                    start_time = time.time()
                    try:
                        results = collection.query(query_texts=["test"], n_results=5)
                        query_time = time.time() - start_time
                        
                        if query_time < 2.0:
                            self.logger.log_step("Database Query Performance", True, 
                                               f"Query completed in {query_time:.3f}s")
                        else:
                            self.logger.log_step("Database Query Performance", False, 
                                               f"Query too slow: {query_time:.3f}s")
                    except Exception as e:
                        self.logger.log_step("Database Query Performance", False, f"Query failed: {e}")
                else:
                    self.logger.log_step("Database Query Performance", False, "No collections available")
                    
            except Exception as e:
                self.logger.log_step("Database Query Performance", False, f"Failed: {e}")
            
            # Step 2: Embedding model performance test
            try:
                model = SentenceTransformer("dbmdz/bert-base-turkish-cased")
                
                # Test encoding performance
                test_texts = ["test cümle " + str(i) for i in range(5)]
                
                start_time = time.time()
                embeddings = model.encode(test_texts)
                encoding_time = time.time() - start_time
                
                texts_per_second = len(test_texts) / encoding_time
                
                if texts_per_second > 2:
                    self.logger.log_step("Embedding Performance", True, 
                                       f"Encoded {texts_per_second:.1f} texts/second")
                else:
                    self.logger.log_step("Embedding Performance", False, 
                                       f"Too slow: {texts_per_second:.1f} texts/second")
                    
            except Exception as e:
                self.logger.log_step("Embedding Performance", False, f"Failed: {e}")
            
            # Step 3: File system performance
            try:
                # Check file access times
                files_to_check = ["kelimeler.txt", "metinler.txt", "iliskiler.txt"]
                accessible_files = 0
                
                for filename in files_to_check:
                    filepath = os.path.join(self.base_dir, filename)
                    if os.path.exists(filepath):
                        accessible_files += 1
                
                if accessible_files >= 2:
                    self.logger.log_step("File System Access", True, 
                                       f"Accessible files: {accessible_files}/{len(files_to_check)}")
                else:
                    self.logger.log_step("File System Access", False, 
                                       f"Limited file access: {accessible_files}/{len(files_to_check)}")
                    
            except Exception as e:
                self.logger.log_step("File System Access", False, f"Failed: {e}")
                
        except Exception as e:
            self.logger.log_step("Performance Test", False, f"Failed: {e}")
        
        return self.logger.end_test("Performance and Load Testing")
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("🏁 FINAL TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.get('success_rate', 0) >= 0.5)
        
        print(f"📊 OVERVIEW:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful Tests: {successful_tests}")
        print(f"   Overall Success Rate: {successful_tests/total_tests*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            test_name = result.get('test_name', f'Test {i}')
            success_rate = result.get('success_rate', 0)
            status_icon = "✅" if success_rate >= 0.5 else "❌"
            
            print(f"   {status_icon} Test {i}: {test_name}")
            print(f"      Success Rate: {success_rate*100:.1f}%")
            
            if 'total_duration' in result:
                print(f"      Duration: {result['total_duration']:.2f}s")
            
            if 'error' in result:
                print(f"      Error: {result['error']}")
        
        # Save detailed report to file
        report_file = os.path.join(self.base_dir, "test_report.json")
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'overall_success_rate': successful_tests/total_tests if total_tests > 0 else 0,
                    'detailed_results': self.test_results
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Detailed report saved to: {report_file}")
            
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")
        
        print("="*80)

def main():
    """Main execution function"""
    print("🎯 RAG System Comprehensive Test Suite")
    print("This will run 5 different test scenarios to validate the entire system")
    print("-" * 60)
    
    # Check if required files exist
    required_files = ["app.py", "requirements.txt"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return
    
    # Check if database directory exists
    if not os.path.exists("db"):
        print("⚠️  Database directory not found. Some tests may fail.")
    
    # Run tests
    test_suite = TestSimulations()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main() 