"""
Comprehensive Embedding Evaluation Script
Tests both hotel and visa embedding models with known ground truth
Compares retrieval accuracy and provides detailed metrics
Compares performance between different embedding models

Run this from M3/Evaluations directory:
    python test_embeddings_comprehensive.py
    python test_embeddings_comprehensive.py --models all-MiniLM-L6-v2 all-mpnet-base-v2
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import time
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.embedding_generator import EmbeddingGenerator
from components.vector_searcher import VectorSearcher


class EmbeddingEvaluator:
    """Evaluate embedding model performance with ground truth data"""
    
    def __init__(self, ground_truth_path: str = "embedding_ground_truth.json", model_name: str = None):
        """
        Initialize evaluator
        
        Args:
            ground_truth_path: Path to ground truth JSON file
            model_name: Embedding model name (if None, uses default)
        """
        self.generator = EmbeddingGenerator(model_name=model_name)
        self.model_name = self.generator.get_model_name()
        
        # Load embeddings for the specific model
        self.searcher = self._load_searcher_for_model(self.model_name)
        
        # Load ground truth
        with open(ground_truth_path, 'r') as f:
            self.ground_truth = json.load(f)
        
        self.hotel_queries = self.ground_truth['hotel_queries']
        self.visa_queries = self.ground_truth['visa_queries']
        
        # Timing statistics
        self.timing_stats = {
            'embedding_times': [],
            'search_times': [],
            'total_times': []
        }
        
        print(f"✓ Loaded {len(self.hotel_queries)} hotel test queries")
        print(f"✓ Loaded {len(self.visa_queries)} visa test queries")
        print(f"✓ Embedding model: {self.generator.get_model_name()}")
        print(f"✓ Embedding dimension: {self.generator.get_dimension()}")
        print(f"✓ FAISS indexes loaded for: {self.model_name}\n")
    
    def _load_searcher_for_model(self, model_name: str) -> VectorSearcher:
        """
        Load VectorSearcher with correct FAISS files for the model
        
        Args:
            model_name: Embedding model name
            
        Returns:
            VectorSearcher instance with model-specific indexes
        """
        searcher = VectorSearcher()
        
        # Load model-specific embedding files
        if 'mpnet' in model_name.lower():
            # Load mpnet model files
            searcher._load_model_indexes('_mpnet')
        else:
            # Load default (MiniLM) model files
            searcher._load_model_indexes('')
        
        return searcher
    
    def _measure_embedding_time(self, query: str) -> Tuple[List[float], float]:
        """
        Measure time to generate embedding
        
        Args:
            query: Query text
            
        Returns:
            Tuple of (embedding, time_in_seconds)
        """
        start_time = time.time()
        embedding = self.generator.embed(query)
        elapsed_time = time.time() - start_time
        return embedding, elapsed_time
    
    def _measure_search_time(self, embedding: List[float], limit: int = 5, intent: str = None) -> Tuple[List[Dict], float]:
        """
        Measure time to search embeddings
        
        Args:
            embedding: Query embedding
            limit: Number of results to retrieve
            intent: Query intent for routing
            
        Returns:
            Tuple of (search_results, time_in_seconds)
        """
        start_time = time.time()
        results = self.searcher.search(
            embedding=embedding,
            limit=limit,
            threshold=0.0,
            intent=intent
        )
        elapsed_time = time.time() - start_time
        return results, elapsed_time
    
    def test_hotel_embeddings(self, top_k: int = 5) -> Dict[str, Any]:
        """
        Test hotel embedding retrieval
        
        Args:
            top_k: Number of top results to retrieve
            
        Returns:
            Results dictionary with metrics
        """
        print("=" * 80)
        print("TESTING HOTEL EMBEDDINGS")
        print("=" * 80)
        
        results = {
            'total_queries': len(self.hotel_queries),
            'top1_correct': 0,
            'top3_correct': 0,
            'top5_correct': 0,
            'failed_queries': [],
            'query_details': []
        }
        
        for i, test_case in enumerate(self.hotel_queries, 1):
            query_id = test_case['id']
            query = test_case['query']
            expected_top1 = test_case['expected_top1']
            expected_top3 = test_case.get('expected_top3', [expected_top1])
            description = test_case['description']
            
            print(f"\n[{i}/{len(self.hotel_queries)}] Query: {query}")
            print(f"Expected: {description}")
            
            # Generate embedding and search with timing
            embedding, embed_time = self._measure_embedding_time(query)
            search_results, search_time = self._measure_search_time(
                embedding,
                limit=top_k,
                intent="HotelSearch"
            )
            total_time = embed_time + search_time
            
            # Track timing
            self.timing_stats['embedding_times'].append(embed_time)
            self.timing_stats['search_times'].append(search_time)
            self.timing_stats['total_times'].append(total_time)
            
            # Extract hotel IDs from results
            retrieved_ids = [str(r.get('hotel_id', '')) for r in search_results]
            
            # Check accuracy
            top1_match = retrieved_ids[0] == expected_top1 if retrieved_ids else False
            top3_match = any(rid in expected_top3 for rid in retrieved_ids[:3])
            top5_match = any(rid in expected_top3 for rid in retrieved_ids[:5])
            
            if top1_match:
                results['top1_correct'] += 1
            if top3_match:
                results['top3_correct'] += 1
            if top5_match:
                results['top5_correct'] += 1
            
            # Print results
            print(f"Retrieved (Top-{min(5, len(retrieved_ids))}):")
            for j, result in enumerate(search_results[:5], 1):
                hotel_id = result.get('hotel_id', 'N/A')
                hotel_name = result.get('hotel_name', 'N/A')
                city = result.get('city', 'N/A')
                similarity = result.get('similarity_score', 0)
                match_marker = "✓" if str(hotel_id) in expected_top3 else "✗"
                print(f"  [{j}] {match_marker} ID:{hotel_id} | {hotel_name} ({city}) | Sim: {similarity:.4f}")
            
            # Status and timing
            status = "✓ PASS" if top1_match else ("⚠ Top-3" if top3_match else "✗ FAIL")
            print(f"Status: {status}")
            print(f"⏱️  Embedding: {embed_time*1000:.2f}ms | Search: {search_time*1000:.2f}ms | Total: {total_time*1000:.2f}ms")
            
            # Record details
            query_detail = {
                'query_id': query_id,
                'query': query,
                'expected_top1': expected_top1,
                'expected_top3': expected_top3,
                'retrieved_top5': retrieved_ids[:5],
                'top1_correct': top1_match,
                'top3_correct': top3_match,
                'top5_correct': top5_match,
                'similarities': [r.get('similarity_score', 0) for r in search_results[:5]]
            }
            results['query_details'].append(query_detail)
            
            if not top3_match:
                results['failed_queries'].append({
                    'query_id': query_id,
                    'query': query,
                    'expected': expected_top3,
                    'retrieved': retrieved_ids[:5]
                })
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.5)
        
        # Calculate accuracy metrics
        results['top1_accuracy'] = results['top1_correct'] / results['total_queries']
        results['top3_accuracy'] = results['top3_correct'] / results['total_queries']
        results['top5_accuracy'] = results['top5_correct'] / results['total_queries']
        
        # Calculate timing metrics for hotel results
        if self.timing_stats['total_times']:
            results['avg_embedding_time_ms'] = (sum(self.timing_stats['embedding_times']) / len(self.timing_stats['embedding_times'])) * 1000
            results['avg_search_time_ms'] = (sum(self.timing_stats['search_times']) / len(self.timing_stats['search_times'])) * 1000
            results['avg_total_time_ms'] = (sum(self.timing_stats['total_times']) / len(self.timing_stats['total_times'])) * 1000
            results['min_total_time_ms'] = min(self.timing_stats['total_times']) * 1000
            results['max_total_time_ms'] = max(self.timing_stats['total_times']) * 1000
        
        # Reset timing stats for next test type
        self.timing_stats = {
            'embedding_times': [],
            'search_times': [],
            'total_times': []
        }
        
        return results
    
    def test_visa_embeddings(self, top_k: int = 5) -> Dict[str, Any]:
        """
        Test visa embedding retrieval
        
        Args:
            top_k: Number of top results to retrieve
            
        Returns:
            Results dictionary with metrics
        """
        print("\n" + "=" * 80)
        print("TESTING VISA EMBEDDINGS")
        print("=" * 80)
        
        results = {
            'total_queries': len(self.visa_queries),
            'top1_correct': 0,
            'top3_correct': 0,
            'top5_correct': 0,
            'failed_queries': [],
            'query_details': []
        }
        
        for i, test_case in enumerate(self.visa_queries, 1):
            query_id = test_case['id']
            query = test_case['query']
            expected_top1 = test_case['expected_top1']
            expected_top3 = test_case.get('expected_top3', [expected_top1])
            description = test_case['description']
            
            print(f"\n[{i}/{len(self.visa_queries)}] Query: {query}")
            print(f"Expected: {description}")
            
            # Generate embedding and search with timing
            embedding, embed_time = self._measure_embedding_time(query)
            search_results, search_time = self._measure_search_time(
                embedding,
                limit=top_k,
                intent="VisaQuestion"
            )
            total_time = embed_time + search_time
            
            # Track timing
            self.timing_stats['embedding_times'].append(embed_time)
            self.timing_stats['search_times'].append(search_time)
            self.timing_stats['total_times'].append(total_time)
            
            # Extract visa IDs from results
            retrieved_ids = []
            for r in search_results:
                from_country = r.get('from_country', '')
                to_country = r.get('to_country', '')
                visa_id = f"{from_country}_to_{to_country}"
                retrieved_ids.append(visa_id)
            
            # Check accuracy
            top1_match = retrieved_ids[0] == expected_top1 if retrieved_ids else False
            top3_match = any(rid in expected_top3 for rid in retrieved_ids[:3])
            top5_match = any(rid in expected_top3 for rid in retrieved_ids[:5])
            
            if top1_match:
                results['top1_correct'] += 1
            if top3_match:
                results['top3_correct'] += 1
            if top5_match:
                results['top5_correct'] += 1
            
            # Print results
            print(f"Retrieved (Top-{min(5, len(retrieved_ids))}):")
            for j, result in enumerate(search_results[:5], 1):
                from_country = result.get('from_country', 'N/A')
                to_country = result.get('to_country', 'N/A')
                visa_type = result.get('visa_type', 'N/A')
                similarity = result.get('similarity_score', 0)
                visa_id = f"{from_country}_to_{to_country}"
                match_marker = "✓" if visa_id in expected_top3 else "✗"
                print(f"  [{j}] {match_marker} {from_country} → {to_country} | {visa_type} | Sim: {similarity:.4f}")
            
            # Status and timing
            status = "✓ PASS" if top1_match else ("⚠ Top-3" if top3_match else "✗ FAIL")
            print(f"Status: {status}")
            print(f"⏱️  Embedding: {embed_time*1000:.2f}ms | Search: {search_time*1000:.2f}ms | Total: {total_time*1000:.2f}ms")
            
            # Record details
            query_detail = {
                'query_id': query_id,
                'query': query,
                'expected_top1': expected_top1,
                'expected_top3': expected_top3,
                'retrieved_top5': retrieved_ids[:5],
                'top1_correct': top1_match,
                'top3_correct': top3_match,
                'top5_correct': top5_match,
                'similarities': [r.get('similarity_score', 0) for r in search_results[:5]]
            }
            results['query_details'].append(query_detail)
            
            if not top3_match:
                results['failed_queries'].append({
                    'query_id': query_id,
                    'query': query,
                    'expected': expected_top3,
                    'retrieved': retrieved_ids[:5]
                })
            
            # Small delay
            time.sleep(0.5)
        
        # Calculate accuracy metrics
        results['top1_accuracy'] = results['top1_correct'] / results['total_queries']
        results['top3_accuracy'] = results['top3_correct'] / results['total_queries']
        results['top5_accuracy'] = results['top5_correct'] / results['total_queries']
        
        # Calculate timing metrics for visa results
        if self.timing_stats['total_times']:
            results['avg_embedding_time_ms'] = (sum(self.timing_stats['embedding_times']) / len(self.timing_stats['embedding_times'])) * 1000
            results['avg_search_time_ms'] = (sum(self.timing_stats['search_times']) / len(self.timing_stats['search_times'])) * 1000
            results['avg_total_time_ms'] = (sum(self.timing_stats['total_times']) / len(self.timing_stats['total_times'])) * 1000
            results['min_total_time_ms'] = min(self.timing_stats['total_times']) * 1000
            results['max_total_time_ms'] = max(self.timing_stats['total_times']) * 1000
        
        return results
    
    def print_summary(self, hotel_results: Dict, visa_results: Dict, model_name: str = None):
        """Print summary statistics and comparison"""
        print("\n" + "=" * 80)
        if model_name:
            print(f"EVALUATION SUMMARY - {model_name}")
        else:
            print("EVALUATION SUMMARY")
        print("=" * 80)
        
        print("\n📊 HOTEL EMBEDDINGS RESULTS:")
        print(f"  Total Queries: {hotel_results['total_queries']}")
        print(f"  Top-1 Accuracy: {hotel_results['top1_accuracy']:.2%} ({hotel_results['top1_correct']}/{hotel_results['total_queries']})")
        print(f"  Top-3 Accuracy: {hotel_results['top3_accuracy']:.2%} ({hotel_results['top3_correct']}/{hotel_results['total_queries']})")
        print(f"  Top-5 Accuracy: {hotel_results['top5_accuracy']:.2%} ({hotel_results['top5_correct']}/{hotel_results['total_queries']})")
        print(f"  Failed Queries: {len(hotel_results['failed_queries'])}")
        print(f"\n  ⏱️  PERFORMANCE METRICS:")
        print(f"    Avg Embedding Time: {hotel_results['avg_embedding_time_ms']:.2f}ms")
        print(f"    Avg Search Time: {hotel_results['avg_search_time_ms']:.2f}ms")
        print(f"    Avg Total Time: {hotel_results['avg_total_time_ms']:.2f}ms")
        print(f"    Min/Max Total Time: {hotel_results['min_total_time_ms']:.2f}ms / {hotel_results['max_total_time_ms']:.2f}ms")
        
        print("\n📊 VISA EMBEDDINGS RESULTS:")
        print(f"  Total Queries: {visa_results['total_queries']}")
        print(f"  Top-1 Accuracy: {visa_results['top1_accuracy']:.2%} ({visa_results['top1_correct']}/{visa_results['total_queries']})")
        print(f"  Top-3 Accuracy: {visa_results['top3_accuracy']:.2%} ({visa_results['top3_correct']}/{visa_results['total_queries']})")
        print(f"  Top-5 Accuracy: {visa_results['top5_accuracy']:.2%} ({visa_results['top5_correct']}/{visa_results['total_queries']})")
        print(f"  Failed Queries: {len(visa_results['failed_queries'])}")
        print(f"\n  ⏱️  PERFORMANCE METRICS:")
        print(f"    Avg Embedding Time: {visa_results['avg_embedding_time_ms']:.2f}ms")
        print(f"    Avg Search Time: {visa_results['avg_search_time_ms']:.2f}ms")
        print(f"    Avg Total Time: {visa_results['avg_total_time_ms']:.2f}ms")
        print(f"    Min/Max Total Time: {visa_results['min_total_time_ms']:.2f}ms / {visa_results['max_total_time_ms']:.2f}ms")
        
        # Comparison
        print("\n📈 COMPARISON (Hotel vs Visa):")
        print(f"  Top-1 Accuracy: {hotel_results['top1_accuracy']:.2%} vs {visa_results['top1_accuracy']:.2%}")
        print(f"  Top-3 Accuracy: {hotel_results['top3_accuracy']:.2%} vs {visa_results['top3_accuracy']:.2%}")
        
        if hotel_results['top1_accuracy'] > visa_results['top1_accuracy']:
            diff = hotel_results['top1_accuracy'] - visa_results['top1_accuracy']
            print(f"  → Hotel embeddings perform {diff:.2%} better on Top-1 accuracy")
        elif visa_results['top1_accuracy'] > hotel_results['top1_accuracy']:
            diff = visa_results['top1_accuracy'] - hotel_results['top1_accuracy']
            print(f"  → Visa embeddings perform {diff:.2%} better on Top-1 accuracy")
        else:
            print(f"  → Both have equal Top-1 accuracy")
        
        # Failed queries details
        if hotel_results['failed_queries']:
            print(f"\n❌ HOTEL QUERIES THAT FAILED (Top-3):")
            for failure in hotel_results['failed_queries']:
                print(f"  Query {failure['query_id']}: {failure['query']}")
                print(f"    Expected: {failure['expected']}")
                print(f"    Retrieved: {failure['retrieved']}")
        
        if visa_results['failed_queries']:
            print(f"\n❌ VISA QUERIES THAT FAILED (Top-3):")
            for failure in visa_results['failed_queries']:
                print(f"  Query {failure['query_id']}: {failure['query']}")
                print(f"    Expected: {failure['expected']}")
                print(f"    Retrieved: {failure['retrieved']}")
    
    def save_results(self, hotel_results: Dict, visa_results: Dict, output_file: str = "embedding_evaluation_results.json"):
        """Save detailed results to JSON file"""
        output = {
            'embedding_model': self.generator.get_model_name(),
            'embedding_dimension': self.generator.get_dimension(),
            'hotel_results': hotel_results,
            'visa_results': visa_results,
            'summary': {
                'hotel_top1_accuracy': hotel_results['top1_accuracy'],
                'hotel_top3_accuracy': hotel_results['top3_accuracy'],
                'visa_top1_accuracy': visa_results['top1_accuracy'],
                'visa_top3_accuracy': visa_results['top3_accuracy']
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"✓ Results saved to {output_file}")
        
def compare_models(model_names: List[str]):
    """
    Compare multiple embedding models
    
    Args:
        model_names: List of model names to compare
    """
    print("=" * 80)
    print("COMPREHENSIVE EMBEDDING EVALUATION - MODEL COMPARISON")
    print("=" * 80)
    print(f"Comparing {len(model_names)} models: {', '.join(model_names)}\n")
    
    all_results = {}
    
    for model_name in model_names:
        print("\n" + "=" * 80)
        print(f"TESTING MODEL: {model_name}")
        print("=" * 80)
        print()
        
        # Initialize evaluator with specific model
        evaluator = EmbeddingEvaluator(model_name=model_name)
        
        # Test hotel embeddings
        hotel_results = evaluator.test_hotel_embeddings(top_k=5)
        
        # Test visa embeddings
        visa_results = evaluator.test_visa_embeddings(top_k=5)
        
        # Print summary
        evaluator.print_summary(hotel_results, visa_results, model_name)
        
        # Save results
        output_file = f"embedding_evaluation_results_{model_name.replace('/', '_')}.json"
        evaluator.save_results(hotel_results, visa_results, output_file)
        
        # Store for comparison
        all_results[model_name] = {
            'hotel': hotel_results,
            'visa': visa_results
        }
    
    # Print model comparison
    print("\n" + "=" * 80)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 80)
    
    print("\n📊 HOTEL EMBEDDINGS - MODEL COMPARISON:")
    print(f"{'Model':<30} {'Top-1':>10} {'Top-3':>10} {'Avg Time':>12}")
    print("-" * 80)
    for model_name, results in all_results.items():
        hotel = results['hotel']
        avg_time = hotel.get('avg_total_time_ms', 0)
        print(f"{model_name:<30} {hotel['top1_accuracy']:>9.2%} {hotel['top3_accuracy']:>9.2%} {avg_time:>11.2f}ms")
    
    print("\n📊 VISA EMBEDDINGS - MODEL COMPARISON:")
    print(f"{'Model':<30} {'Top-1':>10} {'Top-3':>10} {'Avg Time':>12}")
    print("-" * 80)
    for model_name, results in all_results.items():
        visa = results['visa']
        avg_time = visa.get('avg_total_time_ms', 0)
        print(f"{model_name:<30} {visa['top1_accuracy']:>9.2%} {visa['top3_accuracy']:>9.2%} {avg_time:>11.2f}ms")
    
    # Determine best models
    print("\n🏆 BEST MODELS:")
    best_hotel_model = max(all_results.items(), key=lambda x: x[1]['hotel']['top1_accuracy'])
    best_visa_model = max(all_results.items(), key=lambda x: x[1]['visa']['top1_accuracy'])
    
    print(f"  Best for Hotels: {best_hotel_model[0]} ({best_hotel_model[1]['hotel']['top1_accuracy']:.2%} Top-1)")
    print(f"  Best for Visas:  {best_visa_model[0]} ({best_visa_model[1]['visa']['top1_accuracy']:.2%} Top-1)")
    
    # Save comparison results
    comparison_output = {
        'models_tested': model_names,
        'results_by_model': {
            model: {
                'hotel_top1': results['hotel']['top1_accuracy'],
                'hotel_top3': results['hotel']['top3_accuracy'],
                'visa_top1': results['visa']['top1_accuracy'],
                'visa_top3': results['visa']['top3_accuracy']
            }
            for model, results in all_results.items()
        },
        'best_models': {
            'hotel': best_hotel_model[0],
            'visa': best_visa_model[0]
        }
    }
    
    with open('embedding_model_comparison.json', 'w') as f:
        json.dump(comparison_output, f, indent=2)
    
    print(f"\n✓ Comparison results saved to embedding_model_comparison.json")
    
    # Generate comprehensive text report
    generate_text_report(all_results, model_names, "embedding_comparison_report.txt")


def generate_text_report(all_results: Dict, model_names: List[str], output_file: str = "embedding_comparison_report.txt"):
    """
    Generate a comprehensive text report of model comparison
    
    Args:
        all_results: Dictionary of results by model
        model_names: List of model names tested
        output_file: Output filename for the report
    """
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write("COMPREHENSIVE EMBEDDING EVALUATION - DETAILED REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {timestamp}\n")
        f.write(f"Models Compared: {', '.join(model_names)}\n")
        
        # Calculate total test cases
        first_model = list(all_results.values())[0]
        total_hotel = first_model['hotel']['total_queries']
        total_visa = first_model['visa']['total_queries']
        f.write(f"Total Test Cases: {total_hotel + total_visa} ({total_hotel} Hotel + {total_visa} Visa)\n\n")
        
        # Executive Summary
        f.write("=" * 80 + "\n")
        f.write("EXECUTIVE SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        for model_name in model_names:
            results = all_results[model_name]
            hotel = results['hotel']
            visa = results['visa']
            
            f.write(f"Model: {model_name}\n")
            f.write(f"{'─' * 80}\n")
            f.write(f"  Hotel Embeddings:\n")
            f.write(f"    - Top-1 Accuracy: {hotel['top1_accuracy']:.2%} ({hotel['top1_correct']}/{hotel['total_queries']} correct)\n")
            f.write(f"    - Top-3 Accuracy: {hotel['top3_accuracy']:.2%} ({hotel['top3_correct']}/{hotel['total_queries']} correct)\n")
            f.write(f"    - Top-5 Accuracy: {hotel['top5_accuracy']:.2%} ({hotel['top5_correct']}/{hotel['total_queries']} correct)\n")
            f.write(f"    - Failed Queries: {len(hotel['failed_queries'])}\n")
            f.write(f"    - Avg Total Time: {hotel.get('avg_total_time_ms', 0):.2f}ms\n")
            f.write(f"\n")
            f.write(f"  Visa Embeddings:\n")
            f.write(f"    - Top-1 Accuracy: {visa['top1_accuracy']:.2%} ({visa['top1_correct']}/{visa['total_queries']} correct)\n")
            f.write(f"    - Top-3 Accuracy: {visa['top3_accuracy']:.2%} ({visa['top3_correct']}/{visa['total_queries']} correct)\n")
            f.write(f"    - Top-5 Accuracy: {visa['top5_accuracy']:.2%} ({visa['top5_correct']}/{visa['total_queries']} correct)\n")
            f.write(f"    - Failed Queries: {len(visa['failed_queries'])}\n")
            f.write(f"    - Avg Total Time: {visa.get('avg_total_time_ms', 0):.2f}ms\n")
            f.write(f"\n")
        
        # Model Comparison Table
        f.write("\n" + "=" * 80 + "\n")
        f.write("MODEL COMPARISON\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("HOTEL EMBEDDINGS:\n")
        f.write(f"{'Model':<30} {'Top-1':>10} {'Top-3':>10} {'Top-5':>10} {'Avg Time':>12}\n")
        f.write("-" * 80 + "\n")
        for model_name in model_names:
            hotel = all_results[model_name]['hotel']
            avg_time = hotel.get('avg_total_time_ms', 0)
            f.write(f"{model_name:<30} {hotel['top1_accuracy']:>9.2%} {hotel['top3_accuracy']:>9.2%} {hotel['top5_accuracy']:>9.2%} {avg_time:>11.2f}ms\n")
        
        f.write("\nVISA EMBEDDINGS:\n")
        f.write(f"{'Model':<30} {'Top-1':>10} {'Top-3':>10} {'Top-5':>10} {'Avg Time':>12}\n")
        f.write("-" * 80 + "\n")
        for model_name in model_names:
            visa = all_results[model_name]['visa']
            avg_time = visa.get('avg_total_time_ms', 0)
            f.write(f"{model_name:<30} {visa['top1_accuracy']:>9.2%} {visa['top3_accuracy']:>9.2%} {visa['top5_accuracy']:>9.2%} {avg_time:>11.2f}ms\n")
        
        # Best Models
        f.write("\n" + "=" * 80 + "\n")
        f.write("BEST MODELS\n")
        f.write("=" * 80 + "\n\n")
        
        best_hotel_model = max(all_results.items(), key=lambda x: x[1]['hotel']['top1_accuracy'])
        best_visa_model = max(all_results.items(), key=lambda x: x[1]['visa']['top1_accuracy'])
        
        f.write(f"Best for Hotels: {best_hotel_model[0]}\n")
        f.write(f"  - Top-1 Accuracy: {best_hotel_model[1]['hotel']['top1_accuracy']:.2%}\n")
        f.write(f"  - Avg Time: {best_hotel_model[1]['hotel'].get('avg_total_time_ms', 0):.2f}ms\n\n")
        
        f.write(f"Best for Visas: {best_visa_model[0]}\n")
        f.write(f"  - Top-1 Accuracy: {best_visa_model[1]['visa']['top1_accuracy']:.2%}\n")
        f.write(f"  - Avg Time: {best_visa_model[1]['visa'].get('avg_total_time_ms', 0):.2f}ms\n\n")
        
        # Performance Metrics Details
        f.write("\n" + "=" * 80 + "\n")
        f.write("DETAILED PERFORMANCE METRICS\n")
        f.write("=" * 80 + "\n\n")
        
        for model_name in model_names:
            results = all_results[model_name]
            hotel = results['hotel']
            visa = results['visa']
            
            f.write(f"Model: {model_name}\n")
            f.write(f"{'─' * 80}\n\n")
            
            f.write(f"  HOTEL EMBEDDINGS:\n")
            f.write(f"    Avg Embedding Time: {hotel.get('avg_embedding_time_ms', 0):.2f}ms\n")
            f.write(f"    Avg Search Time: {hotel.get('avg_search_time_ms', 0):.2f}ms\n")
            f.write(f"    Avg Total Time: {hotel.get('avg_total_time_ms', 0):.2f}ms\n")
            f.write(f"    Min/Max Total Time: {hotel.get('min_total_time_ms', 0):.2f}ms / {hotel.get('max_total_time_ms', 0):.2f}ms\n\n")
            
            f.write(f"  VISA EMBEDDINGS:\n")
            f.write(f"    Avg Embedding Time: {visa.get('avg_embedding_time_ms', 0):.2f}ms\n")
            f.write(f"    Avg Search Time: {visa.get('avg_search_time_ms', 0):.2f}ms\n")
            f.write(f"    Avg Total Time: {visa.get('avg_total_time_ms', 0):.2f}ms\n")
            f.write(f"    Min/Max Total Time: {visa.get('min_total_time_ms', 0):.2f}ms / {visa.get('max_total_time_ms', 0):.2f}ms\n\n")
        
        # Failed Queries
        f.write("\n" + "=" * 80 + "\n")
        f.write("FAILED QUERIES ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        for model_name in model_names:
            results = all_results[model_name]
            hotel = results['hotel']
            visa = results['visa']
            
            f.write(f"Model: {model_name}\n")
            f.write(f"{'─' * 80}\n\n")
            
            if hotel['failed_queries']:
                f.write(f"  HOTEL QUERIES THAT FAILED (Top-3):\n")
                for failure in hotel['failed_queries']:
                    f.write(f"    Query {failure['query_id']}: {failure['query']}\n")
                    f.write(f"      Expected: {failure['expected']}\n")
                    f.write(f"      Retrieved: {failure['retrieved']}\n\n")
            else:
                f.write(f"  HOTEL: All queries passed!\n\n")
            
            if visa['failed_queries']:
                f.write(f"  VISA QUERIES THAT FAILED (Top-3):\n")
                for failure in visa['failed_queries']:
                    f.write(f"    Query {failure['query_id']}: {failure['query']}\n")
                    f.write(f"      Expected: {failure['expected']}\n")
                    f.write(f"      Retrieved: {failure['retrieved']}\n\n")
            else:
                f.write(f"  VISA: All queries passed!\n\n")
        
        # Footer
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print(f"✓ Text report saved to {output_file}")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Evaluate embedding models for hotel and visa retrieval')
    parser.add_argument('--models', nargs='+', default=['all-MiniLM-L6-v2', 'all-mpnet-base-v2'],
                        help='List of embedding models to test')
    parser.add_argument('--single', action='store_true',
                        help='Test only the default model without comparison')
    
    args = parser.parse_args()
    
    if args.single:
        # Single model evaluation
        print("=" * 80)
        print("COMPREHENSIVE EMBEDDING EVALUATION")
        print("=" * 80)
        print()
        
        evaluator = EmbeddingEvaluator()
        hotel_results = evaluator.test_hotel_embeddings(top_k=5)
        visa_results = evaluator.test_visa_embeddings(top_k=5)
        evaluator.print_summary(hotel_results, visa_results)
        evaluator.save_results(hotel_results, visa_results)
    else:
        # Multi-model comparison
        compare_models(args.models)
    
    print("\n" + "=" * 80)
    print("✓ EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
