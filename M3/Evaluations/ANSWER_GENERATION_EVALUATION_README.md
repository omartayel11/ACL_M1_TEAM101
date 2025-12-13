# Answer Generation Evaluation Guide

## Overview
Comprehensive evaluation system for testing answer generation across multiple LLM models with an LLM judge for quality assessment.

## Test Structure

### Part 1: Generate Answers (test_answer_generation_part1.py)
- Tests 3 LLM models on 15 diverse queries
- Provides pre-defined context for each query
- Generates and saves answers from each model

### Part 2: LLM Judge (test_answer_generation_part2.py)
- Uses an LLM as judge to evaluate answer quality
- Scores answers on 5 criteria (0-10 scale)
- Generates comparison report across all models

## Models Being Tested

1. **openai/gpt-oss-120b** - GPT-OSS 120B (OpenAI)
2. **meta-llama/llama-4-maverick-17b-128e-instruct** - Llama 4 Maverick 17B (Meta)
3. **qwen/qwen3-32b** - Qwen 3 32B (Alibaba)

## Test Cases (15 queries)

### Query Types:
- **HotelSearch** (5 cases): Finding hotels by location, features, ratings
- **VisaQuestion** (3 cases): Visa requirements between countries
- **ReviewQuery** (3 cases): Guest reviews and feedback analysis
- **LocationQuery** (2 cases): Hotels near specific locations
- **AmenityQuery** (1 case): Hotel amenities and facilities
- **HotelComparison** (1 case): Comparing multiple hotels

### Example Test Cases:
1. "What are the best 5-star hotels in Dubai?"
2. "Do I need a visa from China to United States?"
3. "What do guests say about the staff at hotels in Tokyo?"
4. "Compare hotels in New York and London"
5. "Which hotel in Cairo has the best reviews?"

Each test case includes:
- **Query**: The user question
- **Intent**: Classified intent type
- **Context**: Pre-retrieved relevant information
- **Expected Elements**: Key facts that should appear in answer

## Evaluation Criteria

The LLM judge scores each answer on:

1. **ACCURACY** (0-10): Correct use of context without hallucination
2. **COMPLETENESS** (0-10): Addresses all aspects of the question
3. **RELEVANCE** (0-10): Focused and relevant to query
4. **CLARITY** (0-10): Clear, well-structured, easy to understand
5. **GROUNDEDNESS** (0-10): Cites specific details from context

**Overall Score**: Average of all 5 criteria

**Verdict Categories**:
- EXCELLENT: 8.5-10
- GOOD: 7.0-8.4
- ACCEPTABLE: 5.0-6.9
- POOR: 0-4.9

## Running the Tests

### Prerequisites
```bash
cd M3
# Ensure your GROQ_API_KEY is set in .env file
```

### Step 1: Generate Answers
```bash
cd M3/Evaluations
python test_answer_generation_part1.py
```

**Expected Runtime**: 5-10 minutes (15 queries × 3 models = 45 generations)

**Output Files**:
- `answer_generation_openai_gpt-oss-120b.json`
- `answer_generation_meta-llama_llama-4-maverick-17b-128e-instruct.json`
- `answer_generation_qwen_qwen3-32b.json`
- `answer_generation_all_models.json` (combined)

### Step 2: Evaluate with LLM Judge
```bash
python test_answer_generation_part2.py
```

**Expected Runtime**: 10-15 minutes (45 evaluations)

**Output Files**:
- `answer_evaluation_openai_gpt-oss-120b.json`
- `answer_evaluation_meta-llama_llama-4-maverick-17b-128e-instruct.json`
- `answer_evaluation_qwen_qwen3-32b.json`
- `answer_evaluation_all_models.json` (combined)
- `answer_generation_evaluation_report.txt` (comprehensive report)

## Understanding the Results

### JSON Output Structure

#### Part 1 Output (answer_generation_*.json):
```json
{
  "model_name": "openai/gpt-oss-120b",
  "test_date": "2025-12-13T...",
  "total_cases": 15,
  "statistics": {
    "successful": 15,
    "failed": 0,
    "success_rate": 1.0,
    "average_generation_time": 2.34
  },
  "answers": [
    {
      "test_id": 1,
      "query": "What are the best 5-star hotels in Dubai?",
      "intent": "HotelSearch",
      "context": "...",
      "expected_elements": ["The Golden Oasis", "Dubai", ...],
      "generated_answer": "The best 5-star hotel in Dubai is...",
      "generation_time": 2.1,
      "success": true
    }
  ]
}
```

#### Part 2 Output (answer_evaluation_*.json):
```json
{
  "model_name": "openai/gpt-oss-120b",
  "judge_model": "openai/gpt-oss-120b",
  "average_scores": {
    "accuracy": 8.5,
    "completeness": 8.2,
    "relevance": 9.0,
    "clarity": 8.7,
    "groundedness": 8.3,
    "overall": 8.54
  },
  "verdict_distribution": {
    "EXCELLENT": 10,
    "GOOD": 4,
    "ACCEPTABLE": 1
  },
  "evaluations": [
    {
      "test_id": 1,
      "query": "...",
      "answer": "...",
      "evaluation": {
        "accuracy": 9,
        "completeness": 8,
        "relevance": 9,
        "clarity": 9,
        "groundedness": 8,
        "overall_score": 8.6,
        "missing_elements": [],
        "hallucinations": [],
        "strengths": "Clear citation of hotel name and location...",
        "weaknesses": "Could include more specific amenity details",
        "verdict": "EXCELLENT"
      }
    }
  ]
}
```

