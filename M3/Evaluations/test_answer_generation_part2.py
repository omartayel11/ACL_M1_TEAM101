"""
Answer Generation Testing - Part 2: Evaluate Generated Answers
Uses an LLM judge to evaluate the quality of generated answers with checkpoint support.

Features:
- Evaluates answers from Part 1 using LLM judge (GPT-OSS by default)
- Scores on 5 criteria: Accuracy, Completeness, Relevance, Clarity, Groundedness
- 20-second delay between LLM calls to avoid rate limits
- Checkpoint/resume functionality for rate limit errors
- Generates comprehensive evaluation report

Usage:
    python test_answer_generation_part2.py
    
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


class LLMJudge:
    """Uses an LLM to evaluate generated answers."""
    
    def __init__(self, judge_model='openai/gpt-oss-120b'):
        """
        Initialize the LLM judge.
        
        Args:
            judge_model: Model to use as judge
        """
        self.judge_model = judge_model
        self.llm_client = LLMClient()
        self.llm_client.set_model(judge_model)
        print(f"✓ Initialized LLM Judge: {judge_model}")
    
    def evaluate_answer(self, query, context, expected_elements, generated_answer):
        """
        Evaluate a generated answer.
        
        Args:
            query: Original user query
            context: Context provided to the model
            expected_elements: Key elements that should be in the answer
            generated_answer: The answer to evaluate
            
        Returns:
            Dictionary with evaluation scores and reasoning
        """
        evaluation_prompt = f"""You are an expert evaluator for question-answering systems. Evaluate the following answer based on the criteria below.

USER QUERY: {query}

PROVIDED CONTEXT:
{context}

EXPECTED KEY ELEMENTS:
{json.dumps(expected_elements, indent=2)}

GENERATED ANSWER:
{generated_answer}

Evaluate the answer on these 5 criteria (score 0-10 for each):

1. ACCURACY (0-10): Does the answer contain factually correct information based on the context?
   - 0-3: Contains significant errors or misinformation
   - 4-6: Partially correct with some inaccuracies
   - 7-9: Mostly accurate with minor issues
   - 10: Completely accurate

2. COMPLETENESS (0-10): Does the answer address all expected key elements?
   - 0-3: Missing most key elements
   - 4-6: Addresses some key elements
   - 7-9: Covers most key elements
   - 10: Comprehensive, addresses all key elements

3. RELEVANCE (0-10): Is the answer directly relevant to the user's query?
   - 0-3: Off-topic or tangential
   - 4-6: Somewhat relevant but includes unnecessary information
   - 7-9: Highly relevant with minor deviations
   - 10: Perfectly addresses the query

4. CLARITY (0-10): Is the answer clear, well-structured, and easy to understand?
   - 0-3: Confusing or poorly structured
   - 4-6: Understandable but could be clearer
   - 7-9: Clear and well-organized
   - 10: Exceptionally clear and well-presented

5. GROUNDEDNESS (0-10): Is the answer grounded in the provided context (no hallucinations)?
   - 0-3: Contains significant information not in context
   - 4-6: Mostly grounded with some speculation
   - 7-9: Well-grounded with minor extrapolations
   - 10: Completely grounded in provided context

Provide your evaluation in the following JSON format:
{{
    "accuracy": <score 0-10>,
    "completeness": <score 0-10>,
    "relevance": <score 0-10>,
    "clarity": <score 0-10>,
    "groundedness": <score 0-10>,
    "overall_score": <average of all scores>,
    "verdict": "<EXCELLENT|GOOD|ACCEPTABLE|POOR>",
    "reasoning": "<brief explanation of the scores>",
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "weaknesses": ["<weakness 1>", "<weakness 2>", ...]
}}

Verdict Guidelines:
- EXCELLENT: overall_score >= 8.5
- GOOD: overall_score >= 7.0
- ACCEPTABLE: overall_score >= 5.0
- POOR: overall_score < 5.0

