# Rate Limit Handling & Checkpoint Implementation

## Requirements

Both `test_answer_generation_part1.py` and `test_answer_generation_part2.py` need the following modifications:

### 1. 20-Second Delay Between LLM Calls
- Add `time.sleep(20)` after each successful LLM API call
- Skip the delay after the last query/evaluation in the loop

### 2. Rate Limit Detection
- Catch exceptions from LLM calls
- Check if error message contains "rate_limit" or "rate limit" (case-insensitive)
- If rate limit detected:
  - Print warning message
  - Save checkpoint (see below)
  - Raise exception to stop execution
  - Inform user to re-run the script

### 3. Checkpoint System
- **Checkpoint File Naming**:
  - Part 1: `checkpoint_{model_name_sanitized}.json`
  - Part 2: `checkpoint_eval_{model_name_sanitized}.json`
  - Sanitize model names: replace `/` with `_`

- **Checkpoint Contents**:
  ```json
  {
    "model_name": "openai/gpt-oss-120b",
    "results": {...},  // Part 1: results dict with 'answers' list
                       // Part 2: evaluations list
    "next_index": 5,   // Index of next item to process (0-based)
    "timestamp": "2025-12-13T10:30:00"
  }
  ```

- **Checkpoint Load on Start**:
  - Check if checkpoint file exists at beginning of processing
  - If exists:
    - Load checkpoint JSON
    - Extract previous results
    - Extract `next_index` to resume from
    - Print resume message
  - If not exists:
    - Initialize empty results
    - Set `start_index = 0`

- **Checkpoint Save**:
  - Save checkpoint after EACH successful query/evaluation
  - Save checkpoint when rate limit error occurs
  - For rate limit: set `next_index = i - 1` (retry current item)
  - For success: set `next_index = i` (move to next item)

- **Checkpoint Cleanup**:
  - Delete checkpoint file after ALL items successfully processed
  - Print confirmation message

### 4. Loop Modifications
- Add loop enumeration: `for i, item in enumerate(items, 1):`
- Add skip logic at start of loop:
  ```python
  if i - 1 < start_index:
      continue
  ```
- This skips already-processed items when resuming

## Implementation Details

### Part 1 (`test_answer_generation_part1.py`)

**Location**: `test_model()` method around line 72-140

**Changes Needed**:
1. Import `glob` at top
2. Add checkpoint loading before loop (after initializing llm_client)
3. Add skip logic at start of loop
4. Wrap LLM call in try-except with rate limit detection
5. Add checkpoint save after each successful answer
6. Add 20-second delay before next iteration (except last)
7. Add checkpoint deletion after statistics calculation

### Part 2 (`test_answer_generation_part2.py`)

**Location**: `evaluate_model_results()` method around line 151-230

**Changes Needed**:
1. Import `glob` and `time` at top
2. Add `time.sleep(20)` BEFORE LLM call in `evaluate_answer()` method
3. Modify exception handler in `evaluate_answer()` to propagate rate limit errors
4. Add checkpoint loading before loop (after loading model_data)
5. Add skip logic at start of loop
6. Wrap `evaluate_answer()` call in try-except with rate limit detection
7. Add checkpoint save after each successful evaluation
8. Add checkpoint deletion after statistics calculation

## Testing

After implementation:
1. Run Part 1: `python test_answer_generation_part1.py`
2. If rate limit occurs, checkpoint is saved
3. Re-run: `python test_answer_generation_part1.py` - should resume
4. After Part 1 completes, run Part 2: `python test_answer_generation_part2.py`
5. Same checkpoint behavior for Part 2

## Benefits

- **Resilience**: Can survive rate limits without losing progress
- **Cost Efficiency**: No need to re-run already completed queries
- **Time Savings**: Resume exactly where stopped
- **Safety**: Checkpoints saved after each item, minimal loss on failure
