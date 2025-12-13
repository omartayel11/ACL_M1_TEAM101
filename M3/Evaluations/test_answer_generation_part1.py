"""
Answer Generation Testing - Part 1: Generate Answers
Tests multiple LLM models on answer generation with checkpoint support for rate limits.

Features:
- Tests 3 LLM models: GPT-OSS, Llama 4 Maverick, Qwen 3
- Tracks response time, token usage, and estimated cost
- 20-second delay between LLM calls to avoid rate limits
- Checkpoint/resume functionality for rate limit errors
- Saves results per model and combined results

Usage:
    python test_answer_generation_part1.py
    
If rate limit is hit, the script will stop and save a checkpoint.
Run the same command again to resume from the checkpoint.
"""

import json
import time
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_client import LLMClient


class AnswerGenerationTester:
    """Tests answer generation across multiple LLM models with checkpoint support."""
    
    def __init__(self, test_cases_file='answer_generation_test_cases.json'):
        """
        Initialize the tester.
        
        Args:
            test_cases_file: Path to JSON file with test cases
        """
        self.test_cases_file = test_cases_file
        self.checkpoint_file = 'answer_generation_checkpoint.json'
        
        # Models to test
        self.models = [
            'openai/gpt-oss-120b',
            'meta-llama/llama-4-maverick-17b-128e-instruct',
            'qwen/qwen3-32b'
        ]
        
        # Load test cases
        with open(test_cases_file, 'r', encoding='utf-8') as f:
            self.test_cases = json.load(f)
        
        print(f"✓ Loaded {len(self.test_cases)} test cases")
        print(f"✓ Testing {len(self.models)} models")
        print(f"✓ Checkpoint file: {self.checkpoint_file}")
    
    def load_checkpoint(self):
        """Load checkpoint data if exists."""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            print(f"\n📁 Checkpoint found: Resuming from {checkpoint['current_model']}")
            print(f"   Completed queries: {checkpoint['completed_queries']}/{len(self.test_cases)}")
            return checkpoint
        return None
    
    def save_checkpoint(self, model_name, query_index, results):
        """Save checkpoint data."""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'current_model': model_name,
            'completed_queries': query_index,
            'total_queries': len(self.test_cases),
            'results': results
        }
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    def delete_checkpoint(self):
        """Delete checkpoint file after successful completion."""
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            print(f"\n✓ Checkpoint deleted")
    
    def generate_prompt(self, query, context):
        """
        Generate a prompt for the LLM.
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Formatted prompt string
        """
        return f"""You are a helpful travel assistant. Answer the user's question based on the provided context.

Context:
{context}

User Question: {query}

Instructions:
- Provide a clear, concise, and accurate answer
- Base your answer strictly on the provided context
- If the context doesn't contain enough information, say so
- Be natural and conversational

Answer:"""
    
    def test_model(self, model_name, start_from_query=0, existing_results=None):
        """
        Test a single model on all test cases.
        
        Args:
            model_name: Name of the model to test
            start_from_query: Index to resume from (for checkpoints)
            existing_results: Previous results to continue from
            
        Returns:
            Dictionary with test results and statistics
        """
        print(f"\n{'='*80}")
        print(f"Testing Model: {model_name}")
        print(f"{'='*80}")
        
        # Initialize LLM client
        llm_client = LLMClient(model_name=model_name)
        
        # Initialize or continue results
        if existing_results:
            results = existing_results
        else:
            results = []
        
        # Test each query
        for i in range(start_from_query, len(self.test_cases)):
            test_case = self.test_cases[i]
            query_id = test_case['id']
            query = test_case['query']
            context = test_case['context']
            
            print(f"\n[{i+1}/{len(self.test_cases)}] Query ID: {query_id}")
            print(f"Query: {query[:80]}...")
            
            # Generate prompt
            prompt = self.generate_prompt(query, context)
            
            # Generate answer with timing and usage tracking
            start_time = time.time()
            
            try:
                answer, usage = llm_client.generate(
                    prompt,
                    temperature=0.3,
                    max_tokens=400,
                    return_usage=True
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Calculate cost
                cost = LLMClient.calculate_cost(usage)
                
                # Store result
                answer_result = {
                    'query_id': query_id,
                    'query': query,
                    'intent': test_case['intent'],
                    'context': context,
                    'expected_elements': test_case['expected_elements'],
                    'generated_answer': answer,
                    'response_time': response_time,
                    'token_usage': usage,
                    'estimated_cost': cost,
                    'timestamp': datetime.now().isoformat()
                }
                
                results.append(answer_result)
                
                print(f"✓ Answer generated ({response_time:.2f}s, {usage['total_tokens']} tokens, ${cost:.6f})")
                print(f"  Answer preview: {answer[:100]}...")
                
                # Save checkpoint after each query
                self.save_checkpoint(model_name, i + 1, results)
                
                # Wait 20 seconds before next call (except for last query)
                if i < len(self.test_cases) - 1:
                    print(f"⏳ Waiting 20 seconds before next call...")
                    time.sleep(20)
                
            except Exception as e:
                error_msg = str(e)
                print(f"✗ Error: {error_msg}")
                
                # Check if it's a rate limit error
                if 'rate_limit' in error_msg.lower() or 'rate limit' in error_msg.lower():
                    print(f"\n⚠️  RATE LIMIT REACHED")
                    print(f"   Checkpoint saved at query {i}/{len(self.test_cases)}")
                    print(f"   Run the script again to resume from this point")
                    self.save_checkpoint(model_name, i, results)
                    raise Exception("Rate limit reached. Please wait and run again to resume.")
                
                # For other errors, record and continue
                answer_result = {
                    'query_id': query_id,
                    'query': query,
                    'intent': test_case['intent'],
                    'context': context,
                    'expected_elements': test_case['expected_elements'],
                    'generated_answer': None,
                    'response_time': 0,
                    'token_usage': {'total_tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0},
                    'estimated_cost': 0,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(answer_result)
                
                # Save checkpoint
                self.save_checkpoint(model_name, i + 1, results)
                
                # Wait before next call
                if i < len(self.test_cases) - 1:
                    print(f"⏳ Waiting 20 seconds before next call...")
                    time.sleep(20)
        
        # Calculate statistics
        successful_answers = [r for r in results if r['generated_answer'] is not None]
        failed_answers = [r for r in results if r['generated_answer'] is None]
        
        if successful_answers:
            avg_response_time = sum(r['response_time'] for r in successful_answers) / len(successful_answers)
            total_tokens = sum(r['token_usage']['total_tokens'] for r in successful_answers)
            avg_tokens = total_tokens / len(successful_answers)
            total_cost = sum(r['estimated_cost'] for r in successful_answers)
        else:
            avg_response_time = 0
            total_tokens = 0
            avg_tokens = 0
            total_cost = 0
        
        statistics = {
            'model_name': model_name,
            'total_queries': len(self.test_cases),
            'successful': len(successful_answers),
            'failed': len(failed_answers),
            'success_rate': (len(successful_answers) / len(self.test_cases)) * 100,
            'average_response_time': avg_response_time,
            'total_tokens': total_tokens,
            'average_tokens_per_query': avg_tokens,
            'total_estimated_cost': total_cost,
            'average_cost_per_query': total_cost / max(len(successful_answers), 1)
        }
        
        # Print statistics
        print(f"\n{'='*80}")
        print(f"Statistics for {model_name}")
        print(f"{'='*80}")
        print(f"Successful: {statistics['successful']}/{statistics['total_queries']} ({statistics['success_rate']:.1f}%)")
        print(f"Average Response Time: {statistics['average_response_time']:.2f}s")
        print(f"Total Tokens: {statistics['total_tokens']}")
        print(f"Average Tokens/Query: {statistics['average_tokens_per_query']:.1f}")
        print(f"Total Estimated Cost: ${statistics['total_estimated_cost']:.6f}")
        print(f"Average Cost/Query: ${statistics['average_cost_per_query']:.6f}")
        
        return {
            'model_name': model_name,
            'test_date': datetime.now().isoformat(),
            'statistics': statistics,
            'results': results
        }
    
    def run_all_tests(self):
        """Run tests for all models with checkpoint support."""
        print("\n" + "="*80)
        print("ANSWER GENERATION TESTING - PART 1")
        print("="*80)
        print(f"Test cases: {len(self.test_cases)}")
        print(f"Models to test: {len(self.models)}")
        print(f"Rate limit protection: 20-second delay between calls")
        print(f"Checkpoint support: Enabled")
        
        # Check for existing checkpoint
        checkpoint = self.load_checkpoint()
        
        all_results = {}
        
        # Determine where to start
        if checkpoint:
            # Resume from checkpoint
            start_model_idx = self.models.index(checkpoint['current_model'])
            start_query_idx = checkpoint['completed_queries']
            
            # First, complete the interrupted model
            if start_query_idx < len(self.test_cases):
                print(f"\n🔄 Resuming {checkpoint['current_model']} from query {start_query_idx + 1}")
                try:
                    model_results = self.test_model(
                        checkpoint['current_model'],
                        start_from_query=start_query_idx,
                        existing_results=checkpoint['results']
                    )
                    all_results[checkpoint['current_model']] = model_results
                    
                    # Save individual model results
                    output_file = f"answer_generation_{checkpoint['current_model'].replace('/', '_')}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(model_results, f, indent=2, ensure_ascii=False)
                    print(f"\n✓ Saved results to {output_file}")
                    
                except Exception as e:
                    if "Rate limit" in str(e):
                        return  # Exit and let user restart
                    raise
            else:
                # Model was completed, load its results
                all_results[checkpoint['current_model']] = {
                    'model_name': checkpoint['current_model'],
                    'results': checkpoint['results']
                }
            
            # Continue with remaining models
            remaining_models = self.models[start_model_idx + 1:]
        else:
            # Start fresh
            remaining_models = self.models
        
        # Test remaining models
        for model_name in remaining_models:
            try:
                model_results = self.test_model(model_name)
                all_results[model_name] = model_results
                
                # Save individual model results
                output_file = f"answer_generation_{model_name.replace('/', '_')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(model_results, f, indent=2, ensure_ascii=False)
                print(f"\n✓ Saved results to {output_file}")
                
            except Exception as e:
                if "Rate limit" in str(e):
                    return  # Exit and let user restart
                raise
        
        # Save combined results
        combined_output = {
            'test_date': datetime.now().isoformat(),
            'total_models': len(self.models),
            'total_test_cases': len(self.test_cases),
            'model_results': all_results
        }
        
        with open('answer_generation_all_models.json', 'w', encoding='utf-8') as f:
            json.dump(combined_output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved combined results to answer_generation_all_models.json")
        
        # Delete checkpoint after successful completion
        self.delete_checkpoint()
        
        # Print summary
        self.print_summary(all_results)
    
    def print_summary(self, all_results):
        """Print a summary comparison of all models."""
        print("\n" + "="*95)
        print("SUMMARY: MODEL COMPARISON")
        print("="*95)
        print(f"{'Model':<45} {'Success':>8} {'Avg Time':>10} {'Avg Tokens':>12} {'Total Cost':>12}")
        print("-"*95)
        
        for model_name in self.models:
            if model_name in all_results:
                stats = all_results[model_name]['statistics']
                print(f"{model_name:<45} "
                      f"{stats['successful']:>3}/{stats['total_queries']:<4} "
                      f"{stats['average_response_time']:>8.2f}s "
                      f"{stats['average_tokens_per_query']:>11.1f} "
                      f"${stats['total_estimated_cost']:>10.6f}")
        
        print("="*95)
        print("\n✓ Part 1 Complete!")
        print("  Next step: Run test_answer_generation_part2.py to evaluate the generated answers")


def main():
    """Main function."""
    try:
        tester = AnswerGenerationTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        print("   Checkpoint saved. Run the script again to resume.")
    except Exception as e:
        if "Rate limit" not in str(e):
            print(f"\n✗ Error: {e}")
            raise


if __name__ == '__main__':
    main()