Respond ONLY with the JSON, no additional text."""

        try:
            response, usage = self.llm_client.generate(
                evaluation_prompt,
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=800,  # Increased from 600 to allow complete JSON
                return_usage=True
            )
            
            # Parse JSON response
            # Try to extract JSON if wrapped in markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            # Try to parse JSON
            try:
                evaluation = json.loads(response)
            except json.JSONDecodeError as je:
                # If JSON parsing fails, try to fix common issues
                print(f"  ⚠️  JSON parse error, attempting to fix...")
                
                # Try to find JSON object in response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        evaluation = json.loads(json_match.group(0))
                    except:
                        # If still fails, retry with higher max_tokens
                        print(f"  ↻ Retrying with higher token limit...")
                        response, usage = self.llm_client.generate(
                            evaluation_prompt,
                            temperature=0.1,
                            max_tokens=1000,
                            return_usage=True
                        )
                        
                        if "```json" in response:
                            response = response.split("```json")[1].split("```")[0].strip()
                        elif "```" in response:
                            response = response.split("```")[1].split("```")[0].strip()
                        
                        evaluation = json.loads(response)
                else:
                    raise je
            
            evaluation['success'] = True
            evaluation['error'] = None
            evaluation['judge_tokens'] = usage.get('total_tokens', 0)
            evaluation['judge_cost'] = LLMClient.calculate_cost(usage)
            
            return evaluation
            
        except Exception as e:
            print(f"  ✗ Evaluation failed: {e}")
            print(f"  Raw response preview: {str(response)[:200] if 'response' in locals() else 'N/A'}...")
            return {
                'accuracy': 0,
                'completeness': 0,
                'relevance': 0,
                'clarity': 0,
                'groundedness': 0,
                'overall_score': 0,
                'verdict': 'ERROR',
                'reasoning': f'Evaluation failed: {str(e)}',
                'strengths': [],
                'weaknesses': [],
                'success': False,
                'error': str(e),
                'judge_tokens': 0,
                'judge_cost': 0
            }


class ComprehensiveEvaluator:
    """Evaluates all generated answers from Part 1 with checkpoint support."""
    
    def __init__(self, judge_model='openai/gpt-oss-120b'):
        """
        Initialize the evaluator.
        
        Args:
            judge_model: Model to use as judge
        """
        self.judge = LLMJudge(judge_model)
        self.judge_model = judge_model
        self.checkpoint_file = 'answer_evaluation_checkpoint.json'
        
        # Models to evaluate (should match Part 1)
        self.models = [
            'openai/gpt-oss-120b',
            'meta-llama/llama-4-maverick-17b-128e-instruct',
            'qwen/qwen3-32b'
        ]
        
        print(f"✓ Will evaluate answers from {len(self.models)} models")
        print(f"✓ Checkpoint file: {self.checkpoint_file}")
    
    def load_checkpoint(self):
        """Load checkpoint data if exists."""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            print(f"\n📁 Checkpoint found: Resuming from {checkpoint['current_model']}")
            print(f"   Completed evaluations: {checkpoint['completed_evaluations']}")
            return checkpoint
        return None
    
    def save_checkpoint(self, model_name, eval_index, evaluations):
        """Save checkpoint data."""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'current_model': model_name,
            'completed_evaluations': eval_index,
            'evaluations': evaluations
        }
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    def delete_checkpoint(self):
        """Delete checkpoint file after successful completion."""
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            print(f"\n✓ Checkpoint deleted")
    
    def evaluate_model(self, model_name, start_from_eval=0, existing_evaluations=None):
        """
        Evaluate all answers from a single model.
        
        Args:
            model_name: Name of the model to evaluate
            start_from_eval: Index to resume from (for checkpoints)
            existing_evaluations: Previous evaluations to continue from
            
        Returns:
            Dictionary with evaluation results and statistics
        """
        print(f"\n{'='*80}")
        print(f"Evaluating Model: {model_name}")
        print(f"{'='*80}")
        
        # Load the model's answer file
        answer_file = f"answer_generation_{model_name.replace('/', '_')}.json"
        
        if not os.path.exists(answer_file):
            print(f"✗ Answer file not found: {answer_file}")
            print(f"  Please run test_answer_generation_part1.py first")
            return None
        
        with open(answer_file, 'r', encoding='utf-8') as f:
            answer_data = json.load(f)
        
        results = answer_data['results']
        
        # Initialize or continue evaluations
        if existing_evaluations:
            evaluations = existing_evaluations
        else:
            evaluations = []
        
        # Evaluate each answer
        for i in range(start_from_eval, len(results)):
            result = results[i]
            query_id = result['query_id']
            
            print(f"\n[{i+1}/{len(results)}] Evaluating Query ID: {query_id}")
            
            # Skip if answer generation failed
            if result['generated_answer'] is None:
                eval_result = {
                    'query_id': query_id,
                    'evaluation': {
                        'accuracy': 0,
                        'completeness': 0,
                        'relevance': 0,
                        'clarity': 0,
                        'groundedness': 0,
                        'overall_score': 0,
                        'verdict': 'SKIPPED',
                        'reasoning': 'Answer generation failed',
                        'strengths': [],
                        'weaknesses': [],
                        'success': False,
                        'error': 'No answer generated',
                        'judge_tokens': 0,
                        'judge_cost': 0
                    },
                    'timestamp': datetime.now().isoformat()
                }
                evaluations.append(eval_result)
                print(f"  ⊘ Skipped (no answer was generated)")
                continue
            
            try:
                # Remove <think> tags from answer before evaluation (but keep in JSON)
                # This prevents overwhelming the judge LLM's context with reasoning
                answer_for_judge = result['generated_answer']
                if '<think>' in answer_for_judge and '</think>' in answer_for_judge:
                    # Remove everything between <think> and </think>
                    import re
                    answer_for_judge = re.sub(r'<think>.*?</think>\s*', '', answer_for_judge, flags=re.DOTALL)
                    print(f"  (Removed <think> section for judge evaluation)")
                
                # Evaluate the answer
                evaluation = self.judge.evaluate_answer(
                    query=result['query'],
                    context=result['context'],
                    expected_elements=result['expected_elements'],
                    generated_answer=answer_for_judge
                )
                
                eval_result = {
                    'query_id': query_id,
                    'query': result['query'],
                    'generated_answer': result['generated_answer'],
                    'evaluation': evaluation,
                    'timestamp': datetime.now().isoformat()
                }
                
                evaluations.append(eval_result)
                
                if evaluation['success']:
                    print(f"  ✓ Overall Score: {evaluation['overall_score']:.1f}/10 ({evaluation['verdict']})")
                    print(f"    Judge tokens: {evaluation['judge_tokens']}, Cost: ${evaluation['judge_cost']:.6f}")
                else:
                    print(f"  ✗ Evaluation failed")
                
                # Save checkpoint after each evaluation
                self.save_checkpoint(model_name, i + 1, evaluations)
                
                # Wait 20 seconds before next call (except for last evaluation)
                if i < len(results) - 1:
                    print(f"  ⏳ Waiting 20 seconds before next evaluation...")
                    time.sleep(20)
                
            except Exception as e:
                error_msg = str(e)
                print(f"  ✗ Error: {error_msg}")
                
                # Check if it's a rate limit error
                if 'rate_limit' in error_msg.lower() or 'rate limit' in error_msg.lower():
                    print(f"\n⚠️  RATE LIMIT REACHED")
                    print(f"   Checkpoint saved at evaluation {i}/{len(results)}")
                    print(f"   Run the script again to resume from this point")
                    self.save_checkpoint(model_name, i, evaluations)
                    raise Exception("Rate limit reached. Please wait and run again to resume.")
                
                # For other errors, record and continue
                eval_result = {
                    'query_id': query_id,
                    'query': result['query'],
                    'generated_answer': result['generated_answer'],
                    'evaluation': {
                        'accuracy': 0,
                        'completeness': 0,
                        'relevance': 0,
                        'clarity': 0,
                        'groundedness': 0,
                        'overall_score': 0,
                        'verdict': 'ERROR',
                        'reasoning': f'Error: {error_msg}',
                        'strengths': [],
                        'weaknesses': [],
                        'success': False,
                        'error': error_msg,
                        'judge_tokens': 0,
                        'judge_cost': 0
                    },
                    'timestamp': datetime.now().isoformat()
                }
                evaluations.append(eval_result)
                
                # Save checkpoint
                self.save_checkpoint(model_name, i + 1, evaluations)
                
                # Wait before next call
                if i < len(results) - 1:
                    print(f"  ⏳ Waiting 20 seconds before next evaluation...")
                    time.sleep(20)
        
        # Calculate statistics
        successful_evals = [e for e in evaluations if e['evaluation'].get('success', False)]
        
        if successful_evals:
            avg_scores = {
                'accuracy': sum(e['evaluation']['accuracy'] for e in successful_evals) / len(successful_evals),
                'completeness': sum(e['evaluation']['completeness'] for e in successful_evals) / len(successful_evals),
                'relevance': sum(e['evaluation']['relevance'] for e in successful_evals) / len(successful_evals),
                'clarity': sum(e['evaluation']['clarity'] for e in successful_evals) / len(successful_evals),
                'groundedness': sum(e['evaluation']['groundedness'] for e in successful_evals) / len(successful_evals),
                'overall': sum(e['evaluation']['overall_score'] for e in successful_evals) / len(successful_evals)
            }
            
            # Count verdicts
            verdicts = {}
            for e in successful_evals:
                verdict = e['evaluation'].get('verdict', 'UNKNOWN')
                verdicts[verdict] = verdicts.get(verdict, 0) + 1
            
            # Calculate judge metrics
            total_judge_tokens = sum(e['evaluation'].get('judge_tokens', 0) for e in successful_evals)
            total_judge_cost = sum(e['evaluation'].get('judge_cost', 0) for e in successful_evals)
        else:
            avg_scores = {
                'accuracy': 0, 'completeness': 0, 'relevance': 0,
                'clarity': 0, 'groundedness': 0, 'overall': 0
            }
            verdicts = {}
            total_judge_tokens = 0
            total_judge_cost = 0
        
        results = {
            'model_name': model_name,
            'judge_model': self.judge_model,
            'evaluation_date': datetime.now().isoformat(),
            'total_evaluated': len(evaluations),
            'successful_evaluations': len(successful_evals),
            'average_scores': avg_scores,
            'verdict_distribution': verdicts,
            'judge_metrics': {
                'total_tokens': total_judge_tokens,
                'total_cost': total_judge_cost,
                'avg_tokens_per_evaluation': total_judge_tokens / max(len(successful_evals), 1),
                'avg_cost_per_evaluation': total_judge_cost / max(len(successful_evals), 1)
            },
            'evaluations': evaluations
        }
        
        print(f"\n✓ Evaluation complete for {model_name}")
        print(f"  Average Overall Score: {avg_scores['overall']:.2f}/10")
        print(f"  Verdict Distribution: {verdicts}")
        print(f"  Judge tokens used: {total_judge_tokens}")
        print(f"  Judge cost: ${total_judge_cost:.6f}")
        
        return results
    
    def run_all_evaluations(self):
        """Evaluate all models with checkpoint support."""
        print("\n" + "="*80)
        print("ANSWER GENERATION TESTING - PART 2: EVALUATION")
        print("="*80)
        print(f"Judge Model: {self.judge_model}")
        print(f"Models to evaluate: {len(self.models)}")
        print(f"Rate limit protection: 20-second delay between calls")
        print(f"Checkpoint support: Enabled")
        
        # Check for existing checkpoint
        checkpoint = self.load_checkpoint()
        
        all_evaluations = {
            'judge_model': self.judge_model,
            'evaluation_date': datetime.now().isoformat(),
            'model_evaluations': {}
        }
        
        # Determine where to start
        if checkpoint:
            # Resume from checkpoint
            start_model_idx = self.models.index(checkpoint['current_model'])
            start_eval_idx = checkpoint['completed_evaluations']
            
            # First, complete the interrupted model
            model_name = checkpoint['current_model']
            
            # Load answer file to get total count
            answer_file = f"answer_generation_{model_name.replace('/', '_')}.json"
            with open(answer_file, 'r', encoding='utf-8') as f:
                answer_data = json.load(f)
            total_answers = len(answer_data['results'])
            
            if start_eval_idx < total_answers:
                print(f"\n🔄 Resuming {model_name} from evaluation {start_eval_idx + 1}")
                try:
                    eval_results = self.evaluate_model(
                        model_name,
                        start_from_eval=start_eval_idx,
                        existing_evaluations=checkpoint['evaluations']
                    )
                    
                    if eval_results:
                        all_evaluations['model_evaluations'][model_name] = eval_results
                        
                        # Save individual evaluation results
                        output_file = f"answer_evaluation_{model_name.replace('/', '_')}.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(eval_results, f, indent=2, ensure_ascii=False)
                        print(f"\n✓ Saved evaluation to {output_file}")
                    
                except Exception as e:
                    if "Rate limit" in str(e):
                        return  # Exit and let user restart
                    raise
            else:
                # Model was completed, load its results
                output_file = f"answer_evaluation_{model_name.replace('/', '_')}.json"
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        all_evaluations['model_evaluations'][model_name] = json.load(f)
            
            # Continue with remaining models
            remaining_models = self.models[start_model_idx + 1:]
        else:
            # Start fresh
            remaining_models = self.models
        
        # Evaluate remaining models
        for model_name in remaining_models:
            try:
                eval_results = self.evaluate_model(model_name)
                
                if eval_results:
                    all_evaluations['model_evaluations'][model_name] = eval_results
                    
                    # Save individual evaluation results
                    output_file = f"answer_evaluation_{model_name.replace('/', '_')}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(eval_results, f, indent=2, ensure_ascii=False)
                    print(f"\n✓ Saved evaluation to {output_file}")
                
            except Exception as e:
                if "Rate limit" in str(e):
                    return  # Exit and let user restart
                raise
        
        # Save combined evaluations
        with open('answer_evaluation_all_models.json', 'w', encoding='utf-8') as f:
            json.dump(all_evaluations, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved combined evaluations to answer_evaluation_all_models.json")
        
        # Delete checkpoint after successful completion
        self.delete_checkpoint()
        
        # Generate report
        self.generate_report(all_evaluations)
    
    def generate_report(self, all_evaluations):
        """Generate a comprehensive text report."""
        print("\n" + "="*80)
        print("GENERATING COMPREHENSIVE REPORT")
        print("="*80)
        
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("ANSWER GENERATION EVALUATION REPORT")
        report_lines.append("="*80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Judge Model: {all_evaluations['judge_model']}")
        report_lines.append("")
        
        # Collect data for comparison
        model_data = []
        for model in self.models:
            if model in all_evaluations['model_evaluations']:
                eval_data = all_evaluations['model_evaluations'][model]
                if 'average_scores' in eval_data:
                    model_data.append({
                        'name': model,
                        'scores': eval_data['average_scores'],
                        'verdicts': eval_data['verdict_distribution'],
                        'total': eval_data['total_evaluated'],
                        'successful': eval_data['successful_evaluations'],
                        'judge_metrics': eval_data.get('judge_metrics', {})
                    })
        
        # Print scores comparison
        print("\n📊 AVERAGE SCORES COMPARISON")
        print(f"{'Model':<45} {'Overall':>8} {'Accuracy':>8} {'Complete':>8} {'Relevant':>8} {'Clarity':>8} {'Grounded':>8}")
        print("-" * 115)
        
        for data in model_data:
            scores = data['scores']
            print(f"{data['name']:<45} "
                  f"{scores['overall']:>8.2f} "
                  f"{scores['accuracy']:>8.2f} "
                  f"{scores['completeness']:>8.2f} "
                  f"{scores['relevance']:>8.2f} "
                  f"{scores['clarity']:>8.2f} "
                  f"{scores['groundedness']:>8.2f}")
        
        # Add to report
        report_lines.append("AVERAGE SCORES COMPARISON")
        report_lines.append("-"*80)
        report_lines.append(f"{'Model':<45} {'Overall':>8} {'Accuracy':>8} {'Complete':>8} {'Relevant':>8} {'Clarity':>8} {'Grounded':>8}")
        report_lines.append("-"*115)
        
        for data in model_data:
            scores = data['scores']
            report_lines.append(
                f"{data['name']:<45} "
                f"{scores['overall']:>8.2f} "
                f"{scores['accuracy']:>8.2f} "
                f"{scores['completeness']:>8.2f} "
                f"{scores['relevance']:>8.2f} "
                f"{scores['clarity']:>8.2f} "
                f"{scores['groundedness']:>8.2f}"
            )
        
        report_lines.append("")
        
        # Detailed analysis
        report_lines.append("\n" + "=" * 80)
        report_lines.append("DETAILED ANALYSIS")
        report_lines.append("=" * 80)
        
        for model in self.models:
            if model in all_evaluations['model_evaluations']:
                eval_data = all_evaluations['model_evaluations'][model]
                report_lines.append(f"\n{model}")
                report_lines.append("-" * 80)
                
                if 'average_scores' in eval_data:
                    report_lines.append(f"Total Evaluated: {eval_data['successful_evaluations']}/{eval_data['total_evaluated']}")
                    report_lines.append(f"Average Overall Score: {eval_data['average_scores']['overall']:.2f}/10")
                    report_lines.append(f"\nVerdict Distribution:")
                    for verdict, count in sorted(eval_data['verdict_distribution'].items()):
                        percentage = (count / eval_data['successful_evaluations']) * 100
                        report_lines.append(f"  {verdict}: {count} ({percentage:.1f}%)")
                    
                    if 'judge_metrics' in eval_data:
                        metrics = eval_data['judge_metrics']
                        report_lines.append(f"\nJudge Evaluation Metrics:")
                        report_lines.append(f"  Total Tokens: {metrics['total_tokens']}")
                        report_lines.append(f"  Avg Tokens/Evaluation: {metrics['avg_tokens_per_evaluation']:.1f}")
                        report_lines.append(f"  Total Cost: ${metrics['total_cost']:.6f}")
                        report_lines.append(f"  Avg Cost/Evaluation: ${metrics['avg_cost_per_evaluation']:.6f}")
        
        # Best model recommendation
        report_lines.append("\n" + "=" * 80)
        report_lines.append("RECOMMENDATION")
        report_lines.append("=" * 80)
        
        if model_data:
            best_model = max(model_data, key=lambda x: x['scores']['overall'])
            report_lines.append(f"\nBest Overall Model: {best_model['name']}")
            report_lines.append(f"Average Score: {best_model['scores']['overall']:.2f}/10")
            report_lines.append(f"\nStrengths:")
            
            # Find best scores
            for criterion in ['accuracy', 'completeness', 'relevance', 'clarity', 'groundedness']:
                best_in_criterion = max(model_data, key=lambda x: x['scores'][criterion])
                if best_in_criterion['name'] == best_model['name']:
                    report_lines.append(f"  - Best {criterion.capitalize()}: {best_model['scores'][criterion]:.2f}/10")
        
        report_lines.append("\n" + "=" * 80)
        
        # Save report
        report_text = "\n".join(report_lines)
        with open('answer_generation_evaluation_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n✓ Saved comprehensive report to answer_generation_evaluation_report.txt")
        print("\n✓ Part 2 Complete!")
        print("  All evaluations finished successfully")


def main():
    """Main function."""
    try:
        evaluator = ComprehensiveEvaluator()
        evaluator.run_all_evaluations()
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
        print("   Checkpoint saved. Run the script again to resume.")
    except Exception as e:
        if "Rate limit" not in str(e):
            print(f"\n✗ Error: {e}")
            raise


if __name__ == '__main__':
    main()
