# Quantitative Evaluation Tests

## Overview
This folder contains comprehensive quantitative tests for:
1. **Intent Classifier** - 170 test cases covering all 8 intents
2. **Entity Extractor** - 170 test cases covering all entity types

## Test Coverage

### Intent Classifier (170 cases)
- HotelSearch: 40 cases
- HotelRecommendation: 25 cases
- ReviewLookup: 20 cases
- LocationQuery: 15 cases
- VisaQuestion: 20 cases
- AmenityFilter: 25 cases
- CasualConversation: 15 cases
- GeneralQuestionAnswering: 10 cases

### Entity Extractor (170 cases)
- Tests entity extraction for all intents
- Validates correct entities, numeric values, and string matching
- Includes edge cases with typos and variations

## Running the Tests

### Option 1: Run Both Tests Together (Recommended)
```powershell
# PowerShell (Recommended)
cd M3\Evaluations
.\run_all_tests.ps1

# OR Command Prompt
cd M3\Evaluations
run_all_tests.bat
```

### Option 2: Run Tests Individually
```powershell
# Intent Classifier Test
cd M3\Evaluations
python test_intent_classifier.py

# Entity Extractor Test
cd M3\Evaluations
python test_entity_extractor.py
```

## Test Duration
- Each test: ~28 minutes (170 cases × 10 seconds delay)
- Total: ~56 minutes for both tests
- Delay prevents LLM API quota exhaustion

## Output Files
Results are automatically saved to:
- `intent_classifier_results.txt` - Full output with accuracy metrics
- `entity_extractor_results.txt` - Full output with accuracy metrics

## Output Format
Each result file contains:
1. Test progress (case-by-case execution)
2. Overall accuracy percentage
3. Per-intent/category accuracy breakdown with visual bars
4. Detailed failure cases (if any)

## Notes
- Tests use 10-second delays between LLM calls to avoid API rate limits
- All test output is written to files (nothing displayed during execution)
- Console shows only completion status and final accuracy
- Tests use real hotel names from hotels.csv and countries from visa.csv