### Comparison Report

The text report (`answer_generation_evaluation_report.txt`) includes:
1. Overall rankings by average score
2. Detailed breakdown per model
3. Verdict distributions
4. Best model recommendation

### Interpreting Scores

**8.5-10 (EXCELLENT)**:
- Highly accurate with no hallucinations
- Complete coverage of query
- Clear, well-structured answers
- Strong grounding in context

**7.0-8.4 (GOOD)**:
- Mostly accurate with minor issues
- Addresses main points
- Generally clear
- Good use of context

**5.0-6.9 (ACCEPTABLE)**:
- Some accuracy issues
- Missing some details
- Could be clearer
- Moderate grounding

**0-4.9 (POOR)**:
- Significant inaccuracies
- Incomplete or off-topic
- Unclear or confusing
- Weak grounding

## Common Issues and Solutions

### Issue: "File not found" error in Part 2
**Solution**: Run Part 1 first to generate answer files

### Issue: API rate limiting
**Solution**: The scripts include 1-second delays between requests. If still rate-limited, increase sleep time.

### Issue: JSON parsing errors in judge evaluation
**Solution**: Judge may wrap JSON in markdown. Script handles this automatically, but check `raw_response` in error cases.

### Issue: All models have same scores
**Solution**: This could indicate:
- Similar model performance (expected for good prompts)
- Judge model bias (try different judge)
- Context too simple/difficult for all models

## Customization

### Add More Test Cases
Edit `answer_generation_test_cases.json`:
```json
{
  "test_cases": [
    {
      "id": 16,
      "query": "Your new query",
      "intent": "HotelSearch",
      "context": "Relevant context here",
      "expected_elements": ["key", "elements", "to", "check"]
    }
  ]
}
```

### Change Judge Model
Edit `test_answer_generation_part2.py`:
```python
# Use a different model as judge
judge = LLMJudge(judge_model="meta-llama/llama-4-maverick-17b-128e-instruct")
```

### Test Additional Models
Edit `test_answer_generation_part1.py`:
```python
self.models = [
    "openai/gpt-oss-120b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "qwen/qwen3-32b",
    "your-new-model-here"  # Add new model
]
```

### Adjust Evaluation Criteria
Modify the evaluation prompt in `LLMJudge.evaluate_answer()` to add/change criteria.

## Best Practices

1. **Run Part 1 once, Part 2 multiple times**: Generate answers once, then experiment with different judge models or criteria

2. **Review failed cases**: Check `success: false` entries to understand model limitations

3. **Compare with human evaluation**: Sample a few cases and compare judge scores with your own assessment

4. **Look for patterns**: Check if certain query types consistently score lower across all models

5. **Monitor generation times**: Balance quality with speed for production use

## Expected Outcomes

Based on typical LLM performance:

### Generation Speed:
- Fast models: 1-2s per query
- Standard models: 2-4s per query
- Large models: 4-6s per query

### Quality Scores:
- Good models: 7.5-8.5 overall
- Excellent models: 8.5-9.5 overall
- Top tier: 9.0+ overall

### Common Patterns:
- **Accuracy**: Usually highest scored (models stick to context)
- **Completeness**: Often lower (models may miss details)
- **Groundedness**: Varies by model (some cite better than others)
- **Clarity**: Generally high for instruction-tuned models

## Troubleshooting

### No answers generated
- Check GROQ_API_KEY in .env
- Verify model names are correct
- Check API quota/limits

### Low scores across all models
- Review test case contexts (too short/long?)
- Check if expected_elements are realistic
- Verify judge model is working properly

### Evaluation JSON parsing fails
- Judge may not follow JSON format strictly
- Try different judge model
- Check temperature setting (lower = more consistent)

## Next Steps After Evaluation

1. **Select Best Model**: Use highest scoring model for production
2. **Analyze Failures**: Improve prompts for low-scoring queries
3. **A/B Testing**: Deploy top 2 models and compare user satisfaction
4. **Continuous Monitoring**: Re-run evaluations when updating models/prompts

## Files Generated

After complete run:
```
M3/Evaluations/
├── answer_generation_test_cases.json (input)
├── test_answer_generation_part1.py (script)
├── test_answer_generation_part2.py (script)
├── answer_generation_openai_gpt-oss-120b.json
├── answer_generation_meta-llama_llama-4-maverick-17b-128e-instruct.json
├── answer_generation_qwen_qwen3-32b.json
├── answer_generation_all_models.json
├── answer_evaluation_openai_gpt-oss-120b.json
├── answer_evaluation_meta-llama_llama-4-maverick-17b-128e-instruct.json
├── answer_evaluation_qwen_qwen3-32b.json
├── answer_evaluation_all_models.json
└── answer_generation_evaluation_report.txt
```

## References

- LLM Judge methodology: Using LLMs to evaluate LLM outputs
- Evaluation criteria based on RAG best practices
- Context-grounded generation principles
